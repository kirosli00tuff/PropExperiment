# Stage E.6 STATE (K7 bitcoin: code, audit, freeze, screen on the research window)

Lead: Opus 5.5 xhigh, session 0f52aad4-207e-43da-84df-b6a0ead28371. Prompt: docs/prompts/STAGE_E.6.md (commit cdb155e, amended 3eb50c1).
On resume: read this file first, skip finished tasks.

## Hashes in force
- harness v6: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
- E.1 manifest 96166eb3...; E.2a ML 077a57e1...
- cluster freezes: K2 8815a775..., K4 7abcde17..., K5 1d0c974f..., K3 c4fb5da4...; K7: none yet
- ledger: 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
- acct-2: spent 124.673761, left 0.326239

## Task status (times PDT)
- Task 0 startup: done. Start checks 21:22:43, all pass (reports/stage_e6_briefs/start_checks.out). Start suite 21:22:41-21:39:02: 4166 passed, 2 skipped, 1 xfailed (= E.5 end result).
- Task 1 member specs: done 21:40, reports/stage_e6_member_specs.md (section 9 pending Task 1b). Readings K7-L-01..K7-L-12.
  Rulings: K7-expiry-01 coded and run as frozen (K7-L-05; E.2a L-11: every research expiry day in roll blackout);
  vendor-degraded dates excluded by literal table (K7-L-03); program trade date by clock (K7-L-01).
- Task 1b ReleaseChecker-OpusMed (worker-medium, opus): running since 21:31. Brief reports/stage_e6_briefs/1b_release_checker.md.
- Task 2 MemberCoder-A-OpusXHigh (ports) and MemberCoder-B-OpusXHigh (expiry, rev2h, montrend, _calendar): running since 21:37.
  Deviation: coder B started before 1b finished (only MBTX research rows depend on it; follow-up by SendMessage).
  strategy/members/k7/__init__.py created empty (0 bytes) by the lead.
- Next: 1b rulings into specs section 9 and to coder B; gate suite; Task 3 audit (fable).
- Task 1b done 21:47 (ReleaseChecker-OpusMed, 200k tokens): reports/stage_e6_release_check.md/.json, 14 pages under
  reports/stage_e6_briefs/pages/. Rulings R-1b-1..R-1b-4 in specs section 9 (21:47): MBTX drops 2025-12-24 and 2021-12-30, no
  additions; 10 research rows unverifiable (expiry: calendar partly unverified). R-1b-1 sent to coder B by SendMessage.
- Task 2B done 22:14 (MemberCoder-B, 357k tokens): _calendar.py (CRYPTO_FULL_SESSIONS 1782, VENDOR_DEGRADED 11, MBTX 60 = 62 - 2
  drops, MBTX_UNVERIFIED 10), _event_common.py, expiry.py, rev2h.py, montrend.py; tests/test_k7_members_events*.py (134 passed with
  template and freeze tests); mutants 86/87 killed (1 no-op control). Questions ruled 22:14: Q1 coder's reading stands (guard on
  entries only); Q2 keep builder mapping for VENDOR_DEGRADED (confirmation-only effect, open choice); Q3 noted.
- Task 2A done 22:15 (MemberCoder-A, 313k tokens): _port_common.py, cp1.py, cp2.py, cp3.py; tests/test_k7_members_ports*.py (122 passed
  with template tests); mutants 150/153 killed (3 equivalent). Brief's "19.99" case ruled moot (off-grid, engine rejects).
- Files hashed pre-audit: reports/stage_e6_briefs/k7_files_pre_audit.sha256 (22:15).
- Gate suite running since 22:15 (reports/stage_e6_briefs/pytest_gate.out).
- Task 3 MemberAuditor-K7-FableXHigh (worker-xhigh, fable) running since 22:15. Next: rulings, freeze, commit (Task 4).
- Gate suite 22:15:13-22:31:18: 4372 passed, 2 skipped, 1 xfailed (= 4166 + 206 K7 tests). K7 files unchanged vs pre-audit hashes.
- Task 3 done 22:43 (MemberAuditor-K7-FableXHigh, 388k tokens): reports/stage_e6_member_audit.md Part 1: 0 BLOCKING, 1 SHOULD FIX (F-1,
  tests), 8 NOTE; 104/105 mutants killed; tables recomputed equal.
- Task 4 in progress: rulings reports/stage_e6_member_rulings.md (22:45); specs amended (F-2, F-4, F-5); R-T3-1 test fix sent to
  MemberCoder-B (resumed 22:46). Next: after the fix, freeze (write_k7_freeze.py), full suite, commit "K7 member freeze".
- R-T3-1 fixed by MemberCoder-B (tests only; ec-end-close killed by 18 tests; 134 pass; member files unchanged).
- K7 cluster freeze written 22:45:49: reports/stage_e_k7_member_freeze.json, sha256 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462,
  6 members, 11 files; verified (load_cluster_freeze + verify_cluster_code).
- Task 4 suite running since 22:46 (reports/stage_e6_briefs/pytest_task4.out). Then commit "K7 member freeze".
- Task 4 suite 22:46:00-23:04:21: 4372 passed, 2 skipped, 1 xfailed. Commit d661eb6 23:04:30 "feat: K7 member freeze (Stage E.6),
  cluster freeze sha256 46cae308" (22 files). Task 4 done.
- Task 5 next: the frozen runner command, once, out-dir reports/stage_e6_k7_screen.
- Task 5 done: run 23:04:45-23:06:28 exit 0, "K7 research: 6 members, 0 refused", reports/stage_e6_k7_screen/ (13 files), log
  reports/stage_e6_briefs/t5_run.log. Window 265 dates (2025-04-01..2026-06-17; 42 roll blackout, 1 UR-1). All six Tier B (Tier A empty).
  cp1 261 trips -7.4610 t -1.790; cp2 263 -14.3785 t -1.350; cp3 101 -3.1197 t -0.259; expiry 0 trips 0.0 t None; rev2h 384 -28.9198
  t -2.285; montrend 466 -4.7260 t -0.441. Coverage 0.9596-0.9985. MLL liquidations cp2 1, rev2h 2. Power not_run. N = 150 + 6 = 156.
- Task 6 MemberAuditor-K7-FableXHigh resumed ~23:08 for Part 2. Next: Task 7 return, progress, STAGES, end checks.
- Task 6 done 23:07-23:15 (MemberAuditor Part 2): items 1,2,3,5,6 VERIFIED; 4 VERIFIED WITH NOTES; no DISCREPANCY. N = 156.
- Task 7: reports/E.6_RETURN.md drafted; end suite running since 23:07:38 on d661eb6. Next: end checks, cost, progress, STAGES.
- Task 7 done 23:31: reports/E.6_RETURN.md (sections 1-8), progress.md entry, docs/STAGES.md line. End suite 23:07:38-23:24:09:
  4372 passed, 2 skipped, 1 xfailed. End checks 23:24 (reports/stage_e6_briefs/end_checks.out): holdout all_ok, unlocks_logged 0
  (both holdouts); REGISTRATION.md 0 bytes; manifests ALL_OK; v6 OK; K2 K4 K5 K3 K7 freezes OK; ledger unchanged. Cost
  reports/stage_e6_briefs/cost.out. STAGE COMPLETE. Push of d661eb6 owed by the planning chat.
