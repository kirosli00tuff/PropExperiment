"""Stage E.25: write ret_cost.md (return section 8 and the progress entry's Session cost) from cost_raw.txt and
ret_cost_tokens.md (make_cost.py output) plus the lead's task rows (times from `date`, the STATE log and the
transcripts). Usage: python3 -I reports/stage_e25_briefs/gen_cost_section.py <end HH:MM PDT>
"""
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
from assemble_return import status  # noqa: E402

END = sys.argv[1]


def pdt(ts):
    return (datetime.fromisoformat(ts.replace("Z", "+00:00")) - timedelta(hours=7)).strftime("%H:%M")


def minutes(a, b):
    ha, ma = map(int, a.split(":"))
    hb, mb = map(int, b.split(":"))
    return (hb * 60 + mb) - (ha * 60 + ma)


# Lead task rows: (task, owner, model, effort, start, end, status/deviation, initial estimate)
TASKS = [
    ("0 Startup checks", "lead", "opus", "xhigh", "01:27", "01:28", "done", "done 01:28"),
    ("R0 shared brief", "lead", "opus", "xhigh", "01:29", "01:36", "done", "25 min, to 02:05"),
    ("Wave 1 launch, addenda 1-6 handling, slot launches", "lead", "opus", "xhigh", "01:37", "02:01",
     "cut by the usage limit at 02:01", "R1-R13 60 min, to 03:10"),
    ("PAUSE (usage limit)", "-", "-", "-", "02:01", "06:10", "not work time", "-"),
    ("Resume, synthesis v1, power script, wave 2 launch", "lead", "opus", "xhigh", "06:10", "06:35",
     "cut by the usage limit at about 06:35", "T1 triage 20 min, R14-R20 60 min"),
    ("PAUSE (usage limit; laptop reboot about 10:50)", "-", "-", "-", "06:35", "11:15", "not work time", "-"),
    ("Resume, wave 3 launch, synthesis v2, merges", "lead", "opus", "xhigh", "11:15", "11:30", "done",
     "S1-S3 60 min, to 05:30"),
    ("S4 running: return parts drafted; review fixes, re-check", "lead", "opus", "xhigh", "11:30", "11:52", "done",
     "F 20 min, to 06:35"),
    ("Cost, progress, STAGES, end checks, assembly, commit", "lead", "opus", "xhigh", "11:52", END, "done",
     "Ret 35 min, to 07:10"),
]


def main():
    spawns = []
    for line in (B / "cost_raw.txt").read_text().splitlines():
        m = re.match(r"(\S+) (.+?) (claude-\S+) effort=(\S+) msgs=\d+ first=(\S+) last=(\S+) .* total=(\d+)$", line)
        if m and m.group(1) != "lead":
            stem, name, model, eff, first, last, tot = m.groups()
            spawns.append((first, name, model.replace("claude-", ""), eff, pdt(first), pdt(last), int(tot),
                           status(name, first, last)))
    spawns.sort()
    lead_tot = next(int(re.search(r"total=(\d+)", l).group(1))
                    for l in (B / "cost_raw.txt").read_text().splitlines() if l.startswith("lead "))
    out = ["## 8. Session cost", "",
           "Computed at the end from the transcripts (reports/stage_e25_briefs/make_cost.py: the lead's .jsonl and every",
           "subagent transcript under subagents/**, workflow agents included; each message's final usage). Times PDT.",
           "Pauses are their own rows and excluded from work time. These are token counts, not plan-credit percentages.",
           "", "### Final ETA table (actuals; the initial estimate in the last column)", "",
           "| # | Task or spawn | Owner / agent | Model | Effort | Start | End | Minutes | Tokens | Status, deviations | Initial estimate |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    i = 0
    for t, owner, model, eff, s, e, st, est in TASKS:
        i += 1
        out.append(f"| {i} | {t} | {owner} | {model} | {eff} | {s} | {e} | {minutes(s, e)} | "
                   f"{'-' if owner == '-' else 'in the lead total'} | {st} | {est} |")
    for _, name, model, eff, s, e, tot, st in spawns:
        i += 1
        out.append(f"| {i} | spawn | {name} | {model} | {eff} | {s} | {e} | {minutes(s, e)} | {tot:,} | {st} | - |")
    total_min = minutes("01:27", END)
    pause_min = minutes("02:01", "06:10") + minutes("06:35", "11:15")
    work_min = total_min - pause_min
    worker_tot = sum(s[6] for s in spawns)
    out += ["", f"| Cumulative | whole stage | lead + {len(spawns)} spawns | | | 01:27 | {END} | wall {total_min} "
            f"(pauses {pause_min}; work {work_min}) | {lead_tot + worker_tot:,} (lead {lead_tot:,}; workers "
            f"{worker_tot:,}) | | initial estimate: 01:28-07:10 (342 min of work) |", ""]
    tok = (B / "ret_cost_tokens.md").read_text().split("\n\n")
    out += ["### Tokens per model", "", tok[0], "", tok[1], "",
            "One line per worker spawn (agent file by effort: worker-medium, worker-high, worker-xhigh): the spawn rows of the",
            "table above and section 4. The lead's last messages after the count (assembly and commit) are not included.", ""]
    (B / "ret_cost.md").write_text("\n".join(out) + "\n")
    print(f"rows {i}; wall {total_min} pauses {pause_min} work {work_min}; tokens {lead_tot + worker_tot:,}")


if __name__ == "__main__":
    main()
