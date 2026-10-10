## 8. Session cost

Wall clock 11:41 to 12:48 PDT, 2026-10-10 (final commit 12:48:04) (one session, no pause, no usage-limit wait, no outage). Tokens are
summed from this session's transcript and its two subagent transcripts (reports/stage_e10_briefs/cost.py, per-field
final usage per message) up to 12:46:58 PDT; the lead's last steps after that (writing this return, the progress
entry and the final commit) are not in the count.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task | Owner | Model | Effort | Parallel or serial | Start-end | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Read prompt and context | lead | opus | xhigh | serial | 11:41-11:47 | 0:06 | in lead | done [with checks 0:10] |
| 0 | Start checks | lead | opus | xhigh | serial | 11:47:18-11:47:30 | 0:00 | in lead | done |
| 0 | Start suite (detached) | lead | opus | xhigh | parallel with 1-2 | 11:47:32-12:05:36 | 0:18 | in lead | 6913 passed, 3 failed (invocation artifact, file rerun 17/17) [0:17] |
| 1 | C1b text, diff, c1b.py, test, listing evidence | lead | opus | xhigh | serial | 11:48-11:57 | 0:09 | in lead | done [1:00] |
| 1b | Review brief, dry-check and freeze scripts | lead | opus | xhigh | parallel with 2 | 11:57-12:02 | 0:05 | in lead | done (not in the estimate) |
| 2 | Diff review | DiffReviewer-FableXHigh | fable | xhigh | after 1 | 11:58:44-12:14:08 | 0:15 | 2,484,866 | APPROVE WITH FIXES [0:30] |
| 2b | Fixes (R-1..R-5), text and diff regenerated | lead | opus | xhigh | serial | 12:14-12:15 | 0:01 | in lead | done [0:10] |
| 3 | Dry check | lead | opus | xhigh | serial | 12:16:02-12:16:05 | 0:00 | in lead | PASS [0:15] |
| 4 | Freeze manifest, commit b714751 | lead | opus | xhigh | serial | 12:17:07-12:17:35 | 0:00 | in lead | done [0:15] |
| 5 | Register (N 478 -> 480), evaluate once | lead | opus | xhigh | serial | 12:17:46-12:18:38 | 0:01 | in lead | FAIL; 34.7 s run [0:10] |
| 6 | Verdict recomputation | VerdictVerifier-FableXHigh | fable | xhigh | after 5 | 12:19:11-12:29:26 | 0:10 | 2,897,434 | VERIFIED WITH NOTES [0:30] |
| 7a | Return parts drafted | lead | opus | xhigh | parallel with 6 | 12:19-12:29 | 0:10 | in lead | done |
| 7b | End checks | lead | opus | xhigh | serial | 12:29:55-12:30:05 | 0:00 | in lead | all pass |
| 7c | End suite (detached) | lead | opus | xhigh | parallel with 7d | 12:30:09-12:46:32 | 0:16 | in lead | 6990 passed, rc 0 |
| 7d | STAGES, memory, cost, progress, return, commit | lead | opus | xhigh | serial | 12:30-12:48 | 0:18 | in lead (to 12:46:58) | done [7 total 0:50] |
| | **Stage total** | | | | | 11:41-12:48 | **1:07 work** | **45,253,221** | estimate [3:50]; no pause |

Lead versus workers: lead 39,870,921 tokens (88.1%), workers 5,382,300 (11.9%). By tier: opus 88.1%, fable 11.9%.
The estimate's guesses were long: step 1 took 9 minutes, not 60, and each Fable spawn 10-15 minutes, not 30.

### Tokens per model (session a6f2d97b's transcript and its 2 subagent transcripts, 2026-10-10 18:35Z to 19:46:58Z)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,316 | 120,728 | 4,870,416 | 389,840 | 5,382,300 |
| claude-opus-5-5 | 288 | 213,963 | 39,236,246 | 420,424 | 39,870,921 |
| all | 1,604 | 334,691 | 44,106,662 | 810,264 | 45,253,221 |

Per spawn: DiffReviewer-FableXHigh (worker-xhigh, fable, xhigh) 2,484,866; VerdictVerifier-FableXHigh (worker-xhigh,
fable, xhigh) 2,897,434. Raw lines: reports/stage_e18_briefs/cost_raw.txt.

These are token counts from the transcripts, not plan-credit percentages; the session cannot read the /usage meter.
