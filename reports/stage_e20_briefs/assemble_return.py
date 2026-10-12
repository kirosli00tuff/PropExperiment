"""E.20 lead: assemble reports/E.20_RETURN.md from the section files in reports/stage_e20_briefs/ and the start/end checks.
Mechanical; every judgment is in the section files. Usage: python3 reports/stage_e20_briefs/assemble_return.py <end HH:MM>"""
import re, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

B = Path("reports/stage_e20_briefs"); END = sys.argv[1]; PT = ZoneInfo("America/Vancouver")
def rd(n): return (B / n).read_text().rstrip() + "\n"
def checks(n):
    lines = (B / n).read_text().splitlines(); keep = [l for l in lines if not l.startswith("?? ")]
    nu = len(lines) - len(keep)
    i = keep.index("$ git status --short") + 1 if "$ git status --short" in keep else 0
    keep.insert(i, f"[{nu} untracked paths (?? lines) omitted here; full list in reports/stage_e20_briefs/{n}]")
    return "```\n" + "\n".join(keep) + "\n```\n"
def tail_line(n, pat):
    return [l for l in (B / n).read_text().splitlines() if re.search(pat, l)][-1]
# tokens per spawn name from ret_cost_tokens.md
tok = defaultdict(int); spawn_rows = []
for l in rd("ret_cost_tokens.md").splitlines():
    m = re.match(r"\| (.+?) \| (claude-[\w.-]+) \| (\w+) \| ([\dT:-]*) \| ([\dT:-]*) \| ([\d,]+) \|$", l)
    if m:
        name, model, eff, f, la, t = m.groups(); tok[name] += int(t.replace(",", ""))
        def pdt(s): return datetime.fromisoformat(s + "+00:00").astimezone(PT).strftime("%H:%M") if s else ""
        spawn_rows.append((name, model, eff, pdt(f), pdt(la), int(t.replace(",", ""))))
def mins(a, b):
    ta, tb = datetime.strptime(a, "%H:%M"), datetime.strptime(b, "%H:%M"); return int((tb - ta).total_seconds() // 60)
ETA = [  # task, owner, model, effort, start, end, status/deviation
 ("0 Start checks + start suite", "lead", "opus", "xhigh", "10:21", "10:46", "done; suite 7138 passed"),
 ("1 Part A readers x17", "ProductReader-<ROOT>-OpusHigh", "opus", "high", "10:33", "10:58", "done (all 17 at once)"),
 ("5a Code map (workflow, 5 agents)", "CodeMapper-*-OpusHigh", "opus", "high", "10:42", "10:49", "done (lead's addition)"),
 ("1c Consolidation", "lead", "opus", "xhigh", "10:58", "11:01", "done"),
 ("2 H6 code", "H6Coder-OpusXHigh", "opus", "xhigh", "10:40", "11:10", "done; follow-up 15:31-15:33"),
 ("2 H6 review (1st)", "H6Reviewer-FableXHigh", "fable", "xhigh", "11:12", "11:21", "stopped: usage limit"),
 ("PAUSE usage limit", "-", "-", "-", "11:21", "15:10", "excluded from work time"),
 ("2 H6 review (2nd) + fixes", "H6Reviewer-FableXHigh", "fable", "xhigh", "15:12", "15:34", "APPROVE WITH FIXES; fixed"),
 ("3 H6 freeze, commit, register, evaluate", "lead", "opus", "xhigh", "15:34", "15:38", "done; T1-T3 FAIL"),
 ("4 H6 verify", "VerdictVerifier-FableXHigh", "fable", "xhigh", "15:39", "15:55", "VERIFIED WITH NOTES"),
 ("5 Plan review", "PlanReviewer-FableXHigh", "fable", "xhigh", "15:56", "16:18", "BLOCK on PR-1; recheck 16:42-16:47 lifted it"),
 ("5 Swap table (PR-1)", "BackwardTables-OpusXHigh", "opus", "xhigh", "16:19", "16:40", "done (lead's addition)"),
 ("6 Build pattern_search + dry check", "SearchCoder-OpusXHigh", "opus", "xhigh", "16:21", "17:13", "done; fixes 17:29-17:42"),
 ("6b Code review", "SearchReviewer-FableXHigh", "fable", "xhigh", "17:12", "17:29", "APPROVE WITH FIXES (lead's addition)"),
 ("7 Freeze, check --world, register, search, screen", "lead", "opus", "xhigh", "17:34", "17:52", "SCREEN FAIL"),
 ("7 Screen verify (1st)", "ScreenVerifier-FableXHigh", "fable", "xhigh", "17:53", "17:54", "stopped: usage limit"),
 ("10 End suite (detached)", "-", "-", "-", "17:53", "18:12", "7340 passed"),
 ("PAUSE usage limit", "-", "-", "-", "17:54", "20:10", "excluded from work time"),
 ("7 Screen verify (2nd)", "ScreenVerifier-FableXHigh", "fable", "xhigh", "20:12", END, "see section 5"),
 ("8-9 B1 freeze, register, evaluate, verify", "-", "-", "-", "", "", "not run: screen failed"),
 ("10 End checks, cost, return, progress, commit", "lead", "opus", "xhigh", "20:12", END, "done"),
]
pause = sum(mins(s, e) for t, *_, s, e, st in ETA if t.startswith("PAUSE"))
wall = mins("10:21", END); work = wall - pause
eta = ["| Task | Owner | Model | Effort | Start | End | Time (min) | Tokens | Status and deviations |", "|---|---|---|---|---|---|---|---|---|"]
seen = set()
for t, o, m, e, s, en, st in ETA:
    tt = mins(s, en) if s and en else ""
    k = tok.get(o, "") if o not in ("lead", "-") else ""
    if k != "" and o in seen: k = "in the row above"
    elif k != "" and sum(1 for r in ETA if r[1] == o) > 1: k = f"{k:,} (both spawns)"
    seen.add(o)
    if o.startswith("ProductReader"): k = sum(v for n, v in tok.items() if n.startswith("ProductReader-"))
    if o.startswith("CodeMapper"): k = sum(v for n, v in tok.items() if n.startswith("CodeMapper-"))
    ks = k if isinstance(k, str) else f"{k:,}"
    eta.append(f"| {t} | {o} | {m} | {e} | {s} | {en} | {tt} | {ks} | {st} |")
cost = rd("ret_cost_tokens.md"); total_line = [l for l in cost.splitlines() if l.startswith("| all |")][0]
eta.append(f"| Whole stage | lead + workers | | | 10:21 | {END} | {work} work (+{pause} paused; wall {wall}) | {total_line.split('|')[6].strip()} | initial estimate: about 12 h 40 min to 23:00 on a fail; actual work {work // 60} h {work % 60} min |")
out = ["# Stage E.20 return: pattern search with per-product research (Part A, H6, ML search)", "",
       f"Lead Opus 5.5 xhigh, ultracode on; session 2b0cd60b-1622-462e-8c67-e6ae076a3acb; 2026-10-11 10:21-{END} PDT. All times PDT.", "",
       rd("ret_summary.md"), "## 2. Guardrail evidence", "", "### Start checks (10:24)", "", checks("start_checks.txt"),
       "Start suite: `" + tail_line("pytest_start.out", r"passed") + "` (" + tail_line("pytest_start.out", r"^rc ") + ")", "",
       "### End checks (20:12)", "", checks("end_checks.txt"),
       "End suite: `" + tail_line("pytest_end.out", r"passed") + "` (" + tail_line("pytest_end.out", r"^rc ") + ")", "",
       rd("ret_events.md"), "## 3. Results per part", "", rd("ret_results_A_B.md"), rd("ret_results_C.md"), rd("ret_results_C_table.md"),
       "## 4. Delegation record (one row per spawn; tokens from the transcripts)", "",
       "| Spawn (name) | Model | Effort | First (PDT) | Last (PDT) | Tokens |", "|---|---|---|---|---|---|"]
out += [f"| {n} | {m} | {e} | {f} | {l} | {t:,} |" for n, m, e, f, l, t in spawn_rows]
out += ["", rd("ret_verification.md"), rd("ret_open_choices.md"), rd("ret_decisions.md"),
        "## 8. Session cost", "", "### Final ETA table", ""] + eta + ["", "### Tokens per model (transcripts; reports/stage_e20_briefs/make_cost.py)", "",
        "\n".join(cost.splitlines()[:cost.splitlines().index("") + 2]),
        "", "These are token counts, not plan-credit percentages; the /usage meter is the user's to read."]
Path("reports/E.20_RETURN.md").write_text("\n".join(out) + "\n")
print("written reports/E.20_RETURN.md", sum(len(x.split()) for x in out), "words")
