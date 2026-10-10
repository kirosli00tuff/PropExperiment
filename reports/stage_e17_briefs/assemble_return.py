"""Stage E.17: assemble reports/E.17_RETURN.md and the progress entry from the template, the section files, the
collapsed guardrail checks and the cost script's table. Values that exist only at the end are passed as arguments.

Usage (repo root): python3 reports/stage_e17_briefs/assemble_return.py --end-time 02:40 --end-suite "<line>" \
    --end-suite-short 6916 --t16 0:59 --total-work 7:58 --cost-table <cost script output> --h-verify-summary "<text>"
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

B = Path("reports/stage_e17_briefs")


def collapsed(name: str) -> str:
    return subprocess.run([sys.executable, str(B / "collapse_checks.py"), str(B / name)], capture_output=True,
                          text=True, check=True).stdout.rstrip("\n")


def cost_parts(path: Path) -> tuple[str, str, str, str]:
    """(per-transcript lines, the per-model table, the 'all' total, the delegation-share line)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    spawn = [x for x in lines if x.startswith(("lead ", "agent-"))]
    table = [x for x in lines if x.startswith("|")]
    total = next(x for x in table if x.startswith("| all |")).split("|")[-2].strip()
    by_who, by_model = {"lead": 0, "workers": 0}, {}
    for x in spawn:
        n = int(re.search(r"total=(\d+)", x).group(1))
        model = x.split()[1]
        by_who["lead" if x.startswith("lead ") else "workers"] += n
        by_model[model] = by_model.get(model, 0) + n
    grand = sum(by_who.values())
    share = (f"Delegation share: lead {by_who['lead']:,} ({by_who['lead'] / grand:.1%}), workers "
             f"{by_who['workers']:,} ({by_who['workers'] / grand:.1%}); by model "
             + ", ".join(f"{m} {n:,} ({n / grand:.1%})" for m, n in sorted(by_model.items())) + ".")
    return "\n".join(f"    {x}" for x in spawn), "\n".join(table), total, share


def main() -> int:
    ap = argparse.ArgumentParser()
    for name in ("--end-time", "--end-suite", "--end-suite-short", "--t16", "--total-work", "--cost-table",
                 "--h-verify-summary"):
        ap.add_argument(name, required=True)
    a = ap.parse_args()
    spawns, table, total, share = cost_parts(Path(a.cost_table))
    cost_body = (B / "ret_cost_head.md").read_text(encoding="utf-8")
    cost_body += ("\n### Tokens per model (session 0dcecb5d's transcript and its 5 subagent transcripts, "
                  "2026-10-10 01:30Z on; reports/stage_e10_briefs/cost.py)\n\n" + table + "\n\n" + share
                  + "\n\nPer transcript (model, messages, first and last UTC, input, output, cache read, cache "
                  "creation, total):\n\n" + spawns + "\n\nThese are token counts from the transcripts, not "
                  "plan-credit percentages; the session cannot read the /usage meter.\n")
    for k, v in {"{{END_TIME}}": a.end_time, "{{T16}}": a.t16, "{{TOTAL_WORK}}": a.total_work,
                 "{{TOTAL_TOKENS}}": total}.items():
        cost_body = cost_body.replace(k, v)
    doc = (B / "return_template.md").read_text(encoding="utf-8")
    parts = {
        "{{START_CHECKS}}": collapsed("start_checks.txt"),
        "{{POST_C1_CHECKS}}": collapsed("post_c1_purchase_checks.txt"),
        "{{POST_H_CHECKS}}": collapsed("post_h_purchase_checks.txt"),
        "{{END_CHECKS}}": collapsed("end_checks.txt"),
        "{{END_SUITE}}": a.end_suite,
        "{{H_VERIFY_SUMMARY}}": a.h_verify_summary,
        "{{H_VERIFY_END}}": "02:03",
        "{{END_TIME}}": a.end_time,
        "{{RESULTS_PER_STEP}}": (B / "ret_results.md").read_text(encoding="utf-8").rstrip("\n"),
        "{{DELEGATION_ROWS}}": (B / "ret_delegation.md").read_text(encoding="utf-8").rstrip("\n"),
        "{{VERIFICATION}}": (B / "ret_verification.md").read_text(encoding="utf-8").rstrip("\n"),
        "{{OPEN_CHOICES}}": (B / "ret_open_choices.md").read_text(encoding="utf-8").rstrip("\n"),
        "{{DECISIONS}}": (B / "ret_decisions.md").read_text(encoding="utf-8").rstrip("\n"),
        "{{SESSION_COST}}": cost_body.rstrip("\n"),
    }
    for k, v in parts.items():
        doc = doc.replace(k, v)
    if "{{" in doc or "}}" in doc:
        raise SystemExit("unfilled placeholders remain in the return")
    Path("reports/E.17_RETURN.md").write_text(doc, encoding="utf-8")
    entry = (B / "progress_entry.md").read_text(encoding="utf-8")
    entry = entry.replace("{{END_SUITE_SHORT}}", a.end_suite_short).replace("{{SESSION_COST_BODY}}",
                                                                            cost_body.rstrip("\n"))
    if "{{" in entry:
        raise SystemExit("unfilled placeholders in the progress entry")
    (B / "progress_entry_final.md").write_text(entry, encoding="utf-8")
    print("wrote reports/E.17_RETURN.md and", B / "progress_entry_final.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
