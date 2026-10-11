"""EconReviewer Phase B: compare the blind recompute with the grid's headline records.

Reads reports/stage_e19_verify/recompute_v2_se.json (same seeds and means as recompute.json, plus SEs) and
reports/stage_e19_results.json; matches on size, path, edge (zero_k1 / S0.5), f; headline records only
(tail bootstrap, random, all products, d8, continuous, variant base, dll off, pricing standard, b2f off).
Writes compare.json and compare.md (one row per metric and configuration with both values, the combined
SE and the z-score; a difference counts beyond 3 combined SEs).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports" / "stage_e19_verify"
mine = json.loads((OUT / "recompute_v2_se.json").read_text())
res = json.loads((REPO / "reports" / "stage_e19_results.json").read_text())
N = res["settings"]["n_paths"]; NC = res["settings"]["n_cycles"]
EDGE_MAP = {"zero_k1": "zero_k1", "sharpe_0.5": "S0.5"}

idx = {}
for r in res["records"]:
    if r["headline"] and not r["b2f"] and not r["dll"] and r["pricing"] == "standard":
        idx[(r["size"], r["path"], r["edge"], round(r["f"], 2))] = r


def binom_se(p: float, n: int) -> float:
    return math.sqrt(max(p * (1 - p), 0.0) / n)


rows = []
for m in mine["configs"]:
    key = (m["size"], m["path"], EDGE_MAP[m["edge"]], round(m["f"], 2))
    g = idx[key]
    mn, mx, mc = m["attempt"], m["xfa"], m["cycle"]
    pairs = [
        # name, mine, grid, se_mine, se_grid
        ("P(pass)", mn["p_pass"], g["att_p_pass"], mn["p_pass_se"], binom_se(g["att_p_pass"], N)),
        ("mean attempt length", mn["mean_length"], g["att_mean_length"], None, None),
        ("timeout share", mn["timeout_share"], g["att_timeout_share"], binom_se(mn["timeout_share"], N),
         binom_se(g["att_timeout_share"], N)),
        ("user cash per XFA", mx["mean_user_cash"]["mean"], g["xfa_mean_user_cash"], mx["mean_user_cash"]["se"],
         mx["mean_user_cash"]["se"]),  # grid gives no SE: assume the same SE
        ("P(any payout)", mx["p_any_payout"], g["xfa_p_any_payout"], mx["p_any_payout_se"],
         binom_se(g["xfa_p_any_payout"], N)),
        ("cycle net mean", mc["net"]["mean"], g["net_mean"], mc["net"]["se"], g["net_se"]),
        ("cycle net ex API", mc["net_noapi"]["mean"], g["net_ex_api_mean"], mc["net_noapi"]["se"], g["net_ex_api_se"]),
        ("P(no payout)", mc["p_no_payout"], g["p_no_payout"], mc["p_no_payout_se"], binom_se(g["p_no_payout"], NC)),
        ("mean purchases", mc["mean_purchases"], g["mean_purchases"], mc["mean_purchases_se"], mc["mean_purchases_se"]),
        ("net per purchase", mc["net_per_purchase"], g["net_per_purchase"], None, None),
        ("mean cycle days", mc["mean_length"], g["mean_cycle_days"], None, None),
        ("mean API fee", mc["mean_api"], g["fees_api"], None, None),
        ("mean activation fee", mc["mean_fee_act"], g["fees_activation"], None, None),
        ("mean sub fees (P+R)", mc["mean_fee_sub"], g["fees_start"] + g["fees_rebill"] + g["fees_reset"], None, None),
        ("P(reach XFA)", mc["p_reach_xfa"], g["p_reaches_xfa"], binom_se(mc["p_reach_xfa"], NC),
         binom_se(g["p_reaches_xfa"], NC)),
        ("funded XFA net of activation", m["funded_xfa_net_of_activation"], g["per_funded_xfa"],
         mx["mean_user_cash"]["se"], mx["mean_user_cash"]["se"]),
    ]
    for name, a, b, sa, sb in pairs:
        if sa is None:
            z = None; comb = None
        else:
            comb = math.sqrt(sa ** 2 + sb ** 2)
            z = (a - b) / comb if comb > 0 else (0.0 if a == b else float("inf"))
        rows.append({"size": m["size"], "path": m["path"], "edge": key[2], "f": key[3], "metric": name,
                     "mine": a, "grid": b, "diff": a - b, "rel_diff": (a - b) / b if b else None,
                     "combined_se": comb, "z": z,
                     "beyond_3se": (abs(z) > 3) if z is not None else None})

n_tested = sum(1 for r in rows if r["z"] is not None)
n_beyond = sum(1 for r in rows if r["beyond_3se"])
summary = {"n_configs": len(mine["configs"]), "n_metric_rows": len(rows), "n_with_se": n_tested,
           "n_beyond_3se": n_beyond,
           "beyond": [r for r in rows if r["beyond_3se"]],
           "max_abs_z_by_metric": {},
           "max_rel_diff_no_se": {}}
for r in rows:
    if r["z"] is not None:
        cur = summary["max_abs_z_by_metric"].get(r["metric"], 0.0)
        summary["max_abs_z_by_metric"][r["metric"]] = max(cur, abs(r["z"]))
    elif r["rel_diff"] is not None:
        cur = summary["max_rel_diff_no_se"].get(r["metric"], 0.0)
        summary["max_rel_diff_no_se"][r["metric"]] = max(cur, abs(r["rel_diff"]))
(OUT / "compare.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))

# markdown: the seven brief metrics per configuration
md = ["# Blind recompute vs grid (headline: bootstrap, random, d8, continuous, DLL off, pricing standard, API included, policy max)",
      "", f"Mine: {mine['n_paths']} attempts/XFAs, {mine['n_cycles']} cycles, seeds {mine['seeds']}. Grid: {N} paths, {NC} cycles.",
      "z = (mine - grid) / sqrt(se_mine^2 + se_grid^2). Grid SEs: binomial for shares, reported SE for nets; the grid gives",
      "no SE for cash per XFA or purchases, so my SE is used for both sides there.", "",
      "| size | path | edge | f | P(pass) mine/grid (z) | cash/XFA (z) | P(any) (z) | cycle net mine/grid (z) | P(no pay) (z) | purchases (z) | net/purchase mine/grid |",
      "|---|---|---|---|---|---|---|---|---|---|---|"]
by_cfg: dict[tuple, dict] = {}
for r in rows:
    by_cfg.setdefault((r["size"], r["path"], r["edge"], r["f"]), {})[r["metric"]] = r


def cell(r, fmt="{:.3f}"):
    return f"{fmt.format(r['mine'])}/{fmt.format(r['grid'])} ({r['z']:+.1f})" if r["z"] is not None else \
        f"{fmt.format(r['mine'])}/{fmt.format(r['grid'])}"


for key in sorted(by_cfg, key=lambda k: (["50K", "100K", "150K"].index(k[0]), k[1], k[2], k[3])):
    c = by_cfg[key]
    md.append(f"| {key[0]} | {key[1]} | {key[2]} | {key[3]:.2f} | {cell(c['P(pass)'], '{:.4f}')} | "
              f"{cell(c['user cash per XFA'], '{:.0f}')} | {cell(c['P(any payout)'])} | {cell(c['cycle net mean'], '{:.0f}')} | "
              f"{cell(c['P(no payout)'])} | {cell(c['mean purchases'], '{:.2f}')} | {cell(c['net per purchase'], '{:.1f}')} |")
md += ["", f"Rows with a z-score: {n_tested}; beyond 3 combined SEs: {n_beyond}.",
       "Max |z| by metric: " + ", ".join(f"{k} {v:.2f}" for k, v in summary["max_abs_z_by_metric"].items()),
       "Max |rel diff| for metrics without an SE: " + ", ".join(f"{k} {v:.4f}" for k, v in summary["max_rel_diff_no_se"].items())]
(OUT / "compare.md").write_text("\n".join(md) + "\n")
print(f"configs {len(mine['configs'])}, rows {len(rows)}, with SE {n_tested}, beyond 3 SE {n_beyond}")
print("max |z| by metric:", {k: round(v, 2) for k, v in summary["max_abs_z_by_metric"].items()})
print("max |rel| no-SE:", {k: round(v, 4) for k, v in summary["max_rel_diff_no_se"].items()})
for r in summary["beyond"]:
    print("  BEYOND:", r["size"], r["path"], r["edge"], r["f"], r["metric"], round(r["mine"], 4), round(r["grid"], 4), "z", round(r["z"], 2))
