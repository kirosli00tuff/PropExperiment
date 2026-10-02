"""Render the mutant results JSON files as the report's markdown table (stdout)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

AUDIT = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e9_briefs/audit_k8")
rows = []
elapsed = 0.0
changed: list[str] = []
for path in sorted(AUDIT.glob("mutants_results*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    elapsed += data["elapsed_s"]
    changed += data["guarded_files_changed"]
    rows += data["results"]
n = sum(1 for r in rows if not r["id"].startswith("NOOP"))
killed = sum(1 for r in rows if r["status"] == "killed")
survived = [r["id"] for r in rows if r["status"] == "SURVIVED"]
bad = [r["id"] for r in rows if r["status"] == "BAD_MUTANT"]
controls = [r["status"] for r in rows if r["id"].startswith("NOOP")]
print(f"Totals: {n} mutants, {killed} killed, {len(survived)} survived ({', '.join(survived) or 'none'}), "
      f"{len(bad)} badly built ({', '.join(bad) or 'none'}); controls {controls}; guarded files changed: "
      f"{changed or 'none'}; wall time {elapsed / 60:.1f} min.")
print()
print("| Id | Module | Mutant | Result | Tests failing (count; first two) |")
print("|---|---|---|---|---|")
for r in rows:
    if r["id"].startswith("NOOP"):
        continue
    names = ", ".join(x.split("::")[-1] for x in r.get("failing", [])[:2])
    what = r["what"].replace("|", "\\|")
    print(f"| {r['id']} | {r['module']} | {what} | {r['status']} | {r.get('failed', '')}; {names} |")
if len(sys.argv) > 1:
    pass
