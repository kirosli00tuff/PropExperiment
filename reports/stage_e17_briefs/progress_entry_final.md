
## 2026-10-09/10 — Stage E.17: C1 STOPPED at C10; the base-rule batch H1-H5 run once, all five FAIL ($121.86 spent)

Prompt docs/prompts/STAGE_E.17.md (V24-V30; V30 amended to a $124.00 budget). Lead Opus 5.5 xhigh, sessions 0dcecb5d
and c71b1fb9 (usage logged under 0dcecb5d). Return: reports/E.17_RETURN.md.

- **C1 (backward NG replication): STOPPED.**
  - Registered (N 471 -> 473), bought (642 chunks, $57.817332) and evaluated once under harness v11 (ba1ce996...).
  - The run stopped at guard C10: g17_mbt, live on 87/84 NG rows in E.12, is n/a by design in 2010-2019 (MBT did not
    exist), and the freeze has no exemption. That contradiction was decidable from frozen files before registration.
  - Fable verified the stop. Nothing was learned about the NG hypothesis; not rerun.
- **Base-rule batch E16-H1..H5: all five FAIL** (base case, Holm 0.05, N 478).
  - H1 mean -0.161 risk units, t -20.0. H2 +0.344, p 0.068, n 56. H3 -0.015, p 0.60. H4 -0.048, t -6.7. H5 -0.149,
    p 0.93.
  - DSR about 0; the stress and 1.5 x slippage cases are worse. Fable verified every verdict number (H5 with a note on
    its sparse-component sigma).
  - H1's gross momentum is positive but about a quarter of D8 cost.
  - No holdout-2 read and no meta-labeling (V28).
- **Purchase:** harness v12 (ece91ae8...) added plan ext2010h. The A3 selection (ZT ZF ZB CL ZL ZS UB TN RTY LE HE,
  933 chunks) cost $64.038166. Ten roots ran on the fallback window: YM HG 6S 6J 6A 6B 6N ZM ZW 6C.
- **Funds:** $121.855498 billed in the stage; acct-2 is about $3.14 short of the user's $125 figure.
- **Guardrails:** holdouts all_ok with 0 unlocks; REGISTRATION.md 0 bytes; every quote guarded by the run's own ledger
  lines. Commits a21d82d (v11), 558a7ce (C1), d30f50c (v12) and the final one. Suites: start 6815, v11 6815, v12 6916,
  end 6916.
- **Incident:** the first Claude session ended mid-buy (19:38); the buy resumed with the same command, leaving one
  $0.075 orphan commit. Long jobs then ran detached.

### Session cost

Wall clock 18:34 (2026-10-09) to 02:22 (2026-10-10) PDT. One break, not counted as work: the first Claude
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
| 16 | Return drafts (parallel with 15), rulings, end checks, end suite, cost, progress, STAGES, final commit | lead | opus | xhigh | 01:41 | 02:22 | 0:41 [0:45] | lead | done |
| Total | Stage E.17 | lead + 5 spawns | | | 18:34 | 02:22 | 7:44 work, break excluded [about 11:00] | 163,370,316 | C1 STOPPED; H1-H5 FAIL |

### Tokens per model (session 0dcecb5d's transcript and its 5 subagent transcripts, 2026-10-10 01:30Z on; reports/stage_e10_briefs/cost.py)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,022 | 288,913 | 15,329,973 | 1,117,016 | 16,738,924 |
| claude-opus-5-5 | 876 | 438,993 | 144,885,165 | 1,306,358 | 146,631,392 |
| all | 3,898 | 727,906 | 160,215,138 | 2,423,374 | 163,370,316 |

Delegation share: lead 125,244,059 (76.7%), workers 38,126,257 (23.3%); by model claude-fable-5-1 16,738,924 (10.2%), claude-opus-5-5 146,631,392 (89.8%).

Per transcript (model, messages, first and last UTC, input, output, cache read, cache creation, total):

    lead claude-opus-5-5 msgs=314 first=2026-10-10T01:34:08.287Z last=2026-10-10T09:21:23.106Z in=666 out=313985 cread=123945574 ccreate=983834 total=125244059
    agent-a092f29e8ebc7951d claude-fable-5-1 msgs=12 first=2026-10-10T02:10:49.954Z last=2026-10-10T02:26:19.186Z in=354 out=44850 cread=1334816 ccreate=168922 total=1548942
    agent-a3f9947473bd4761c claude-fable-5-1 msgs=34 first=2026-10-10T08:40:22.699Z last=2026-10-10T09:03:41.201Z in=1028 out=95212 cread=6838850 ccreate=288233 total=7223323
    agent-a463ba71418f7066b claude-opus-5-5 msgs=105 first=2026-10-10T05:51:32.236Z last=2026-10-10T06:16:19.631Z in=210 out=125008 cread=20939591 ccreate=322524 total=21387333
    agent-a6de7832a8ed6d053 claude-fable-5-1 msgs=34 first=2026-10-10T05:51:29.920Z last=2026-10-10T06:08:27.369Z in=1058 out=61010 cread=4230286 ccreate=196967 total=4489321
    agent-ab2dedb725a4e6538 claude-fable-5-1 msgs=21 first=2026-10-10T06:18:06.225Z last=2026-10-10T07:12:06.529Z in=582 out=87841 cread=2926021 ccreate=462894 total=3477338

These are token counts from the transcripts, not plan-credit percentages; the session cannot read the /usage meter.
