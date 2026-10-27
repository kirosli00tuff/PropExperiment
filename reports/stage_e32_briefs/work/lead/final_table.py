"""Stage E.32 final ETA table: lead task rows and pauses (times from reports/stage_e32_STATE.md) merged with the
worker rows of deleg32.py's TSV (times and tokens from the transcripts). Prints markdown.

Usage: python3 final_table.py <deleg_all.tsv> <lead tokens a51871c6> <lead tokens 900dd54a> <lead tokens 89bc0cd0>
       <total tokens> <work minutes> <pause minutes> <end HH:MM>
"""
from __future__ import annotations

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Vancouver")
EFFORT = {"worker-medium": "medium", "worker-high": "high", "worker-xhigh": "xhigh"}

# (start, end, task, model/effort, status); 10-26 times carry the date
LEAD = [
    ("10-26 22:21", "10-26 22:42", "Lead: read inputs, plan, estimate table, start checks", "opus (xhigh)", "done"),
    ("10-26 22:42", "10-26 23:01", "Lead: Part 0 seal (tool, 26 tests, 114 files), store-test subsets", "opus (xhigh)", "done"),
    ("10-26 23:05", "10-26 23:15", "Lead: seal doc, P1 hash check 156/156, p7_thresholds.py, design notes", "opus (xhigh)", "done"),
    ("10-26 23:16", "10-27 00:14", "PAUSE 1 (planner request)", "-", "not work"),
    ("10-27 00:15", "10-27 00:51", "Lead: resume, M6/P6 execution variants, X1 corrections to the seal doc, cftc terms, reviewer briefs", "opus (xhigh)", "done"),
    ("10-27 00:51", "10-27 02:32", "USAGE LIMIT 1", "-", "not work"),
    ("10-27 02:32", "10-27 03:12", "Lead: resume (continuation script), test-bar ruling, p7_final.py, protocol v0.1, brief front", "opus (xhigh)", "done"),
    ("10-27 03:12", "10-27 07:31", "USAGE LIMIT 2", "-", "not work"),
    ("10-27 07:31", "10-27 08:02", "Lead: protocol v0.2, relaunches, Part V draft, v0.3 (45 items)", "opus (xhigh)", "done"),
    ("10-27 08:02", "10-27 08:39", "PLANNED CONTEXT WIPE", "-", "not work"),
    ("10-27 08:39", "10-27 08:42", "Lead: resume checks, re-check plan, estimate table", "opus (xhigh)", "done"),
    ("10-27 08:42", "10-27 09:01", "Full pytest (background shell, nice 10)", "-", "8,116 passed, 1 known failure"),
    ("10-27 08:42", "10-27 08:57", "Lead: model checks, deleg32.py, drafts", "opus (xhigh)", "done"),
    ("10-27 08:57", "10-27 12:35", "USAGE LIMIT 3", "-", "not work"),
    ("10-27 12:35", "10-27 12:38", "Lead: pytest failure investigation (clean worktree at HEAD)", "opus (xhigh)", "predates E.32"),
    ("10-27 12:38", "10-27 12:42", "Lead: re-check rulings, protocol v0.4", "opus (xhigh)", "done"),
    ("10-27 12:42", "10-27 12:58", "Lead: return drafts; spot-check rulings, v0.5", "opus (xhigh)", "done"),
    ("10-27 13:06", "10-27 13:08", "Lead: final-check rulings, v0.6, FREEZE v1.0", "opus (xhigh)", "done"),
    ("10-27 13:08", "END", "Lead: brief assembly, end checks, return, progress, STAGES, cost, commit", "opus (xhigh)", "done"),
]


def parse(s: str) -> datetime:
    return datetime.strptime("2026-" + s, "%Y-%m-%d %H:%M").replace(tzinfo=PT)


def main() -> None:
    tsv, la, lb, lc, total, work, pause, end = sys.argv[1:9]
    rows = []
    for st, en, task, model, status in LEAD:
        en2 = "10-27 " + end if en == "END" else en
        a, b = parse(st), parse(en2)
        mins = int((b - a).total_seconds() // 60)
        rows.append((a, f"{task} | {model} | {st}-{en2[6:] if en2[:5] == st[:5] else en2} | {mins} min | "
                        f"{'-' if model == '-' else '(lead)'} | {status}"))
    for line in open(tsv, encoding="utf-8"):
        sid, run, name, atype, model, _n, first, last, tok = line.rstrip("\n").split("\t")
        a = datetime.fromisoformat(first.replace("Z", "+00:00")).astimezone(PT)
        b = datetime.fromisoformat(last.replace("Z", "+00:00")).astimezone(PT)
        mins = (b - a).total_seconds() / 60
        where = run if run != "agent" else "Agent"
        rows.append((a, f"{name} ({atype}, {where}) | {model.replace('claude-', '')} ({EFFORT.get(atype, '?')}) | "
                        f"{a:%m-%d %H:%M}-{b:%H:%M} | {mins:.0f} min | {int(tok):,} | done"))
    rows.sort(key=lambda r: r[0])
    print("| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |")
    print("|---|---|---|---|---|---|---|")
    for i, (_, r) in enumerate(rows, 1):
        print(f"| {i} | {r} |")
    print(f"| - | Lead session a51871c6, whole | opus 5.5 (xhigh) | 10-26 22:21-10-27 00:51 | - | {int(la):,} | - |")
    print(f"| - | Lead session 900dd54a, whole | opus 5.5 (xhigh) | 02:32-08:02 | - | {int(lb):,} | - |")
    print(f"| - | Lead session 89bc0cd0, whole | opus 5.5 (xhigh) | 08:39-{end} | - | {int(lc):,} | - |")
    print(f"| total | Stage E.32 | - | 10-26 22:21-10-27 {end} | work {work} (pauses {pause}) | {int(total):,} | "
          f"initial estimate (10-26 23:01): done by about 11:20 PDT 10-27; this session's estimate (08:41): 10:40 |")


if __name__ == "__main__":
    main()
