"""Stage E.18: assemble reports/E.18_RETURN.md from its parts (sections in the prompt's fixed order).
Usage: python3 reports/stage_e18_briefs/assemble_return.py <final commit hash or 'pending'>"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

B = Path("reports/stage_e18_briefs")
OUT = Path("reports/E.18_RETURN.md")


def collapsed(path: Path) -> str:
    return subprocess.run([sys.executable, "reports/stage_e17_briefs/collapse_checks.py", str(path)],
                          capture_output=True, text=True, check=True).stdout.rstrip()


def tail(path: Path, n: int) -> str:
    return "\n".join(path.read_text().rstrip().splitlines()[-n:])


def main() -> int:
    final = sys.argv[1] if len(sys.argv) > 1 else "pending"
    part = lambda name: (B / name).read_text().rstrip()  # noqa: E731
    events = f"""| Event | Evidence | Time (PDT) |
|---|---|---|
| Start checks | reports/stage_e18_briefs/start_checks.txt | 11:47:18 |
| Start suite | reports/stage_e18_briefs/pytest_start.out | 11:47:32-12:05:36 |
| C1b text, code, test written | file mtimes (c1b.py 11:52:07, prereg first version 11:56:07) | 11:48-11:57 |
| Diff review (DiffReviewer-FableXHigh) | reports/stage_e18_review.md lines 5-6; transcript | 11:58:43-12:14:08 |
| Rulings R-1..R-5 applied, text regenerated | reports/stage_e18_prereg_C1b.md mtime | 12:14:38 |
| Dry check | reports/stage_e18_dry_check.json started/finished | 12:16:02-12:16:05 |
| Freeze manifest written / verified | reports/stage_e18_freeze.json mtime; verify run | 12:17:07 / 12:17:22 |
| Freeze commit b714751 "C1b freeze" | git log | 12:17:35 |
| Registration r003-C1b (N 478 -> 480) | ledger/trial_registrations.jsonl time_local | 12:17:48 |
| Evaluation launched (detached) | reports/stage_e18_briefs/c1b_evaluate.log line 1 | 12:18:03 |
| Run-once marker | reports/stage_e18_c1b_RUN_ONCE.json started_local | 12:18:05 |
| Result (verdict FAIL) | reports/stage_e18_c1b_result.json finished_local | 12:18:38 |
| Verdict verification (VerdictVerifier-FableXHigh) | reports/stage_e18_review.md lines 245-366; recompute on disk 12:23:48 | 12:19:13-12:29:08 |
| End checks | reports/stage_e18_briefs/end_checks.txt | 12:29:55 |
| End suite | reports/stage_e18_briefs/pytest_end.out | 12:30:09-{tail(B / 'pytest_end.out', 1)[11:19]} |
| Final commit "Stage E.18 C1b evaluated" | git log | {final} |
"""
    sec2 = f"""## 2. Guardrail evidence

Start and end checks, verbatim (reports/stage_e18_briefs/checks.sh: E.17's script with E.18's paths). Only the
earlier stages' untracked evidence-page lines are collapsed into one line with their count.

### Start checks (11:47)

```
{collapsed(B / 'start_checks.txt')}
```

Start suite, `uv run pytest -q -p no:cacheprovider` (run with PYTHONPYCACHEPREFIX set; see section 6 item 9):

```
{tail(B / 'pytest_start.out', 6)}
```

Rerun of the failing file without the prefix:

```
{tail(B / 'pytest_start_rerun_harness_freeze.out', 3)}
```

### End checks (12:29), with the C1b freeze verification and the run-once listing appended

```
{collapsed(B / 'end_checks.txt')}
```

End suite, `uv run pytest -q -p no:cacheprovider` (at nice 10, no prefix):

```
{tail(B / 'pytest_end.out', 4)}
```

Summary: holdout all_ok with 0 unlocks at start and end; REGISTRATION.md 0 bytes; the spend ledger unchanged
(36,402 lines, 034a454b..., at start and end); N 478 at start, 480 at end (one registration, r003-C1b); harness
v12 unchanged; every freeze verified (E.1/E.2a, K1-K8, v2, C1's E.14 freeze and its inputs except the replaced harness
manifest, E.16, C1b). No TopstepX call, no credential, no edit under live/ or ops/, no push. No worker or background
shell was running at the end (`pgrep` before the final commit).

### Order of events

{events}"""
    doc = "\n\n".join([
        "# Stage E.18 return: C1b (C1 re-registered with the C10 fix) evaluated once: FAIL; N = 480",
        "Prompt docs/prompts/STAGE_E.18.md (V24-V31). Lead Opus 5.5 xhigh, session a6f2d97b-f5fc-4d95-a054-c5010e1ff6d0, "
        "2026-10-10. All times PDT (America/Vancouver), from `date`, file mtimes, git and the registry. STATE: "
        "reports/stage_e18_STATE.md.",
        part("ret_summary.md"), sec2, part("ret_results.md"), part("ret_delegation.md"),
        part("ret_verification.md"), part("ret_open_choices.md"), part("ret_decisions.md"), part("ret_cost.md"),
    ]) + "\n"
    OUT.write_text(doc)
    print(f"written {OUT}: {len(doc.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
