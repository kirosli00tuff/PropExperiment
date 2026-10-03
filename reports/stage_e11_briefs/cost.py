"""Stage E.11 session cost (copied from E.10): per-model token sums for the lead transcript and every subagent transcript,
within a UTC time slice.

Same inputs as reports/stage_e4_briefs/cost.py, with one fix: a streamed assistant message is logged once per
content block, and its usage grows from block to block (output_tokens especially). E.4's script kept the FIRST
record per (message id, request id), which undercounts output (E.10 check: CatalogWriter first 8,285 vs final
256,608 output tokens). This script keeps the per-field MAXIMUM over a message's records, i.e. its final usage.

Usage: python3 reports/stage_e10_briefs/cost.py <from ISO UTC> <to ISO UTC> <session id>
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

PROJ = Path.home() / ".claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment"
FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def scan(path: Path, lo: str, hi: str):
    per_msg, model_of, first, last = {}, {}, None, None
    for line in path.open(encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("timestamp") or ""
        msg = e.get("message") or {}
        if not (lo <= ts < hi) or e.get("type") != "assistant" or not isinstance(msg, dict) or "usage" not in msg:
            continue
        key = (msg.get("id"), e.get("requestId"))
        u = msg["usage"]
        cur = per_msg.setdefault(key, [0, 0, 0, 0])
        for i, f in enumerate(FIELDS):
            cur[i] = max(cur[i], int(u.get(f) or 0))
        model_of[key] = msg.get("model", "unknown")
        first = first or ts
        last = ts
    per_model = defaultdict(lambda: [0, 0, 0, 0])
    for key, vals in per_msg.items():
        for i, v in enumerate(vals):
            per_model[model_of[key]][i] += v
    return per_model, first, last, len(per_msg)


def main() -> None:
    lo, hi, sid = sys.argv[1], sys.argv[2], sys.argv[3]
    files = [("lead", PROJ / f"{sid}.jsonl")] + [
        (p.stem, p) for p in sorted((PROJ / sid / "subagents").glob("*.jsonl"))]
    total = defaultdict(lambda: [0, 0, 0, 0])
    for name, path in files:
        if not path.exists():
            continue
        pm, first, last, n = scan(path, lo, hi)
        for model, v in pm.items():
            print(f"{name} {model} msgs={n} first={first} last={last} in={v[0]} out={v[1]} cread={v[2]} "
                  f"ccreate={v[3]} total={sum(v)}")
            for i in range(4):
                total[model][i] += v[i]
    print("| Model | Input | Output | Cache read | Cache creation | Total |")
    print("|---|---|---|---|---|---|")
    allv = [0, 0, 0, 0]
    for model, v in sorted(total.items()):
        print(f"| {model} | {v[0]:,} | {v[1]:,} | {v[2]:,} | {v[3]:,} | {sum(v):,} |")
        allv = [a + b for a, b in zip(allv, v)]
    print(f"| all | {allv[0]:,} | {allv[1]:,} | {allv[2]:,} | {allv[3]:,} | {sum(allv):,} |")


if __name__ == "__main__":
    main()
