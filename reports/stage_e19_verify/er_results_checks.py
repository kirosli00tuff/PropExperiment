"""EconReviewer Phase B: checks on reports/stage_e19_results.json for the verdict questions.

1 zero-edge sign across every record; 2 S0 (costless zero drift) nets; 3 optimum-f pattern per family;
4 diagnostic f gaps; 5 churn arithmetic and a reset-inclusive alternative; 6 normal-tail twins;
7 break-even and optimum recomputed from the saved per-cycle nets. Writes results_checks.json.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports" / "stage_e19_verify"
RES = json.loads((REPO / "reports" / "stage_e19_results.json").read_text())
RULES = json.loads((REPO / "reports" / "stage_e19_rules.json").read_text())
recs = RES["records"]
BAND = (0.05, 0.1, 0.15, 0.2, 0.25)
out: dict = {}

# 1 ---- zero-edge sign
zero = [r for r in recs if r["edge"] in ("zero_k1", "zero_k3")]
pos = [r for r in zero if r["net_mean"] > 0]
pos_ex = [r for r in zero if r["net_ex_api_mean"] > 0]
head_band_zero = [r for r in zero if r["headline"] and r["f"] in BAND]
min_t = min(-r["net_mean"] / r["net_se"] for r in head_band_zero)
worst = max(head_band_zero, key=lambda r: r["net_mean"])
out["zero_edge_sign"] = {
    "n_zero_records": len(zero), "n_positive_net": len(pos),
    "positive_list": [(r["job_id"], r["path"], r["pricing"], r["b2f"], round(r["net_mean"], 1)) for r in pos],
    "n_positive_net_ex_api": len(pos_ex),
    "positive_ex_api_list": [(r["job_id"], r["path"], r["pricing"], r["b2f"], round(r["net_ex_api_mean"], 1)) for r in pos_ex],
    "headline_band_min_t_below_zero": round(min_t, 1),
    "headline_band_least_negative": (worst["job_id"], worst["path"], worst["pricing"], worst["b2f"],
                                     round(worst["net_mean"], 1), round(worst["net_se"], 1)),
    "ph_voluntary_close_positive": [(r["job_id"], r["path"], r["pricing"], round(r["ph_voluntary_close_mean"], 1))
                                    for r in zero if r.get("ph_voluntary_close_mean") is not None and r["ph_voluntary_close_mean"] > 0],
    "ph_copy_traded_positive_n": sum(1 for r in zero if r.get("ph_copy_traded_mean") is not None and r["ph_copy_traded_mean"] > 0),
}

# 2 ---- S0 nets at headline band f
s0 = [r for r in recs if r["headline"] and r["edge"] == "S0" and not r["b2f"]]
out["S0_costless_zero_drift"] = {
    "n": len(s0), "n_positive": sum(r["net_mean"] > 0 for r in s0),
    "positive_band": sorted([(r["size"], r["path"], r["dll"], r["pricing"], r["f"], round(r["net_mean"], 1), round(r["net_se"], 1))
                             for r in s0 if r["net_mean"] > 0 and r["f"] in BAND]),
    "positive_diag": sorted([(r["size"], r["path"], r["dll"], r["pricing"], r["f"], round(r["net_mean"], 1), round(r["net_se"], 1))
                             for r in s0 if r["net_mean"] > 0 and r["f"] not in BAND]),
    "50K_f0.25_dll_off": sorted([(r["path"], r["pricing"], round(r["net_mean"], 1), round(r["net_se"], 1))
                                 for r in s0 if r["size"] == "50K" and r["f"] == 0.25 and not r["dll"]]),
}

# 3 ---- optimum f pattern per family (band only)
groups: dict[tuple, dict[float, dict]] = defaultdict(dict)
for r in recs:
    if r["f"] in BAND and not r["b2f"]:
        groups[(r["family"], r["variant"], r["size"], r["path"], r["dll"], r["pricing"], r["edge"])][r["f"]] = r
argmax = Counter(); non25 = []
mono = Counter()
for key, d in groups.items():
    if len(d) < 3:
        continue
    fs = sorted(d)
    best = max(fs, key=lambda f: (d[f]["net_mean"], -f))
    argmax[(key[0], best)] += 1
    nets = [d[f]["net_mean"] for f in fs]
    mono[(key[0], all(np.diff(nets) > 0))] += 1
    if best != 0.25:
        non25.append((*key, best, [round(d[f]["net_mean"]) for f in fs]))
out["optimum_band_pattern"] = {
    "n_groups": sum(1 for d in groups.values() if len(d) >= 3),
    "argmax_counts_by_family": {f"{k[0]}@{k[1]}": v for k, v in sorted(argmax.items())},
    "strictly_increasing_counts": {f"{k[0]}:{k[1]}": v for k, v in sorted(mono.items())},
    "non_0.25_groups": non25,
}

# 4 ---- diagnostic gaps (derived.optimum_all_f)
diag = RES["derived"]["optimum_all_f"]
d35 = [(r["f0.35_minus_f0.25"]["diff"], r["f0.35_minus_f0.25"]["paired_se"]) for r in diag if "all_f" in r]
d50 = [(r["f0.50_minus_f0.25"]["diff"], r["f0.50_minus_f0.25"]["paired_se"]) for r in diag if "all_f" in r]
best_all = Counter(r["all_f"]["best_f"] for r in diag if "all_f" in r)
neg50 = [(r["size"], r["path"], r["dll"], r["pricing"], r["edge"], round(r["f0.50_minus_f0.25"]["diff"]), round(r["f0.50_minus_f0.25"]["paired_se"]))
         for r in diag if "all_f" in r and r["f0.50_minus_f0.25"]["diff"] < 0]
out["diagnostic_f"] = {
    "n": len(d35),
    "f0.35_gt_f0.25": sum(d > 0 for d, _ in d35), "f0.35_gt_3se": sum(d > 3 * s for d, s in d35),
    "f0.50_gt_f0.25": sum(d > 0 for d, _ in d50), "f0.50_gt_3se": sum(d > 3 * s for d, s in d50),
    "best_of_all_7_counts": {str(k): v for k, v in sorted(best_all.items())},
    "f0.50_below_f0.25_cases": neg50,
    "by_edge_mean_gap35": {e: round(float(np.mean([r["f0.35_minus_f0.25"]["diff"] for r in diag if "all_f" in r and r["edge"] == e])), 1)
                           for e in sorted({r["edge"] for r in diag})},
    "by_edge_mean_gap50": {e: round(float(np.mean([r["f0.50_minus_f0.25"]["diff"] for r in diag if "all_f" in r and r["edge"] == e])), 1)
                           for e in sorted({r["edge"] for r in diag})},
}

# 5 ---- churn arithmetic and the reset-inclusive alternative
err = []; alt_rates = []; alt_rows = []
for r in recs:
    if "churn_combine_days_mean" not in r:
        continue
    rate = 21 * r["mean_purchases"] / r["churn_combine_days_mean"]
    err.append(abs(rate - r["purchases_per_21_combine_days"]))
    R = RULES["sizes"][r["size"]]["combine"]["reset_price_usd"][r["pricing"]]
    paid_resets = r["fees_reset"] / R
    n_fails = r["mean_attempts"] - r["p_reaches_xfa"]
    credit_resets = n_fails - paid_resets
    alt = 21 * (r["mean_purchases"] + credit_resets) / r["churn_combine_days_mean"]
    alt_rates.append(alt)
    if r["headline"] and not r["b2f"] and not r["dll"] and r["pricing"] == "standard" and r["edge"] in ("zero_k1", "S0.5"):
        alt_rows.append((r["size"], r["path"], r["edge"], r["f"], round(r["purchases_per_21_combine_days"], 2),
                         round(r["combine_breaches_per_21_combine_days"], 2), round(alt, 2),
                         round(r["slots5_purchases_per_21_days_first252"], 2), round(5 * alt, 2)))
alt_rates = np.array(alt_rates)
out["churn"] = {
    "max_abs_err_purchases_rate": max(err), "n_records": len(err),
    "purchases_rate_range": [round(min(r["purchases_per_21_combine_days"] for r in recs), 2),
                             round(max(r["purchases_per_21_combine_days"] for r in recs), 2)],
    "note": "alt = (paid purchases + credit resets) per 21 Combine-phase days per account = start + rebills + every reset",
    "alt_rate_range": [round(float(alt_rates.min()), 2), round(float(alt_rates.max()), 2)],
    "alt_rate_gt_2_share": float((alt_rates > 2).mean()), "alt_rate_gt_4_share": float((alt_rates > 4).mean()),
    "alt_rate_gt_2_band_headline_f": sorted({(r["f"]) for r, a in zip([x for x in recs if "churn_combine_days_mean" in x], alt_rates)
                                             if a > 2 and r["headline"] and r["f"] in BAND}),
    "headline_rows (size, path, edge, f, purch/21d, breaches/21d, alt/21d, 5slot_first252, 5x alt)": alt_rows,
}

# 6 ---- normal-tail twins at zero_k1 and S0.5 (dll off, pricing standard, b2f off)
idx_h = {(r["size"], r["path"], r["edge"], r["f"]): r for r in recs
         if r["headline"] and not r["b2f"] and not r["dll"] and r["pricing"] == "standard"}
tw = []
for r in recs:
    if r["family"] == "tail_normal" and not r["b2f"] and r["pricing"] == "standard" and r["edge"] in ("zero_k1", "S0.5", "S0"):
        h = idx_h[(r["size"], r["path"], r["edge"], r["f"])]
        tw.append((r["size"], r["path"], r["edge"], r["f"], round(h["net_mean"]), round(r["net_mean"]),
                   round((r["net_mean"] - h["net_mean"]) / math.sqrt(r["net_se"] ** 2 + h["net_se"] ** 2), 1)))
out["normal_tail_twins"] = {"n": len(tw), "n_sign_flip": sum((a > 0) != (b > 0) for *_, a, b, _z in tw),
                            "rows (size, path, edge, f, boot net, normal net, z)": sorted(tw)}

# 7 ---- break-even and optimum recomputed
be = RES["derived"]["break_even"]
S = [0, 0.15, 0.3, 0.5, 0.75, 1.0]
be_err = []
for row in be:
    for f in BAND:
        ms = [idx_all["net_mean"] for idx_all in [next(x for x in recs if x["headline"] and not x["b2f"] and x["size"] == row["size"]
                                                        and x["path"] == row["path"] and x["dll"] == row["dll"] and x["pricing"] == row["pricing"]
                                                        and x["edge"] == e and x["f"] == f) for e in ["S0", "S0.15", "S0.3", "S0.5", "S0.75", "S1"]]]
        if ms[0] > 0:
            mine = "< 0"
        else:
            mine = f"> {S[-1]:g}"
            for i in range(1, 6):
                if ms[i] >= 0:
                    mine = S[i - 1] + (0 - ms[i - 1]) * (S[i] - S[i - 1]) / (ms[i] - ms[i - 1]); break
        theirs = row[f"f{f:.2f}"]
        be_err.append(0.0 if isinstance(mine, str) or isinstance(theirs, str) else abs(mine - theirs)
                      if not (isinstance(mine, str) ^ isinstance(theirs, str)) else 9.9)
out["break_even_recompute"] = {"n": len(be_err), "max_abs_err": max(be_err)}
# optimum from the saved nets (one cell)
runs = REPO / "reports" / "stage_e19_runs"
job = "bootstrap-random-all-d8-continuous__50K__{e}__f{f:.2f}__dll0__base.npz"
nets = {}
for f in BAND:
    with np.load(runs / job.format(e="zero_k1", f=f)) as z:
        nets[f] = z["standard|standard"]
means = {f: float(v.mean()) for f, v in nets.items()}
best = max(BAND, key=lambda f: means[f]); runner = sorted(BAND, key=lambda f: -means[f])[1]
d = nets[best] - nets[runner]
their = next(r for r in RES["derived"]["optimum_band"] if r["size"] == "50K" and r["path"] == "standard" and not r["dll"]
             and r["pricing"] == "standard" and r["edge"] == "zero_k1")
out["optimum_recompute_50K_std_zero"] = {
    "mine": {"best_f": best, "mean": means[best], "se": float(nets[best].std(ddof=1) / math.sqrt(nets[best].size)),
             "runner_up": runner, "gap": float(d.mean()), "gap_paired_se": float(d.std(ddof=1) / math.sqrt(d.size))},
    "theirs": {k: their[k] for k in ("best_f", "mean", "se", "runner_up_f", "gap", "gap_paired_se")},
    "npz_mean_equals_record": abs(means[0.25] - idx_h[("50K", "standard", "zero_k1", 0.25)]["net_mean"]) < 1e-6,
}
(OUT / "results_checks.json").write_text(json.dumps(out, indent=1, default=str))
for k, v in out.items():
    print("==", k); print(json.dumps(v, default=str)[:1800])
