"""Stage E.19: assemble reports/E.19_RETURN.md from its parts (sections in the prompt's fixed order).
Usage: python3 reports/stage_e19_briefs/assemble_return.py"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

B = Path("reports/stage_e19_briefs")
OUT = Path("reports/E.19_RETURN.md")


def collapsed(path: Path) -> str:
    return subprocess.run([sys.executable, "reports/stage_e17_briefs/collapse_checks.py", str(path)],
                          capture_output=True, text=True, check=True).stdout.rstrip()


def section(md: str, start: str, stop: str | None) -> str:
    a = md.index(start)
    b = md.index(stop, a + len(start)) if stop else len(md)
    return md[a:b].rstrip()


def main() -> int:
    part = lambda name: (B / name).read_text().rstrip()  # noqa: E731
    tables = part("results_tables.md")
    t3 = section(tables, "| size | path | DLL | pricing | f 0.05", "### Effective net Sharpe")
    t4 = section(tables, "| edge | size | path | pricing | best f", "## T5")
    t4 = "\n".join(l for l in t4.splitlines() if l.startswith("| edge") or l.startswith("|---") or "| 5 |" in l)
    rs = Path("reports/stage_e19_returns_summary.md").read_text()
    returns = section(rs, "| Path | Window CT", "| Vehicle |")
    results = (part("ret_results.md").replace("{RULE_TABLE}", part("rule_table.md"))
               .replace("{RETURNS_TABLE}", returns).replace("{KEY_NUMBERS}", part("key_numbers.md"))
               .replace("{BREAK_EVEN}", t3).replace("{CAMPAIGNS}", t4))
    state = Path("reports/stage_e19_STATE.md").read_text()
    choices = state[state.index("## Lead decisions so far"):].split("\n", 1)[1].strip()
    guard = f"""## 2. Guardrail evidence

No purchase and no Databento call (spend ledger 36,402 lines, sha256 034a454b..., the same at start and end); N = 480
at start and end (registry 4 lines, sha256 55b1d24c..., unchanged; nothing registered); holdouts all_ok with 0
unlocks at start and end; REGISTRATION.md 0 bytes; harness v12 preflight OK at start and end; no file under live/,
ops/, ml_route_v2/, rules/, sim/, screening/ or data/ code changed (git diff check in both blocks); no TopstepX or
ProjectX call, no credential, no key printed. End suite: {part("suite_line.txt")}

### Start checks (17:03), verbatim (untracked page lists collapsed)

```
{collapsed(B / "start_checks.txt")}
```

### End checks, verbatim (untracked page lists collapsed)

```
{collapsed(B / "end_checks.txt")}
```"""
    verification = f"""## 5. Verification

Two Fable xhigh reviewers, independent of the authors (L-8): RulesReviewer-FableXHigh checked the rule table
against its quotes and the terms (reports/stage_e19_review_rules.md); EconReviewer-FableXHigh rebuilt the returns,
wrote its own simulator, recomputed the headline blind (recompute.json written 17:57, before any result existed),
compared, reviewed the code, and in Phase C recomputed every remaining verdict cell (reports/stage_e19_review.md,
reports/stage_e19_verify/). Result: the headline reproduces (per path to 1e-11 on identical shocks; 60
configurations within 2.6 total SD; 48 campaign quantiles within one purchase or 1.3%; 11/11 hand paths to the cent).
Counts: rules review 1 BLOCKING, 4 SHOULD FIX, 14 NOTE; model review 0 BLOCKING, 3 SHOULD FIX, 11 NOTE. Rulings in
full: reports/stage_e19_rulings.md.

{part("verification_table.md")}"""
    doc = "\n\n".join([
        "# Stage E.19 return: prop economics, the Topstep Combine-to-XFA funnel in the user's wallet\n\n"
        "Prompt docs/prompts/STAGE_E.19.md (V22, V31, V32). Lead Opus 5.5 xhigh, session 087ee4a8. All times PDT "
        "(America/Vancouver), 2026-10-10. Results: reports/stage_e19_results.md and .json.",
        part("ret_summary.md"), guard, results, part("ret_delegation.md"), verification,
        "## 6. Open choices (every decision the lead made on its own, with the reason)\n\n" + choices,
        part("ret_decisions.md"), part("ret_cost.md")])
    OUT.write_text(doc + "\n")
    print(OUT, len(doc.split()), "words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
