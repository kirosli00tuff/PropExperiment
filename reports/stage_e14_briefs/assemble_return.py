"""Stage E.14: assemble reports/E.14_RETURN.md from return_body.md, the check outputs, the open choices and the
session cost (reports/stage_e10_briefs/cost.py over this session's transcripts). Also writes cost_section.md for
the progress entry. Usage: python3 assemble_return.py <end time HH:MM> <cost UTC upper bound>
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

B = Path("reports/stage_e14_briefs")
SESSION = "19c73927-ec62-4304-916b-b9a703235eab"
PAGES = re.compile(r"^\?\? reports/stage_e1[23]_briefs/(pages/|margin_pages/)")
AGENTS = {  # id: (description, file, model, effort, start, end, status)
    "aa29ceb3163cd20f4": ("CalendarProbe-OpusHigh", "worker-high", "opus", "high", "00:34", "03:06",
                          "done: probe (Part A 01:32) and release calendars (Part B)"),
    "aed2e457ec2c07eb1": ("CalendarBuilder-Equity-OpusHigh", "worker-high", "opus", "high", "00:34", "02:28",
                          "done: equity, rates, FX, grains"),
    "a614eb4f44068543d": ("CalendarBuilder-Commod-OpusHigh", "worker-high", "opus", "high", "00:36", "01:33",
                          "done: energy, metals, full sessions"),
    "a94b80ceda0f5c25b": ("V10Coder-OpusXHigh", "worker-xhigh", "opus", "xhigh", "00:38", "01:29",
                          "done: harness v10 (worktree, e577d55)"),
    "a87e3dc1a4f58c0e5": ("C1Coder-OpusXHigh", "worker-xhigh", "opus", "xhigh", "01:29", "02:48",
                          "done: c1_replication (1169b71) and one follow-up via SendMessage (5c4a1cd, 02:46-02:48)"),
    "abd1bd206c07dc282": ("FreezeReviewer-FableXHigh", "worker-xhigh", "fable", "xhigh", "03:06", "03:26",
                          "done: APPROVE WITH FIXES (1 BLOCKING, 2 SHOULD FIX, 12 NOTE)"),
    "a20004c7b6f8a32a3": ("VerdictVerifier-FableXHigh", "worker-xhigh", "fable", "xhigh", "03:30", "03:39",
                          "done: all MATCH (0 BLOCKING, 1 SHOULD FIX, 5 NOTE)"),
}


def checks(name: str) -> str:
    lines = Path(B / name).read_text().splitlines()
    out, n = [], 0
    for line in lines:
        if PAGES.match(line):
            n += 1
            if n == 1:
                out.append("<<COLLAPSED>>")
            continue
        out.append(line)
    return "\n".join(out).replace(
        "<<COLLAPSED>>", f"[{n} lines '?? reports/stage_e12_briefs/margin_pages/' and '?? reports/stage_e13_briefs/"
                         f"pages/...' (the E.12/E.13 DO_NOT_COMMIT page folders) collapsed here; full text in "
                         f"reports/stage_e14_briefs/{name}]")


def fmt(n: int) -> str:
    return f"{n:,}"


def cost(hi: str) -> tuple[str, dict]:
    raw = subprocess.run(["python3", "reports/stage_e10_briefs/cost.py", "2026-10-05T07:20:00Z", hi, SESSION],
                         capture_output=True, text=True, check=True).stdout
    (B / "cost_raw.txt").write_text(raw)
    per = {}
    for line in raw.splitlines():
        m = re.match(r"^(lead|agent-(\w+)) (\S+) msgs=(\d+) .*in=(\d+) out=(\d+) cread=(\d+) ccreate=(\d+) "
                     r"total=(\d+)", line)
        if m:
            key = "lead" if m.group(1) == "lead" else m.group(2)
            per[key] = {"model": m.group(3), "msgs": int(m.group(4)), "in": int(m.group(5)),
                        "out": int(m.group(6)), "cread": int(m.group(7)), "ccreate": int(m.group(8)),
                        "total": int(m.group(9))}
    table = raw[raw.index("| Model |"):].strip()
    return table, per


def main(end_time: str, hi: str) -> None:
    body = (B / "return_body.md").read_text()
    table, per = cost(hi)
    rows = []
    for aid, (desc, f, model, eff, s, e, status) in AGENTS.items():
        tok = per.get(aid, {}).get("total")
        rows.append(f"| {desc} | {f} | {model} | {eff} | {s} | {e} | {fmt(tok) if tok else 'n/a'} | {status} |")
    lead = per["lead"]["total"]
    workers = sum(v["total"] for k, v in per.items() if k != "lead")
    by_model: dict[str, int] = {}
    for v in per.values():
        by_model[v["model"]] = by_model.get(v["model"], 0) + v["total"]
    total = lead + workers
    eta_raw = (B / "eta_final.md").read_text()
    eta_raw = (eta_raw.replace("{{LEAD_TOK}}", fmt(lead)).replace("{{WORKER_TOK}}", fmt(workers))
               .replace("{{TOTAL_TOK}}", fmt(total)))
    eta, wall = eta_raw.split("WALL=")
    spawn_line = "; ".join(f"{AGENTS[a][0]} ({AGENTS[a][1]}, {AGENTS[a][2]} {AGENTS[a][3]}) {fmt(per[a]['total'])}"
                           for a in AGENTS if a in per)
    share = ", ".join(f"{m} {fmt(t)} ({t / total:.1%})" for m, t in sorted(by_model.items()))
    cost_md = f"""Wall clock: 00:26 to {end_time} PDT, {wall.strip()} of work; no pause and no usage-limit wait.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

{eta.strip()}

### Tokens per model (this session's transcript and its {len(AGENTS)} subagent transcripts, 07:20Z to {hi})

Computed with reports/stage_e10_briefs/cost.py (final usage per streamed message); raw output
reports/stage_e14_briefs/cost_raw.txt. Token counts, not plan-credit percentages.

{table}

Per spawn: {spawn_line}.

Delegation share: lead {fmt(lead)} ({lead / total:.1%}), workers {fmt(workers)} ({workers / total:.1%}). By model:
{share}."""
    (B / "cost_section.md").write_text(cost_md + "\n")
    choices = (B / "open_choices.md").read_text().split("\n", 2)[2].strip()
    purchase_block = Path("reports/stage_e14_purchase.md").read_text().split("```")[1].strip()
    sec2 = f"""## 2. Guardrail evidence

### Start (00:26 PDT), quoted verbatim (reports/stage_e14_briefs/start_checks.txt; script checks.sh)

```
{checks('start_checks.txt')}
```
Start suite (without PYTHONPYCACHEPREFIX): `{Path(B / 'pytest_start.out').read_text().splitlines()[-2].strip()}` (00:26-00:43).

### After the purchase point (03:07 PDT; nothing was bought), quoted verbatim

```
{purchase_block}
```
Ledger then: 27,756 lines, sha256 0312fbc0b1ca2da652ca7caaab2313ccbbc6920ae3a19d9651ff2e94cd1c48fb; acct-1 spent
118.390020 (headroom 1.609980), acct-2 spent 231.599730 (headroom 18.070270), as at the start.

### End (03:39 PDT), quoted verbatim (reports/stage_e14_briefs/end_checks.txt)

Run just before this return was written. The untracked files are this stage's outputs, which the final commit adds,
except the git-ignored GEX CSV and its copies and the coder worktrees.

```
{checks('end_checks.txt')}
```
End suite (without PYTHONPYCACHEPREFIX): `{Path(B / 'pytest_end.out').read_text().splitlines()[-2].strip()}`.

### Order of events per test (times PDT; git commit times from `git log --date=iso-local`)

| Test | Event | Time | Evidence |
|---|---|---|---|
| C2 | SqueezeMetrics terms read; CSV fetched once | 00:38:50 / 00:43:01 | pages/gex/fetch_log.txt; gex/fetch_record.txt |
| C2 | Fresh ES quote ($0.00 lines) | 01:29:26-01:32:41 | ledger lines from 08:29:29Z; quotes_es2011.json |
| C2 | GEX < 0 count 135 (first equity file); stop ruled; cap reset to 0.00 | 01:33 / 01:34 / 01:34:22 | gex_count_first.out; data/config.py mtime |
| C2 | Count rerun on the final equity calendar, two implementations: 135 | 02:28:59-02:29:00 | gex_count_final.out, gex_count_v10helper_final.out |
| C2 | No freeze, no registration, no purchase, no evaluation | n/a | ledger/trial_registrations.jsonl (baseline only); ledger (quotes only) |
| C1 | Probe written; ruled (rule does not fire) | 01:32:17 / 01:36 | stage_e14_probe.md |
| C1 | Calendars final (group files; releases) | 01:31:48-02:26:14; 03:05:37 | file mtimes; stage_e14_calendars.md |
| C1 | Fresh quote of the set ($0.00 lines) | 01:33-01:56 | quotes_ext2010.json |
| C1 | Fable freeze review | 03:06-03:26 | stage_e14_review.md |
| C1 | Harness v10 commit dc93e9b; freeze commit 1680982 | 03:29:15 / 03:29:42 | git log |
| C1 | M1 fit and q (before any 2010-2019 byte; none exists) | 03:29:54-03:29:57 | stage_e14_c1_model.json; STATE |
| C1 | Not registered, not bought, not evaluated (awaits funds) | n/a | trial registry; ledger |

Incident (Fable F-V6): the Task 8 verifier's first look at the CSV printed two rows' values (2011-05-02,
2011-05-03), after C2's stop; nothing was derived from them. No other guardrail event: no TopstepX call, no key
printed, no write to REGISTRATION.md, no edit under live/ or ops/, no MES store opened, no push.

"""
    body = body.replace("## 3. Results per task", sec2 + "## 3. Results per task")
    body = (body.replace("{{END_TIME}}", end_time).replace("{{DELEGATION_ROWS}}", "\n".join(rows))
            .replace("{{OPEN_CHOICES}}", choices).replace("{{COST}}", cost_md))
    assert "{{" not in body
    Path("reports/E.14_RETURN.md").write_text(body)
    print("written", len(body.splitlines()), "lines; lead", fmt(lead), "workers", fmt(workers), "total", fmt(total))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
