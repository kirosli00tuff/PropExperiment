# Stage E.21 STATE (multi-day round: TSMOM-12, trend blend, turn-of-month, combined book)

Lead: Opus 5.5 xhigh, ultracode on, interactive session 13fe2d4e-086f-4929-8325-9ef707bdf0cf.
All times PDT (America/Vancouver), from `date` or file mtimes. Prompt: docs/prompts/STAGE_E.21.md.
Session start 03:04:10. Five-hour window: 4 h 00 (no new evaluation unless registered) = 07:04;
4 h 30 (checkpoint and write the return) = 07:34; end 08:04.

## Hashes in force (start)
- Harness v12: ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32 (preflight OK 03:10)
- E.14 C1 afc5c10f...; E.16 5274aa97...; E.18 5ed208a2...; E.20 H6 22e606f0...; E.20 search 94ee86b0...
  (all OK 03:10). E.14 inputs list: the known pre-existing mismatch on
  reports/stage_e2b_harness_freeze.json (identical at E.20 start and end).
- Trial registry: 6 lines, sha256 2acc993e741fc0745f50947f534d7da753368a2551fb4b705e3c3d583ce11a8d, N 528
- Spend ledger: 36402 lines, sha256 034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
- Stores: 34 of 34 match reports/stage_e17_run_manifest.json (03:10)

## N
- 528 at start. 532 after r006-E21 (04:12:12).

## Guards
- E.21 freeze: 0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e (04:11)
- Holdout: all_ok True, unlocks_logged 0 (03:10). REGISTRATION.md 0 bytes (03:10).
- No bar read before the marker (04:12:28); the evaluation reads bars from then on.

## Task status
| Step | Status | Start | End | Artifacts |
|---|---|---|---|---|
| 0 Startup checks | done: all pass | 03:10 | 03:10 | reports/stage_e21_briefs/start_checks.txt, checks.sh |
| 0 Start pytest (detached) | done: 7340 passed, 3 skipped, 3 xfailed, rc 0 (20:22) | 03:10 | 03:31 | reports/stage_e21_briefs/pytest_start.out |
| 1 Readers: SpecReaderTrend, SpecReaderTOM, SpecReaderPost2010, PropEdReader (opus high, workflow wf_18fed4b8-d89) | done: 4/4; trend T1 match, T2 HOP 10% scaling mismatch, TOM parenthetical mismatch, PropEd automation unresolved | 03:13 | 03:33 | reports/stage_e21_briefs/spec_*.md, reports/stage_e21_proped_rules.md/.json |
| 2a Lead spec (lead) | done (DRAFT; section A pending readers) | 03:13 | 03:18 | reports/stage_e21_briefs/lead_spec.md |
| 2b MultidayCoder-OpusXHigh (opus xhigh) | done: 52 tests, ruff clean, calendar counts (no bar row); 4 questions | 03:18 | 03:46 | multiday/, tests/test_multiday_*.py, reports/stage_e21_briefs/multiday_build.md, calendar_counts.* |
| 3a0 Prereg DRAFT (lead; power table; sections 5-6 pending counts and readers) | done | 03:19 | 03:20 | reports/stage_e21_prereg.md |
| 2c Literature rulings A1-A11 (lead) into lead_spec section A; coder told no code change (SendMessage) | done | 03:33 | 03:36 | reports/stage_e21_briefs/lead_spec.md section A |
| 2d Lead rulings Q1 (S_M window = later of windows/R-S4/R-S3), Q2 (T3 sigma in eligibility), Q3-Q4 accepted; A12 T3 NYSE day numbering (from counts: futures calendar books US holidays as trade dates) | done | 03:47 | 03:49 | lead_spec section A (A12) |
| 2e MultidayCoder fixes Q1, Q2, A12 (SendMessage) | done: 57 tests, ruff clean, counts re-run (T3 NQ 154/164, RTY 73/80) | 03:48 | 03:51 | multiday/, tests, calendar_counts.* |
| 3b FreezeReviewer-FableXHigh (fable xhigh) | done: APPROVE WITH FIXES (0 BLOCKING, 2 SHOULD FIX, 6 NOTE) | 03:51 | 04:02 | reports/stage_e21_review_freeze.md |
| 3c Lead rulings FR-1..FR-8 (lead_spec section B; prereg FR-3/5/7 text) | done | 04:02 | 04:03 | reports/stage_e21_briefs/lead_spec.md B, reports/stage_e21_prereg.md |
| 3d MultidayCoder fixes FR-1, FR-2, FR-6, FR-7 (SendMessage) | done: 61 tests (lead rerun 04:07: 61 passed), ruff clean | 04:03 | 04:07 | multiday/, tests |
| 3e FreezeReviewer recheck (SendMessage) | done: APPROVE; FR-9 NOTE (backstop on an era-None mark) accepted as hardening | 04:07 | 04:10 | reports/stage_e21_review_freeze.md (Recheck) |
| 3f MultidayCoder FR-9 hardening (SendMessage); lead: section B, FROZEN status lines | done: 62 tests (lead rerun 04:11), ruff clean | 04:10 | 04:11 | multiday/book.py, tests |
| 3g Freeze manifest built and verified | done: reports/stage_e21_freeze.json sha256 0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e (66 files, 18 inputs) | 04:11 | 04:11 | reports/stage_e21_freeze.json |
| 3h Commit 'E.21 freeze' | done: 839efc9 at 04:12:01 (git) | 04:12 | 04:12 | git |
| 4a Register E21 | done: r006-E21, ids E21-T1..T4, N 528 -> 532, time_local 2026-10-14T04:12:12-07:00, freeze 0bb899e5..., harness ece91ae8... (registry line 7) | 04:12 | 04:12 | ledger/trial_registrations.jsonl |
| 4b Evaluate once (detached, nice 10, /usr/bin/time -v) | done rc 0: ALL FAIL. T1 Sharpe 0.498 CI [-0.06,1.05] t 1.78 p 0.042; T2 0.436 [-0.11,0.98] t 1.56 p 0.064; T3 0.146 [-0.40,0.71] t 0.53 p 0.30; T4 0.117 [-0.37,0.60] t 0.43 p 0.34; Holm rejects none; 2:11 wall, 1.47 GB peak | 04:12 | 04:14 | reports/stage_e21_runs/, reports/stage_e21_RUN_ONCE.json, briefs/evaluate.log |
| 5 VerdictVerifier-FableXHigh (fable xhigh) | done: VERIFIED WITH NOTES (0 BLOCKING, 0 SHOULD FIX, 5 NOTE); 152 numbers MATCH; VV-1 lookback missing bars = weekend double roll instants (store metadata) | 04:15 | 04:35 | reports/stage_e21_review_verdict.md |
| 4c EconWorker-OpusHigh F8 (opus high) | done: K_min T1 $415K-$691K (LE binds), T2 $323K-$538K, T3 $34K-$57K; PropEd T1/T2 breach 46-100% (One Plan 24-57%); T4 vol dominated by 3 H5-scaling spikes | 04:15 | 04:20 | reports/stage_e21_economics.md/.json |
| 6a End pytest (detached) | done: 7402 passed, 3 skipped, 3 xfailed, rc 0 (20:33) | 04:15 | 04:35 | reports/stage_e21_briefs/pytest_end.out |
| 6b End checks | done: all pass; holdout 0 unlocks; N 532; ledger unchanged; E.21 freeze verifies | 04:35 | 04:36 | reports/stage_e21_briefs/end_checks.txt |
| 6c Return, progress.md, STAGES.md, cost, final commit | running | 04:36 | | reports/E.21_RETURN.md |


## Next step
Stage complete after the final commit 'Stage E.21 multi-day round'. Nothing running (checked 04:40: no evaluate, pytest or worker process). No push.
