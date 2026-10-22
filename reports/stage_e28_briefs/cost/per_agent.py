"""E.28 per-spawn token lines: joins cost.py (E.26 rglob copy) per-agent sums with each agent's .meta.json
(description = role name, agentType = effort file, model) and its workflow run. Usage: per_agent.py <cost.txt> <session id>"""
import json, re, sys
from pathlib import Path
PROJ = Path.home() / ".claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment"
from datetime import datetime
from zoneinfo import ZoneInfo
cost, sid = sys.argv[1], sys.argv[2]
ts = lambda t: datetime.fromisoformat(t.replace("Z", "+00:00"))
pdt = lambda t: ts(t).astimezone(ZoneInfo("America/Vancouver")).strftime("%H:%M")
mins = lambda a, b: round((ts(b) - ts(a)).total_seconds() / 60)
meta = {p.stem.replace(".meta", ""): (p, json.loads(p.read_text())) for p in (PROJ / sid / "subagents").rglob("agent-*.meta.json")}
rows = []
for line in open(cost):
    m = re.match(r"(agent-\S+) (claude-\S+) msgs=\d+ first=(\S+) last=(\S+) .* total=(\d+)", line)
    if not m:
        continue
    a, model, first, last, tot = m.groups()
    p, md = meta.get(a, (None, {}))
    run = p.parent.name if p and p.parent.name.startswith("wf_") else "Agent tool"
    rows.append((first, md.get("description", "?"), md.get("agentType", "?"), model, run, pdt(first), pdt(last), mins(first, last), int(tot)))
print("| Agent | Effort file | Model | Run | First (PDT) | Last (PDT) | Min | Tokens |\n|---|---|---|---|---|---|---|---|")
for r in sorted(rows):
    print(f"| {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]:,} |")
print(f"\n{len(rows)} spawns, {sum(r[8] for r in rows):,} tokens. Min is first to last message, so it includes any usage-limit pause the agent spanned.")
