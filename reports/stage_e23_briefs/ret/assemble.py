"""Assemble reports/E.23_RETURN.md from the section drafts in this folder (lead, Stage E.23)."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEFS = HERE.parent
REPO = BRIEFS.parent.parent


def tracked_only(name: str) -> str:
    lines = (BRIEFS / name).read_text().splitlines()
    return "\n".join(x for x in lines if not x.startswith("?? "))


def untracked_count(name: str) -> int:
    return sum(1 for x in (BRIEFS / name).read_text().splitlines() if x.startswith("?? "))


def tail(name: str, n: int) -> str:
    return "\n".join((BRIEFS / name).read_text().splitlines()[-n:])


def sec(name: str) -> str:
    return (HERE / name).read_text().rstrip() + "\n"


final = BRIEFS / "end_checks_final.txt"
if final.exists():
    tmp = Path("/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/09fe7046-23b3-4a60-9a36-ff97fd7dcbf1/scratchpad")
    (tmp / "a.txt").write_text(tracked_only("end_checks.txt") + "\n")
    (tmp / "b.txt").write_text(tracked_only("end_checks_final.txt") + "\n")
    diff = subprocess.run(["diff", str(tmp / "a.txt"), str(tmp / "b.txt")], capture_output=True, text=True).stdout.rstrip()
    final_block = (
        "### 2.3 Final checks before the commit (reports/stage_e23_briefs/end_checks_final.txt; its difference from the "
        f"05:21:40 run, untracked lines omitted: {untracked_count('end_checks_final.txt')} in the final run)\n\n```\n{diff}\n```\n\n"
        "Every other tracked line is identical to the 05:21:40 run:\n"
        "- holdout all_ok with 0 unlocks, REGISTRATION.md 0 bytes;\n"
        "- harness v13 dd2bcc60... OK;\n"
        "- spend ledger 36,402 lines, 034a454b...;\n"
        "- N = 538 (9 lines, 25c04088...);\n"
        "- the E.23 freeze verified (20 inputs, 5 ids, exit 0), and both markers read-only.\n"
    )
else:
    final_block = "### 2.3 Final checks before the commit\n\nFINAL_CHECKS_PENDING\n"

head = f"""# Stage E.23 return: the program's intraday triggers at multi-day holds

Prompt: docs/prompts/STAGE_E.23.md. Lead: Opus 5.5 at xhigh, under ultracode. Session 09fe7046-23b3-4a60-9a36-ff97fd7dcbf1,
unattended. Date 2026-10-17; all times are PDT (America/Vancouver).

Key files:
- Prereg: reports/stage_e23_prereg.md. Freeze: reports/stage_e23_freeze.json (sha256 24dcf4dd...). Registry: r008-E23.
- Results: reports/stage_e23_runs/discovery/discovery_result.json and reports/stage_e23_runs/confirmation/confirmation_result.json.
- Markers: reports/stage_e23_RUN_ONCE_discovery.json and reports/stage_e23_RUN_ONCE_confirmation.json.
- Verification: reports/stage_e23_briefs/verify/verdict_verify.md.

"""

sec2 = f"""## 2. Guardrail evidence

Script: reports/stage_e23_briefs/checks.sh (E.22's checks plus the E.23 freeze and the markers). Every line is quoted
verbatim except the untracked (`??`) lines of `git status --short`, which are omitted: {untracked_count('start_checks.txt')}
at the start and {untracked_count('end_checks.txt')} at the end (Open choice 26). The full files are
reports/stage_e23_briefs/start_checks.txt and end_checks.txt.

The five failing earlier-freeze checks are the expected harness-v13 failures:
- the E.14 C1 inputs list;
- E.16 and E.18;
- E.20 H6 and the E.20 search.

Each pinned v12 files that v13 rewrote, and none was edited. The suite's one failure, tests/test_h6_rod_run.py, has the
same cause.

### 2.1 Start checks (02:03:59-02:04:14)

```
{tracked_only('start_checks.txt')}
```

Start suite, `uv run pytest -q -p no:cacheprovider` (detached at nice 10, 02:04:19-02:28:56; reports/stage_e23_briefs/pytest_start.out):

```
{tail('pytest_start.out', 3)}
```

### 2.2 End checks (05:21:40-05:22:01, after both reads)

```
{tracked_only('end_checks.txt')}
```

End suite (detached at nice 10, 05:22:14-05:41:25; at least 8 GB free at launch; reports/stage_e23_briefs/pytest_end.out).
The code is identical to the final commit's; the 94 new trigger_hold tests are included.

```
{tail('pytest_end.out', 3)}
```

{final_block}
"""

parts = [head, sec("sec1_summary.md"), sec2, sec("sec2_order.md"), sec("sec3_results.md"), sec("sec4_delegation.md"),
         sec("sec5_verification.md"), sec("sec6_open_choices.md"), sec("sec7_decisions.md"), sec("sec8_cost.md")]
text = "\n".join(parts)
(REPO / "reports" / "E.23_RETURN.md").write_text(text)
print("written", len(text.splitlines()), "lines; placeholders:",
      [p for p in ("FINAL_CHECKS_PENDING", "VERIFIER_END", "VERIFIER_STATUS", "FINAL_END", "COST_PENDING") if p in text])
