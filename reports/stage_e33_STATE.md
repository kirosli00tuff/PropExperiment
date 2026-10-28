# Stage E.33 STATE (lead checkpoint file; resume from here)

Prompt: docs/prompts/STAGE_E.33.md. Protocol: reports/stage_e32_discovery_protocol.md FROZEN v1.0
sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05 (verified 14:35 PDT).
Lead session 86e80bc3-d62a-42e1-b5fd-5c881ccf8b54 (Opus 5.5 xhigh, Ultracode on). Times PDT (America/Vancouver).
Deadlines (prompt): search cut 07:00 PDT 2026-10-28 (whole sets), work stops 08:00, return by 08:45, nothing runs
after 09:00. Planner notes (user message at launch): E.32 P9 window 2017-05-22; D1 pending: NO C1 registration
before 2026-10-27 18:00 PDT unless the planner confirms D1 earlier (if the user drops the added DSR, a hashed
protocol amendment arrives before C1); Fable low: on a failed Fable call or a transcript showing another model, use
Opus 5.5 xhigh in a fresh context and say so; never Sonnet; never sacrifice a check for usage.

Shared spec for coders: reports/stage_e33_briefs/INTERFACE.md. Briefs: reports/stage_e33_briefs/briefs/.

## Task status

| # | Task | Owner | Status | Start | End | Artifacts |
|---|---|---|---|---|---|---|
| A1a | Start checks (git, holdout, soy seal, REGISTRATION 0 B, harness v14, ledger, N 538, protocol sha) | lead | done | 14:35 | 14:36 | reports/stage_e33_briefs/checks_start.txt |
| A1b | Discovery hashes 156/156 (verify_discovery_hashes.py sha c329f443...), manifests 09396842... x4 | lead | done | 14:35:54 | 14:36:23 | reports/stage_e33_briefs/verify_discovery_hashes.out, manifest_hashes.txt |
| A1c | Guard dry check (test-window file refused) | lead | done: 4 of 4 refused, rc 0 | 15:06:47 | 15:06:48 | reports/stage_e33_briefs/guard_dry_check_start.txt |
| A2 | No Databento call (standing) | all | in force | | | |
| B0 | Interface spec, STATE, briefs, estimate table | lead | done | 14:37 | 14:47 | INTERFACE.md |
| B1-data | guard33, data33, cal33, ZS/ZL re-split, ZM split check, G6 clock report | DataCoder-OpusXHigh | done (80 tests; G6 0 of 39 months flagged) | 14:47 | 15:08 | pipeline/guard33.py data33.py cal33.py split33.py check33.py g6_33.py; work/G6_clock_report.md; work/DataCoder_readings.md (21 readings) |
| B1-feat | feat33 + builder (Coder-A features) | FeatureCoder-OpusXHigh | done (56 tests; 20 B3 dates, code c22b0a50f4cd; probe 7.6/10.9/12.0 s per date pass 1, full build about 31 min at 3 procs) | 14:47 (cut 15:27, resumed 02:02) | 02:20 | pipeline/feat33.py build_features33.py; work/probe_features.md; work/FeatureCoder_readings.md (FA-1 junction = B-OPEN-1) |
| B1-lab | lab33 + builder (Coder-A labels, weights, sim fields) | LabelCoder-OpusXHigh | done (39 tests; 3-date probe) | 14:47 | 15:06 | pipeline/lab33.py, build_labels33.py, work/probe_labels.md, work/LabelCoder_readings.md |
| B2-feat | implB features (Coder-B) | FeatureCoder2-OpusXHigh | done (50 tests; 20 B3 dates, code 345ba20d4f97) | 14:47 (cut 15:27, resumed 02:02) | 02:15 | implB/featB.py dayB.py replayB.py calB.py build_featB.py; implB/FeatureCoder2_readings.md (B-OPEN-1 junction) |
| B2-lab | implB labels (Coder-B) | LabelCoder2-OpusXHigh | done (33 tests; 120 tables on 20 dates) | 14:47 | 15:11 | implB/labB*.py, derived/e33/implB/labels (efdde5c74ee1), implB/LabelCoder2_readings.md (LB-1..19) |
| B1-search | search33 (P5, P6.1, P3.5, P3.8, P6.2) | SearchCoder-OpusXHigh | done 15:19 (33 tests); follow-up mid_move hit rate done 02:04 (35 tests) | 14:47 | 15:19 | pipeline/search33.py run_search33.py tests/test_search33.py; work/SearchCoder_readings.md (S1-S20) |
| B5-code | select33 (P8), synth33, run_proofs33 | ProofCoder-OpusXHigh | done (50 tests; plant F3_4 beta 0.367, oracle F15 0.3498 se 0.0048) | 15:07 (cut 15:27, resumed 02:02) | 02:19 | pipeline/select33.py synth33.py run_proofs33.py; work/ProofCoder_calibration.json; work/ProofCoder_readings.md; derived/e33/proofs/seed9000 |
| B5iii+B6 | published-example reproductions; cost33 | StatsCostCoder-OpusXHigh | done (52 tests; DSR 0.9004 and BH exact; PBO 12,870 vs printed 12,780 misprint; AFML from secondary sources) | 15:08 (cut 15:27, resumed 02:02) | 02:03 | pipeline/cost33.py tests/test_cost33.py tests/test_stats_repro33.py; work/StatsCostCoder_readings.md; pages/LOG.md |
| B3+B4 | agreement harness, LT1-LT7, record-level synthetic streams | TestCoder-OpusXHigh | running from 15:16 | 15:16 | | |
| B5-run | 40 proof searches (4,800 fits) | lead-run job (setsid nohup, nice 10, 8 procs, lgbm 4 thr) | RUNNING from 02:36; seed order 1,101,2,102,...,20,120; expected 9-13 h, so partial at the 07:50 stop | 02:36 | | work/logs/proofs_run.log; derived/e33/proofs/seed<s>; work/B5_proofs.md (summary) |
| B7 | PipelineReviewer, MathReviewer (fable xhigh, model confirmed) | reviewers | after B3-B6 | | | |
| B7-freeze | protocol readings file, pipeline freeze sha256 list | lead | | | | |
| C1 | registration of 300 (not before 18:00 PDT) | lead | | | | |
| C2 | feature store, labels, 1,800 fits | lead-run jobs | | | | |
| D1-D3 | selection, robustness, distribution | StatsCoder-OpusXHigh | | | | |
| D4 | VerifyWorker (opus xhigh fresh) | | | | | |
| D5 | StatsReviewer (fable xhigh confirmed) | | | | | |
| E | finalists or clean negative; return | lead | | | | |

## Decisions and readings log (lead)
- 14:45 Coders run as Agent-tool workers (resumable with SendMessage for small fix briefs after B3/B7); fan-out
  reviews and verifications run as workflows.
- 14:45 B3 dates rule: OOF = the 796 dates sorted; idx = numpy.random.default_rng(20261028).choice(796, 20,
  replace=False); dates = sorted(OOF[idx]); excluded dates may be drawn (counted).
- 14:45 Thread cap across heavy jobs: at most 2 heavy jobs, total threads <= 10 (half the cores), each job <= 8.

## Pauses
- USAGE LIMIT 2 (5-hour limit, HTTP 429 on PipelineReviewer, TestCoder, FeatureCoder, FeatureCoder2 and the lead): about 03:15 to 07:01 PDT 10-28 (3 h 46 min). Not work. The detached proof job kept running.
- USAGE LIMIT 1 (weekly limit, HTTP 429 on all 6 workers): about 15:27 PDT 10-27 to 02:01 PDT 10-28 (10 h 34 min). Not work.
- 14:52 Protocol readings DRAFT opened: reports/stage_e33_protocol_readings.md (R-L1 probe on synthetic seed9000 table;
  R-L2 label values only in equality checks before C1; R-L3 proof rerun keyed to executed-code hashes; R-L4 planted
  pass = per-seed Tier A non-empty >= 14/20; R-L5 B3 dates rule; R-L6 P9 window).
- 14:55 C1 freeze builder written and dry-checked (300 ids valid): reports/stage_e33_briefs/work/lead/c1_freeze.py.
- 14:55 Wave-2 briefs on disk: brief_ProofCoder.md, brief_StatsCostCoder.md, brief_TestCoder.md.
- 15:06 DataCoder milestones 1-4 done (guard33 44 tests; data33; ZS/ZL split 14:57-14:59, 816/816 each, = raw on 3
  dates; cal33: P1.4 excluded 52 of 816 (49 OOF); 54 segments; release counts asserted exactly; limits None 0).
- 15:06 LabelCoder finding: 2021-07-01 rule 5 removes every minute (ZMZ1 at 385.6/385.7 above the 08:30 definition's
  HL 384.9; band 384.9/324.9 unchanged 06-30..07-02: limits in the definitions may lag a limit move). P3.6 as written;
  count the affected dates as a data finding (no outcome involved).
- 15:12 LabelCoder2 finding LB-15: Z4 limit fields change only on Sundays, so rule 5 measures the 2% distance to a band
  up to 5 days old (removed all F05 minutes on 2021-07-09, 142 on 2022-06-03, 82 on 2021-04-01). Protocol as written;
  data finding + user decision (also binds the test stage, which runs the frozen pipeline).
- 15:20 Label table gains `mid_move` (P6.2 reported-only hit rate); LabelCoder and SearchCoder resumed for it; INTERFACE.md 4.2 updated.
- 15:21 SearchReviewer-OpusXHigh (pre-proof review, opus xhigh fresh; extra to B7) briefed: briefs/brief_SearchReviewer.md; spawns when the worker count is below 6.
- 02:01 (10-28) RESUME after the weekly reset. Holdout unlocks_logged 0 (all six stores). No E.33 process alive.
  Plan: resume the 6 cut workers by SendMessage (FeatureCoder, FeatureCoder2, ProofCoder, StatsCostCoder, SearchCoder
  follow-up, TestCoder); then SearchReviewer; B3, B4, B5 proofs, B6, B7, freeze. C1 only if the FULL 300 can still
  finish by the 07:00 search cut (it cannot be expected: about 6 h remain to the 08:00 stop); otherwise no
  registration (N stays 538) and Parts C-E are reported as not run, with a continuation decision for the user.
- 02:03 SearchReviewer-OpusXHigh spawned (pre-proof review of search33).
- 02:16 ProofCoder timing (full-size test seed 9101, 8 procs): 13-20 min per seed -> 40 proof searches about 9-13 h at
  the P5 thread cap of 8. They cannot finish before the 08:00 stop. Plan: launch the production proofs (detached,
  resumable, interleaved seed order 1,101,2,102,...) right after the SearchReviewer verdict; stop them by 07:50; report
  the seeds done as an interim with no pass/fail; the rest finish under the same executed-code hashes in a continuation
  stage. B7 reviews run this session on everything except the proof outcomes. No C1 in this session.
- 02:18 SearchReview: 0 BLOCKING, 4 SHOULD FIX (SF1 code hash in DONE markers; SF2 infra errors not failed fits; SF3 collateral kills; SF4 load-phase kills), 10 NOTE; SearchCoder fixing SF1-SF4 before the proofs. ProofReviewer-FableXHigh (select33/synth33/run_proofs33) and MathReviewer-FableXHigh (B7) spawned; models to be confirmed from transcripts.
- 02:18 Model check from transcripts (message.model): ProofReviewer-FableXHigh claude-fable-5-1 (11 msgs), MathReviewer-FableXHigh claude-fable-5-1 (12 msgs). No fallback needed.
- 02:32 SearchCoder SF1-SF4 fixed 02:24 (45 tests; search33 a7d30b2a..., run_search33 d44fb7c1..., marker code hash 323a82ff...). ProofReview (Fable confirmed) 02:32: 0 BLOCKING, 2 SHOULD FIX (summary must show failed configs; manifest must pin uv.lock and library versions), 11 NOTE; agrees Q3 'continue'. ProofCoder fixing both before launch.
- 02:36 Production proofs launched after ProofCoder SF1-SF2 fixes (52 tests; run_proofs33 4a0f4e98..., select33 9b992806..., synth33 5a5ed5b9...). Q9 accepted (report-only 'best' = top traded configuration). Stop rule this session: kill the proof job by 07:50 (resumable from DONE markers under the same pinned code and versions).
- 02:44 B3 full_r1: labels 0 mismatches (all 6 labels, 20 dates), sigma 0; features 35,473 cells in 34 columns explained by FD1-FD5. MathReview (Fable confirmed): 16/16 features and 12/12 labels agree with both A and B; B5 arithmetic reproduced; 0 BLOCKING, 1 SHOULD FIX (= FD3). Rulings R-B3-* written to the readings draft; fixes sent: FeatureCoder (FD1, FD2, FD3a, FD4, FD5, D1), FeatureCoder2 (FD3a-c), LabelCoder (D1, D2).
- 02:48 LabelCoder D1/D2 applied: lab33 ff0181fc391c (42 tests); 20-date labels identical to 17934b7b23b1 in every column; TestCoder told to update 2 tests that asserted the old behaviour and to rerun B3 when both feature rebuilds land.
- 03:08 PipelineReviewer-FableXHigh spawned 03:09 (B7 first bullet). Proofs at 03:08: 286 folds in 32 min (about 13.4 min per seed; about 23 of 40 seeds by 07:50); seeds 1 and 101 done. TestCoder asked to run LT7 on the seed-1 fold models.
- 03:09 Model check (transcript message.model): PipelineReviewer-FableXHigh claude-fable-5-1 (19 msgs).
- 07:01 RESUME. Holdout unlocks 0 (6 stores). Proof job alive (32 seed folders). Wrap-up briefs to TestCoder, PipelineReviewer, FeatureCoder, FeatureCoder2 (hard stop 07:38). Plan: stop proofs about 07:50; end checks; pytest; cost; return; commit. No freeze, no C1 (N stays 538).
- 07:05 FeatureCoder final: feat33 code 6873427a6150 (65 tests), B3-fix rebuild of the 20 dates done 03:28 (21c501f2e3e2 = dead partial build). FeatureCoder2 final: fb69badd4bb9 (56 tests), rebuild done 03:28. TestCoder rerunning B3 on these by 07:38.
- 07:05 Proofs interim (B5_proofs.md, 06:55): 30 of 40 seeds done. Null 15/15 Tier A empty, 0 failed, best SR_d -0.0757..0.0602; centred null SR SD 0.0420 vs 0.0354. Planted 15/15 Tier A non-empty, 0 failed: pass count 15 >= 14 (planted proof passes whatever the last 5 seeds give); T30 configurations entered Tier A in 0 planted seeds. About 8.6 min per seed. Stop watcher armed: first seed boundary after 07:40, hard stop 07:56 (logs/proofs_stop.log).
- 07:06 TestCoder final: B3 full_r2 labels 0, sigma 0, features 57/59 (FD6 F3_11 5,385 cells; FD7 F3_9 10 cells) -> rulings for the continuation; B4 LT2-LT6 pass, synthetic streams 59/59; LT1 timing probe only; LT7 50/50 decisions, 11/11 fills on 3 draws (superseded build). PipelineReview provisional NOT YET (0/3/10).
- 07:45 Proof job stopped 07:44:02 at the seed-boundary after seed 118 (36/40 seeds: null 18/18 empty, planted 18/18 non-empty, 0 failed). End checks 07:44 pass (N 538, ledger unchanged, holdout 0, guard 4/4). Full pytest started 07:45 in background.

## FINAL STATUS (07:47 PDT 10-28; for the continuation stage E.33b, resume from here)
- DONE: A (all gates); B1 (pipeline A code); B2 (implementation B code); B5 (iii); B6; B7 MathReviewer; pre-proof
  SearchReview and ProofReview with fixes; B3 run full_r2 (labels and sigma exact; features 57/59).
- OPEN, in order: (1) rule B3 residuals FD6 (F3_11 mixed fill-plus-cancel record; feat33.py 493-513 vs replayB.py
  140-154) and FD7 (F3_9 fill naming an order not yet in the book, 2022-09-01), fix, rerun B3 to 59/59; (2) LT1 (200
  draws) and LT7 at scale (tests_b4/run_lt1_lt7.py, about 50 min) on the final feature build; (3) the last proof seeds
  19, 119, 20, 120: `uv run python reports/stage_e33_briefs/work/pipeline/run_proofs33.py --seeds
  1,101,...,20,120 --max-procs 8 --lgbm-threads 4` resumes from the DONE markers and refuses if any pinned code or
  library differs (seed 19's started folds carry one interruption each); (4) PipelineReviewer: finish its scope and its
  SF1-SF3 (readings file final; freeze list incl. screening/, funnel/, p7_final.py, E.31 modules; F3_11), verdict GO;
  (5) readings file final and hashed; freeze list (sha256 of every code file, configs, uv.lock); (6) the P5 probe on the
  seed9000 table and the projection in this file; (7) C1 with reports/stage_e33_briefs/work/lead/c1_freeze.py (N 538 ->
  838), run marker; (8) feature store (816 dates, about 31 min at 3 processes), labels, the 1,800 fits; D1-D5; E.
- No registration was made; N 538. No real outcome was computed.
- Agent handles for SendMessage are in the scratchpad agents.tsv of session 86e80bc3 (lost on reboot; a new session
  starts fresh workers from the briefs under reports/stage_e33_briefs/briefs/).
