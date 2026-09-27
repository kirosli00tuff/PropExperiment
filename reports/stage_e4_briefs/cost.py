"""Stage E.4 session cost: sum each assistant message's usage (input, output, cache read, cache creation)
by model, for the lead transcript and every subagent transcript, within a UTC time slice (one per part).
Same method as reports/stage_e2b_briefs/token_accounting.py, plus the time slice.

Usage: python3 reports/stage_e4_briefs/cost.py <from ISO UTC> <to ISO UTC> [session id ...]
Messages are de-duplicated by (message id, request id): a streamed message is logged once per content block.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

PROJ = Path.home() / ".claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment"
FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def scan(path: Path, lo: str, hi: str):
    seen, per_model, first, last = set(), defaultdict(lambda: [0, 0, 0, 0]), None, None
    for line in path.open(encoding="utf-8"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("timestamp") or ""
        if not (lo <= ts < hi):
            continue
        msg = e.get("message") or {}
        if e.get("type") != "assistant" or not isinstance(msg, dict) or "usage" not in msg:
            continue
        key = (msg.get("id"), e.get("requestId"))
        if key in seen:
            continue
        seen.add(key)
        u = msg["usage"]
        row = per_model[msg.get("model", "?")]
        for i, f in enumerate(FIELDS):
            row[i] += int(u.get(f) or 0)
        first = ts if first is None or ts < first else first
        last = ts if last is None or ts > last else last
    return per_model, first, last


def main() -> None:
    lo, hi = sys.argv[1], sys.argv[2]
    sessions = sys.argv[3:] or ["17ffffc1-5761-44c4-9f3b-5ee8c14fb08c"]
    total = defaultdict(lambda: [0, 0, 0, 0])
    for sid in sessions:
        files = [("lead", PROJ / f"{sid}.jsonl")] + [
            (p.stem, p) for p in sorted((PROJ / sid).glob("subagents/**/*.jsonl"))]
        for name, p in files:
            if not p.is_file():
                continue
            pm, first, last = scan(p, lo, hi)
            for m, r in pm.items():
                print(f"{sid[:8]} {name} {m} first={first} last={last} in={r[0]} out={r[1]} "
                      f"cread={r[2]} ccreate={r[3]} total={sum(r)}")
                for i in range(4):
                    total[m][i] += r[i]
    print("| Model | Input | Output | Cache read | Cache creation | Total |")
    print("|---|---|---|---|---|---|")
    allr = [0, 0, 0, 0]
    for m, r in sorted(total.items()):
        print(f"| {m} | {r[0]:,} | {r[1]:,} | {r[2]:,} | {r[3]:,} | {sum(r):,} |")
        allr = [a + b for a, b in zip(allr, r)]
    print(f"| all | {allr[0]:,} | {allr[1]:,} | {allr[2]:,} | {allr[3]:,} | {sum(allr):,} |")


if __name__ == "__main__":
    main()
