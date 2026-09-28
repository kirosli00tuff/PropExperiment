# Stage E.7 STATE (K1 equity index: code, audit, freeze, screen on the research window)

Lead: Opus 5.5 xhigh, session 99bb7678-38d8-413c-82c8-d103cf2d3163. Prompt: docs/prompts/STAGE_E.7.md (commit c865a87).
On resume: read this file first, skip finished tasks.

## Hashes in force
- harness v6: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
- E.1 manifest 96166eb3...; E.2a ML 077a57e1...
- cluster freezes: K2 8815a775..., K4 7abcde17..., K5 1d0c974f..., K3 c4fb5da4..., K7 46cae308...; K1: none yet
- ledger: 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
- acct-2: spent 124.673761, left 0.326239; MNQ, M2K, MYM step 2: not_bought

## Task status (times PDT, 2026-09-28)
- Task 0 startup: start checks 00:48:29 all pass (reports/stage_e7_briefs/start_checks.out): HEAD c865a87, clean tree
  (only the new briefs dir), holdout all_ok 0 unlocks (both), REGISTRATION.md 0 bytes, manifests ALL_OK, v6 preflight OK,
  K2 K4 K5 K3 K7 freezes OK, K1 none, ledger as above. Start suite running since 00:49 (reports/stage_e7_briefs/pytest_start.out;
  expected E.6 end: 4372 passed, 2 skipped, 1 xfailed).
- Next: Task 1b spawn (ReleaseChecker-OpusMed), Task 1 specs (lead).
- Task 1b ReleaseChecker-OpusMed (worker-medium, opus): running since 00:52. Brief reports/stage_e7_briefs/1b_release_checker.md.
- Task 1 member specs: done 01:00, reports/stage_e7_member_specs.md (section 9 pending Task 1b). Readings K1-L-01..K1-L-16.
  Key: K1-L-01 VXN used from 08:30 CT per the entry (the prompt's "KF1 08:35" is K1-ml-01's row; flagged); K1-L-02 V of the
  EC-CAL trade date before d (missing after early-halt holidays: no trade); 11 declarations.
- Task 2 MemberCoder-A-OpusXHigh (ports) and MemberCoder-B-OpusXHigh (vxnband, vwap, _calendar, _vxn): running since 01:03.
  Deviation: coder B started before 1b finished (only the VXN table depends on it; follow-up by SendMessage).
  strategy/members/k1/__init__.py created empty (0 bytes) by the lead.
- Next: 1b rulings into specs section 9 and to coder B; gate suite; Task 3 audit (fable).
- Start suite 00:48:45-01:06:00 (run WITH a PYTHONPYCACHEPREFIX): 3 failed, 4369 passed, 2 skipped, 1 xfailed; the 3 are the
  known bytecode tests of tests/test_harness_freeze.py that fail under a prefix (E.3). Re-run without the prefix 01:07:
  17 passed (reports/stage_e7_briefs/pytest_start_bytecode_rerun.out). Start baseline = 4372 passed, 2 skipped, 1 xfailed
  (= E.6 end). Later suites run without the prefix, as E.6's did. Task 0 done.
- Task 1b done 01:08 (ReleaseChecker-OpusMed, 178k tokens, 12.7 min): reports/stage_e7_release_check.md/.json; VXN file
  data/vendor/index_history/vxn/VXN_History.csv sha256 f1b00135... (+ new manifest.jsonl, 3 Wayback copies, FRED copy);
  17 pages under reports/stage_e7_briefs/pages/. Rulings R-1b-1..R-1b-8 in specs section 9 (01:12): VXN kept, research rows
  all kept (label: not point-in-time checked); DROPPED_VXN 2021-04-02, 2021-12-24 (carry-forward on NYSE closures),
  2024-02-01 (revised 11.20 -> 17.33); 9 research dates without V (K1-L-02); CPI 14 keep; calendar 16 keep. Rulings sent
  to coder B by SendMessage 01:13.
- 01:22 coder B overwrote coder A's scratchpad mutants.py (shared scratchpad, same name; no repo file touched); coder A told to rewrite it as coderA_mutants.py.
- Task 2B done 01:38 (MemberCoder-B, 371k tokens, 35 min): _calendar.py (EQUITY_TRADE_DATES 1846, EQUITY_FULL_SESSIONS 1779;
  early-halt and F tests agree; 3 roots agree), _vxn.py (1794 rows = 1797 - 3 drops; CLOSE as exact strings), _event_common.py,
  vxnband.py, vwap.py; tests/test_k1_members_tables.py, _vxnband.py, _vwap.py (146 passed with template and freeze tests);
  mutants 82/84 killed (VW-31, VW-32 equivalent: sum(volume)=0 clause); engine-level reversal test passes. No questions.
- Task 2A done 02:06 (MemberCoder-A, 376k tokens, 63 min): _port_common.py, cp1.py, cp2.py, cp3.py; tests/test_k1_members_ports*.py
  (268 cases; 315 passed with template and freeze tests); mutants 178/182 killed (4 equivalent). The harness refused the
  subagent's .md write; the lead saved its report text to reports/stage_e7_coder_A.md (02:08). Notes: (1) the engine refuses
  opens without a prior-date price-limit reference (harness; affects at most the window's first date); (2) early_halt_ct
  follows the CT date, so post-holiday evening bars carry the halt label (CP3 reads it on CT date d only).
- Files hashed pre-audit: reports/stage_e7_briefs/k1_files_pre_audit.sha256 (02:08, 19 files).
- Gate suite running since 02:08:53 (reports/stage_e7_briefs/pytest_gate.out; no PYTHONPYCACHEPREFIX).
- Task 3 MemberAuditor-K1-FableXHigh (worker-xhigh, fable) spawning 02:09. Brief reports/stage_e7_briefs/auditor_task3_K1.md.
- Gate suite 02:08:53-02:25:09: 4739 passed, 2 skipped, 1 xfailed (= 4372 + 367 K1 tests). K1 files unchanged vs pre-audit hashes (02:33). Audit still running (mutant sweep).
- Task 3 done 02:45 (MemberAuditor-K1-FableXHigh, 428k tokens): reports/stage_e7_member_audit.md Part 1: 0 BLOCKING, 1 SHOULD FIX
  (F-1, tests), 9 NOTE; tables recomputed equal; 106/113 mutants killed (4 equivalent; VB-26, VW-28 = F-1); readings stand.
- Task 4 in progress: rulings reports/stage_e7_member_rulings.md (02:46); specs amended (C9 line refs; K1-L-14 10(c) R-T3-2 label
  on the 3 CP2 trials). R-T3-1 + R-T3-4 test-only fix sent to MemberCoder-B (resumed 02:46). Next: after the fix, verify
  member hashes unchanged, freeze (write_k1_freeze.py), full suite, commit "K1 member freeze".
- R-T3-1/R-T3-4 fixed by MemberCoder-B 02:47 (tests only; VB-26/VW-28 killed by the new evening tests; 150 pass); member files,
  generator and VXN file equal the pre-audit hashes; only tests/test_k1_members_vwap.py and _vxnband.py changed.
- K1 cluster freeze written 02:47:46: reports/stage_e_k1_member_freeze.json, sha256
  cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2, 11 members, 11 files; verified (load + verify_cluster_code).
- Task 4 suite running since 02:48 (reports/stage_e7_briefs/pytest_task4.out). Then commit "K1 member freeze".
- Task 4 suite 02:48-03:04:15: 4743 passed, 2 skipped, 1 xfailed. Commit 9113abd 03:04:26 "feat: K1 member freeze (Stage E.7),
  cluster freeze sha256 cf48f514" (29 files; VXN files force-added). Task 4 done.
- Task 5 next: the frozen runner command, once, out-dir reports/stage_e7_k1_screen.
- Task 5 done: run 03:04:36-03:07:26 exit 0, "K1 research: 11 members, 0 refused", reports/stage_e7_k1_screen/ (23 files), log
  reports/stage_e7_briefs/t5_run.log, summary reports/stage_e7_briefs/t5_summary.out. Window 299 dates (2025-04-01..2026-06-12;
  15 roll blackout, 2 UR-1). All 11 Tier B (Tier A empty). Coverage 0.9996-1.0. Power not_run (StartRuleMissing).
  cp1 MNQ 284 trips 4.4725 t 0.333; M2K 285 -2.9538 -0.975; MYM 286 -8.2648 -1.822; cp2 MNQ 296 -8.4855 -0.293; M2K 297 2.8543
  0.366; MYM 295 -10.7871 -1.071; cp3 MNQ 118 10.3082 0.285; M2K 140 -14.1300 -1.287; MYM 131 -16.1497 -1.218; vxnband 25
  -11.5237 -0.775; vwap 3502 -56.3758 -1.115. MLL liquidations 1,1,2,2,0,5,4,6,8,1,8. N = 156 + 11 = 167.
- Task 6 MemberAuditor-K1-FableXHigh resumed ~03:09 for Part 2 (brief reports/stage_e7_briefs/auditor_task6_K1.md).
- 03:15 cost method: reports/stage_e7_briefs/cost.py takes the LAST usage record per message id (final output count); E.4's cost.py (used E.4-E.6) keeps the first, which understates output tokens (streamed partials). Cache reads unaffected. End suite running since 03:09 (pytest_end.out).
- Task 6 done 03:08-03:17 (MemberAuditor Part 2): items 0,1,2,3,5 VERIFIED; 4, 6 VERIFIED WITH NOTES; no DISCREPANCY. N = 167.
  Note: K1-cp3-01 MNQ's Tier B rests on 4 MLL-closed trips (-$5,443.56; zeroed: mean 46.72, t 1.56); lead: tier stands (MLL is
  the frozen account model; zeroing is a bound, not an estimate); flagged for the user. First window date untradeable for
  CP2/vwap (no prior-settlement proxy; harness).
- Task 7 in progress: return document, progress, STAGES; end suite running since 03:09.
- Task 7 done 03:32: reports/E.7_RETURN.md (sections 1-8), progress.md entry, docs/STAGES.md line. End suite 03:08:00-03:24:18:
  4743 passed, 2 skipped, 1 xfailed. End checks 03:24 (reports/stage_e7_briefs/end_checks.out): holdout all_ok, unlocks_logged 0
  (both); REGISTRATION.md 0 bytes; manifests ALL_OK; v6 OK; K2 K4 K5 K3 K7 K1 freezes OK; ledger unchanged. Cost
  reports/stage_e7_briefs/cost.out (115,063,741 tokens). STAGE COMPLETE. Push of 9113abd owed by the planning chat.
