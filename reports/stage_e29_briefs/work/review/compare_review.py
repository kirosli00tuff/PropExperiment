"""Stage E.29 review: compares work/review/out/*.json (review_run.py) with the stored cells and E.28's records.

Writes compare_review.json beside itself and prints a short summary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CELLS = HERE.parent / "basket" / "cells"
OUT = HERE / "out"
E28 = {(p["firm"], p["code"]): p for p in json.loads((REPO / "reports/stage_e28_briefs/A3_econ.json").read_text())["pairs"]}


def stored(cid: str) -> dict[str, Any]:
    return json.loads((CELLS / f"{cid}.json").read_text())


def g_of(rec: dict[str, Any], key: str) -> Any:
    return rec[key]["g"] if key in rec else None


def beats(c: dict[str, Any], b0: dict[str, Any]) -> str:
    inf = float("inf")
    t = inf if c["threshold"]["g"] is None else c["threshold"]["g"]
    p = inf if c["x10K"]["g"] is None else c["x10K"]["g"]
    tb = inf if b0["threshold"]["g"] is None else b0["threshold"]["g"]
    pb = inf if b0["x10K"]["g"] is None else b0["x10K"]["g"]
    return "yes" if (t <= tb - 2 and p <= pb) else "no"


rows: dict[str, list[dict[str, Any]]] = {"confirm": [], "reseed": [], "b0": [], "alone": []}
for p in sorted(OUT.glob("*.json")):
    r = json.loads(p.read_text())
    tag = r["review_tag"]
    cid = p.stem.split("__", 1)[1]
    s = stored(cid)
    if tag == "alone":
        row = {"cell": cid}
        for case in ("limit", "market"):
            ck = r[case]["grid_check"]["checks"]["ev"]
            row[case] = {"stored_g": s[case]["g"], "bisection_g": r[case]["g_bisection"], "confirmed_g": r[case]["g"],
                         "violations": ck.get("violations"), "n_checked": ck.get("n_checked"),
                         "max_below": ck.get("max_below")}
        rows["alone"].append(row)
        print("alone", cid, {c: (row[c]["stored_g"], row[c]["confirmed_g"], row[c]["violations"], row[c]["n_checked"])
                             for c in ("limit", "market")})
        continue
    row: dict[str, Any] = {"cell": cid, "stored_thr_g": s["threshold"]["g"], "stored_x10K_g": g_of(s, "x10K")}
    if tag == "confirm":
        gc = r["grid_check"]["checks"]
        row |= {"bisection_thr_g": r["threshold"]["g_bisection"], "confirmed_thr_g": r["threshold"]["g"],
                "bisection_x10K_g": r["x10K"]["g_bisection"], "confirmed_x10K_g": r["x10K"]["g"],
                "ev_check": {k: gc["ev"].get(k) for k in ("n_checked", "n_dense_points", "violations", "max_below",
                                                          "corrected_g")},
                "p10k_check": {k: gc["p10k"].get(k) for k in ("n_checked", "n_dense_points", "violations",
                                                              "max_below", "corrected_g")},
                "n_dense_filled_gaps": r["grid_check"]["n_dense_filled_gaps"], "repro_equal": r["repro"]["equal"],
                "n_evaluations": r["n_evaluations"]}
        row["bisection_reproduces_stored"] = (row["bisection_thr_g"] == row["stored_thr_g"]
                                              and row["bisection_x10K_g"] == row["stored_x10K_g"])
        row["thr_moved_steps"] = (None if None in (row["confirmed_thr_g"], row["stored_thr_g"])
                                  else row["confirmed_thr_g"] - row["stored_thr_g"])
        row["x10K_moved_steps"] = (None if None in (row["confirmed_x10K_g"], row["stored_x10K_g"])
                                   else row["confirmed_x10K_g"] - row["stored_x10K_g"])
    elif tag == "reseed":
        row |= {"seed": r["review_info"]["seed"], "z_old": r["review_info"]["z_attempt_row0_old"],
                "z_new": r["review_info"]["z_attempt_row0_new"], "new_thr_g": r["threshold"]["g"],
                "new_x10K_g": r["x10K"]["g"], "cost_per_attempt_new": r["cost_per_attempt_usd"],
                "cost_per_attempt_stored": s["cost_per_attempt_usd"]}
        row["thr_diff_steps"] = row["new_thr_g"] - row["stored_thr_g"] if None not in (row["new_thr_g"], row["stored_thr_g"]) else None
        row["x10K_diff_steps"] = row["new_x10K_g"] - row["stored_x10K_g"] if None not in (row["new_x10K_g"], row["stored_x10K_g"]) else None
        if s["basket"] != "B0":
            b0_id = f"limit__primary__{s['firm']}__B0__{s['setting']}__rNA"
            b0s = stored(b0_id)
            row["beats_stored"] = beats(s, b0s)
            row["beats_new_vs_stored_B0"] = beats(r, b0s)
            b0n = OUT / f"reseed__{b0_id}.json"
            if b0n.exists():
                row["beats_new_vs_new_B0"] = beats(r, json.loads(b0n.read_text()))
    else:
        firm = s["firm"]
        e = E28[(firm, "QM")]
        same_evals = all(a == b for a, b in zip(r["evaluations"], s["evaluations"])) and \
            len(r["evaluations"]) == len(s["evaluations"])
        row |= {"case": s["case"], "new_thr": r["threshold"]["value"], "new_x10K": r.get("x10K", {}).get("value"),
                "new_cost": r.get("cost_per_attempt_usd"), "e28_mu_star_lim": e["mu_star_lim"],
                "e28_mu_star_mkt": e["mu_star_mkt"], "e28_mu10K": e["mu10K"], "e28_cost": e["cost_per_attempt_usd"],
                "evaluations_bit_equal_to_stored_cell": same_evals}
        if s["case"] == "limit":
            row["match_e28"] = (r["threshold"]["value"] == e["mu_star_lim"] and r["x10K"]["value"] == e["mu10K"]
                                and r["cost_per_attempt_usd"] == e["cost_per_attempt_usd"])
        else:
            row["match_e28"] = r["threshold"]["value"] == e["mu_star_mkt"]
    rows[tag].append(row)

(HERE / "compare_review.json").write_text(json.dumps(rows, indent=1))
for tag, rs in rows.items():
    if tag == "alone":
        continue
    print(f"== {tag} ({len(rs)})")
    for x in rs:
        c = x["cell"].replace("limit__primary__", "").replace("market__primary__", "mkt:")
        if tag == "confirm":
            print(c, "thr", x["stored_thr_g"], "->", x["confirmed_thr_g"], "x10K", x["stored_x10K_g"], "->",
                  x["confirmed_x10K_g"], "bis=stored", x["bisection_reproduces_stored"], "viol",
                  x["ev_check"]["violations"], x["p10k_check"]["violations"], "nchk", x["ev_check"]["n_checked"],
                  x["p10k_check"]["n_checked"], "maxbelow_ev", x["ev_check"]["max_below"], "repro", x["repro_equal"])
        elif tag == "reseed":
            print(c, "thr", x["stored_thr_g"], "->", x["new_thr_g"], "x10K", x["stored_x10K_g"], "->",
                  x["new_x10K_g"], "beats", x.get("beats_stored"), x.get("beats_new_vs_stored_B0"),
                  x.get("beats_new_vs_new_B0"), "z", x["z_old"][:1], x["z_new"][:1])
        else:
            print(c, x["new_thr"], x["new_x10K"], x["new_cost"], "| e28", x["e28_mu_star_lim"], x["e28_mu_star_mkt"],
                  x["e28_mu10K"], x["e28_cost"], "match", x["match_e28"], "bit-equal", x["evaluations_bit_equal_to_stored_cell"])
