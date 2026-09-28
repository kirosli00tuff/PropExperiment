"""Stage E.5 Task C4 (and D4): build a cluster's hashed confirmation list (JSON first, then the markdown that embeds
the JSON's sha256). Lead script; run once per cluster, before any confirmation read.

Usage: uv run python reports/stage_e5_briefs/build_list.py CLUSTER HARNESS_SHA256 POWER_DIR [NGS_CHECK_JSON]
Inputs, all frozen or recorded: the cluster freeze (screening.stage_e_freeze), E.4's research cluster record (tiers and
D9 labels), the source-window labels (catalog R-04 and reports/stage_e2a_source_window_amendment.md, restated below),
the start-rule file reports/stage_e_start_rule_<K>.json, the research re-run records in POWER_DIR (their `power` field:
the runner's D4 power check at the confirmation supply), the frozen epsilon table, and for K4 the NGS check.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from screening.stage_e_freeze import load_cluster_freeze
from screening.stage_e_stats_units import frozen_epsilon
from screening.stage_e_verdict import BOOTSTRAP_SEED_BASE, HOLM_K, parse_list

ROOT = Path(__file__).resolve().parents[2]
PROGRAM_N = 150  # E.4 final section: 102 after E.3 + 12 (K4) + 9 (K5) + 27 (K3); counts screened trials
E4_DIRS = {"K4": "reports/stage_e4_k4_screen", "K5": "reports/stage_e4b_k5_screen"}
# Source-window labels. Catalog-labelled (R-04, reports/stage_e1_freeze_rulings.md FA-06): K4-apipre-01, K4-eiafade-01,
# K4-eiamom-01, K4-ovr-01, K5-fomc-01, K5-ovr-01. Amendment (reports/stage_e2a_source_window_amendment.md lines 58-66,
# governing column): K4-cp1/2/3-01, K5-cp1/2/3-01, K5-pmfix-01, K5-preauc-01 keep it; K4-ngpre-01 is NOT source-overlap.
NOT_SOURCE_OVERLAP = {"K4-ngpre-01"}
DOCS = ("docs/NULL_CRITERIA_E.md", "docs/STAGE_E_DESIGN.md", "docs/DECISIONS.md", "reports/stage_e5_harness_plan.md",
        "reports/stage_e2a_source_window_amendment.md", "reports/stage_e2a_epsilon.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_file(cluster: str, member: str, window: str) -> str:
    return f"{cluster}_{member.replace(' ', '_')}_{window}.json"


def main() -> int:
    cluster, harness, power_dir = sys.argv[1], sys.argv[2], ROOT / sys.argv[3]
    ngs_path = ROOT / sys.argv[4] if len(sys.argv) > 4 else None
    freeze = load_cluster_freeze(cluster)
    e4 = ROOT / E4_DIRS[cluster]
    tiers = {m["member_id"]: m for m in json.loads((e4 / f"{cluster}_research_cluster.json").read_text())["tiers"]["members"]}
    start_path = ROOT / f"reports/stage_e_start_rule_{cluster}.json"
    start_doc = json.loads(start_path.read_text())
    starts = {r: e["s_x"] for r, e in start_doc["products"].items()}
    ngs_unverifiable = None
    if ngs_path is not None:
        ngs = json.loads(ngs_path.read_text())
        s_ng = starts.get("NG")
        ngs_unverifiable = sorted(r["date"] for r in ngs["ngs"] if r["verdict"] == "unverifiable" and r["date"] >= s_ng)
    trials, inputs = [], {}
    for m in sorted(freeze.members, key=lambda m: m.ordinal):
        vehicle = next(leg.root for leg in m.legs if leg.traded)
        eps = frozen_epsilon(vehicle)
        t = tiers[m.label]
        base = m.label.split(" ")[0]
        labels = list(t["labels"])  # D9 labels (OC-H) from E.4's tiers
        if base not in NOT_SOURCE_OVERLAP:
            labels.append("source-overlap")
        if base == "K4-ngpre-01":
            labels.append("calendar partly unverified")  # E.4: 3 research-window NGS releases unverifiable
        power = None
        rec_path = power_dir / record_file(cluster, m.label, "research")
        if rec_path.is_file():
            rec = json.loads(rec_path.read_text())
            inputs[str(rec_path.relative_to(ROOT))] = sha(rec_path)
            p = rec.get("power")
            if isinstance(p, dict) and p.get("status") == "run":
                c = p["check"]
                power = {"status": "run", "supply_days": p["supply_days"], "label": c["label"],
                         "inconclusive_by_design": c["inconclusive_by_design"], "n_b_chosen": c["n_b_chosen"],
                         "n_b_analytic": c["n_b_analytic"], "n_b_sim": c["n_b_sim"], "n_a_chosen": c["n_a_chosen"],
                         "research_days": c["research_days"], "mean_ticks": c["mean_ticks"],
                         "sd_day_ticks": c["sd_day_ticks"], "vif_boot": c["vif_boot"], "seed": c["seed"],
                         "flags": list(c["flags"])}
                if c["inconclusive_by_design"]:
                    labels.append("inconclusive by design")
            else:
                power = p
        trials.append({"ordinal": m.ordinal, "member": m.label, "vehicle": vehicle, "legs": [l.root for l in m.legs],
                       "q_c": eps.q_c, "eps_ticks": eps.eps_ticks, "eps_usd_per_day_at_q": eps.eps_usd_per_day_at_q,
                       "tier": t["tier"], "run": t["tier"] in ("A", "B"), "labels": labels,
                       "bootstrap_seed": BOOTSTRAP_SEED_BASE + m.ordinal, "power": power,
                       "s_x": {r: starts[r] for r in (l.root for l in m.legs)}})
    for rel in DOCS + (str(start_path.relative_to(ROOT)),) + ((str(ngs_path.relative_to(ROOT)),) if ngs_path else ()):
        inputs[rel] = sha(ROOT / rel)
    payload = {
        "schema": "stage_e_confirmation_list/1", "cluster": cluster, "stage": "E.5",
        "created_pdt": datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds"),
        "harness_sha256": harness, "cluster_freeze_sha256": freeze.sha256, "k_holm": HOLM_K, "program_n": PROGRAM_N,
        "bootstrap": {"seed_base": BOOTSTRAP_SEED_BASE, "resamples": 10000, "mean_block": 5.0, "ucb_quantile": 0.95},
        "start_dates": starts,
        "confirmation_window": {r: [s, "2024-02-29"] for r, s in starts.items()},
        "rules": {
            "null": "NULL_CRITERIA_E 3: UCB95 < eps_X and Phi(eps_X / SE_boot - 1.645) >= 0.80; zero trips or SE_boot = 0 "
                    "inconclusive; < 30 closed trips 'null by inactivity'; a trial labelled 'inconclusive by design' is not "
                    "covered; OC-H-excluded trials are listed, not run, not covered (L-E5-5).",
            "edge_chain": "D5 with V14: Holm over the Tier A one-sided p at 0.05 / K, K = 9 (V14 b); composite verdict "
                          "pending, not built unless the rest passes (V14 a); DSR > 0.95 at program N with the Sharpe "
                          "variance over Tier A, or over every run trial of the cluster when Tier A has one member "
                          "(V14 c); daily t > 3.0 one-sided; CSCV PBO < 0.5 on 8 contiguous blocks over Tier A, or over "
                          "every run trial when Tier A has one member (L-E5-3), aligned on the union of the run trials' "
                          "window dates, zeros off each trial's dates.",
            "wording": "A trial passing Holm, DSR, t and PBO reads 'edge candidate, composite pending', never 'edge'; a "
                       "source-overlap trial adds 'no edge claim without a registered holdout read'.",
            "code": "screening/stage_e_verdict.py under the harness sha256 above; one confirmation run per cluster.",
        },
        "ngs_unverifiable_in_confirmation_window": ngs_unverifiable,
        "inputs": inputs, "trials": trials,
    }
    parse_list(payload)  # the verdict module must accept it before it is written
    out_dir = Path(os.environ.get("E5_LIST_OUT_DIR", ROOT / "reports"))  # a dry run writes elsewhere
    out_json = out_dir / f"stage_e5_{cluster.lower()}_confirmation_list.json"
    raw = (json.dumps(payload, indent=1) + "\n").encode()
    with out_json.open("xb") as fh:
        fh.write(raw)
    json_sha = hashlib.sha256(raw).hexdigest()
    out_md = out_dir / f"stage_e5_{cluster.lower()}_confirmation_list.md"
    with out_md.open("x") as fh:
        fh.write(render_md(payload, out_json.name, json_sha))
    print(f"wrote {out_json} sha256 {json_sha}")
    print(f"wrote {out_md} sha256 {sha(out_md)}")
    return 0


def render_md(p: dict, json_name: str, json_sha: str) -> str:
    k = p["cluster"]
    L = [f"# Stage E.5 {k} confirmation list (hashed before any confirmation read)", "",
         f"STATUS: FROZEN at commit (\"{k} confirmation list\"). Written by the E.5 lead {p['created_pdt']} against the E.5 prompt,",
         "before any bar of the confirmation window was read by any run. After the commit nothing in this file or its JSON changes.",
         f"The machine-read list is reports/{json_name}, sha256 **{json_sha}**; this file restates it for a reader (the JSON",
         "governs where they differ). Shape after reports/stage_d1f_confirmation_list.md.", "",
         "## 0. Provenance", "",
         f"- Harness: v6 {p['harness_sha256']} (reports/stage_e2b_harness_freeze.json; the verdict code is screening/stage_e_verdict.py).",
         f"- Cluster freeze: reports/stage_e_{k.lower()}_member_freeze.json, sha256 {p['cluster_freeze_sha256']}.",
         f"- Holm K = {p['k_holm']} (V14 b). Program N for DSR = {p['program_n']} (E.4's final section; screened trials).",
         f"- Bootstrap: stationary, mean block {p['bootstrap']['mean_block']}, B = {p['bootstrap']['resamples']:,}, a fresh generator per trial seeded "
         f"{p['bootstrap']['seed_base']} + list ordinal, np.quantile {p['bootstrap']['ucb_quantile']} (NULL_CRITERIA_E 3).",
         "- Inputs and their sha256:"]
    L += [f"  - {path}: {h}" for path, h in sorted(p["inputs"].items())]
    L += ["", "## 1. Windows (D4)", "", "| Root | S_X | Confirmation window |", "|---|---|---|"]
    L += [f"| {r} | {s} | {w[0]}..{w[1]} |" for r, (s, w) in ((r, (p['start_dates'][r], p['confirmation_window'][r])) for r in p['start_dates'])]
    L += ["", "Embargo (March 2024) and holdout-2 (2024-04-01..2025-03-31) sealed on arrival (reports/stage_e5_purchase.md); never read.", "",
          "## 2. The frozen list", "",
          "| Ord | Trial | Vehicle | q_c | eps_X ticks/ct/day ($/day at q_c) | Tier | Run | Labels | S_X | Seed | Power (supply, n_b, label) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in p["trials"]:
        pw = t["power"]
        pws = (f"{pw['supply_days']}, {pw['n_b_chosen']}, {pw['label']}" if isinstance(pw, dict) and pw.get("status") == "run"
               else "not run" if pw is None else str(pw.get("status")))
        L.append(f"| {t['ordinal']} | {t['member']} | {t['vehicle']} | {t['q_c']} | {t['eps_ticks']} (${t['eps_usd_per_day_at_q']:.2f}) | "
                 f"{t['tier']} | {'yes' if t['run'] else 'no'} | {', '.join(t['labels']) or '-'} | "
                 f"{', '.join(f'{r} {d}' for r, d in t['s_x'].items())} | {t['bootstrap_seed']} | {pws} |")
    if p.get("ngs_unverifiable_in_confirmation_window") is not None:
        L += ["", f"K4-ngpre-01's storage dates: the confirmation-window NGS rows were checked against EIA's record (reports/stage_e5_ngs_check.md);",
              "five rows were dropped by C9's rule (lead ruling R-C3-1, the K4 C9 table amendment commit); unverifiable in the confirmation window: "
              f"{len(p['ngs_unverifiable_in_confirmation_window'])}. The label \"calendar partly unverified\" comes from E.4's three unverifiable",
              "research-window releases (2025-05-01, 2025-05-29, 2025-06-18)."]
    L += ["", "## 3. Tests and decision rules (fixed now)", ""]
    L += [f"- **{name}.** {text}" for name, text in p["rules"].items()]
    L += ["- **Per trial reported:** theta_hat, UCB95, SE_boot, p_upper, n_days, closed trips, trips per day r, theta_hat / r, UCB95 / r,",
          "  achieved null power Phi(eps_X / SE_boot - 1.645), the null status; for Tier A every edge-chain step.",
          "- **Cluster statement:** NULL_CRITERIA_E 1 and 7 with the per-exposure resolution table.", "",
          "## 4. Hashing record", "",
          f"The JSON was written first (sha256 above); this file embeds that hash and is hashed second; both hashes go into the commit",
          f"message \"{k} confirmation list\". The confirmation run (python -m screening.stage_e_runner --window confirmation) happens only",
          "after that commit, once."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
