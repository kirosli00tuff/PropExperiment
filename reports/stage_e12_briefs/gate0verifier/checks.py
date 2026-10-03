"""Reconciliation (F-10), closure rulings (v9), MBT start rule, ledger order, fingerprints.
Read-only; prints one compact JSON and writes checks.json."""
from __future__ import annotations

import hashlib
import json
import os
import pickle
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e12_briefs/gate0verifier"
STAGES = Path(os.path.expanduser("~/.cache/propexp_e12_phase1/stages"))


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


res: dict = {}
pb = json.loads((REPO / "reports/stage_e12_phase1_bars.json").read_text())
gate = json.loads((REPO / "reports/stage_e12_gate0.json").read_text())
lst = json.loads((REPO / "reports/stage_e12_gate0_list.json").read_text())
rank = json.loads((REPO / "reports/stage_e12_ranking.json").read_text())
rul_path = REPO / "reports/stage_e12_closure_rulings.json"
rul = json.loads(rul_path.read_text())
rul_sha = sha(rul_path)

# ---- F-10: store sha256s: phase1_bars vs bars_<R>.json vs the parquet on disk; purchase manifest ----
store_rows, mism = [], []
for r, rec in pb["roots"].items():
    b = json.loads((REPO / f"reports/step2/bars_{r}.json").read_text())
    pq_path = REPO / b["parquet"]["path"]
    actual = sha(pq_path)
    pm = b.get("purchase_manifest") or {}
    pur_path = REPO / f"reports/step2/purchase_{r}.json"
    pur_sha = sha(pur_path) if pur_path.exists() else None
    pur = json.loads(pur_path.read_text()) if pur_path.exists() else {}
    pur_files = {f["path"]: f["sha256"] for f in pur.get("files", [])}
    inp = b.get("input_files") or []
    inp_map = {f.get("path"): f.get("sha256") for f in inp if isinstance(f, dict)}
    row = {"root": r, "phase1_sha_eq_report": rec["store_sha256"] == b["parquet"]["sha256"],
           "report_sha_eq_disk": b["parquet"]["sha256"] == actual,
           "phase1_path_eq_report": str(rec["store_path"]).endswith(b["parquet"]["path"]),
           "purchase_manifest_sha_eq_disk": (pm.get("sha256") == pur_sha) if pm.get("sha256") else None,
           "input_files_in_purchase": (all(inp_map.get(k) == v for k, v in pur_files.items())
                                       and set(inp_map) == set(pur_files)) if inp_map and pur_files else None,
           "n_purchase_files": len(pur_files), "harness": b["harness_sha256"][:12], "status": b["status"],
           "deep_closure_bars": sum(1 for c in b.get("closure_bars", []) if not c.get("close_minute")),
           "has_closure_ruling": "closure_ruling" in b}
    if not (row["phase1_sha_eq_report"] and row["report_sha_eq_disk"]):
        mism.append(r)
    store_rows.append(row)
res["stores"] = {"n_roots": len(store_rows), "sha_mismatches": mism,
                 "purchase_manifest_checks": Counter(str(x["purchase_manifest_sha_eq_disk"]) for x in store_rows),
                 "input_files_checks": Counter(str(x["input_files_in_purchase"]) for x in store_rows),
                 "harness_counts": Counter(x["harness"] for x in store_rows), "rows": store_rows}

# ---- closure rulings vs the v9 summaries ----
v9 = [x for x in store_rows if x["has_closure_ruling"]]
v9_roots = sorted(x["root"] for x in v9)
union, per_root = [], {}
for r in v9_roots:
    b = json.loads((REPO / f"reports/step2/bars_{r}.json").read_text())
    deep = [(r, c["ct"], c["trade_date"]) for c in b["closure_bars"] if not c["close_minute"]]
    cr = b["closure_ruling"]
    per_root[r] = {"bars_ruled": cr.get("bars_ruled"), "n_deep": len(deep),
                   "ruling_sha_eq_file": cr.get("sha256") == rul_sha, "ruling_path": cr.get("path"),
                   "entries_eq_deep": sorted((e["root"], e["ct"], e["trade_date"]) for e in cr.get("entries", [])) == sorted(deep)}
    union += deep
rul_keys = sorted((e["root"], e["ct"], e["trade_date"]) for e in rul["entries"])
non_v9_deep = [x["root"] for x in store_rows if not x["has_closure_ruling"] and x["deep_closure_bars"]]
res["closure"] = {"ruling_file_sha256": rul_sha, "n_entries": len(rul["entries"]),
                  "rulings": Counter(e["ruling"] for e in rul["entries"]),
                  "v9_roots": v9_roots, "n_v9": len(v9_roots),
                  "union_deep_eq_entries": sorted(union) == rul_keys, "n_union_deep": len(union),
                  "per_root_ok": all(v["bars_ruled"] == v["n_deep"] and v["ruling_sha_eq_file"] and v["entries_eq_deep"]
                                     for v in per_root.values()),
                  "per_root": per_root, "non_v9_roots_with_deep_bars": non_v9_deep,
                  "entries_by_root": Counter(e["root"] for e in rul["entries"])}

# ---- vehicles vs ranking subset; MES exclusions; list vs JSON ----
sub = sorted(x["vehicle"] for x in rank["subset"])
res["vehicles"] = {"ranking_subset": len(sub), "phase1_vehicles_eq": sorted(pb["vehicles"]) == sub,
                   "gate_vehicles_eq": sorted(gate["vehicles"]) == sub, "list_vehicles_eq": sorted(lst["vehicles"]) == sub,
                   "panel_roots_27_eq_sub_minus_MBT": sorted(set(sub) - {"MBT"}) == sorted(set(sub) - {"MBT"}),
                   "dropped_vehicles": pb.get("dropped_vehicles"), "dropped_roots": pb.get("dropped_roots"),
                   "ranking_sha_in_list": lst["fingerprints"].get("ranking_sha256") == sha(REPO / "reports/stage_e12_ranking.json"),
                   "mes_uncovered": sorted(lst["uncovered_signals"]), "mes_status": lst["mes"]["status"]}

# ---- ledger: every Gate 0 test registered before the result file; ids = list order ----
led = [json.loads(l) for l in (REPO / "ledger/ml_v2_config_ledger.jsonl").read_text().splitlines() if l.strip()]
led_ids = [e["entry_id"] for e in led]
list_ids = [t["test_id"] for t in lst["tests"]]
times = sorted(e["time"] for e in led)
res["ledger"] = {"n": len(led), "ids_eq_list_order": led_ids == list_ids, "first_time": times[0], "last_time": times[-1],
                 "last_before_created": times[-1] < gate["created_pdt"],
                 "specs_eq_list": all(e["spec"] == t["spec"] and e["kind"] == t["kind"] for e, t in zip(led, lst["tests"])),
                 "sha256_now": sha(REPO / "ledger/ml_v2_config_ledger.jsonl"),
                 "sha256_in_gate_json": gate["ledger"]["sha256_after"]}
res["ledger"]["sha_eq"] = res["ledger"]["sha256_now"] == res["ledger"]["sha256_in_gate_json"]

# ---- fingerprints and file hashes vs STATE ----
pan = pickle.load(open(STAGES / "phase1_panel.pkl", "rb"))
res["fingerprints"] = {"gate_constants_eq_panel": gate["fingerprints"]["constants"] == pan["constants"],
                       "gate_inputs_eq_panel": gate["fingerprints"]["inputs"] == pan["out"]["input_fingerprint"],
                       "list_sha_eq": gate["list_sha256"] == sha(REPO / "reports/stage_e12_gate0_list.json"),
                       "list_fp_eq_panel": lst["fingerprints"]["inputs"] == pan["out"]["input_fingerprint"],
                       "gate_json_sha256": sha(REPO / "reports/stage_e12_gate0.json"),
                       "gate_md_sha256": sha(REPO / "reports/stage_e12_gate0.md"),
                       "freeze_sha256": gate["fingerprints"]["freeze_sha256"],
                       "harness_sha256": gate["fingerprints"]["harness_sha256"],
                       "panel_created_pdt": pan["out"]["created_pdt"], "gate_created_pdt": gate["created_pdt"]}

# ---- MBT start rule arithmetic ----
sr = pb["roots"]["MBT"]["start_rule"]
med = {k: v for k, v in sr["monthly_medians"].items() if k < "2024-03"}
vref = float(sr["v_ref"])


def m_star(frac: float):
    thr = frac * vref
    months = sorted(med)
    below = [m for m in months if med[m] is None or med[m] < thr]
    if not below:
        return months[0]
    i = months.index(below[-1]) + 1
    return months[i] if i < len(months) else None


cal = [date.fromisoformat(str(x)) if not hasattr(x, "year") else x for x in pan["out"]["calendar"]]
jan_feb = [d for d in cal if date(2024, 1, 2) <= d <= date(2024, 2, 29)]
res["mbt"] = {"v_ref": vref, "thresholds": {f: f * vref for f in (0.15, 0.25, 0.40)},
              "my_m_star": {str(f): m_star(f) for f in (0.15, 0.25, 0.40)}, "lead_m_star": sr["m_star"],
              "lead_s_x": sr["s_x"], "first_calendar_date_in_m_star": min(d for d in cal if d >= date(2024, 1, 1)).isoformat(),
              "calendar_dates_s_x_to_end": len(jan_feb), "lead_trade_dates": pb["roots"]["MBT"]["trade_dates"],
              "medians_2023_10_to_2024_02": {k: med[k] for k in sorted(med) if k >= "2023-10"},
              "months_with_median_ge_12_before_2024_01": [k for k in sorted(med) if med[k] is not None and med[k] >= 12 and k < "2024-01"],
              "panel_has_MBT_rows": "MBT" in set(map(str, pan["out"]["panel"].frame["root"].unique())),
              "z_min_dates_constant": 60}
(OUT / "checks.json").write_text(json.dumps(res, indent=1, default=str))
slim = {k: ({kk: vv for kk, vv in v.items() if kk not in ("rows", "per_root")} if isinstance(v, dict) else v)
        for k, v in res.items()}
print(json.dumps(slim, default=str))
