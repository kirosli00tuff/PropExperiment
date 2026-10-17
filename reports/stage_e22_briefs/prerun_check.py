"""Stage E.22 Part A: pre-run check of one cluster's committed confirmation list (harness review R-1 mitigation).

Usage: uv run python reports/stage_e22_briefs/prerun_check.py CLUSTER
Checks, before the cluster's run-once confirmation run: the list JSON is tracked and unchanged against HEAD;
its cluster_freeze_sha256 equals the loaded cluster freeze's; every trial's vehicle equals its member's traded
leg and its legs equal the member's legs, ordinal for ordinal; the list's harness equals the committed manifest;
the out-dir and the marker do not exist yet. Prints one line per check; exit 0 only when all pass.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from screening.stage_e_freeze import load_cluster_freeze

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    cluster = sys.argv[1]
    k = cluster.lower()
    lst = ROOT / f"reports/stage_e22_{k}_confirmation_list.json"
    d = json.loads(lst.read_bytes())
    fr = load_cluster_freeze(cluster)
    ok = True

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        ok &= cond
        print(f"{'PASS' if cond else 'FAIL'} {name}{': ' + detail if detail else ''}")

    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(lst.relative_to(ROOT))], cwd=ROOT,
                             capture_output=True).returncode == 0
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(lst.relative_to(ROOT))], cwd=ROOT).returncode == 0
    check("list tracked and unchanged vs HEAD", tracked and clean)
    check("cluster_freeze_sha256", d["cluster_freeze_sha256"] == fr.sha256, f"{d['cluster_freeze_sha256'][:12]} vs {fr.sha256[:12]}")
    manifest = hashlib.sha256((ROOT / "reports/stage_e2b_harness_freeze.json").read_bytes()).hexdigest()
    check("harness_sha256 = committed manifest", d["harness_sha256"] == manifest, manifest[:12])
    members = {m.ordinal: m for m in fr.members}
    check("trial ordinals = freeze ordinals", sorted(t["ordinal"] for t in d["trials"]) == sorted(members))
    for t in d["trials"]:
        m = members.get(t["ordinal"])
        if m is None:
            check(f"ordinal {t['ordinal']} in freeze", False)
            continue
        traded = next(leg.root for leg in m.legs if leg.traded)
        same = t["member"] == m.label and t["vehicle"] == traded and t["legs"] == [leg.root for leg in m.legs]
        if not same:
            check(f"trial {t['ordinal']} {t['member']}", False, f"freeze {m.label} {traded} {[l.root for l in m.legs]}")
    check("every trial's member, vehicle and legs = freeze", ok)
    check("out-dir absent", not (ROOT / f"reports/stage_e22_confirm_{k}").exists())
    check("marker absent", not (ROOT / f"reports/stage_e22_{cluster}_RUN_ONCE.json").exists())
    print("ALL PASS" if ok else "CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
