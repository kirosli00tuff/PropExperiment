"""Start/end check for Stage E.2b: both freeze manifests and the E.2a hashed tables."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
AUDIT_BLOB = {"reports/stage_e1_freeze_audit.md": "848f331", "reports/stage_e2a_declaration_audit.md": "ba67073"}
def sha(b): return hashlib.sha256(b).hexdigest()
bad = 0
for man in ["reports/stage_e1_freeze.json", "reports/stage_e2a_ml_freeze.json"]:
    raw = (ROOT / man).read_bytes()
    d = json.loads(raw); n_ok = 0
    for rel, info in d["files"].items():
        if rel in AUDIT_BLOB:
            b = subprocess.run(["git", "show", f"{AUDIT_BLOB[rel]}:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout
            src = f"blob@{AUDIT_BLOB[rel]}"
        else:
            b = (ROOT / rel).read_bytes(); src = "worktree"
        ok = sha(b) == info["sha256"] and len(b) == info["bytes"]
        n_ok += ok
        if not ok: bad += 1; print("MISMATCH", man, rel, src)
    print(f"{man}: manifest sha256 {sha(raw)} files {n_ok}/{len(d['files'])} match")
TABLES = {
 "reports/stage_e2a_costs.json": "f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14",
 "reports/stage_e2a_vehicle_sizes.json": "280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325",
 "reports/stage_e2a_vehicles.json": "1f1cafee4330961799f33d5493e640897cfa79827be98597dbaba23292e29913",
 "reports/stage_e2a_vehicle_rule_readings.md": "8c3c29dd6531782b6b98d75192071977b8caebd37c48de6cab0afd1642d6b458",
 "reports/stage_e2a_epsilon_declaration.md": "ccdb8ec53f9015d45f60de7d7b6a8a37f1fc8e3dd921723e78b01d158be28c7c",
 "reports/stage_e2a_epsilon_declaration_addendum.md": "e6253be2274303f8b219bef539b3807935bbe80e0c1462289c56ff0dc6b88d32",
 "reports/stage_e2a_source_window_amendment.md": "9fe401c1c156ebba38162256bf151d9888dec00e42cd24026d348d039e64f13d",
 "reports/stage_e2a_epsilon.json": "4e2c773182a23e7d073305ca4eb0134d3b3ac554ccc8215730bc1e194eaff496",
}
for rel, h in TABLES.items():
    got = sha((ROOT / rel).read_bytes()); ok = got == h
    bad += not ok
    print(f"{'OK      ' if ok else 'MISMATCH'} {rel} {got[:8]}...{got[-4:]}")
print("ALL_OK" if bad == 0 else f"FAILURES {bad}")
sys.exit(1 if bad else 0)
