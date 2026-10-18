"""Stage E.25 lead: session cost from transcripts (CLAUDE.md "Session cost"): the lead's .jsonl plus every subagent
transcript under subagents/**, including workflow agents (reports/stage_e10_briefs/cost.py's scan, which keeps each
message's final usage). Adapted from reports/stage_e22_briefs/make_cost.py: this session's id, E.25's start, effort
from the role-name suffix for workflow agents, times printed in PDT (UTC-7).
Usage: python3 reports/stage_e25_briefs/make_cost.py <to ISO UTC>. Writes cost_raw.txt and ret_cost_tokens.md here."""
import importlib.util, json, sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

spec = importlib.util.spec_from_file_location("cost10", "reports/stage_e10_briefs/cost.py")
c10 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c10)
SID = "37fc9660-82d1-49fd-be83-50b822ab0a5b"
LO, HI = "2026-10-18T08:25:00Z", sys.argv[1]
OUT = Path("reports/stage_e25_briefs")
root = c10.PROJ / SID / "subagents"
EFF = {"worker-medium": "medium", "worker-high": "high", "worker-xhigh": "xhigh", "worker-max": "max"}
SUFFIX = (("XHigh", "xhigh"), ("Max", "max"), ("High", "high"), ("Med", "medium"))


def effort_from_label(label):
    for suf, eff in SUFFIX:
        if label.endswith(suf):
            return eff
    return "?"


def pdt(ts):
    if not ts:
        return ""
    t = datetime.fromisoformat(ts.replace("Z", "+00:00")) - timedelta(hours=7)
    return t.strftime("%H:%M")


labels = {}
for j in root.glob("workflows/*/journal.jsonl"):
    for line in j.open():
        e = json.loads(line)
        if e.get("type") == "started":
            labels[e["agentId"]] = e.get("label", "")
rows, total, lead_tot, worker_tot = [], defaultdict(lambda: [0, 0, 0, 0]), 0, 0
files = [("lead", c10.PROJ / f"{SID}.jsonl", "lead (Opus 5.5)", "xhigh")]
for p in sorted(root.glob("*.jsonl")) + sorted(root.glob("workflows/*/agent-*.jsonl")):
    meta = p.with_suffix(".meta.json")
    m = json.loads(meta.read_text()) if meta.exists() else {}
    aid = p.stem.replace("agent-", "")
    name = m.get("description") or labels.get(aid) or aid
    eff = EFF.get(m.get("agentType")) or effort_from_label(name)
    files.append((p.stem, p, name, eff))
raw = []
for stem, path, name, eff in files:
    pm, first, last, n = c10.scan(path, LO, HI)
    for model, v in pm.items():
        if sum(v) == 0:
            continue
        raw.append(f"{stem} {name} {model} effort={eff} msgs={n} first={first} last={last} in={v[0]} out={v[1]} "
                   f"cread={v[2]} ccreate={v[3]} total={sum(v)}")
        for i in range(4):
            total[model][i] += v[i]
        rows.append((name, model, eff, first, last, sum(v)))
        if stem == "lead":
            lead_tot += sum(v)
        else:
            worker_tot += sum(v)
(OUT / "cost_raw.txt").write_text("\n".join(raw) + "\n")
out = ["| Model | Input | Output | Cache read | Cache creation | Total |", "|---|---|---|---|---|---|"]
allv = [0, 0, 0, 0]
for model, v in sorted(total.items()):
    out.append(f"| {model} | {v[0]:,} | {v[1]:,} | {v[2]:,} | {v[3]:,} | {sum(v):,} |")
    allv = [a + b for a, b in zip(allv, v)]
out.append(f"| all | {allv[0]:,} | {allv[1]:,} | {allv[2]:,} | {allv[3]:,} | {sum(allv):,} |")
g = sum(allv)
out += ["", f"Delegation share: lead {lead_tot:,} ({lead_tot / g:.1%}), workers {worker_tot:,} ({worker_tot / g:.1%}). "
        "By model: " + ", ".join(f"{m} {sum(v) / g:.1%}" for m, v in sorted(total.items())), "",
        "| Spawn (name) | Model | Effort | First (PDT) | Last (PDT) | Tokens |", "|---|---|---|---|---|---|"]
for name, model, eff, first, last, t in sorted(rows, key=lambda r: r[3] or ""):
    out.append(f"| {name} | {model} | {eff} | {pdt(first)} | {pdt(last)} | {t:,} |")
(OUT / "ret_cost_tokens.md").write_text("\n".join(out) + "\n")
print("\n".join(out[:8]))
print(f"spawn rows: {len(rows)}")
