"""Stage E.21: assemble reports/E.21_RETURN.md from the lead's section files and generated tables.
Usage: python3 reports/stage_e21_briefs/assemble_return.py <end HH:MM PDT>. Reads only files under
reports/stage_e21_briefs/ and reports/stage_e21_economics.md; run after make_cost.py."""

from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

B = Path("reports/stage_e21_briefs")
END = sys.argv[1]


def read(name: str) -> str:
    return (B / name).read_text().rstrip("\n")


def checks_block(src: str) -> str:
    out, n, in_status = [], 0, False
    for line in (B / src).read_text().splitlines():
        if line.startswith("$ git status --short"):
            in_status = True
            out.append(line)
            continue
        if in_status and line.startswith("$ "):
            out.append(f"[{n} untracked paths (?? lines) omitted here; full list in "
                       f"reports/stage_e21_briefs/{src}]")
            in_status = False
        if in_status and line.startswith("??"):
            n += 1
            continue
        out.append(line)
    return "\n".join(out)


def pytest_line(src: str) -> str:
    lines = [ln for ln in (B / src).read_text().splitlines() if ln.strip()]
    return "\n".join(lines[-2:])


def pdt(utc_iso: str) -> str:
    t = datetime.fromisoformat(utc_iso.replace("Z", "")) - timedelta(hours=7)
    return t.strftime("%H:%M")


def spawn_tokens() -> tuple[dict[str, tuple[str, str, str, str, int]], str]:
    rows, text = {}, read("ret_cost_tokens.md")
    for line in text.splitlines():
        m = re.match(r"\| (.+?) \| (claude-[\w-]+) \| (\w+) \| (\S+) \| (\S+) \| ([\d,]+) \|", line)
        if m:
            name, model, eff, first, last, tok = m.groups()
            rows[name] = (model, eff, pdt(first), pdt(last), int(tok.replace(",", "")))
    return rows, text


def minutes(a: str, b: str) -> int:
    fa, fb = datetime.strptime(a, "%H:%M"), datetime.strptime(b, "%H:%M")
    return int((fb - fa).total_seconds() // 60)


# (task, owner, model, effort, mode, start, end, spawn name or None, status, initial estimate)
ROWS = [
    ("0 Startup checks", "lead", "opus", "xhigh", "first", "03:04", "03:10", None,
     "done; all pass", "03:04-03:10"),
    ("0b Start pytest (detached)", "lead (shell)", "-", "-", "parallel", "03:10", "03:31", None,
     "7340 passed, 3 skipped, 3 xfailed", "~22 min, ~03:32"),
    ("1 SpecReaderTrend", "SpecReaderTrend-OpusHigh", "opus", "high", "4 at once", "03:13", "03:19",
     "SpecReaderTrend-OpusHigh", "done", "<=50 min, ~04:05"),
    ("1 SpecReaderTOM", "SpecReaderTOM-OpusHigh", "opus", "high", "4 at once", "03:13", "03:33",
     "SpecReaderTOM-OpusHigh", "done", "<=50 min, ~04:05"),
    ("1 SpecReaderPost2010", "SpecReaderPost2010-OpusHigh", "opus", "high", "4 at once", "03:13",
     "03:25", "SpecReaderPost2010-OpusHigh", "done", "<=50 min, ~04:05"),
    ("1 PropEdReader", "PropEdReader-OpusHigh", "opus", "high", "4 at once", "03:13", "03:26",
     "PropEdReader-OpusHigh", "done; automation unresolved", "<=50 min, ~04:05"),
    ("2a Lead spec, prereg draft", "lead", "opus", "xhigh", "parallel with 1", "03:13", "03:20", None,
     "done", "~7 min"),
    ("2b MultidayCoder (build, then fixes Q1/Q2/A12, FR-1/2/6/7, FR-9 via SendMessage)",
     "MultidayCoder-OpusXHigh", "opus", "xhigh", "parallel with 1 (deviation: the plan said after 1)",
     "03:18", "04:11", "MultidayCoder-OpusXHigh", "done: 62 tests, ruff clean", "~80 min, ~04:45"),
    ("2c Literature and calendar rulings A1-A12, Q1-Q4", "lead", "opus", "xhigh", "serial", "03:33",
     "03:49", None, "done", "~10 min, ~04:15"),
    ("3b FreezeReviewer (review and recheck)", "FreezeReviewer-FableXHigh", "fable", "xhigh",
     "serial", "03:51", "04:10", "FreezeReviewer-FableXHigh",
     "APPROVE WITH FIXES (0 BLOCKING, 2 SHOULD FIX, 6 NOTE); recheck APPROVE (+FR-9 NOTE)",
     "~25 min, ~05:25"),
    ("3g Freeze manifest, commit 839efc9", "lead", "opus", "xhigh", "serial", "04:11", "04:12", None,
     "done", "~20 min with fixes, ~05:45"),
    ("4a Register r006-E21 (N 528 -> 532)", "lead", "opus", "xhigh", "serial", "04:12", "04:12", None,
     "done 04:12:12", "in 3c"),
    ("4b Evaluate once (detached)", "lead (shell)", "-", "-", "serial", "04:12", "04:14", None,
     "rc 0; 2:11 wall; 1.47 GB peak; all FAIL", "~20 min, ~06:05"),
    ("4c F8 economics", "EconWorker-OpusHigh", "opus", "high", "parallel with 5", "04:15", "04:20",
     "EconWorker-OpusHigh", "done", "~25 min, ~06:30"),
    ("5 Verdict verification", "VerdictVerifier-FableXHigh", "fable", "xhigh", "parallel with 4c",
     "04:15", "04:35", "VerdictVerifier-FableXHigh", "VERIFIED WITH NOTES (152 numbers MATCH)",
     "~30 min, ~06:35"),
    ("6a End pytest (detached)", "lead (shell)", "-", "-", "parallel", "04:15", "04:35", None,
     "7402 passed, 3 skipped, 3 xfailed", "~22 min"),
    ("6b End checks", "lead", "opus", "xhigh", "serial", "04:35", "04:36", None, "all pass", "-"),
    ("6c Return, progress, STAGES, cost, commit", "lead", "opus", "xhigh", "last", "04:36", END, None,
     "done", "~35 min, ~07:10"),
]


def eta_table(spawns: dict) -> str:
    out = ["| Task | Owner | Model | Effort | Mode | Start | End | Time (min) | Tokens | Status and "
           "deviations | [Initial estimate] |", "|" + "---|" * 11]
    for task, owner, model, eff, mode, s, e, spawn, status, est in ROWS:
        tok = f"{spawns[spawn][4]:,}" if spawn in spawns else ("in lead" if owner == "lead" else "-")
        out.append(f"| {task} | {owner} | {model} | {eff} | {mode} | {s} | {e} | {minutes(s, e)} | {tok} | "
                   f"{status} | [{est}] |")
    lead = spawns.get("lead (Opus 5.5)")
    workers = sum(v[4] for k, v in spawns.items() if k != "lead (Opus 5.5)")
    total = workers + (lead[4] if lead else 0)
    out.append(f"| **Stage total** | lead + 8 workers | | | | 03:04 | {END} | {minutes('03:04', END)} | "
               f"{total:,} (lead {lead[4] if lead else 0:,}; workers {workers:,}) | no pauses; "
               f"no outage | [cumulative ETA ~07:10] |")
    return "\n".join(out)


ORDER = """| Event | Time (PDT) | Evidence |
|---|---|---|
| Prompt commit | 2026-10-14 03:03:14 | 03cdf50 (git) |
| Start checks | 03:10:05 | reports/stage_e21_briefs/start_checks.txt |
| Literature check (4 readers) | 03:13-03:33 | workflow wf_18fed4b8-d89; spec_*.md mtimes 03:19-03:33 |
| Literature rulings A1-A11 | 03:35 | lead_spec section A |
| Calendar-only counts (no bar row); A12 ruling | 03:42-03:50; 03:48 | calendar_counts.json written 03:42:22, re-run 03:50:38 |
| Freeze review | 03:51-04:02; recheck 04:07-04:10 | reports/stage_e21_review_freeze.md (mtime 04:09:54) |
| Freeze manifest | 04:11:30 | reports/stage_e21_freeze.json sha256 0bb899e5... |
| Freeze commit | 04:12:01 | 839efc9 "E.21 freeze" (git) |
| Registration | 04:12:12 | r006-E21, ledger/trial_registrations.jsonl line 7 |
| Run-once marker (before any bar) | 04:12:28 | reports/stage_e21_RUN_ONCE.json |
| Evaluation complete | 04:14:35 | reports/stage_e21_runs/verdict.json |
| Verification | 04:15-04:35 | reports/stage_e21_review_verdict.md (mtime 04:35:29) |
| End checks | 04:35:56 | reports/stage_e21_briefs/end_checks.txt |"""


def main() -> int:
    spawns, cost_text = spawn_tokens()
    cost_pdt = re.sub(r"(\| )(2026-10-14T\d\d:\d\d:\d\d)( \|)", lambda m: m.group(1) + pdt(m.group(2)) +
                      " PDT" + m.group(3), cost_text).replace("First (UTC)", "First").replace(
        "Last (UTC)", "Last")
    econ = Path("reports/stage_e21_economics.md").read_text()
    t3_prop = econ[econ.index("### T3 (daily sd"):econ.index("## 4. Assumptions")].rstrip()
    parts = [
        "# Stage E.21 return: multi-day round (TSMOM-12, trend blend, turn of the month, combined "
        "book) on 17 roots, 2010-2024; all four FAIL; N = 532",
        "",
        "Prompt docs/prompts/STAGE_E.21.md. Lead Opus 5.5 xhigh, ultracode on, session "
        "13fe2d4e-086f-4929-8325-9ef707bdf0cf, 2026-10-14 03:04-" + END + " PDT, unattended. All times PDT "
        "(America/Vancouver).",
        "",
        read("ret_s1_summary.md"),
        "",
        "## 2. Guardrail evidence",
        "",
        "### Start checks (verbatim; reports/stage_e21_briefs/start_checks.txt)",
        "",
        "```", checks_block("start_checks.txt"), "$ uv run pytest -q -p no:cacheprovider (detached, "
        "03:10-03:31)", pytest_line("pytest_start.out"), "```",
        "",
        "The E.14 inputs-list mismatch on reports/stage_e2b_harness_freeze.json is pre-existing and identical at "
        "E.20's start and end (the harness freeze file was rewritten for v12 after E.14).",
        "",
        "### End checks (verbatim; reports/stage_e21_briefs/end_checks.txt)",
        "",
        "```", checks_block("end_checks.txt"), "$ uv run pytest -q -p no:cacheprovider (detached, "
        "04:15-04:35)", pytest_line("pytest_end.out"), "```",
        "",
        "Changed between start and end: ledger/trial_registrations.jsonl gained line 7 (r006-E21; 6 -> 7 lines, "
        "sha256 2acc993e... -> 085ed33c...); the spend ledger is unchanged (36,402 lines, 034a454b...). "
        "Harness v12 is unchanged and was verified at start and end with a fresh PYTHONPYCACHEPREFIX. No file "
        "under live/, ops/, screening/, rules/, sim/, data/holdout.py or base_rules/ changed. Nothing dated "
        "2024-03-01 or later was read (the stores end 2024-02-29 and base_rules refuses later dates). No "
        "TopstepX call, no Databento call, no push. Peak memory of the evaluation 1.47 GB (nice 10); at most "
        "two heavy jobs at once (the verifier and the end pytest).",
        "",
        "### Order of events",
        "",
        ORDER,
        "",
        "## 3. Results",
        "",
        read("ret_s3_text.md").split("### 3.3")[0].rstrip(),
        "",
        "#### PropEd rule table (generated from reports/stage_e21_proped_rules.json)",
        "",
        read("ret_s3_proped_table.md"),
        "",
        "### 3.3" + read("ret_s3_text.md").split("### 3.3")[1],
        "",
        read("ret_s3_tables.md"),
        "",
        "### 3.4 F8 descriptive economics (EconWorker-OpusHigh; reports/stage_e21_economics.md and .json)",
        "",
        "- Personal account (capital at which every root holds at least one contract at full signal; E.13 C2 "
        "per-contract dollar risk; F8 micros where they exist, full-size flagged): T1 about $691K at 15% and "
        "$415K at 25% annual volatility (book volatility 16.6%); T2 $538K and $323K (12.9%); T3 (MNQ, M2K) $57K "
        "and $34K (17.5%). Live cattle (full-size LE) binds T1 and T2; at $100K, 4 to 7 of the 17 roots round to "
        "zero contracts.",
        "- The integer book at its smallest integer size tracks the fractional book (correlation >= 0.995): "
        "daily / 5-day dollar sd T1 $6,540 / $14,520, T2 $5,099 / $10,958, T3 $535 / $1,190.",
        "- No weekend holds (flat every Friday, two extra fills per root per weekend): T1's mean turns negative "
        "on costs alone (-$4.9K a year at that size), T2 about -$0.3K, T3 about +$0.4K.",
        "- PropEd (automation UNCONFIRMED on every row): T1 and T2 breach the drawdown in 46-100% of rolling "
        "21-day windows (One Plan 750K 24-57%), exceed the micro-contract caps on 57-99% of days, and hold roots "
        "PropEd does not list (M6E, micro yields, TN, UB, HE, LE). T3 fits the $7.5K-$10K-drawdown plans and "
        "Standard 150K (breach 0-1.4%), but T3 failed. Phidias Premium 50K ($2,500 EOD trailing, semi-automated "
        "only) matches PropEd's $2,500 plans.",
        "- T4 has no contract book; its realized volatility is 120 risk units a year, 13.0 without the 8 days "
        "with |value| > 10 (the H5-scaling spikes, section 5 FR-4 and section 7 item 3).",
        "",
        "#### T3 against each PropEd plan (from reports/stage_e21_economics.md)",
        "",
        t3_prop,
        "",
        "## 4. Delegation record",
        "",
        "| Spawn (CLI name) | Agent file | Model | Effort | Start-end (PDT) | Objective | Output | Result |",
        "|---|---|---|---|---|---|---|---|",
        "| SpecReaderTrend-OpusHigh | worker-high (workflow wf_18fed4b8-d89) | opus | high | 03:13-03:19 | T1/T2 "
        "and F3 vs MOP 2012, HOP 2017 | reports/stage_e21_briefs/spec_trend.md | done; T2 scaling mismatch, "
        "chained-return claim rejected |",
        "| SpecReaderTOM-OpusHigh | worker-high (same workflow) | opus | high | 03:13-03:33 | T3 vs Lakonishok-"
        "Smidt, McConnell-Xu; post-2008 | spec_tom.md | done; parenthetical mismatch |",
        "| SpecReaderPost2010-OpusHigh | worker-high (same workflow) | opus | high | 03:13-03:25 | post-2010 trend "
        "and TOM-futures evidence | spec_post2010.md | done; AQR 0.389, SG 0.352 |",
        "| PropEdReader-OpusHigh | worker-high (same workflow) | opus | high | 03:13-03:26 | PropEd plans and "
        "rules | reports/stage_e21_proped_rules.md/.json | done; automation unresolved |",
        "| MultidayCoder-OpusXHigh | worker-xhigh | opus | xhigh | 03:18-04:11 (build 03:18-03:46; 4 SendMessage "
        "rounds) | multiday/ to the lead spec, tests, calendar counts | multiday/, tests/test_multiday_*.py, "
        "multiday_build.md | done; 62 tests |",
        "| FreezeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 03:51-04:02; recheck 04:07-04:10 | adversarial "
        "freeze review | reports/stage_e21_review_freeze.md | APPROVE WITH FIXES; recheck APPROVE |",
        "| EconWorker-OpusHigh | worker-high | opus | high | 04:15-04:20 | F8 economics | "
        "reports/stage_e21_economics.md/.json, briefs/econ/economics.py | done |",
        "| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | 04:15-04:35 | independent recomputation of "
        "every verdict number | reports/stage_e21_review_verdict.md | VERIFIED WITH NOTES |",
        "",
        "Tokens per spawn are in section 8 (transcripts). Reserved to the lead and not delegated: the decomposition, "
        "the lead spec and prereg, every ruling (A1-A12, Q1-Q4, FR-1..FR-9, VV-1..VV-5), the registration, the "
        "evaluation command, the verdicts and this synthesis.",
        "",
        read("ret_s5_verification.md"),
        "",
        read("ret_open_choices.md"),
        "",
        read("ret_s7_decisions.md"),
        "",
        "## 8. Session cost",
        "",
        "### Final ETA table (actuals; PDT; the initial estimate in brackets)",
        "",
        eta_table(spawns),
        "",
        "### Tokens per model (transcripts; reports/stage_e21_briefs/make_cost.py over the lead's .jsonl and "
        "every subagent transcript, each message's final usage)",
        "",
        cost_pdt,
    ]
    Path("reports/E.21_RETURN.md").write_text("\n".join(parts) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
