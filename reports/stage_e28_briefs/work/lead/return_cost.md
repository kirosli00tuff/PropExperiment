=== COST ===
Tokens are from the transcripts, per message at its final usage, by reports/stage_e26_briefs/cost.py (the copy
that also globs workflow agents); never estimated. Session 1: transcript bc87cf0f, window 2026-10-21 01:00-24:00 PDT,
output reports/stage_e28_briefs/cost/cost_session1.txt. Session 2: transcript c4961140 through 22:02 PDT
(cost_session2.txt); the few calls after that (the commit and the closing reply) are not counted.

Wall clock. Session 1: 02:06-16:43 = 14 h 37 min, with usage-limit pauses 03:10-05:10, 06:19-10:10 and 11:10-15:10
(9 h 51 min, not work): work about 4 h 46 min. Session 2: 16:51-22:02; work 16:51-17:25 (34 min) and 21:54-22:02;
the wait for the key (17:25-20:30, a name-only poll, no work), the idle 20:30-20:42 and the reboot outage
20:42-21:54 are not work.

Session 1:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 7,628 | 3,552,572 | 699,284,400 | 12,697,818 | 715,542,418 |
| claude-fable-5-1 | 7,418 | 999,352 | 41,026,571 | 3,221,371 | 45,254,712 |
| claude-sonnet-5-5 | 222 | 112,074 | 9,249,346 | 1,418,328 | 10,779,970 |
| all | 15,268 | 4,663,998 | 749,560,317 | 17,337,517 | 771,577,100 |

Session 2:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 578 | 280,726 | 49,104,369 | 1,317,906 | 50,703,579 |
| all | 578 | 280,726 | 49,104,369 | 1,317,906 | 50,703,579 |

Both sessions:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 8,206 | 3,833,298 | 748,388,769 | 14,015,724 | 766,245,997 |
| claude-fable-5-1 | 7,418 | 999,352 | 41,026,571 | 3,221,371 | 45,254,712 |
| claude-sonnet-5-5 | 222 | 112,074 | 9,249,346 | 1,418,328 | 10,779,970 |
| all | 15,846 | 4,944,724 | 798,664,686 | 18,655,423 | 822,280,679 |

Lead versus workers: lead 99,313,743 (session 1 83,468,827, session 2 15,844,916), 12.1%; workers
722,966,936 (62 spawns: 60 in session 1, 2 in session 2), 87.9%. By tier: Opus 93.2%, Fable
5.5%, Sonnet 1.3%. Cache reads are 97.1% of all tokens.

Per worker spawn, session 2 (cost/per_agent_session2.md):

@@INCLUDE reports/stage_e28_briefs/cost/per_agent_session2.md@@

PilotFixer's and DeltaReviewer's spans include the idle time between their two rounds (17:05-17:14, 17:14-17:20).

Per worker spawn, session 1 (cost/per_agent_session1.md; times PDT; re-runs after usage-limit cuts are separate rows):

@@INCLUDE reports/stage_e28_briefs/cost/per_agent_session1.md@@

### Final ETA table (actuals)

No initial estimate table was found in either session's transcript (searched the lead's replies for an ETA table),
so the actuals stand without one. Worker tokens are in the per-spawn tables above; "lead" rows are in the lead totals.

| # | Task | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|---|---:|---|
| A0 | Start checks | lead | opus | xhigh | 02:07 | 02:13 | 6 min | lead | done |
| A1 | Ranking spec hashed | lead | opus | xhigh | 02:14 | 02:14 | 1 min | lead | done, before any lookup |
| A2 | Readers: C1, C2 x11, A0, A1 x8, A2 x6; brief v1 | 27 workers, lead | opus | high | 02:20 | 05:19 | spans pause 1 | see table | done; cut agents re-run |
| P1 | **usage-limit pause** | | | | 03:10 | 05:10 | 2 h 00 min | | excluded |
| A3 | MathReviewer G1-G6; BriefFixers | 6 Fable + 6 Sonnet | fable, sonnet | xhigh, high | 06:05 | 11:11 | spans pause 2 | see table | done; G1, G4, G6 files reused after cuts |
| P2 | **usage-limit pause** | | | | 06:19 | 10:10 | 3 h 51 min | | excluded |
| A4 | Fact table, blind scorer, economics | FactTable, BlindScorer, EconCoder | opus | high, xhigh | 10:12 | 16:08 | spans pause 3 | see table | done; EconCoder resumed |
| P3 | **usage-limit pause** | | | | 11:10 | 15:10 | 4 h 00 min | | excluded |
| A5 | Rulings v1; Part C final | lead | opus | xhigh | 15:13 | 15:16 | 3 min | lead | done |
| A6 | B1/B2 drafts; pilot code | lead; PilotCoder-OpusXHigh | opus | xhigh | 15:15 | 16:00 | 45 min | see table | done |
| A7 | Ranking v1; spec for QG; two Fable reviews | lead; RankingReviewer, SpecReviewer | opus, fable | xhigh | 16:05 | 16:35 | 30 min | see table | done; RR-01 moved the top pair |
| A8 | Spec fixes; rulings v2; ranking v2; spec for QM | lead; ScoreApplierV2 | opus, sonnet | xhigh, high | 16:34 | 16:41 | 7 min | see table | done; session cut 16:43 |
| B0 | E.28b startup, start checks | lead | opus | high | 16:51 | 16:54 | 3 min | lead | done; key absent |
| B1 | S1 code fixes for QM | PilotFixer-OpusXHigh | opus | xhigh | 16:54 | 17:05 | 11 min | 23,722,826 (both rounds) | done; 168 pass |
| B2 | S2 delta review | DeltaReviewer-OpusXHigh | opus | xhigh | 17:06 | 17:14 | 8 min | 11,135,837 (both rounds) | NO GO (RD-01, RD-02) |
| B3 | RD-01..03 fixes | PilotFixer-OpusXHigh | opus | xhigh | 17:14 | 17:20 | 6 min | (in B1) | done; 204 pass |
| B4 | Re-check | DeltaReviewer-OpusXHigh | opus | xhigh | 17:20 | 17:22 | 2 min | (in B2) | GO |
| B5 | Ranking file; return drafts; session-1 cost | lead | opus | high | 17:15 | 17:25 | 10 min | lead | done |
| P4 | **wait for the key (name-only poll)** | | | | 17:25 | 20:30 | 3 h 05 min | | excluded; key never appeared |
| P5 | **idle, then reboot outage** | | | | 20:30 | 21:54 | 1 h 24 min | | excluded; reboot 20:42 |
| B6 | S3: not run | | | | 20:30 | 20:30 | 0 | | key absent at the deadline |
| B7 | S5: V47 read; return; progress; STAGES; end checks; cost | lead | opus | high | 21:54 | 22:02 | see below | lead | done |
| | **Cumulative** | | | | 02:06 | 22:02 | work: session 1 about 4 h 46 min, session 2 34 min + 21:54-22:02 | **822,280,679** (lead 99,313,743; workers 722,966,936) | no initial estimate on disk |
=== COST_PROGRESS ===
### Session cost

Tokens are from the transcripts, per message at its final usage, by reports/stage_e26_briefs/cost.py (the copy
that also globs workflow agents); never estimated. Session 1: transcript bc87cf0f, window 2026-10-21 01:00-24:00 PDT,
output reports/stage_e28_briefs/cost/cost_session1.txt. Session 2: transcript c4961140 through 22:02 PDT
(cost_session2.txt); the few calls after that (the commit and the closing reply) are not counted.

Wall clock. Session 1: 02:06-16:43 = 14 h 37 min, with usage-limit pauses 03:10-05:10, 06:19-10:10 and 11:10-15:10
(9 h 51 min, not work): work about 4 h 46 min. Session 2: 16:51-22:02; work 16:51-17:25 (34 min) and 21:54-22:02;
the wait for the key (17:25-20:30, a name-only poll, no work), the idle 20:30-20:42 and the reboot outage
20:42-21:54 are not work.

Session 1:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 7,628 | 3,552,572 | 699,284,400 | 12,697,818 | 715,542,418 |
| claude-fable-5-1 | 7,418 | 999,352 | 41,026,571 | 3,221,371 | 45,254,712 |
| claude-sonnet-5-5 | 222 | 112,074 | 9,249,346 | 1,418,328 | 10,779,970 |
| all | 15,268 | 4,663,998 | 749,560,317 | 17,337,517 | 771,577,100 |

Session 2:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 578 | 280,726 | 49,104,369 | 1,317,906 | 50,703,579 |
| all | 578 | 280,726 | 49,104,369 | 1,317,906 | 50,703,579 |

Both sessions:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---:|---:|---:|---:|---:|
| claude-opus-5-5 | 8,206 | 3,833,298 | 748,388,769 | 14,015,724 | 766,245,997 |
| claude-fable-5-1 | 7,418 | 999,352 | 41,026,571 | 3,221,371 | 45,254,712 |
| claude-sonnet-5-5 | 222 | 112,074 | 9,249,346 | 1,418,328 | 10,779,970 |
| all | 15,846 | 4,944,724 | 798,664,686 | 18,655,423 | 822,280,679 |

Lead versus workers: lead 99,313,743 (session 1 83,468,827, session 2 15,844,916), 12.1%; workers
722,966,936 (62 spawns: 60 in session 1, 2 in session 2), 87.9%. By tier: Opus 93.2%, Fable
5.5%, Sonnet 1.3%. Cache reads are 97.1% of all tokens.

Per worker spawn, session 2 (cost/per_agent_session2.md):

@@INCLUDE reports/stage_e28_briefs/cost/per_agent_session2.md@@

PilotFixer's and DeltaReviewer's spans include the idle time between their two rounds (17:05-17:14, 17:14-17:20).

Per worker spawn, session 1 (cost/per_agent_session1.md; times PDT; re-runs after usage-limit cuts are separate rows):

@@INCLUDE reports/stage_e28_briefs/cost/per_agent_session1.md@@

### Final ETA table (actuals)

No initial estimate table was found in either session's transcript (searched the lead's replies for an ETA table),
so the actuals stand without one. Worker tokens are in the per-spawn tables above; "lead" rows are in the lead totals.

| # | Task | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|---|---:|---|
| A0 | Start checks | lead | opus | xhigh | 02:07 | 02:13 | 6 min | lead | done |
| A1 | Ranking spec hashed | lead | opus | xhigh | 02:14 | 02:14 | 1 min | lead | done, before any lookup |
| A2 | Readers: C1, C2 x11, A0, A1 x8, A2 x6; brief v1 | 27 workers, lead | opus | high | 02:20 | 05:19 | spans pause 1 | see table | done; cut agents re-run |
| P1 | **usage-limit pause** | | | | 03:10 | 05:10 | 2 h 00 min | | excluded |
| A3 | MathReviewer G1-G6; BriefFixers | 6 Fable + 6 Sonnet | fable, sonnet | xhigh, high | 06:05 | 11:11 | spans pause 2 | see table | done; G1, G4, G6 files reused after cuts |
| P2 | **usage-limit pause** | | | | 06:19 | 10:10 | 3 h 51 min | | excluded |
| A4 | Fact table, blind scorer, economics | FactTable, BlindScorer, EconCoder | opus | high, xhigh | 10:12 | 16:08 | spans pause 3 | see table | done; EconCoder resumed |
| P3 | **usage-limit pause** | | | | 11:10 | 15:10 | 4 h 00 min | | excluded |
| A5 | Rulings v1; Part C final | lead | opus | xhigh | 15:13 | 15:16 | 3 min | lead | done |
| A6 | B1/B2 drafts; pilot code | lead; PilotCoder-OpusXHigh | opus | xhigh | 15:15 | 16:00 | 45 min | see table | done |
| A7 | Ranking v1; spec for QG; two Fable reviews | lead; RankingReviewer, SpecReviewer | opus, fable | xhigh | 16:05 | 16:35 | 30 min | see table | done; RR-01 moved the top pair |
| A8 | Spec fixes; rulings v2; ranking v2; spec for QM | lead; ScoreApplierV2 | opus, sonnet | xhigh, high | 16:34 | 16:41 | 7 min | see table | done; session cut 16:43 |
| B0 | E.28b startup, start checks | lead | opus | high | 16:51 | 16:54 | 3 min | lead | done; key absent |
| B1 | S1 code fixes for QM | PilotFixer-OpusXHigh | opus | xhigh | 16:54 | 17:05 | 11 min | 23,722,826 (both rounds) | done; 168 pass |
| B2 | S2 delta review | DeltaReviewer-OpusXHigh | opus | xhigh | 17:06 | 17:14 | 8 min | 11,135,837 (both rounds) | NO GO (RD-01, RD-02) |
| B3 | RD-01..03 fixes | PilotFixer-OpusXHigh | opus | xhigh | 17:14 | 17:20 | 6 min | (in B1) | done; 204 pass |
| B4 | Re-check | DeltaReviewer-OpusXHigh | opus | xhigh | 17:20 | 17:22 | 2 min | (in B2) | GO |
| B5 | Ranking file; return drafts; session-1 cost | lead | opus | high | 17:15 | 17:25 | 10 min | lead | done |
| P4 | **wait for the key (name-only poll)** | | | | 17:25 | 20:30 | 3 h 05 min | | excluded; key never appeared |
| P5 | **idle, then reboot outage** | | | | 20:30 | 21:54 | 1 h 24 min | | excluded; reboot 20:42 |
| B6 | S3: not run | | | | 20:30 | 20:30 | 0 | | key absent at the deadline |
| B7 | S5: V47 read; return; progress; STAGES; end checks; cost | lead | opus | high | 21:54 | 22:02 | see below | lead | done |
| | **Cumulative** | | | | 02:06 | 22:02 | work: session 1 about 4 h 46 min, session 2 34 min + 21:54-22:02 | **822,280,679** (lead 99,313,743; workers 722,966,936) | no initial estimate on disk |
=== T_S5 ===
- 21:54-22:02 S5: V47 read, return section 7 rewritten to follow it, progress entry, STAGES line, end checks (22:00),
  session cost (22:02); then one commit, no push.
