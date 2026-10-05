"""Stage E.14: write reports/stage_e14_c1_freeze_inputs.json, the list of every file test C1's freeze pins.

Each entry: path, sha256, bytes, role. The freeze (reports/stage_e14_prereg_C1.md) cites this file's sha256;
the later session verifies every entry before it registers, buys or evaluates. Prints the manifest's sha256 and
the count per role only.

Usage (from the repository root): python3 reports/stage_e14_briefs/c1_freeze_inputs.py <harness sha256>
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

OUT = Path("reports/stage_e14_c1_freeze_inputs.json")
ROLES = {
    "design": ["reports/stage_e13_prereg_ngrepl.md", "reports/stage_e13_ng_replication_draft.md",
               "reports/stage_e13_rulings.md", "docs/prompts/STAGE_E.14.md"],
    "calendar": sorted(glob.glob("data/calendars/hist2010/*.json"))
                + ["reports/stage_e14_cal_releases.json", "reports/stage_e14_cal_energy_full_sessions.json"],
    "calendar_report": ["reports/stage_e14_probe.md", "reports/stage_e14_calendars.md",
                        "reports/stage_e14_cal_financials.md", "reports/stage_e14_cal_commod.md",
                        "reports/stage_e14_cal_releases.md"],
    "code": sorted(glob.glob("c1_replication/*.py")) + ["c1_replication/README.md"],
    "test": sorted(glob.glob("tests/test_c1_*.py")) + sorted(glob.glob("tests/_c1_*.py")),
    "e12_state": ["reports/stage_e14_c1_e12_state_manifest.json", "reports/stage_e12_ml_v2_freeze.json",
                  "reports/stage_e12_gate0.json", "reports/stage_e12_gate0_list.json",
                  "ml_route_v2/constants.py"],
    "harness": ["reports/stage_e2b_harness_freeze.json"],
    "quote": ["reports/stage_e14_quotes_ext2010.json"],
}


def sha(path: str) -> tuple[str, int]:
    raw = Path(path).read_bytes()
    return hashlib.sha256(raw).hexdigest(), len(raw)


def main(harness_sha256: str) -> None:
    files = []
    for role, paths in ROLES.items():
        for p in paths:
            h, n = sha(p)
            files.append({"path": p, "sha256": h, "bytes": n, "role": role})
    if sha("reports/stage_e2b_harness_freeze.json")[0] != harness_sha256:
        raise SystemExit("the harness manifest is not the expected one")
    doc = {"schema": "stage_e14_c1_freeze_inputs/1", "test": "C1",
           "harness_manifest_sha256": harness_sha256,
           "e12_state_copy": "~/.cache/propexp_e14_c1/e12_state_copy",
           "files": files}
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    counts: dict[str, int] = {}
    for f in files:
        counts[f["role"]] = counts.get(f["role"], 0) + 1
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest(), len(files), counts)


if __name__ == "__main__":
    main(sys.argv[1])
