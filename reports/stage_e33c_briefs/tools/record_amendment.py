"""Append the protocol 0.3 amendment record beside registration r009-E33 (ledger/trial_amendments.jsonl; one line, once).

screening.trial_registry refuses to amend a registration, so the amendment lives in its own append-only file next to
the registry. N does not change (no configuration is added). Usage: python3 -I record_amendment.py <repo> <review verdict>
"""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

repo = Path(sys.argv[1])
verdict = sys.argv[2]
led = repo / "ledger/trial_amendments.jsonl"
reg = repo / "ledger/trial_registrations.jsonl"


def sha(rel: str) -> str:
    return hashlib.sha256((repo / rel).read_bytes()).hexdigest()


entries = [json.loads(x) for x in led.read_text().splitlines() if x.strip()] if led.exists() else []
if any(e.get("amendment_id") == "a001-E33" for e in entries):
    raise SystemExit("a001-E33 is already recorded: an amendment line is written once")
last = [json.loads(x) for x in reg.read_text().splitlines() if x.strip()][-1]
assert last["entry_id"] == "r009-E33" and last["n_after"] == 838, last["entry_id"]
v03 = "reports/stage_e32_discovery_protocol_v0.3.md"
v03_sha = sha(v03)
sha_file = (repo / "reports/stage_e32_discovery_protocol_v0.3.sha256").read_text().split()[0]
assert sha_file == v03_sha, "the 0.3 sha256 file does not match the 0.3 text"
rec = {
    "schema": "trial-amendment/1", "amendment_id": "a001-E33", "registration": "r009-E33", "test": "E33",
    "time_local": datetime.now().astimezone().isoformat(timespec="seconds"),
    "decision": "V53 (docs/DECISIONS.md, user 2026-10-28 18:04 PDT)",
    "protocol_from": {"path": "reports/stage_e32_discovery_protocol.md", "version": "FROZEN v1.0 (the prompt's 0.2)",
                      "sha256": sha("reports/stage_e32_discovery_protocol.md")},
    "protocol_to": {"path": v03, "version": "0.3", "sha256": v03_sha},
    "diff": {"path": "reports/stage_e33c_briefs/protocol_v0.3.diff", "sha256": sha("reports/stage_e33c_briefs/protocol_v0.3.diff")},
    "changed": "P5 compute-stop reference (R_0.3 replaces the synthetic-probe reference; 3x stop kept) and the P10 "
               "clause that names it; status paragraph",
    "reference": {"path": "reports/stage_e33c_briefs/ref_v03.json", "sha256": sha("reports/stage_e33c_briefs/ref_v03.json"),
                  "method_script_sha256": sha("reports/stage_e33c_briefs/tools/project_ref_v03.py")},
    "review": {"path": "reports/stage_e33c_briefs/review/AmendReview_c.md", "verdict": verdict,
               "sha256": sha("reports/stage_e33c_briefs/review/AmendReview_c.md")},
    "n_before": 838, "n_after": 838, "configurations_added": 0,
    "note": "Stage E.33c S2: the search resumes the same registration from its DONE markers; no outcome was read.",
}
with open(led, "a") as fh:
    fh.write(json.dumps(rec, sort_keys=True) + "\n")
print(json.dumps({k: rec[k] for k in ("amendment_id", "registration", "time_local", "n_after")}),
      "| 0.3 sha256", v03_sha)
