"""Compare my recomputation (written first) with the lead's reports/stage_e12_gate0.json and the
build's filter table. Writes compare.json and compare.md (tables) to this folder."""
from __future__ import annotations

import json
import math
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e12_briefs/gate0verifier"
STAGES = Path(os.path.expanduser("~/.cache/propexp_e12_phase1/stages"))
TOL_A, TOL_B = 1e-6, 1e-4

lead = json.loads((REPO / "reports/stage_e12_gate0.json").read_text())
mine = json.loads((OUT / "my_summary.json").read_text())
my_a = pd.read_csv(OUT / "my_family_a.csv").set_index("test_id")
my_b = pd.read_csv(OUT / "my_family_b.csv").set_index("test_id")
my_cs = pd.read_csv(OUT / "my_c_sigma.csv").set_index(["root", "horizon"])
lead_tests = {t["test_id"]: t for t in lead["tests"]}
lead_a = {k: v for k, v in lead_tests.items() if v["family"] == "A"}
lead_b = {k: v for k, v in lead_tests.items() if v["family"] == "B"}


def rel(a, b):
    if a is None or b is None:
        return float("nan") if (a is None) != (b is None) else 0.0
    a, b = float(a), float(b)
    if math.isnan(a) and math.isnan(b):
        return 0.0
    if math.isinf(a) or math.isinf(b):
        return 0.0 if a == b else float("inf")
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


findings = []
# ---- step 1: filter ----
with open(STAGES / "phase1_filter.pkl", "rb") as fh:
    filt = pickle.load(fh)["out"]
lead_cs = filt["c_sigma"].set_index(["root", "horizon"])
cs_rows = []
for key, r in my_cs.iterrows():
    L = lead_cs.loc[key]
    cs_rows.append({"root": key[0], "horizon": key[1], "my_c": r["c_ticks"], "lead_c": L["c_ticks"],
                    "my_sigma": r["sigma_ticks"], "lead_sigma": L["sigma_ticks"],
                    "my_ratio": r["ratio"], "lead_ratio": L["ratio"], "my_n": int(r["n_rows"]),
                    "lead_n": int(L["n_rows"]), "my_adm": bool(r["admissible"]),
                    "lead_adm": bool(L["admissible"]),
                    "max_rel": max(rel(r["c_ticks"], L["c_ticks"]), rel(r["sigma_ticks"], L["sigma_ticks"]),
                                   rel(r["ratio"], L["ratio"]))})
cs = pd.DataFrame(cs_rows)
cs.to_csv(OUT / "compare_c_sigma.csv", index=False)
lead_adm_pairs = sorted(tuple(p) for p in lead["admissible_pairs"])
my_adm_pairs = sorted(tuple(p) for p in mine["step1_filter"]["admissible"])
filter_ok = (cs["max_rel"].max() <= TOL_A and (cs["my_n"] == cs["lead_n"]).all()
             and (cs["my_adm"] == cs["lead_adm"]).all() and lead_adm_pairs == my_adm_pairs
             and sorted(tuple(p) for p in filt["admissible"]) == my_adm_pairs)
if not filter_ok:
    findings.append("filter table or admissible pairs differ")

# ---- family B ----
b_rows = []
for tid, L in lead_b.items():
    M = my_b.loc[tid]
    d = {"test_id": tid, "my_mean": M["mean_g_ticks"], "lead_mean": L["mean_gross_ticks"],
         "my_cost": M["cost_ticks"], "lead_cost": L["cost_ticks"], "my_t": M["t_B"], "lead_t": L["t_B"],
         "my_p": M["p_one_sided"], "lead_p": L["p"], "my_n_trades": int(M["n_trades"]),
         "lead_n_trades": int(L["n_trades"]), "my_n_dates": int(M["n_dates"]), "lead_n_dates": int(L["n_dates"]),
         "my_n_obs": int(M["n_pair_rows"]), "lead_n_obs": int(L["n_obs"])}
    d["max_rel"] = max(rel(d["my_mean"], d["lead_mean"]), rel(d["my_cost"], d["lead_cost"]),
                       rel(d["my_t"], d["lead_t"]), rel(d["my_p"], d["lead_p"]))
    d["counts_exact"] = (d["my_n_trades"] == d["lead_n_trades"] and d["my_n_dates"] == d["lead_n_dates"]
                         and d["my_n_obs"] == d["lead_n_obs"])
    b_rows.append(d)
cb = pd.DataFrame(b_rows)
cb.to_csv(OUT / "compare_family_b.csv", index=False)
b_ok = bool(cb["max_rel"].max() <= TOL_B and cb["counts_exact"].all() and set(lead_b) == set(my_b.index))
if not b_ok:
    findings.append(f"family B: max rel {cb['max_rel'].max():.3g}, counts exact {cb['counts_exact'].all()}")

# ---- family A ----
a_rows = []
for tid, L in lead_a.items():
    M = my_a.loc[tid]
    d = {"test_id": tid, "my_mean": M["mean_m_d"], "lead_mean": L["mean"], "my_t": M["t"], "lead_t": L["t"],
         "my_p": M["p_two_sided"], "lead_p": L["p"], "my_ic": M["ic_spearman"], "lead_ic": L["ic_spearman"],
         "my_gsign": M["gross_ticks_sign"], "lead_gsign": L["gross_ticks_sign"],
         "my_n_dates": int(M["n_dates"]), "lead_n_dates": int(L["n_dates"]),
         "my_n_obs": int(M["n_obs"]), "lead_n_obs": int(L["n_obs"]), "seeded": bool(M["seeded_choice"])}
    d["max_rel"] = max(rel(d["my_mean"], d["lead_mean"]), rel(d["my_t"], d["lead_t"]),
                       rel(d["my_p"], d["lead_p"]), rel(d["my_ic"], d["lead_ic"]),
                       rel(d["my_gsign"], d["lead_gsign"]))
    d["counts_exact"] = d["my_n_dates"] == d["lead_n_dates"] and d["my_n_obs"] == d["lead_n_obs"]
    a_rows.append(d)
ca = pd.DataFrame(a_rows)
ca.to_csv(OUT / "compare_family_a.csv", index=False)
seeded = ca[ca["seeded"]]
a_ok = bool(ca["max_rel"].max() <= TOL_A and ca["counts_exact"].all() and set(lead_a) == set(my_a.index))
if not a_ok:
    findings.append(f"family A: max rel {ca['max_rel'].max():.3g}, counts exact {ca['counts_exact'].all()}")

# ---- Holm: my p for the best pair, the lead's p for the others ----
best_id = mine["step2_cpcv"]["best_pair_by_t_B_n_ge_30"]["test_id"]
lead_elig = [t for t in lead_b.values() if t["n_trades"] >= 30]
lead_best = max(lead_elig, key=lambda t: t["t_B"])["test_id"]
pvals = [(lead_tests[t]["p"] if t != best_id else float(my_b.loc[best_id, "p_one_sided"]), t)
         for t in lead_tests]
pvals.sort()
m = len(pvals)
holm_rows, still = {}, True
for i, (p_, t) in enumerate(pvals):
    th = 0.05 / (m - i)
    still = still and p_ <= th
    holm_rows[t] = {"rank": i + 1, "threshold": th, "rejected": still, "p": p_}
mine_h = holm_rows[best_id]
lead_h = {"rank": lead_tests[best_id]["holm_rank"], "threshold": lead_tests[best_id]["holm_threshold"],
          "rejected": lead_tests[best_id]["holm_rejected"]}
holm_ok = (mine_h["rank"] == lead_h["rank"] and rel(mine_h["threshold"], lead_h["threshold"]) <= 1e-12
           and mine_h["rejected"] == lead_h["rejected"])
# internal consistency of the lead's Holm table
lead_sorted = sorted(lead_tests.values(), key=lambda t: (t["p"], t["test_id"]))
holm_internal = all(t["holm_rank"] == i + 1 and abs(t["holm_threshold"] - 0.05 / (m - i)) < 1e-15
                    for i, t in enumerate(lead_sorted))
n_rej_lead = sum(bool(t["holm_rejected"]) for t in lead_tests.values())
if not (holm_ok and holm_internal):
    findings.append("Holm row of the best pair or the Holm table differs")

# ---- verdict, pooled, N ----
my_pool = mine["step2_cpcv"]["pooled_b"]
pool_rel = max(rel(my_pool["mean_g_ticks"], lead["pooled_b"]["mean_g_ticks"]),
               rel(my_pool["mean_cost_ticks"], lead["pooled_b"]["mean_cost_ticks"]),
               rel(my_pool["t"], lead["pooled_b"]["t"]))
pool_ok = pool_rel <= TOL_B and my_pool["n_trades"] == lead["pooled_b"]["n_trades"] \
    and my_pool["n_dates"] == lead["pooled_b"]["n_dates"]
verdict_ok = (lead["verdict"] == ("PASS" if mine["my_verdict"]["passed"] else "FAIL")
              and list(lead["passing_pairs"]) == mine["my_verdict"]["passing"])
n_ok = (lead["n_a"] == mine["step7_N"]["n_a"] and lead["n_b"] == mine["step7_N"]["n_b"]
        and lead["n_contributed"] == mine["step7_N"]["n_a_plus_b"] and lead["n_holm_family"] == 273)
my_pairs_t3 = int((my_b["t_B"] >= 3).sum())
lead_pairs_t3 = sum(t["t_B"] >= 3 for t in lead_b.values())

res = {
    "filter": {"ok": filter_ok, "max_rel": float(cs["max_rel"].max()), "n_pairs": len(cs),
               "my_admissible": len(my_adm_pairs), "lead_admissible": len(lead_adm_pairs)},
    "family_b": {"ok": b_ok, "n": len(cb), "max_rel": float(cb["max_rel"].max()),
                 "n_counts_exact": int(cb["counts_exact"].sum()),
                 "best_pair_mine": best_id, "best_pair_lead": lead_best,
                 "best_row": cb[cb["test_id"] == best_id].iloc[0].to_dict(),
                 "pairs_t_ge_3_mine": my_pairs_t3, "pairs_t_ge_3_lead": lead_pairs_t3},
    "family_a": {"ok": a_ok, "n": len(ca), "max_rel": float(ca["max_rel"].max()),
                 "n_counts_exact": int(ca["counts_exact"].sum()),
                 "seeded_rows": seeded.to_dict(orient="records"),
                 "seeded_max_rel": float(seeded["max_rel"].max())},
    "holm": {"ok": bool(holm_ok), "internal_consistent": bool(holm_internal), "m": m,
             "best_pair_mine": mine_h, "best_pair_lead": lead_h, "n_rejected_lead": n_rej_lead,
             "n_rejected_my_holm": mine["my_holm"]["n_rejected"]},
    "pooled_b": {"ok": bool(pool_ok), "max_rel": pool_rel, "mine": my_pool, "lead": lead["pooled_b"]},
    "verdict": {"ok": bool(verdict_ok), "lead": lead["verdict"], "lead_passing": lead["passing_pairs"],
                "mine": "PASS" if mine["my_verdict"]["passed"] else "FAIL",
                "my_passing": mine["my_verdict"]["passing"]},
    "N": {"ok": bool(n_ok), "lead": {k: lead[k] for k in ("n_a", "n_b", "n_contributed", "n_holm_family")},
          "mine": mine["step7_N"]},
    "lead_meta": {"created_pdt": lead["created_pdt"], "list_sha256": lead["list_sha256"],
                  "ledger": lead["ledger"], "fingerprints": lead["fingerprints"], "schema": lead["schema"]},
    "findings": findings,
}
(OUT / "compare.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps({k: (v["ok"] if isinstance(v, dict) and "ok" in v else None) for k, v in res.items()}))
print("filter max_rel", res["filter"]["max_rel"], "| B max_rel", res["family_b"]["max_rel"],
      "| A max_rel", res["family_a"]["max_rel"], "| seeded max_rel", res["family_a"]["seeded_max_rel"])
print("best", best_id, "lead best", lead_best, "| holm mine", mine_h, "| lead", lead_h)
print("pooled rel", pool_rel, "| findings", findings)
