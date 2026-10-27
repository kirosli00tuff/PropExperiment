"""Stage E.32 session cost: reports/stage_e10_briefs/cost.py's scan (final usage per message), over the lead
transcript and EVERY subagent transcript under <session>/subagents/ recursively (workflow agents live in
subagents/workflows/<run>/; cost.py globs only the top level). Prints one line per transcript (with the first user
prompt's first words as a label), the per-model table, and lead versus workers.

Usage: python3 reports/stage_e32_briefs/work/lead/cost32.py <from ISO UTC> <to ISO UTC> <session id> [...more ids]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "stage_e10_briefs"))
from cost import PROJ, scan  # noqa: E402


def label(path: Path) -> str:
    for line in path.open(encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "user":
            c = e.get("message", {}).get("content")
            s = c if isinstance(c, str) else json.dumps(c)
            i = s.find("You are ")
            return (s[i + 8:i + 40] if i >= 0 else s[:32]).replace("\n", " ")
    return "?"


def main() -> None:
    lo, hi, sids = sys.argv[1], sys.argv[2], sys.argv[3:]
    total, lead, workers = defaultdict(lambda: [0] * 4), defaultdict(lambda: [0] * 4), defaultdict(lambda: [0] * 4)
    for sid in sids:
        files = [("lead", PROJ / f"{sid}.jsonl")] + [
            (p.relative_to(PROJ / sid / "subagents").as_posix(), p)
            for p in sorted((PROJ / sid / "subagents").rglob("agent-*.jsonl"))]
        for name, path in files:
            if not path.exists():
                continue
            pm, first, last, n = scan(path, lo, hi)
            tag = "lead" if name == "lead" else label(path)
            for model, v in pm.items():
                print(f"{sid[:8]} {name} [{tag}] {model} msgs={n} first={first} last={last} in={v[0]} out={v[1]} "
                      f"cread={v[2]} ccreate={v[3]} total={sum(v)}")
                for i in range(4):
                    total[model][i] += v[i]
                    (lead if name == "lead" else workers)[model][i] += v[i]
    for title, table in (("all", total), ("lead", lead), ("workers", workers)):
        print(f"\n## {title}\n| Model | Input | Output | Cache read | Cache creation | Total |\n|---|---|---|---|---|---|")
        allv = [0] * 4
        for model, v in sorted(table.items()):
            print(f"| {model} | {v[0]:,} | {v[1]:,} | {v[2]:,} | {v[3]:,} | {sum(v):,} |")
            allv = [a + b for a, b in zip(allv, v)]
        print(f"| all | {allv[0]:,} | {allv[1]:,} | {allv[2]:,} | {allv[3]:,} | {sum(allv):,} |")


if __name__ == "__main__":
    main()
