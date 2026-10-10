Wall clock 18:34 (2026-10-09) to {{END_TIME}} (2026-10-10) PDT. One break, not counted as work: the first Claude
session ended at about 19:38, taking the C1 buy process with it, and the next started at 19:41 (about 0:04, its own
row). No usage-limit pause.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task / spawn | Owner | Model | Effort | Start | End | Time [estimate] | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0-3 | Prompt and context, start checks, start suite, C1 and E.16 freeze verification, guard/A3/hash prep | lead | opus | xhigh | 18:34 | 18:54 | 0:20 [0:34] | lead | done; suite 6815 passed |
| 5 | Fresh C1 quote and guard | lead | opus | xhigh | 18:54 | 19:07 | 0:13 [0:08] | lead | done; $57.742330 |
| 6 | v11 edit, manifest, suite, commit a21d82d | lead | opus | xhigh | 19:07 | 19:29 | 0:22 [0:40] | lead | done; +line 196 (V11-R1) |
| 6r | HarnessReviewer-FableXHigh (v11) | worker-xhigh | fable | xhigh | 19:10 | 19:26 | 0:16 [0:25] | 1,548,942 | APPROVE |
| 7a | Register C1, buy 642 chunks | lead | opus | xhigh | 19:29 | 22:41 | 3:12 incl. the break [1:00-1:40] | lead | done; 17 s a chunk (estimate 10 s); resumed after the session end |
| - | Break: the Claude session ended; the next session resumed the buy | | | | 19:38 | 19:42 | 0:04 (not work) | | the orphan commit $0.075002 |
| 7b | Post-purchase checks, six stores, hash files, evaluation, commit 558a7ce | lead | opus | xhigh | 22:41 | 22:51 | 0:10 [1:10] | lead | STOPPED at C10 |
| 7v | VerdictVerifier-FableXHigh (C1's STOP) | worker-xhigh | fable | xhigh | 22:51 | 23:08 | 0:17 [0:45] | 4,489,321 | VERIFIED WITH NOTES |
| 8a | V12Coder-OpusXHigh | worker-xhigh | opus | xhigh | 22:51 | 23:16 | 0:25 [1:15] | 21,387,333 | done |
| 8b | HarnessReviewer-FableXHigh (v12; caps follow-up 00:07-00:12) | worker-xhigh | fable | xhigh | 23:18 | 00:12 | 0:17 + 0:05 [0:45] | 3,477,338 | APPROVE WITH FIXES, then APPROVE |
| 9 | ext2010h quote, guard, A3 selection, fallback list | lead | opus | xhigh | 23:36 | 00:03 | 0:27 [0:20] | lead | done; 11 roots |
| 8c | Caps, manifest, suite, commit d30f50c | lead | opus | xhigh | 00:04 | 00:30 | 0:26 [0:40] | lead | done; suite 6916 passed |
| 10 | Register E16-H1..H5 | lead | opus | xhigh | 00:30 | 00:30 | 0:01 [0:10] | lead | N 478 |
| 11 | Buy 933 chunks in 4 processes | lead | opus | xhigh | 00:30 | 01:27 | 0:56 [0:45] | lead | done; $64.038166 |
| 12 | Post-purchase checks, 11 stores, run manifest, dry check | lead | opus | xhigh | 01:27 | 01:31 | 0:04 [0:35] | lead | done |
| 13-14 | H1-H5 once each, verdict | lead | opus | xhigh | 01:31 | 01:40 | 0:09 [0:45] | lead | all five FAIL |
| 15 | VerdictVerifier-FableXHigh (H1-H5) | worker-xhigh | fable | xhigh | 01:40 | 02:03 | 0:23 [1:00] | 7,223,323 | H1-H4 VERIFIED, H5 WITH NOTES |
| 16 | Return drafts (parallel with 15), rulings, end checks, end suite, cost, progress, STAGES, final commit | lead | opus | xhigh | 01:41 | {{END_TIME}} | {{T16}} [0:45] | lead | done |
| Total | Stage E.17 | lead + 5 spawns | | | 18:34 | {{END_TIME}} | {{TOTAL_WORK}} work, break excluded [about 11:00] | {{TOTAL_TOKENS}} | C1 STOPPED; H1-H5 FAIL |
