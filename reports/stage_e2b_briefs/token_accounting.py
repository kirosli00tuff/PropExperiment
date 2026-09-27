"""Stage E.2b session cost: tokens per model and per agent from this session's transcripts.

Sums each assistant message's usage (input, output, cache read, cache creation) once per
message id (streamed messages repeat their usage), by model, for the lead's transcript and each
subagent transcript under ~/.claude/projects/<project>/<session>/subagents/. Times in PDT.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PDT = ZoneInfo("America/Vancouver")
PROJECT = Path.home() / ".claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment"
SESSION = sys.argv[1] if len(sys.argv) > 1 else "0d3e5a56-56e0-4685-ae6b-02b6cf7efbe7"
FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def scan(path: Path) -> dict:
    by_id: dict[str, tuple[str, dict]] = {}
    stamps: list[str] = []
    for line in path.open(encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "timestamp" in d:
            stamps.append(d["timestamp"])
        msg = d.get("message") or {}
        if d.get("type") == "assistant" and isinstance(msg, dict) and msg.get("usage"):
            by_id[msg.get("id") or f"{path}:{len(by_id)}"] = (msg.get("model", "?"), msg["usage"])
    per_model: dict[str, dict[str, int]] = defaultdict(lambda: dict.fromkeys(FIELDS, 0))
    for model, usage in by_id.values():
        for f in FIELDS:
            per_model[model][f] += int(usage.get(f) or 0)
    def pdt(s: str) -> str:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(PDT).strftime("%H:%M")
    return {"per_model": dict(per_model), "first": pdt(min(stamps)) if stamps else "",
            "last": pdt(max(stamps)) if stamps else "", "messages": len(by_id)}


def total(pm: dict) -> int:
    return sum(sum(v.values()) for v in pm.values())


lead = scan(PROJECT / f"{SESSION}.jsonl")
agents = {}
for p in sorted((PROJECT / SESSION / "subagents").glob("agent-*.jsonl")):
    meta = p.with_suffix(".meta.json")
    desc = json.loads(meta.read_text()).get("description", "") if meta.is_file() else ""
    agents[p.stem.removeprefix("agent-")] = {**scan(p), "description": desc}

grand: dict[str, dict[str, int]] = defaultdict(lambda: dict.fromkeys(FIELDS, 0))
for pm in [lead["per_model"]] + [a["per_model"] for a in agents.values()]:
    for m, u in pm.items():
        for f in FIELDS:
            grand[m][f] += u[f]
print("| Model | Input | Output | Cache read | Cache creation | Total |")
print("|---|---|---|---|---|---|")
for m, u in sorted(grand.items()):
    print(f"| {m} | {u['input_tokens']:,} | {u['output_tokens']:,} | {u['cache_read_input_tokens']:,} | "
          f"{u['cache_creation_input_tokens']:,} | {sum(u.values()):,} |")
all_total = sum(sum(u.values()) for u in grand.values())
print(f"| all | | | | | {all_total:,} |")
print()
print(f"lead ({lead['first']}-{lead['last']}): {total(lead['per_model']):,} "
      f"({100 * total(lead['per_model']) / all_total:.1f}%) {sorted(lead['per_model'])}")
print("| Agent id | Description | First | Last | Model | Tokens |")
print("|---|---|---|---|---|---|")
for aid, a in agents.items():
    print(f"| {aid[:9]} | {a['description']} | {a['first']} | {a['last']} | "
          f"{','.join(sorted(a['per_model']))} | {total(a['per_model']):,} |")
workers = all_total - total(lead["per_model"])
print(f"\nworkers: {workers:,} ({100 * workers / all_total:.1f}%)")
