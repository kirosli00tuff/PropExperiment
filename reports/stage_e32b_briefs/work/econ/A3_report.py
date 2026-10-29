"""A3 collector: pairs/*.json -> reports/stage_e28_briefs/A3_econ.json and the generated tables (A3_tables.md).

No scoring: the file carries the spec's section 3 economic inputs (mu*_lim, mu*_mkt, mu10K, cost per attempt,
room and the limits) per (firm, candidate) pair, with provenance, flags and sensitivities.
Usage: uv run python A3_report.py
"""

from __future__ import annotations

if __name__ == "__main__":  # E.32b guard (added to the copy only)
    raise SystemExit("E.32b copy of an E.28 script: reference only (it writes E.28 paths or regenerates "
                     "A3_inputs.json); do not run")

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

WORK = Path(__file__).resolve().parent
REPO = WORK.parents[3]
sys.path.insert(0, str(WORK))

import A3_funnel as F  # noqa: E402
import A3_models as M  # noqa: E402
from A3_run import INPUTS, PAIRS_DIR, _fingerprint  # noqa: E402

OUT_JSON = REPO / "reports" / "stage_e28_briefs" / "A3_econ.json"
TABLES = WORK / "A3_tables.md"
SPEC = REPO / "reports" / "stage_e28_ranking_spec.md"
REQUIRED = ("firm", "code", "plan", "F_rt_usd", "F_rt_ticks", "F_rt_source", "S_rt_ticks", "v", "sigma_T",
            "mu_star_lim", "mu_star_mkt", "mu10K", "cost_per_attempt_usd", "MLL_usd", "DLL_usd", "DLL_ticks",
            "position_limit", "room", "flags")
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _f(x: Any, nd: int = 2) -> str:
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    return f"{x:,.{nd}f}"


def load_pairs(prefix: str = "") -> tuple[list[dict[str, Any]], list[str]]:
    fp = _fingerprint()
    inputs = json.loads(INPUTS.read_text())
    recs, missing = [], []
    for p in inputs["pairs"]:
        path = PAIRS_DIR / f"{prefix}{p['firm']}__{p['code']}.json"
        if not path.exists():
            missing.append(f"{p['firm']}:{p['code']}")
            continue
        r = json.loads(path.read_text())
        if r.get("fingerprint") != fp:
            missing.append(f"{p['firm']}:{p['code']} (stale)")
            continue
        recs.append(r)
    return recs, missing


def check_below(r: dict[str, Any], evals: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Do all cached evaluations below each threshold lie on the negative side (EV < 0, P10K < 0.5)?"""
    if not r.get("computed"):
        return None
    out = {}
    for name, key, cost, neg in (("mu_star_lim", "ev", r["c_lim_ticks"], lambda e: e["ev"] < 0),
                                 ("mu_star_mkt", "ev", r["c_mkt_ticks"], lambda e: e["ev"] < 0),
                                 ("mu10K", "p10k", r["c_lim_ticks"], lambda e: e["p10k"] < 0.5)):
        mu = r[name]
        lim = 4.0 + 1e-9 if isinstance(mu, str) else mu - 1e-9
        below = [e for e in evals if e["d"] + cost < lim]
        out[name] = {"n_cached_below": len(below), "all_negative_side": all(neg(e) for e in below)}
    return out


GRID_DIR = WORK / "gridcheck"


def grid_block(r: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Attach the grid confirmation (A3_gridcheck.py) and apply any correction it found (the spec's definition:
    the smallest grid mu with f >= 0). Returns the block and the names of corrected thresholds."""
    path = GRID_DIR / f"{r['firm']}__{r['code']}.json"
    if not r.get("computed") or not path.exists():
        return None, []
    g = json.loads(path.read_text())
    if g.get("fingerprint") != r.get("fingerprint"):
        return None, []
    corrected = []
    for name, chk in g["checks"].items():
        k = chk.get("corrected_k")
        if k is None:
            continue
        r[f"{name}_bisection"] = r[name]
        r[name] = round((k + 100 if name == "mu_star_mkt" else k) * 0.01, 2)
        corrected.append(name)
    block = {"file": str(path.relative_to(REPO)), "n_points": g["n_points"],
             "n_new_evaluations": g["n_new_evaluations"], "n_dense_filled_gaps": g["n_dense_filled_gaps"],
             "repro_of_stored_point": g["repro"], "ev_decreasing_steps_on_lattice": g["ev_decreasing_steps_on_lattice"],
             "checks": g["checks"], "runtime_s": g["runtime_s"],
             "all_confirmed": all(c.get("confirmed", True) for c in g["checks"].values())}
    return block, corrected


def _tests_line() -> str | None:
    out = WORK / "test_A3_econ.out"
    if not out.exists():
        return None
    return next((ln.strip() for ln in out.read_text().splitlines() if " passed" in ln or " failed" in ln), None)


def _grid_summary(recs: list[dict[str, Any]]) -> dict[str, Any]:
    comp = [r for r in recs if r.get("computed")]
    gbs = [r["grid_confirmation"] for r in comp if r.get("grid_confirmation")]
    return {"pairs_computed": len(comp), "pairs_checked": len(gbs),
            "pairs_all_thresholds_confirmed": sum(1 for g in gbs if g["all_confirmed"]),
            "pairs_with_correction": [f"{r['firm']}:{r['code']}" for r in comp
                                      if any(k.endswith("_bisection") for k in r)],
            "repro_equal": sum(1 for g in gbs if g["repro_of_stored_point"] and g["repro_of_stored_point"]["equal"]),
            "repro_checked": sum(1 for g in gbs if g["repro_of_stored_point"]),
            "points_evaluated_total": sum(g["n_points"] for g in gbs),
            "new_evaluations_total": sum(g["n_new_evaluations"] for g in gbs),
            "pairs_with_ev_decreasing_steps": sum(1 for g in gbs if g["ev_decreasing_steps_on_lattice"] > 0)}


def firm_block() -> dict[str, Any]:
    out = {}
    for name, m in M.firm_models().items():
        t = m.terms
        out[name] = {
            "plan": m.plan, "evaluation_trailing": m.eval_trail, "attempt_max_days": m.attempt_max_days,
            "evaluation_rules": {k: getattr(m.eval_rules.combine, k) for k in (
                "profit_target_usd", "mll_usd", "mll_floor_max_rel_usd", "dll_usd", "consistency_type",
                "consistency_frac", "min_trading_days")},
            "evaluation_dll_usd": m.eval_dll_usd,
            "funded_rules": ("prop_econ simulate_xfas, E.19 record (standard path)" if m.funded is None
                             else m.funded.__dict__),
            "fees": {"start_usd": t.monthly_usd, "rebill_usd": t.monthly_usd if t.period_days < 10**6 else None,
                     "rebill_period_trading_days": t.period_days if t.period_days < 10**6 else None,
                     "reset_usd": t.reset_usd, "activation_usd": t.activation_usd, "split": t.split,
                     "rebill_adds_reset_credit": t.rebill_adds_credit, "reset_pushes_rebill": t.reset_pushes_rebill,
                     "attempt_cap": t.attempt_cap, "back2funded": t.b2f_on},
            "api_monthly_usd": m.api_monthly_usd, "api_period_trading_days": m.api_period_days,
            "MLL_usd": m.mll_usd, "DLL_usd": m.dll_usd,
            "mapping": [{"rule": a, "firm_value": b, "model_form": c, "kind": d} for a, b, c, d in M.MAPPING[name]],
        }
    return out


def _grid_txt(r: dict[str, Any]) -> str:
    g = r.get("grid_confirmation")
    if not g:
        return "-"
    if any(k.endswith("_bisection") for k in r):
        return "corrected"
    return f"ok ({g['n_points']} pts)" if g["all_confirmed"] else "NOT confirmed"


def results_table(recs: list[dict[str, Any]]) -> list[str]:
    lines = []
    for firm in FIRMS:
        rows = sorted((r for r in recs if r["firm"] == firm), key=lambda r: r["code"])
        if not rows:
            continue
        lines += [f"### {firm}: {rows[0]['plan']}", "",
                  "| code | v USD | F_rt USD | F_rt ticks | sigma_T | mu*_lim | mu*_mkt | mu10K | cost/attempt USD |"
                  " room | DLL ticks | pos. limit | grid check | sensitivities | flags |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            sens = r.get("sensitivities") or {}
            s_txt = []
            if "mu_star_lim_ex_api" in sens:
                s_txt.append(f"ex-API mu*_lim {_f(sens['mu_star_lim_ex_api'])}")
            if "alt_fee" in sens:
                s_txt.append(f"fee {_f(sens['alt_fee']['F_rt_usd'])}: mu*_lim {_f(sens['alt_fee']['mu_star_lim'])}")
            if "S_rt_mean" in sens:
                s_txt.append(f"S_rt {_f(sens['S_rt_mean']['S_rt_ticks'], 3)}: mu*_mkt "
                             f"{_f(sens['S_rt_mean']['mu_star_mkt'])}")
            short = [fl.split(":")[0] for fl in r["flags"] if not fl.startswith(("fee conflict", "fee: commission",
                                                                                  "S_rt default"))]
            lines.append(
                f"| {r['code']} | {_f(r['v'], 4)} | {_f(r['F_rt_usd'])} | {_f(r['F_rt_ticks'], 3)} | "
                f"{_f(r['sigma_T'], 2)} | {_f(r['mu_star_lim'])} | {_f(r['mu_star_mkt'])} | {_f(r['mu10K'])} | "
                f"{_f(r['cost_per_attempt_usd'], 1)} | {_f(r['room'], 2)} | {_f(r['DLL_ticks'], 1)} | "
                f"{_f(r['position_limit'], 0)} | {_grid_txt(r)} | {'; '.join(s_txt)} | {'; '.join(short)} |")
        lines.append("")
    return lines


def main() -> int:
    recs, missing = load_pairs()
    inputs = json.loads(INPUTS.read_text())
    clean = []
    for r in recs:
        r = dict(r)
        evals = r.pop("evaluations", [])
        r["n_evaluations"] = len(evals)
        r["check_below"] = check_below(r, evals)
        r["evaluations_file"] = str((PAIRS_DIR / f"{r['firm']}__{r['code']}.json").relative_to(REPO))
        gb, corrected = grid_block(r)
        r["grid_confirmation"] = gb
        if r.get("computed") and gb is None:
            missing.append(f"{r['firm']}:{r['code']} (grid check)")
        if corrected:
            r["flags"] = [*r["flags"], f"threshold corrected by the grid check: {', '.join(corrected)}"]
        clean.append({**{k: r.get(k) for k in REQUIRED}, **{k: v for k, v in r.items() if k not in REQUIRED}})
    mono = json.loads((WORK / "A3_monotone.json").read_text()) if (WORK / "A3_monotone.json").exists() else None
    regress = json.loads((WORK / "A3_regress_e19.json").read_text())
    opt2 = [json.loads(p.read_text()) for p in sorted(PAIRS_DIR.glob("opt2__*.json"))]
    doc = {
        "stage": "E.28", "part": "A, Layer 2 economics (spec section 3)", "worker": "EconCoder-OpusXHigh",
        "generated_pdt": subprocess.run(["date", "+%Y-%m-%d %H:%M:%S %Z"], capture_output=True, text=True,
                                        env={"TZ": "America/Vancouver"}).stdout.strip(),
        "spec": {"path": str(SPEC.relative_to(REPO)), "sha256": sha(SPEC)},
        "fingerprint": _fingerprint(),
        "model": {"round_trips_per_day": F.T_RT, "size": 1, "paths_per_pool": F.N_PATHS, "cycles": F.N_CYCLES,
                  "campaign_replications": F.N_REPS, "horizon_trading_days": F.HORIZON,
                  "attempt_cap": F.ATTEMPT_CAP, "max_payout_records": F.MAX_PAYOUTS,
                  "campaign_days": F.CAMPAIGN_DAYS, "campaign_target_usd": F.CAMPAIGN_TARGET,
                  "mu_grid": "0, 0.01, ..., 4 ticks", "base_seed": F.BASE_SEED,
                  "daily_pnl": "normal, mean T (mu - c) v, sd sqrt(T) sigma_T v; intraday path a Brownian bridge "
                               "to the close (E.19 normal source); worst = bridge minimum",
                  "c_lim": "F_rt / v", "c_mkt": "F_rt / v + S_rt"},
        "rules_records": {
            "topstep": {"path": "reports/stage_e19_rules.json", "sha256": sha(REPO / "reports/stage_e19_rules.json"),
                        "note": "refreshed by Stage E.26 Task 4 (02:20-02:25 PDT, reports/stage_e26_STATE.md); used "
                                "as the brief directs; the simulator's values are unchanged from E.19's record"},
            **{f: {"path": f"reports/stage_e28_briefs/A2_firm_{f}.json",
                   "sha256": sha(REPO / f"reports/stage_e28_briefs/A2_firm_{f}.json")}
               for f in ("lucid", "tradeify", "mffu", "bulenox")},
            "platforms": {"path": "reports/stage_e28_briefs/A2_platforms.json",
                          "note": "no API or platform fee in it; firm API fees from the firm records"}},
        "open_choices_applied": {
            "OC-1": "sigma_1m and R_d in ticks for candidates without owned window data from the owned sibling on "
                    "the same price: x_ticks(cand) = x_ticks(sibling) x tick(sibling) / tick(cand); volume never "
                    "transfers; SIL, SI, MET, ETH and the micro yields unknown (no A1 value)",
            "OC-2": "ADV: A0 v_0 median for owned roots, otherwise A1's published figures; both kept where both "
                    "exist (candidates block); ADV is not an input of the economic model"},
        "firm_models": firm_block(),
        "candidates": {c: {k: v for k, v in row.items() if k not in ("S_rt_entries",)}
                       for c, row in inputs["candidates"].items()},
        "pairs": sorted(clean, key=lambda r: (r["firm"], r["code"])),
        "sensitivity_bulenox_option2": [{k: r.get(k) for k in ("code", "mu_star_lim", "mu_star_mkt", "mu10K",
                                                                "cost_per_attempt_usd", "flags")} for r in opt2],
        "checks": {"regression_e19": regress, "monotone_scan": mono, "missing_pairs": missing,
                   "unit_tests": _tests_line(),
                   "grid_confirmation_summary": _grid_summary(clean)},
        "runtimes": json.loads((WORK / "A3_runtimes.json").read_text()) if (WORK / "A3_runtimes.json").exists()
        else None,
    }
    OUT_JSON.write_text(json.dumps(doc, indent=1))
    TABLES.write_text("\n".join(results_table(clean)))
    n_comp = sum(1 for r in clean if r.get("computed"))
    print(f"{len(clean)} pairs ({n_comp} computed), missing {len(missing)}: {missing}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
