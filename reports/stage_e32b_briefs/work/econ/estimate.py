"""Full-run time estimate from the measured jobs (fixture timing run and the regression), written to timing.json.

Evaluations per job are fitted per curve type (primary, dir60) as a + b * cap (least squares on the fixture's
measured jobs), applied to every job of a full run on the fixture's shape (E.28's 116 computable non-NQ pairs,
sigma_h = sigma_1m sqrt(h)); E_dir curves (top 15 x 3) use the measured topstep|MNQ E_dir mean (the high-sigma
case, so an upper figure). Wall time = evaluations / measured throughput (evaluations per wall second on 6
workers, from the regression's full chunks). Usage: PYTHONPATH=. uv run python <this file>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))

import econ32b_inputs as I  # noqa: E402

FIRMS = {"topstep", "lucid", "tradeify", "mffu", "bulenox"}
N_EDIR_PAIRS = 15


def parts(tag: str) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted((WORK / "parts" / tag).glob("*.json"))]


def fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = 0.0 if sxx == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / sxx
    return my - b * mx, b


def chunk_throughput(log: Path) -> list[dict]:
    """Evaluations per wall second for each finished regression chunk (from the per-job lines and 'done:' lines)."""
    out, evals = [], 0
    for line in log.read_text().splitlines():
        m = re.search(r" (\d+) evals \|", line)
        if m:
            evals += int(m.group(1))
        d = re.search(r"done: wall ([\d.]+) s, peak PSS (\d+) MB", line)
        if d:
            out.append({"evals": evals, "wall_s": float(d.group(1)), "peak_pss_mb": int(d.group(2)),
                        "evals_per_s": evals / float(d.group(1))})
            evals = 0
    return out


def main() -> int:
    fx = parts("fixture")
    rows = [{"pair": r["job"]["pair"], "curve": r["job"]["curve"], "cap": r["job"]["k_max"] / 100,
             "evals": r["n_evaluations"], "runtime_s": r["runtime_s"],
             "s_per_eval": round(r["runtime_s"] / r["n_evaluations"], 2),
             "thresholds": {n: [c["mu_star_mkt"], c["mu10K_mkt"]] for n, c in r["cases"].items()}} for r in fx]
    coef = {}
    for curve in ("primary", "dir60"):
        sel = [r for r in rows if r["curve"] == curve]
        coef[curve] = fit([r["cap"] for r in sel], [r["evals"] for r in sel])
    edir = [r["evals"] for r in rows if r["curve"] in ("dir30", "dir120", "dir240")]
    edir_mean = sum(edir) / len(edir) if edir else 0.0
    f3 = json.loads((WORK / "fixture" / "F3_fixture.json").read_text())
    f4 = json.loads((WORK / "fixture" / "F4_fixture.json").read_text())
    jobs, meta, _ = I.jobs_from_facts(f3, f4, FIRMS)
    pred = sum(coef[j["curve"]][0] + coef[j["curve"]][1] * j["k_max"] / 100 for j in jobs)
    pred_edir = 3 * N_EDIR_PAIRS * edir_mean
    worst = sum(j["k_max"] // 10 + 1 for j in jobs)
    thr = chunk_throughput(WORK / "regress_run.log")
    eps = min(c["evals_per_s"] for c in thr) if thr else None
    reg = parts("regress")
    out = {"fixture_jobs": rows, "fit_evals_vs_cap": {k: {"a": a, "b": b} for k, (a, b) in coef.items()},
           "edir_mean_evals_measured": edir_mean, "full_run_shape": {"pairs": len(meta), "jobs": len(jobs)},
           "predicted_evals": {"pass1": round(pred), "pass2_edir_top15": round(pred_edir),
                               "worst_case_pass1_all_above_cap": worst},
           "regression": {"jobs": len(reg), "evals": sum(r["n_evaluations"] for r in reg),
                          "job_seconds": round(sum(r["runtime_s"] for r in reg), 1), "chunks": thr},
           "throughput_evals_per_wall_s_6_workers": eps}
    if eps:
        out["predicted_wall_h"] = {"pass1": round(pred / eps / 3600, 2), "pass2": round(pred_edir / eps / 3600, 2),
                                   "pass1_worst_case": round(worst / eps / 3600, 2)}
    (WORK / "timing.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("fixture_jobs", "regression")}, indent=1))
    print("regression:", {k: v for k, v in out["regression"].items() if k != "chunks"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
