# Stage E.9 STATE (K8 cross-market: code, audit, freeze, screen on the research window)

Lead: Opus 5.5 xhigh, session 20d17daf-bbde-4768-93fa-814f35cbb398. Prompt: docs/prompts/STAGE_E.9.md (commit 0d255d6).
On resume: read this file first, skip finished tasks.

## Hashes in force
- harness v6: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
- E.1 manifest 96166eb3...; E.2a ML 077a57e1...
- cluster freezes: K2 8815a775..., K4 7abcde17..., K5 1d0c974f..., K3 c4fb5da4..., K7 46cae308..., K1 cf48f514...,
  K6 a6f8b497...; K8: none yet
- release calendar reports/stage_e2b_release_calendar.json sha256 839f2437...
- ledger: 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
- acct-2: spent 124.673761, left 0.326239; step 2: MES none (owned), MGC sealed, MCL sealed, 6C MBT MNQ not_bought
- N before this stage: 194 (reports/E.8_RETURN.md)

## Task status (times PDT; 2026-10-01 22:12 onward)
- Task 0 startup: start checks 22:13:05 all pass (reports/stage_e9_briefs/start_checks.out): HEAD 9770828 (descendant of
  0d255d6, which holds docs/prompts/STAGE_E.9.md), clean tree (only the new briefs dir), holdout all_ok 0 unlocks (both),
  REGISTRATION.md 0 bytes, manifests ALL_OK, v6 preflight OK, K2 K4 K5 K3 K7 K1 K6 freezes OK, K8 none, ledger as above.
  Start suite running since 22:13 without PYTHONPYCACHEPREFIX (E.6-E.8 precedent: 3 bytecode tests fail under a prefix)
  (reports/stage_e9_briefs/pytest_start.out; expected E.8 end: 5373 passed, 2 skipped, 1 xfailed).
- Vehicles (frozen): gold MGC q_c 1; CAD 6C q_c 1 (undersized); Nasdaq-100 MNQ q_c 1. Signal legs MES, MCL, MBT.
- Start suite 22:13:16-22:26:04 (no prefix): 5373 passed, 2 skipped, 1 xfailed (= E.8 end). Task 0 done 22:26.
- Task 1b ReleaseChecker-OpusMed (worker-medium, opus) spawned 22:21; brief reports/stage_e9_briefs/1b_release_checker.md.
- Task 1 member specs: reports/stage_e9_member_specs.md sections 0-6 written 22:21-22:26 (readings K8-L-01..K8-L-17);
  section 7 (rulings after 1b) pending. strategy/members/k8/__init__.py created empty (0 bytes) 22:27.
- Coder briefs written: reports/stage_e9_briefs/2A_member_coder_A.md (tables + flight), 2B_member_coder_B.md (oilcad,
  wkndbtc). Spawn after 1b and spec section 7.
- Task 2A MemberCoder-A-OpusXHigh (worker-xhigh, opus) spawned 22:29 (tables first, then flight); section 7 corrections,
  if any, go to it by SendMessage. Prepared: reports/stage_e9_briefs/auditor_task3_K8.md, write_k8_freeze.py.
- Task 1b done 22:32 (ReleaseChecker-OpusMed, 22:21-22:32, 231k tokens): reports/stage_e9_release_check.md/.json, 48 pages.
  A: all rows keep except WPSR 2025-12-29, 2026-05-28 (E.4 drops; still in the frozen calendar). B: 54 eligible Mondays.
  C: 24/7 from 2026-05-29 16:00 CT; 51/3 Mondays. D: blackouts MGC 18, MCL 45, 6C 15, MBT 42, MNQ 15; MES unverifiable.
- Task 1 done 22:33: spec section 7 rulings R-1b-1..R-1b-6 (C6 skip set = frozen calendar unchanged; MES blackouts by the
  runner; 2026-06-01 full session; counts flight 303, oilcad 304, wkndbtc 303, Mondays 54). Coder A told by SendMessage.
- Task 2B MemberCoder-B-OpusXHigh (worker-xhigh, opus) spawned 22:33 (oilcad, wkndbtc).
- Task 2B done 23:07 (MemberCoder-B-OpusXHigh, 22:33-23:07, 348k tokens): oilcad.py, wkndbtc.py; tests/test_k8_members_oilcad.py
  (60 tests, also the shared K8 test kit), _wkndbtc.py (39); mutants 88/91 killed (3 equivalent: O43, O47, O52). Harness
  refused B's .md write; lead saved reports/stage_e9_coder_B.md from B's final message 23:08. Incident: B's heredoc made two
  empty stray files "0" and "=" in the repo root (23:06:58), deleted by B at once; lead confirmed absent 23:08.
- Task 2A done 23:08 (MemberCoder-A-OpusXHigh, 22:29-23:08, 374k tokens): _calendar.py, _releases.py (GUARD_INSTANTS MGC 312,
  6C 513, MNQ 313; no correction), gen_k8_tables.py, flight.py; tests _tables, _flight, _flight_exits, _flight_engine; mutants
  87/87 killed. Report reports/stage_e9_coder_A.md. Notes: r_k as exact integer pairs (fractions not on the allowlist);
  earlier tables differ from K8's in the confirmation window (K3 FX 14 dates 2022-23; K4, K5 keep 2024-07-03): flag for user.
- Pre-audit hashes 23:09: reports/stage_e9_briefs/k8_files_pre_audit.sha256 (13 files). Freeze dry run: 4 declarations OK;
  check_cluster_sources K8 OK; members __init__ OK.
- Gate suite 23:09:25-23:21:20: 5582 passed, 2 skipped, 1 xfailed (= 5373 + 209 K8 tests); K8 files unchanged 23:33.
- Task 3 MemberAuditor-K8-FableXHigh (worker-xhigh, fable) spawned 23:09 (Fable available). Brief auditor_task3_K8.md.
- Task 3 done 23:37 (MemberAuditor-K8-FableXHigh, 23:10-23:37, 401k tokens): reports/stage_e9_member_audit.md Part 1:
  0 BLOCKING, 0 SHOULD FIX, 8 NOTE; tables recomputed identical; 143/146 auditor mutants killed (3 equivalent).
- Task 4: rulings reports/stage_e9_member_rulings.md (23:38; R-T3-1..R-T3-8; specs K8-L-04 wording only, no code or test
  change). K8 cluster freeze written 23:39: reports/stage_e_k8_member_freeze.json, sha256
  99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7, 4 members, 7 files; verified. K8 files = pre-audit hashes.
  Task 4 suite running since 23:39 (reports/stage_e9_briefs/pytest_task4.out). Then commit "K8 member freeze"
  (message reports/stage_e9_briefs/commit_freeze_msg.txt).
- Task 4 suite 23:39:30-23:52:26: 5582 passed, 2 skipped, 1 xfailed; K8 files and freeze unchanged. Commit 558a5dc 23:52:52
  "feat: K8 member freeze (Stage E.9), cluster freeze sha256 99f5a6ce" (18 files). Task 4 done.
- Task 5 done: run 23:53:04-23:53:59 exit 0, "K8 research: 4 members, 0 refused", reports/stage_e9_k8_screen/ (9 files), log
  reports/stage_e9_briefs/t5_run.log, summary reports/stage_e9_briefs/t5_summary.out. Power not_run (StartRuleMissing).
  Tier A: K8-flight-01 HEOD MGC (55 trips, mean 10.676 ticks/day, t 1.395), K8-wkndbtc-01 MNQ (39 trips, 28.975, t 1.072).
  Tier B: K8-flight-01 H30 MGC (55, 4.270, t 0.976), K8-oilcad-01 6C (552, -4.454, t -5.907; MLL 2; fill_guard_deferral 8).
  No labels; coverage all pass (min MBT 0.9739). N = 194 + 4 = 198.
- Task 6 MemberAuditor-K8-FableXHigh resumed 23:55 for Part 2 (brief reports/stage_e9_briefs/auditor_task6_K8.md).
- Task 6 done 00:03 (MemberAuditor Part 2, 23:55-00:03, 483k tokens cumulative): items 0, 1, 2, 3, 5, 6 VERIFIED; 4 VERIFIED
  WITH NOTES (wkndbtc 2026-03-16 no trip, unexplained without prices; 5 oilcad exits one minute late, missing 6C bar by
  elimination); no DISCREPANCY. Sensitivity: HEOD t 1.085 without its largest day (0.751 without two); wkndbtc t 0.781
  without 2026-06-08 (its only post-24/7 trip). fill_guard_deferral 8 = 4 WPSR exit deferrals x 2; no entry deferral.
- PAUSE 00:04:21-00:23:26 PDT (19 min): the session exited by accident (user) and was resumed; the end suite started 23:55
  died at about 50% (kept as reports/stage_e9_briefs/pytest_end_interrupted.out). Same transcript 20d17daf continues.
- End suite re-run since 00:24 (reports/stage_e9_briefs/pytest_end.out). Task 7 in progress: descriptive figures
  reports/stage_e9_briefs/t7_descriptive.out; MES blackouts from the flight record (15 dates).
- End suite re-run 00:23:58-00:38:01: 5582 passed, 2 skipped, 1 xfailed. End checks 00:26:54 all pass (K8 freeze OK,
  ledger unchanged, holdout 0 unlocks, REGISTRATION.md 0 bytes). docs/STAGES.md line written 00:27.
- Task 7 done 00:41: reports/E.9_RETURN.md (sections 1-8), progress.md entry with Session cost, cost
  reports/stage_e9_briefs/cost.out (99,814,881 tokens at 00:38). Program N = 198.
- STAGE COMPLETE 00:41. Push of 558a5dc owed by the planning chat. Next: the ML route (V17).
