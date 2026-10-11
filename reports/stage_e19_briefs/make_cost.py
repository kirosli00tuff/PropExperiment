"""Stage E.19 lead: delegation record (return section 4) and session cost (section 8 and progress.md) from
reports/stage_e10_briefs/cost.py run on this session. Usage: python3 reports/stage_e19_briefs/make_cost.py <to ISO UTC>
Writes ret_delegation.md, ret_cost.md and cost_raw.txt in reports/stage_e19_briefs/."""
import re
import subprocess
import sys
from pathlib import Path

B = Path("reports/stage_e19_briefs")
SID = "087ee4a8-1bec-45a0-a9cd-046722cb28a9"
raw = subprocess.run([sys.executable, "reports/stage_e10_briefs/cost.py", "2026-10-10T23:50:00Z", sys.argv[1], SID],
                     capture_output=True, text=True, check=True).stdout
(B / "cost_raw.txt").write_text(raw)
tok = {}
for line in raw.splitlines():
    m = re.match(r"(lead|agent-\w+) (\S+) msgs=\d+ .* total=(\d+)", line)
    if m:
        tok[m.group(1)] = (m.group(2), int(m.group(3)))
table = raw[raw.index("| Model |"):].strip()
SPAWNS = [  # agent id, name, agent file, model, effort, start, end, status and deviations
    ("a2b134658eeacc664", "TopstepRules-OpusHigh", "worker-high", "opus", "high", "17:09", "17:24", "done; 214 rules, 42 practices; terms reading L-11"),
    ("aac9637cb97f1f4c7", "FunnelCoder-OpusXHigh", "worker-xhigh", "opus", "xhigh", "17:09", "17:41", "done; 117 tests; one lead message 17:24 (final-rules facts)"),
    ("a21c81015c1e47405", "ReturnsCoder-OpusHigh", "worker-high", "opus", "high", "17:09", "17:15", "done; 15 tests; 4 spec questions (L-10)"),
    ("a26dc9f9451939d12", "GridCoder-OpusHigh", "worker-high", "opus", "high", "17:43", "19:26", "done; run restarted 18:02 to add churn metrics (RR-1); 780 jobs, 0 failures"),
    ("a26e02eeeaadca02a", "RulesReviewer-FableXHigh", "worker-xhigh", "fable", "xhigh", "17:43", "18:00", "done; 1 BLOCKING (RR-1), 4 SHOULD FIX, 14 NOTE; started early (rules final)"),
    ("a84ae281fe19f09bb", "EconReviewer-FableXHigh", "worker-xhigh", "fable", "xhigh", "17:43", "19:56", "done; Phase A 17:43-17:59 blind, B 19:27-19:46, C 19:46-19:56 (two resumes by message); 0 / 3 / 11"),
]
rows = ["| Agent (description) | Agent file | Model | Effort | Start | End | Tokens (transcript) | Status, deviations |",
        "|---|---|---|---|---|---|---|---|"]
wsum = 0
for aid, name, fil, model, eff, st, en, note in SPAWNS:
    m, t = tok.get(f"agent-{aid}", ("?", 0))
    wsum += t
    rows.append(f"| {name} | {fil} | {model} ({m}) | {eff} | {st} | {en} | {t:,} | {note} |")
lead = tok["lead"][1]
(B / "ret_delegation.md").write_text(
    "## 4. Delegation record\n\nOne row per spawn (six spawns; at most three ran at once). Tokens: input + output + cache read + cache "
    "creation from each transcript (reports/stage_e10_briefs/cost.py, per-field final usage per message).\n\n" + "\n".join(rows) + "\n")
total = lead + wsum
eta = (B / "eta_final.md").read_text().rstrip()
cost = f"""## 8. Session cost

Wall clock 16:54 to the final commit (see the ETA table's last rows), 2026-10-10, one session: no pause, no usage-limit
wait, no outage. Tokens are summed from this session's transcript and its six subagent transcripts up to
{sys.argv[1]} (reports/stage_e10_briefs/cost.py; raw output reports/stage_e19_briefs/cost_raw.txt); the lead's
last steps after that (the final assembly and the commit) are not in the count. Never estimated.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

{eta}

### Tokens per model

{table}

Delegation share: lead {lead:,} ({100 * lead / total:.1f}%), workers {wsum:,} ({100 * wsum / total:.1f}%). Per worker: section 4.
"""
(B / "ret_cost.md").write_text(cost)
print("lead", lead, "workers", wsum, "total", total)
