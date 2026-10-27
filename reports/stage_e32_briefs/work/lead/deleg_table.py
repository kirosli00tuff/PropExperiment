"""Stage E.32: turn deleg32.py's TSV (stdin) into the return's delegation table, times in America/Vancouver.

Usage: python3 deleg32.py <from> <to> <sids...> | python3 deleg_table.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Vancouver")
EFFORT = {"worker-medium": "medium", "worker-high": "high", "worker-xhigh": "xhigh", "worker-max": "max"}


def pt(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(PT)


def main() -> None:
    rows = [line.rstrip("\n").split("\t") for line in sys.stdin if line.strip()]
    rows.sort(key=lambda r: r[6])
    print("| # | Agent | Session / run | Agent file | Model (transcript) | Effort | Start PDT | End PDT | Minutes | Tokens |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    total = 0
    for i, (sid, run, name, atype, model, _n, first, last, tok) in enumerate(rows, 1):
        a, b = pt(first), pt(last)
        mins = (b - a).total_seconds() / 60
        total += int(tok)
        print(f"| {i} | {name} | {sid} {run} | {atype} | {model} | {EFFORT.get(atype, '?')} | "
              f"{a:%m-%d %H:%M} | {b:%m-%d %H:%M} | {mins:.0f} | {int(tok):,} |")
    print(f"| | all workers | | | | | | | | {total:,} |")


if __name__ == "__main__":
    main()
