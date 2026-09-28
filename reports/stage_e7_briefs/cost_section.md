**Wall clock** 00:48-03:32 PDT (2 h 44 min), all of it work: no pause, no usage-limit wait, no crash. First estimate
3 h 12 min (to about 04:00; the prompt expected about 1.5 h); the cumulative ETA moved about +15 min at 02:06 (coder A's 63
minutes against 40) and back as the audit, run and recomputation came in shorter. The four full suites (16-17 minutes each)
are about 66 minutes of the wall clock, three of them overlapping worker time.

**Final ETA table** (PDT; tokens from the transcripts; no pause rows, since none occurred):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks (start suite in background to 01:06) | lead | opus | xhigh | 00:48 | 00:52 | 4 min | in lead | done; suite = E.6's end result after the bytecode re-run |
| 1 Member specs (section 9 at 01:12) | lead | opus | xhigh | 00:50 | 01:00 | 10 min | in lead | done |
| 1b Event checks, free series | ReleaseChecker-OpusMed | opus | medium | 00:52 | 01:08 | 16 min | 9,055,436 | done; 3 confirmation-window VXN drops |
| 2A Ports | MemberCoder-A-OpusXHigh | opus | xhigh | 01:03 | 02:06 | 63 min | 23,182,817 | done; .md write refused, saved by the lead |
| 2B New members, tables (+ R-T3-1/R-T3-4 02:46-02:47) | MemberCoder-B-OpusXHigh | opus | xhigh | 01:03 | 02:47 | 37 min | 27,445,017 | done; started before 1b finished (logged) |
| 2g Gate suite | lead | - | - | 02:09 | 02:25 | 16 min | in lead | 4739 passed |
| 3 Fidelity audit | MemberAuditor-K1-FableXHigh | fable | xhigh | 02:09 | 02:45 | 36 min | 14,969,310 (Parts 1 and 2) | 0 blocking, 1 should-fix, 9 notes |
| 4 Rulings, fix, freeze, suite, commit 9113abd | lead | opus | xhigh | 02:45 | 03:04 | 19 min | in lead | done |
| 5 Screening run | lead | opus | xhigh | 03:04 | 03:07 | 3 min | in lead | 11 members, 0 refused |
| 6 Recomputation | MemberAuditor-K1-FableXHigh (resumed) | fable | xhigh | 03:08 | 03:17 | 9 min | above | no discrepancy |
| 7 Result, return, end suite (03:08-03:24), end checks, cost, progress | lead | opus | xhigh | 03:07 | 03:32 | 25 min | in lead | done |
| **Stage** | | | | 00:48 | 03:32 | **2 h 44 min wall and work** | **115,063,741** (lead 40,411,161, 35.1%; workers 74,652,580, 64.9%) | first estimate 3 h 12 min; the prompt expected about 1.5 h |

**Tokens per model** (the lead transcript 99bb7678's .jsonl plus every worker transcript under its subagents/ folder;
each assistant message counted once by message id, from its LAST usage record, so output tokens are final counts;
reports/stage_e7_briefs/cost.py, cost.out; the lead's last messages after the count, about 03:25-03:32, are not included):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,228 | 179,275 | 13,434,512 | 1,354,295 | 14,969,310 |
| claude-opus-5-5 | 892 | 540,396 | 96,296,997 | 3,256,146 | 100,094,431 |
| all | 2,120 | 719,671 | 109,731,509 | 4,610,441 | 115,063,741 |

Per worker spawn: ReleaseChecker-OpusMed (worker-medium, opus, medium) 9,055,436; MemberCoder-A-OpusXHigh (worker-xhigh,
opus, xhigh) 23,182,817; MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh, incl. its resumption) 27,445,017;
MemberAuditor-K1-FableXHigh (worker-xhigh, fable, xhigh, Parts 1 and 2) 14,969,310.

Delegation share: lead 35.1%, workers 64.9%; by model opus 87.0%, fable 13.0%. Cache reads are 95.4% of all tokens. Method
note: E.4-E.6 kept each message's first usage record, which understates output tokens; with that method this session's
output would read about 166k instead of 720k (cache reads unchanged). These are token counts, not plan-credit percentages;
the /usage meter is the user's to record.
