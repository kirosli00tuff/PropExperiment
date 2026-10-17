"""Stage E.22 Part A: build one cluster's hashed confirmation list (JSON first; the combined markdown
reports/stage_e22_confirmation_list.md embeds each JSON's sha256). Lead script, adapted from
reports/stage_e5_briefs/build_list.py; run once per cluster, before any confirmation read.

Usage: uv run python reports/stage_e22_briefs/build_list.py CLUSTER HARNESS_SHA256 POWER_DIR [UNTESTABLE_JSON]

Inputs, all frozen or recorded: the cluster freeze, the screening cluster record (tiers, D9 labels), the
source-window labels (catalog R-04 and reports/stage_e2a_source_window_amendment.md, governing column), the
start-rule files (merged by screening.stage_e_start_dates), the price-path declaration
reports/stage_e22_price_paths.json, the research re-run records in POWER_DIR (their `power` field: the
runner's D4 power check at the confirmation supply), the frozen epsilon table. Lead rulings:
reports/stage_e22_briefs/partA_rulings.md (K = 5, N = 533, eps operative, R-E22-A13 for no-record trials).
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
from screening.stage_e_start_dates import start_dates_for
from screening.stage_e_stats_units import frozen_epsilon
from screening.stage_e_verdict import BOOTSTRAP_SEED_BASE, parse_list

ROOT = Path(__file__).resolve().parents[2]
K_HOLM = 5         # R-E22-A10: clusters with a non-empty Tier A (K3, K4, K5, K6, K8)
PROGRAM_N = 533    # R-E22-A11: 532 + E22-F1, registered in this stage
SCREEN_DIRS = {"K3": "reports/stage_e4c_k3_screen", "K5": "reports/stage_e4b_k5_screen",
               "K6": "reports/stage_e8_k6_screen", "K8": "reports/stage_e9_k8_screen"}
# Amendment governing column (reports/stage_e2a_source_window_amendment.md:36): labels removed from
# K2-predrift-01, K3-ldnmom-01, K3-mehedge-01, K4-ngpre-01, K8-flight-01, K8-oilcad-01; every other member of
# K3, K5, K6, K8 keeps "source-overlap" (K5-fomc-01 and K5-ovr-01 by R-04; every K6 member per E.8; K8-wkndbtc-01).
NOT_SOURCE_OVERLAP = {"K3-ldnmom-01", "K3-mehedge-01", "K8-flight-01", "K8-oilcad-01"}
PRICE_PATHS = "reports/stage_e22_price_paths.json"
# Lead notes (descriptive; not verdict labels). Keyed by member base id or full trial label.
NOTES = {
    "K6-limitcont-01 HE": ["Tier A on a single trip (research t 1.002 = sqrt(273/272))",
                           "limits are the frozen initial limits; expanded limits not encoded (K6-L-07)",
                           "settlements by the D9.7 proxy (one bar's close); official settlements not tested (R-T3-2)"],
    "K6-limitcont-01 LE": ["limits are the frozen initial limits; expanded limits not encoded (K6-L-07)",
                           "settlements by the D9.7 proxy; limit table partly contradicted by CME (R-1b-2)"],
    "K6-cp2-01": ["tick history not source-verified for the research window (K6-L-16 13(a))"],
    "K8-wkndbtc-01": ["confirmation window wholly in the weekend-closure regime (E.9 (b))"],
    "K3": ["K3's frozen FX_FULL_SESSIONS keeps 14 2022-2023 dates the harness flattens at 11:30 (R-A2-1): kept as frozen"],
}
DOCS = ("docs/NULL_CRITERIA_E.md", "docs/STAGE_E_DESIGN.md", "docs/DECISIONS.md",
        "reports/stage_e2a_source_window_amendment.md", "reports/stage_e2a_epsilon.json",
        "reports/stage_e22_briefs/partA_rulings.md", PRICE_PATHS)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_file(cluster: str, member: str, window: str) -> str:
    return f"{cluster}_{member.replace(' ', '_')}_{window}.json"


def power_object(p: dict | None) -> tuple[dict | None, bool]:
    if isinstance(p, dict) and p.get("status") == "run":
        c = p["check"]
        return ({"status": "run", "supply_days": p["supply_days"], "label": c["label"],
                 "inconclusive_by_design": c["inconclusive_by_design"], "n_b_chosen": c["n_b_chosen"],
                 "n_b_analytic": c["n_b_analytic"], "n_b_sim": c["n_b_sim"], "n_a_chosen": c["n_a_chosen"],
                 "research_days": c["research_days"], "mean_ticks": c["mean_ticks"],
                 "sd_day_ticks": c["sd_day_ticks"], "vif_boot": c["vif_boot"], "seed": c["seed"],
                 "flags": list(c["flags"])}, bool(c["inconclusive_by_design"]))
    return p, False


def main() -> int:
    cluster, harness, power_dir = sys.argv[1], sys.argv[2], ROOT / sys.argv[3]
    unt_doc = json.loads((ROOT / sys.argv[4]).read_text()) if len(sys.argv) > 4 else {}
    # the runner's stage_e_untestable/1 declaration: {"members": {label: {"label", "reason", "missing_leg"}}}
    notrun = unt_doc.get("members", {})  # member -> {"label", "reason", "missing_leg"}
    freeze = load_cluster_freeze(cluster)
    scr = ROOT / SCREEN_DIRS[cluster]
    tiers = {m["member_id"]: m for m in json.loads((scr / f"{cluster}_research_cluster.json").read_text())["tiers"]["members"]}
    paths = {v: e["path"] for v, e in json.loads((ROOT / PRICE_PATHS).read_text())["paths"].items()}
    leg_roots = sorted({leg.root for m in freeze.members for leg in m.legs})
    path_roots = sorted({paths.get(r, r) for r in leg_roots})
    starts_path, provenance = start_dates_for(path_roots)
    starts = {r: str(starts_path[paths.get(r, r)]) if starts_path[paths.get(r, r)] is not None else None
              for r in leg_roots}
    trials, inputs = [], {}
    for m in sorted(freeze.members, key=lambda m: m.ordinal):
        vehicle = next(leg.root for leg in m.legs if leg.traded)
        eps = frozen_epsilon(vehicle)
        t = tiers[m.label]
        base = m.label.split(" ")[0]
        labels = list(t["labels"])  # D9 labels (OC-H) from the screening tiers
        if base not in NOT_SOURCE_OVERLAP:
            labels.append("source-overlap")
        notes = list(NOTES.get(m.label, [])) + list(NOTES.get(base, [])) + list(NOTES.get(cluster, []))
        run = t["tier"] in ("A", "B")
        power = None
        rec_path = power_dir / record_file(cluster, m.label, "research")
        if rec_path.is_file():
            rec = json.loads(rec_path.read_text())
            inputs[str(rec_path.relative_to(ROOT))] = sha(rec_path)
            power, by_design = power_object(rec.get("power"))
            if by_design:
                labels.append("inconclusive by design")
                run = False  # R-E22-A9: a by-design trial is not run (declared to the runner; R-E22-A13 p = 1)
        if m.label in notrun:
            spec = notrun[m.label]
            if spec["label"] not in labels:
                labels.append(spec["label"])
            notes.append(f"not run ({spec['label']}): {spec['reason']}")
            if spec.get("missing_leg"):
                notes.append(f"missing leg: {spec['missing_leg']}")
            run = False
        elif "inconclusive by design" in labels:
            raise SystemExit(f"{m.label}: inconclusive by design but not in the not-run declaration")
        mapped = {r: paths[r] for r in (l.root for l in m.legs) if r in paths}
        if mapped:
            notes.append("price path declared before any read (reports/stage_e22_price_paths.json): "
                         + ", ".join(f"{v} on {p} bars with {v}'s costs, tick value and q_c" for v, p in mapped.items()))
        trials.append({"ordinal": m.ordinal, "member": m.label, "vehicle": vehicle, "legs": [l.root for l in m.legs],
                       "q_c": eps.q_c, "eps_ticks": eps.eps_ticks, "eps_usd_per_day_at_q": eps.eps_usd_per_day_at_q,
                       "tier": t["tier"], "run": run, "labels": labels,
                       "bootstrap_seed": BOOTSTRAP_SEED_BASE + m.ordinal, "power": power,
                       "s_x": {r: starts[r] for r in (l.root for l in m.legs)},
                       "price_path": mapped, "notes": notes})
    for rel in DOCS + ((sys.argv[4],) if len(sys.argv) > 4 else ()):
        inputs[rel] = sha(ROOT / rel)
    for v in provenance.values():  # start-rule files that gave each S_X (list review F1)
        for f in (v.get("files") or []) if isinstance(v, dict) else []:
            inputs[f["path"]] = sha(ROOT / f["path"])
    payload = {
        "schema": "stage_e_confirmation_list/1", "cluster": cluster, "stage": "E.22",
        "created_pdt": datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds"),
        "harness_sha256": harness, "cluster_freeze_sha256": freeze.sha256, "k_holm": K_HOLM, "program_n": PROGRAM_N,
        "bootstrap": {"seed_base": BOOTSTRAP_SEED_BASE, "resamples": 10000, "mean_block": 5.0, "ucb_quantile": 0.95},
        "start_dates": {r: s for r, s in starts.items() if s is not None},
        "price_paths": {r: paths[r] for r in leg_roots if r in paths},
        "confirmation_window": {r: [s, "2024-02-29"] for r, s in starts.items() if s is not None},
        "rules": {
            "null": "NULL_CRITERIA_E 3: UCB95 < eps_X and Phi(eps_X / SE_boot - 1.645) >= 0.80; zero trips or SE_boot = 0 "
                    "inconclusive; < 30 closed trips 'null by inactivity'; a trial labelled 'inconclusive by design' or "
                    "'untestable on owned data' is not covered; OC-H-excluded trials are listed, not run, not covered (L-E5-5).",
            "edge_chain": "D5 with V14 and the E.22 rulings: Holm over the Tier A one-sided p at 0.05 / K, K = 5 "
                          "(R-E22-A10), a Tier A trial with no record at p = 1 (R-E22-A13); composite verdict pending, "
                          "not built unless the rest passes (V14 a); DSR > 0.95 at program N = 533 (R-E22-A11) with the "
                          "Sharpe variance over Tier A, or over every run trial of the cluster when fewer than two Tier A "
                          "series exist (V14 c); daily t > 3.0 one-sided; CSCV PBO < 0.5 on 8 contiguous blocks over Tier A, "
                          "or over every run trial when fewer than two Tier A series exist (L-E5-3), aligned on the union of "
                          "the run trials' window dates, zeros off each trial's dates.",
            "wording": "A trial passing Holm, DSR, t and PBO reads 'edge candidate, composite pending', never 'edge'; a "
                       "source-overlap trial adds 'no edge claim without a registered holdout read'.",
            "code": "screening/stage_e_verdict.py under the harness sha256 above; one confirmation run per cluster, behind "
                    "a run-once marker.",
        },
        "inputs": inputs, "trials": trials,
    }
    parse_list(payload)  # the verdict module must accept it before it is written
    out_dir = Path(os.environ.get("E22_LIST_OUT_DIR", ROOT / "reports"))  # a dry run writes elsewhere
    out_json = out_dir / f"stage_e22_{cluster.lower()}_confirmation_list.json"
    raw = (json.dumps(payload, indent=1) + "\n").encode()
    with out_json.open("xb") as fh:
        fh.write(raw)
    print(f"wrote {out_json} sha256 {hashlib.sha256(raw).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
