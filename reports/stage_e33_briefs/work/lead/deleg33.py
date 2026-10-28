"""E.33 delegation record: per worker transcript, the role, agent file, model(s) read from message.model, the PDT
span and the tokens (each assistant message counted once, at its final usage), plus the lead's own transcript.

Usage: uv run python reports/stage_e33_briefs/work/lead/deleg33.py [session id]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SESSION = sys.argv[1] if len(sys.argv) > 1 else "86e80bc3-d62a-42e1-b5fd-5c881ccf8b54"
ROOT = Path.home() / ".claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment"
PDT = ZoneInfo("America/Vancouver")
FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def scan(path: Path) -> dict:
    final: dict[str, tuple[str, dict]] = {}
    times: list[datetime] = []
    for line in path.read_text().splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = rec.get("timestamp")
        if ts:
            times.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
        msg = rec.get("message")
        if rec.get("type") != "assistant" or not isinstance(msg, dict) or "usage" not in msg:
            continue
        final[msg.get("id") or f"{path.name}:{len(final)}"] = (msg.get("model", "?"), msg["usage"])
    models = Counter(m for m, _ in final.values())
    by_model: dict[str, list[int]] = {}
    for model, usage in final.values():
        row = by_model.setdefault(model, [0, 0, 0, 0])
        for k, f in enumerate(FIELDS):
            row[k] += int(usage.get(f) or 0)
    return {"models": models, "by_model": by_model, "start": min(times) if times else None,
            "end": max(times) if times else None}


def fmt(t: datetime | None) -> str:
    return t.astimezone(PDT).strftime("%m-%d %H:%M") if t else "?"


def main() -> int:
    sub = ROOT / SESSION / "subagents"
    rows, totals = [], {}
    for jl in sorted(sub.glob("agent-*.jsonl"), key=lambda p: p.stat().st_mtime):
        meta_path = jl.with_suffix("").with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        s = scan(jl)
        tok = sum(sum(v) for v in s["by_model"].values())
        for model, v in s["by_model"].items():
            acc = totals.setdefault(model, [0, 0, 0, 0])
            for k in range(4):
                acc[k] += v[k]
        rows.append((s["start"], meta.get("description", jl.stem), meta.get("agentType", "?"),
                     ", ".join(f"{m} ({n} msgs)" for m, n in s["models"].most_common()),
                     fmt(s["start"]), fmt(s["end"]), tok))
    lead = scan(ROOT / f"{SESSION}.jsonl")
    lead_tok = sum(sum(v) for v in lead["by_model"].values())
    for model, v in lead["by_model"].items():
        acc = totals.setdefault(model, [0, 0, 0, 0])
        for k in range(4):
            acc[k] += v[k]
    print("| Agent | Agent file | Model (transcript) | First record PDT | Last record PDT | Tokens |")
    print("|---|---|---|---|---|---|")
    for _, desc, atype, models, a, b, tok in sorted(rows, key=lambda r: r[0] or datetime.max.replace(tzinfo=PDT)):
        print(f"| {desc} | {atype} | {models} | {a} | {b} | {tok:,} |")
    print(f"| lead (session {SESSION[:8]}) | - | "
          f"{', '.join(f'{m} ({n} msgs)' for m, n in lead['models'].most_common())} | {fmt(lead['start'])} | "
          f"{fmt(lead['end'])} | {lead_tok:,} |")
    print("\n| Model | Input | Output | Cache read | Cache creation | Total |")
    print("|---|---|---|---|---|---|")
    grand = [0, 0, 0, 0]
    for model, v in sorted(totals.items()):
        print(f"| {model} | {v[0]:,} | {v[1]:,} | {v[2]:,} | {v[3]:,} | {sum(v):,} |")
        grand = [g + x for g, x in zip(grand, v)]
    print(f"| all | {grand[0]:,} | {grand[1]:,} | {grand[2]:,} | {grand[3]:,} | {sum(grand):,} |")
    workers = sum(r[6] for r in rows)
    print(f"\nlead {lead_tok:,} ({lead_tok / max(1, sum(grand)):.1%}); workers {workers:,} "
          f"({workers / max(1, sum(grand)):.1%}); all {sum(grand):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
