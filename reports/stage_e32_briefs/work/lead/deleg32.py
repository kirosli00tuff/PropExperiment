"""Stage E.32 delegation record: one line per agent transcript with its name (the .meta.json description),
agent file, models seen in message.model, first and last message times (UTC) and tokens per model, using
reports/stage_e10_briefs/cost.py's scan over <session>/subagents/** recursively. Reads transcripts only.

Usage: python3 reports/stage_e32_briefs/work/lead/deleg32.py <from ISO UTC> <to ISO UTC> <session id> [...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "stage_e10_briefs"))
from cost import PROJ, scan  # noqa: E402


def meta(path: Path) -> tuple[str, str]:
    m = path.with_name(path.name.replace(".jsonl", ".meta.json"))
    if not m.exists():
        return "?", "?"
    d = json.loads(m.read_text(encoding="utf-8"))
    return d.get("description", "?"), d.get("agentType", "?")


def main() -> None:
    lo, hi, sids = sys.argv[1], sys.argv[2], sys.argv[3:]
    for sid in sids:
        for path in sorted((PROJ / sid / "subagents").rglob("agent-*.jsonl")):
            pm, first, last, n = scan(path, lo, hi)
            if not pm:
                continue
            name, atype = meta(path)
            run = path.parent.name if path.parent.name.startswith("wf_") else "agent"
            for model, v in pm.items():
                print(f"{sid[:8]}\t{run}\t{name}\t{atype}\t{model}\t{n}\t{first}\t{last}\t{sum(v)}")


if __name__ == "__main__":
    main()
