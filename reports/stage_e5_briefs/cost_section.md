**Final ETA table** (PDT; tokens from the transcripts; pauses shown as their own rows and excluded from the work total):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup, start suite | lead | opus | xhigh | 12:23 | 12:37 | 14 min | in lead | done |
| A1 Inventory, plan, rulings | lead | opus | xhigh | 12:27 | 12:37 | 10 min | in lead | done |
| A2 Change set (+ 2 follow-ups) | HarnessBuilder-OpusXHigh | opus | xhigh | 12:36 | 13:41 | 65 min | 37,076,657 | done; K3 stop point ruled (R-A2-1) |
| C3 NGS check (started during Part A) | ReleaseChecker-OpusMed | opus | medium | 12:36 | 13:26 | 50 min | 8,593,252 | done; moved ahead of B2 |
| A3 Replays (b720c5aa), suite | lead | opus | xhigh | 13:13 | 13:28 | 15 min | in lead | done |
| A3 Review | HarnessReviewer-FableXHigh | fable | xhigh | 13:18 | 13:37 | 19 min | 3,101,653 | done |
| A4 Fixes, v5 manifest, v5 replays | lead | opus | xhigh | 13:33 | 13:50 | 17 min | in lead | done |
| PAUSE: machine crash | - | - | - | 13:50 | 13:53 | 3 min | - | excluded |
| A4 Suite (stopped for the pause) | lead | - | - | 13:54 | 13:58 | 4 min | in lead | stopped, rerun |
| PAUSE: user (usage) | - | - | - | 13:58 | 17:35 | 217 min | - | excluded |
| A4 Resume checks, suite, v5 commit 2c0bfe0 | lead | opus | xhigh | 17:35 | 17:53 | 18 min | in lead | done |
| B1 Quote, caps, v6 commit ce3cb66 | lead | opus | xhigh | 17:53 | 18:13 | 20 min | in lead | done |
| B2 Buy K4, buy K5, status, bars, report | lead | opus | xhigh | 18:13 | 18:52 | 39 min | in lead | done; $21.196568 = quote |
| C1 Start rules K4, K5 | lead | opus | xhigh | 18:52 | 18:53 | 1 min | in lead | done; S_MGC empty |
| C2 Power re-runs K4, K5 | lead | opus | xhigh | 18:54 | 19:00 | 6 min | in lead | done; R-D-1 (K5 stopped) |
| C3 Table amendment | MemberCoder-OpusXHigh | opus | xhigh | 18:59 | 19:07 | 8 min | 4,998,610 | done |
| C3 Freeze, audit Part 1, commit 41d6adf | lead + ConfirmAuditor-K4-FableXHigh | opus / fable | xhigh | 19:05 | 19:14 | 9 min | auditor below | done |
| C4 K4 list, commit 4161032 | lead | opus | xhigh | 19:14 | 19:15 | 1 min | in lead | done |
| C5 K4 run (once), verdicts | lead | opus | xhigh | 19:15 | 19:23 | 8 min | in lead | done: null |
| C6 Recomputation (Part 2) | ConfirmAuditor-K4-FableXHigh | fable | xhigh | 19:23 | 19:31 | 8 min | 4,238,978 (Parts 1 and 2) | done: no discrepancy |
| Part D K5 (C4-C6) | - | - | - | - | - | - | - | not run (R-D-1); ConfirmAuditor-K5 not spawned |
| End suite, end checks, return, cost | lead | opus | xhigh | 19:23 | 19:43 | 20 min | in lead | done |
| **Stage** | | | | 12:23 | 19:43 | **7 h 20 min wall, 3 h 40 min of work excluding the 3 h 40 min of pauses** | **146,528,258** (lead 88,519,108, 60%; workers 58,009,150, 40%) | estimate was about 9 h of work to 21:30 (22:45 with the table amendment); K5 stopped at C2, which removed about 1.5 h |

**Tokens per model** (the lead transcript b56ee083's .jsonl, which also holds the two resumed sessions' messages, plus every worker
transcript under its subagents/ folder, from 12:00 PDT to the end; messages de-duplicated by message and request id;
reports/stage_e5_briefs/cost.out; the lead's last messages after the count are not included):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,322 | 3,670 | 6,656,181 | 679,458 | 7,340,631 |
| claude-opus-5-5 | 1,090 | 278,565 | 136,021,295 | 2,886,677 | 139,187,627 |
| all | 2,412 | 282,235 | 142,677,476 | 3,566,135 | 146,528,258 |

**Per worker spawn:**
- MemberCoder-OpusXHigh (worker-xhigh, opus, xhigh; C3 table amendment): 4,998,610 tokens, 18:59-19:07
- ConfirmAuditor-K4-FableXHigh (worker-xhigh, fable, xhigh; C3 audit Part 1 + C6 recomputation Part 2): 4,238,978 tokens, 19:08-19:31
- HarnessReviewer-FableXHigh (worker-xhigh, fable, xhigh; A3 review): 3,101,653 tokens, 13:18-13:37
- HarnessBuilder-OpusXHigh (worker-xhigh, opus, xhigh; A2 change set + 2 follow-ups): 37,076,657 tokens, 12:36-13:41
- ReleaseChecker-OpusMed (worker-medium, opus, medium; C3 NGS check): 8,593,252 tokens, 12:36-13:26

**Delegation share:** lead 60.4%, workers 39.6%; by tier opus 95.0%, fable 5.0%. About 97% of all tokens are
cache reads, as in E.0 and E.2a. These are token counts, not plan-credit percentages; the /usage meter is the user's to read.