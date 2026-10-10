"""Check 5 (VerdictVerifier-FableXHigh, Stage E.17): registration and input hashes of C1's run.

Read-only. Compares, against the files on disk: the freeze file's sha256 and the registry entry
r001-C1; the harness manifest (screening.harness_freeze.check); the model JSON and both M1
payloads; the store-hashes and calendar-hashes files and every file they list; the six ext2010
stores; c1_replication's code hashes; and the marker's inputs block against the result's. Writes
reports/stage_e17_c1_verify/hashes.json. Prints hashes, booleans and counts only.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.nice(10)

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

OUT = REPO / "reports" / "stage_e17_c1_verify" / "hashes.json"
RESULT = REPO / "reports" / "stage_e14_c1_result.json"
MARKER = REPO / "reports" / "stage_e14_c1_RUN_ONCE.json"
FREEZE = REPO / "reports" / "stage_e14_prereg_C1.md"
FREEZE_SHA256 = "afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b"
HARNESS_SHA256 = "ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292"
REGISTRY = REPO / "ledger" / "trial_registrations.jsonl"
MODEL = REPO / "reports" / "stage_e14_c1_model.json"
MODEL_DIR = Path.home() / ".cache" / "propexp_e14_c1" / "m1"
STORE_HASHES = REPO / "reports" / "stage_e17_c1_store_hashes.json"
CALENDAR_HASHES = REPO / "reports" / "stage_e17_c1_calendar_hashes.json"
CODE_DIR = REPO / "c1_replication"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> tuple[int, str]:
    proc = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main() -> int:
    from screening import harness_freeze

    result = json.loads(RESULT.read_bytes())
    marker = json.loads(MARKER.read_bytes())
    inputs = result["inputs"]
    rec: dict = {"schema": "stage_e17_c1_verify/hashes/1"}

    # Freeze file: sha256, git state.
    freeze_sha = sha256(FREEZE)
    rec["freeze"] = {"sha256_on_disk": freeze_sha, "expected": FREEZE_SHA256,
                     "equal": freeze_sha == FREEZE_SHA256,
                     "result_inputs_equal": inputs["freeze"]["sha256"] == FREEZE_SHA256,
                     "git_ls_files_rc": git("ls-files", "--error-unmatch", str(FREEZE.relative_to(REPO)))[0],
                     "git_diff_quiet_rc": git("diff", "--quiet", "HEAD", "--", str(FREEZE.relative_to(REPO)))[0]}

    # Registry entry.
    entries = [json.loads(line) for line in REGISTRY.read_text().splitlines() if line.strip()]
    c1 = [e for e in entries if e.get("entry_id") == "r001-C1"]
    e = c1[0] if c1 else {}
    rec["registry"] = {"lines": len(entries), "r001_C1_entries": len(c1),
                       "test": e.get("test"), "test_ids": e.get("test_ids"),
                       "freeze_sha256_equal": e.get("freeze_sha256") == FREEZE_SHA256,
                       "harness_sha256_equal": e.get("harness_sha256") == HARNESS_SHA256,
                       "n_before": e.get("n_before"), "n_after": e.get("n_after"),
                       "time_local": e.get("time_local"),
                       "result_inputs_registry": inputs["registry"],
                       "result_inputs_match": (inputs["registry"]["entry_id"] == "r001-C1"
                                               and inputs["registry"]["n_before"] == e.get("n_before")
                                               and inputs["registry"]["n_after"] == e.get("n_after"))}

    # Harness manifest: screening.harness_freeze.check against the expected sha256.
    problems, digest = harness_freeze.check(REPO, HARNESS_SHA256)
    rec["harness"] = {"manifest_sha256": digest, "expected": HARNESS_SHA256,
                      "equal": digest == HARNESS_SHA256, "problems": len(problems),
                      "problems_head": problems[:5],
                      "result_inputs_equal": inputs["harness_sha256"] == HARNESS_SHA256}

    # Model JSON and M1 payloads.
    model_sha = sha256(MODEL)
    model = json.loads(MODEL.read_bytes())
    payloads = {}
    for h in ("h60", "hF"):
        p = MODEL_DIR / f"c1_m1_{h}.ridge"
        payloads[h] = {"path": str(p), "exists": p.exists(),
                       "sha256": sha256(p) if p.exists() else None,
                       "model_json": model["m1"][h].get("payload_sha256"),
                       "result_inputs": inputs["model"]["m1_payload_sha256"][h]}
        payloads[h]["equal"] = (payloads[h]["sha256"] == payloads[h]["model_json"]
                                == payloads[h]["result_inputs"])
    rec["model"] = {"sha256_on_disk": model_sha, "result_inputs": inputs["model"]["sha256"],
                    "equal": model_sha == inputs["model"]["sha256"],
                    "feature_cols_sha256_equal": model["feature_cols_sha256"] == inputs["model"]["feature_cols_sha256"],
                    "q_repr_equal": {h: model["q"][h]["q_repr"] == inputs["model"]["q"][h] for h in ("h60", "hF")},
                    "m1_payloads": payloads}

    # Store hashes file and the six stores.
    sh_sha = sha256(STORE_HASHES)
    sh = json.loads(STORE_HASHES.read_bytes())
    stores = {}
    for root, expected in sh["stores"].items():
        p = REPO / inputs["stores"][root]["path"]
        on_disk = sha256(p) if p.exists() else None
        stores[root] = {"path": str(p.relative_to(REPO)), "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else None,
                        "sha256_on_disk": on_disk, "hashes_file": expected,
                        "result_inputs": inputs["stores"][root]["sha256"],
                        "result_world": result["world"]["roots"][root]["sha256"],
                        "equal": on_disk == expected == inputs["stores"][root]["sha256"]
                        == result["world"]["roots"][root]["sha256"]}
    rec["store_hashes_file"] = {"sha256_on_disk": sh_sha, "result_inputs": inputs["store_hashes_file"]["sha256"],
                                "equal": sh_sha == inputs["store_hashes_file"]["sha256"]}
    rec["stores"] = stores

    # Calendar hashes file and every file it lists.
    ch_sha = sha256(CALENDAR_HASHES)
    ch = json.loads(CALENDAR_HASHES.read_bytes())
    cals = {}
    for g, v in ch["calendars"].items():
        p = REPO / v["path"]
        on_disk = sha256(p)
        cals[g] = {"path": v["path"], "sha256_on_disk": on_disk, "hashes_file": v["sha256"],
                   "result_inputs": inputs["calendar_inputs"]["calendars"][g]["sha256"],
                   "equal": on_disk == v["sha256"] == inputs["calendar_inputs"]["calendars"][g]["sha256"]}
    for key in ("releases", "energy_full_sessions"):
        p = REPO / ch[key]["path"]
        on_disk = sha256(p)
        res = inputs["calendar_inputs"].get(key, {})
        cals[key] = {"path": ch[key]["path"], "sha256_on_disk": on_disk, "hashes_file": ch[key]["sha256"],
                     "result_inputs": res.get("sha256"),
                     "equal": on_disk == ch[key]["sha256"] and (res.get("sha256") in (None, on_disk))}
    rec["calendar_hashes_file"] = {"sha256_on_disk": ch_sha,
                                   "result_inputs": inputs["calendar_inputs"]["hashes_file"]["sha256"],
                                   "equal": ch_sha == inputs["calendar_inputs"]["hashes_file"]["sha256"]}
    rec["calendars"] = cals

    # c1_replication code hashes versus the result's and the model JSON's.
    code = {p.name: sha256(p) for p in sorted(CODE_DIR.glob("*.py"))}
    rec["code"] = {"on_disk": code, "equal_result": code == inputs["code_sha256"],
                   "equal_model_json": code == model["code_sha256"],
                   "differences_vs_result": sorted(k for k in set(code) | set(inputs["code_sha256"])
                                                   if code.get(k) != inputs["code_sha256"].get(k))}

    # Marker versus result.
    rec["marker"] = {"inputs_equal_result": marker["inputs"] == inputs,
                     "started_equal": marker["started_local"] == result["started_local"],
                     "out": marker["out"], "marker_keys": sorted(marker.keys()),
                     "marker_inputs_keys": sorted(marker["inputs"].keys())}

    # The other pinned inputs the result records.
    v2 = REPO / "reports" / "stage_e12_ml_v2_freeze.json"
    g0 = REPO / "reports" / "stage_e12_gate0_list.json"
    rec["v2_freeze"] = {"sha256_on_disk": sha256(v2), "result_inputs": inputs["v2_freeze"]["sha256"],
                        "equal": sha256(v2) == inputs["v2_freeze"]["sha256"]}
    rec["gate0_list"] = {"sha256_on_disk": sha256(g0), "result_inputs": inputs["gate0_list"]["sha256"],
                         "equal": sha256(g0) == inputs["gate0_list"]["sha256"]}

    checks = {
        "freeze": rec["freeze"]["equal"] and rec["freeze"]["result_inputs_equal"]
        and rec["freeze"]["git_ls_files_rc"] == 0 and rec["freeze"]["git_diff_quiet_rc"] == 0,
        "registry": rec["registry"]["r001_C1_entries"] == 1 and rec["registry"]["freeze_sha256_equal"]
        and rec["registry"]["test_ids"] == ["C1-T1", "C1-T2"] and rec["registry"]["n_before"] == 471
        and rec["registry"]["n_after"] == 473 and rec["registry"]["result_inputs_match"],
        "harness": rec["harness"]["equal"] and rec["harness"]["problems"] == 0 and rec["harness"]["result_inputs_equal"],
        "model": rec["model"]["equal"] and all(p["equal"] for p in payloads.values())
        and rec["model"]["feature_cols_sha256_equal"] and all(rec["model"]["q_repr_equal"].values()),
        "store_hashes_file": rec["store_hashes_file"]["equal"],
        "stores": all(s["equal"] for s in stores.values()),
        "calendar_hashes_file": rec["calendar_hashes_file"]["equal"],
        "calendars": all(c["equal"] for c in cals.values()),
        "code": rec["code"]["equal_result"] and rec["code"]["equal_model_json"],
        "marker": rec["marker"]["inputs_equal_result"] and rec["marker"]["started_equal"],
        "v2_freeze": rec["v2_freeze"]["equal"], "gate0_list": rec["gate0_list"]["equal"],
    }
    rec["checks"] = checks
    rec["all_pass"] = all(checks.values())
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n")
    for k, v in checks.items():
        print(f"{k}: {'ok' if v else 'FAIL'}")
    print(f"harness manifest sha256 {digest} problems {len(problems)}")
    print(f"all pass: {rec['all_pass']}; written {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
