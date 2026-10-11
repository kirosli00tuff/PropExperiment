"""EconReviewer Phase B: Monte Carlo spread across three independent shock/cycle seeds of my simulator.

For each of the 60 configurations: the across-seed SD of the cycle mean net, P(pass), mean purchases and
cash per XFA (an estimate of the TOTAL Monte Carlo SD, pool sampling included) against the within-cycle SE
the grid reports (which conditions on the 20,000-path pools); and the grid's value against the three-seed
mean with a combined SE = sd_total x sqrt(1 + 1/3). Writes spread.json and spread.md.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports" / "stage_e19_verify"
runs = [json.loads((OUT / f).read_text()) for f in ("recompute_v2_se.json", "recompute_seed100.json", "recompute_seed200.json")]
res = json.loads((REPO / "reports" / "stage_e19_results.json").read_text())
EDGE = {"zero_k1": "zero_k1", "sharpe_0.5": "S0.5"}
grid = {(r["size"], r["path"], r["edge"], round(r["f"], 2)): r for r in res["records"]
        if r["headline"] and not r["b2f"] and not r["dll"] and r["pricing"] == "standard"}
rows = []
for i, m in enumerate(runs[0]["configs"]):
    key = (m["size"], m["path"], EDGE[m["edge"]], round(m["f"], 2))
    cs = [run["configs"][i] for run in runs]
    assert all((c["size"], c["path"], c["edge"], c["f"]) == (m["size"], m["path"], m["edge"], m["f"]) for c in cs)
    g = grid[key]
    nets = np.array([c["cycle"]["net"]["mean"] for c in cs]); se_in = np.mean([c["cycle"]["net"]["se"] for c in cs])
    pp = np.array([c["attempt"]["p_pass"] for c in cs]); pur = np.array([c["cycle"]["mean_purchases"] for c in cs])
    cash = np.array([c["xfa"]["mean_user_cash"]["mean"] for c in cs])
    sd_net = nets.std(ddof=1); comb = sd_net * math.sqrt(1 + 1 / 3)
    rows.append({"size": key[0], "path": key[1], "edge": key[2], "f": key[3],
                 "net_seeds": nets.round(1).tolist(), "net_mean3": float(nets.mean()), "net_sd_total": float(sd_net),
                 "net_se_within": float(se_in), "ratio_total_over_within": float(sd_net / se_in),
                 "grid_net": g["net_mean"], "grid_se": g["net_se"],
                 "z_grid_vs_mean3_total": float((g["net_mean"] - nets.mean()) / comb) if comb > 0 else None,
                 "ppass_seeds": pp.round(4).tolist(), "grid_ppass": g["att_p_pass"],
                 "ppass_sd_total": float(pp.std(ddof=1)), "ppass_se_binomial": float(math.sqrt(pp.mean() * (1 - pp.mean()) / 20000)),
                 "purch_seeds": pur.round(2).tolist(), "grid_purch": g["mean_purchases"], "purch_sd_total": float(pur.std(ddof=1)),
                 "purch_se_within": float(cs[0]["cycle"]["mean_purchases_se"]),
                 "cash_seeds": cash.round(1).tolist(), "grid_cash": g["xfa_mean_user_cash"], "cash_sd_total": float(cash.std(ddof=1)),
                 "cash_se_within": float(cs[0]["xfa"]["mean_user_cash"]["se"]),
                 "grid_within_3sd_total": bool(abs(g["net_mean"] - nets.mean()) <= 3 * comb)})
ratios = np.array([r["ratio_total_over_within"] for r in rows])
zs = np.array([r["z_grid_vs_mean3_total"] for r in rows])
summary = {"n_configs": len(rows), "ratio_total_over_within_net": {"median": float(np.median(ratios)), "min": float(ratios.min()),
                                                                    "max": float(ratios.max()),
                                                                    "by_size": {s: float(np.median([r["ratio_total_over_within"] for r in rows if r["size"] == s])) for s in ("50K", "100K", "150K")}},
           "grid_vs_mean3_abs_z_max": float(np.abs(zs).max()), "n_grid_beyond_3sd_total": int(sum(not r["grid_within_3sd_total"] for r in rows)),
           "purch_ratio_total_over_within_median": float(np.median([r["purch_sd_total"] / r["purch_se_within"] for r in rows])),
           "ppass_ratio_total_over_binomial_median": float(np.median([r["ppass_sd_total"] / r["ppass_se_binomial"] for r in rows])),
           "cash_ratio_total_over_within_median": float(np.median([r["cash_sd_total"] / r["cash_se_within"] for r in rows])),
           "sign_agreement_net": all((r["grid_net"] > 0) == (r["net_mean3"] > 0) for r in rows),
           "sign_disagreements": [(r["size"], r["path"], r["edge"], r["f"], r["grid_net"], r["net_seeds"]) for r in rows if (r["grid_net"] > 0) != (r["net_mean3"] > 0)]}
(OUT / "spread.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
md = ["# Three-seed spread of my recompute vs the grid (headline, DLL off, pricing standard, API included)", "",
      "net: cycle mean net ($). sd_total = SD across my 3 independent seeds (pools redrawn); se_within = the per-cycle SE the grid reports",
      "(conditions on the pools). z = (grid - mean of 3 seeds) / (sd_total x sqrt(4/3)).", "",
      "| size | path | edge | f | my 3 nets | grid net (se) | sd_total | se_within | ratio | z | P(pass) seeds / grid | purchases seeds / grid |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['size']} | {r['path']} | {r['edge']} | {r['f']:.2f} | {r['net_seeds']} | {r['grid_net']:.0f} ({r['grid_se']:.0f}) | "
              f"{r['net_sd_total']:.0f} | {r['net_se_within']:.0f} | {r['ratio_total_over_within']:.1f} | {r['z_grid_vs_mean3_total']:+.1f} | "
              f"{r['ppass_seeds']} / {r['grid_ppass']:.4f} | {r['purch_seeds']} / {r['grid_purch']:.2f} |")
md += ["", json.dumps(summary, indent=1)]
(OUT / "spread.md").write_text("\n".join(md) + "\n")
print(json.dumps(summary, indent=1))
