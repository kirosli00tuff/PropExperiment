# Stage E.17 STATE (C1 completed, then the base-rule batch H1 to H5)

Prompt docs/prompts/STAGE_E.17.md. Lead Opus 5.5 xhigh, session 0dcecb5d-5f79-4bc8-8a23-a1ca768d375b. All times PDT
(America/Vancouver), from `date`. On resume: read this file first and skip finished steps.

## Amendments received during the stage (before any quote)

- 18:35 PDT (planning chat, relaying the user): budget $122.50 (balance $126.25); commit 5f9671d.
- 18:37 PDT (planning chat, correction): acct-2's balance is exactly $130.23; budget $126.30; commit 7447677.
- 18:38 PDT (planning chat, FINAL, superseding both lines above): the user's choice, **$124.00** in total billed
  spend (A1); A3's greedy selection uses each root's fresh quote x 1.03 against $124.00 minus Part 1's billed
  amount. Nothing else changes. docs/DECISIONS.md V30 amendment, commit 8e5707c (on local main before step 2).

## In force

- Budget (A1 as amended, FINAL): $124.00 total billed in this stage, C1 plus Part 2. Billed so far: $57.817332 (C1). Left: $66.182668.
- Harness: v11 ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292 (commit a21d82d, 19:28:52); v10 was fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b.
- C1 freeze: reports/stage_e14_prereg_C1.md afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b.
- E.16 freeze: reports/stage_e16_freeze.json manifest 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4.
- Ledger at start: 29,040 lines, sha256 a9ad6ab59b94818407042d4faf1ccaaa3bab72447376dcce631f3312cc12b2de;
  acct-1 spent 118.390020 (cap 120.00), acct-2 spent 231.599730 (cap 249.67, headroom 18.070270).
- Trial registry: N = 473 after C1's registration 19:29:06 (2 lines, sha256 4b1bf93d...); at start N = 471 (sha256 a73b4de8...).
- acct-2 cap 291.08 (v11); E14_EXT2010_SESSION_CAP_USD 59.47. Billed in E.17 (Part 1, C1): $57.817332 (incl. the orphan commit $0.075002). Budget left for Part 2: B = 124.00 - 57.817332 = $66.182668.

## Steps (hand-off reports/stage_e16_handoff.md steps 1-15, with A1-A7)

| Step | Status | Start | End | Artifacts / notes |
|---|---|---|---|---|
| 0 read prompt and context | done | 18:34 | 18:36 | |
| 1 start checks | done | 18:37 | 18:37 | reports/stage_e17_briefs/start_checks.txt: all pass (holdout all_ok 0 unlocks; REGISTRATION.md 0 bytes; v10 preflight OK; clusters K1-K8 OK; v2 freeze 91 files; N 471; C1 freeze and 43 inputs OK; E.16 freeze 97 files OK; git diff vs 8f388c8 clean) |
| 1 start suite | done | 18:37:38 | 18:54:28 | reports/stage_e17_briefs/pytest_start.out: 6815 passed, 2 skipped, 3 xfailed, rc=0 (16:47) |
| 2 verify C1's freeze by script | done | 18:37:55 | 18:37:58 | reports/stage_e17_briefs/verify_freeze.py (E.15's, output path changed); verify_freeze.json sha256 5029b5c767369900e6b5bfb1887d7af5207deae47b2bd9c7314f6a11fb211d55: ALL_OK (43 inputs, freeze tracked/no diff/only 1680982, E.12 state 51 files, model + payloads + q, v10 preflight) |
| 3 verify the E.16 freeze | done | 18:37 | 18:37 | in start_checks.txt: freeze_manifest.py verify OK (97 files, 5274aa97...); git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md exit 0. Part 2 may proceed |
| prep: E.17 quote guard | done | 18:40 | 18:41 | reports/stage_e17_briefs/fresh_quote_guard.py; dry run on E.15 attempt 2's lines refused (exit 1: 642 failed, tool JSON != ledger sum) |
| prep: A3 selection script (fixed before any quote, no market data) | done | 18:43 | 18:45 | reports/stage_e17_briefs/a3_select.py; E.12 ranking sha256 43f80e90... verified; priority order ZT, ZF, ZB, CL, ZL, ZS, UB, TN, YM, RTY, LE, HG, 6S, HE, 6J, 6A, 6B, 6N, ZM, ZW, 6C; budget left = $124.00 - acct-2 billed since start, falls by each taken root's quote x 1.03 |
| prep: C1 calendar hash file (README step 3; no market data) | done | 18:46 | 18:46 | reports/stage_e17_c1_calendar_hashes.json sha256 d5e48579d2bd70b2e73d7583010e7c7ef61f94cc58fe68b07e7734a12911f6f8 (byte-identical to E.15's; written by reports/stage_e17_briefs/write_hash_files.py, E.15's with output names changed); v12 brief drafted: reports/stage_e17_briefs/brief_v12.md (spawn only after C1's evaluation, U1) |
| 5 fresh C1 quote under v10 (acct-2 unlocked) | done | 18:54:50 | 19:06:57 | ledger 29,040 lines and UTC start 2026-10-10T01:54:50+00:00 recorded first; v10 preflight OK; reports/stage_e17_briefs/quote_ext2010.log ("quoted 642 of 642 chunks; 0 failed"), quotes_ext2010.json (tool, not trusted). GUARD reports/stage_e17_briefs/fresh_quote_c1.json (sha256 1203ed6f...) ok: 642 own lines, 0 problems, total $57.742330 (NG 8.570392, NQ 10.625886, ZN 10.106134, 6E 11.072096, GC 11.182294, ZC 6.185528), x1.03 $59.474600 <= $124.00, session cap 59.47 <= 60.00; ledger 29,682 lines after |
| 6 harness v11 (edit, manifest, Fable review, suite, commit) | done | 19:07 | 19:28:52 | data/config.py ACCOUNT_2_CAP_USD 249.67 -> 291.08 (231.599730 + 59.474600 = 291.074330, up), E14_EXT2010_SESSION_CAP_USD 0.00 -> 59.47 (down); tests: test_e14_config_v10.py:20,32-33; test_e14_pull_hist.py:300 AND :196 (also pins the session cap; not in the freeze's list; open choice); test_stage_e_config_v8.py:64-65 (freeze cites 62-64; E.15 item 14). Manifest v11 ba1ce99672b7e5bbb33f0cfabb89ba618d207d701348da1b1681ecfa7d932292 (only those 4 file entries + created/head differ from v10); preflight OK; cap tests 56 passed. HarnessReviewer-FableXHigh spawned 19:10 (brief reports/stage_e17_briefs/brief_v11_review.md); full suite started 19:10:38 -> reports/stage_e17_briefs/pytest_v11.out | Fable APPROVE (0 BLOCKING, 0 SHOULD FIX, 4 NOTE; review 19:24-19:25; rulings V11-R1..R4 in reports/stage_e17_rulings.md). Suite on v11: 6815 passed, 2 skipped, 3 xfailed, rc=0 (19:10:38-19:28:22). COMMIT a21d82d 'harness v11, acct-2 cap for C1' 19:28:52 (5 files; the ledger's 642 quote lines left for C1's commit) |
| 7a register C1 | done | 19:29:04 | 19:29:06 | v11 preflight OK; r001-C1: C1-T1, C1-T2, N 471 -> 473 (2026-10-09T19:29:06-07:00); registry sha256 4b1bf93d86a2b65b66e52c32aee927641b0d2fb1e5581a1fddbe54a4b521e585; reports/stage_e17_briefs/c1_register.log |
| 7b C1 buy (642 chunks, session stage-E.14-ext2010, cap 59.47) | done | 19:29:15 | 22:40:40 | ledger 29,682 lines before (UTC 02:29:15); reports/stage_e17_briefs/c1_buy.log. INTERRUPTION: the previous Claude session ended about 19:38-19:41 and its background shell took the buy with it; last settled chunk NG 2013-02 (19:37:41, 33 chunks settled, session $2.370217); NG 2013-03 was COMMITTED ($0.075002, 19:37:46) but not settled, and no target or .partial file exists. RESUMED 19:42:33 with the identical command as a detached process (setsid nohup, appending to the same log; ledger 29,783 lines before); the orphan commit stays in the ledger and counts against the caps and the budget (conservative; open choice) | FINISHED rc=0 22:40:40: 642 chunks (33 skipped as settled, 609 bought after the resume), no billed-above-quote stop; free symbology and the dataset condition fetched; session spent $57.817332 (quote $57.742330 + the orphan commit $0.075002); acct-2 spent $289.417062 (cap 291.08, headroom 1.662938); ledger 31,610 lines |
| 7b' post-purchase checks | done | 22:41:08 | 22:41 | reports/stage_e17_briefs/post_c1_purchase_checks.txt: holdout all_ok 0 unlocks; REGISTRATION.md 0; v11 preflight OK; clusters OK; v2 freeze 91; N 473; ledger 31,610 lines sha256 ba22273f...; E.16 freeze OK; C1 freeze inputs: 1 expected mismatch, reports/stage_e2b_harness_freeze.json (v10 -> v11, allowed by C1's freeze section 11) |
| 7c build the six ext2010 stores | done | 22:41:36 | 22:46:57 | reports/stage_e17_briefs/c1_store_build.log: all six 'built', rc=0, 5:20 wall, peak RSS 1.47 GB; summaries reports/hist/bars_<ROOT>_ext2010.json (window 2010-06-07..2019-04-30; trade dates NG 2284, NQ 2283, ZN 2287, 6E 2283, GC 2282, ZC 2241; 0 unsourced rows) |
| 7c' C1 hash files (before the run) | done | 22:47 | 22:47 | STORE hashes reports/stage_e17_c1_store_hashes.json sha256 b77bfc183943a07561c6a79020820b43fb8c757e3023ef2e042093c48d3d2a08 (NG d3781174..., NQ d4cf098a..., ZN e3a048b5..., 6E 59e81a4a..., GC 0776767f..., ZC ae0f54ec...); CALENDAR hashes reports/stage_e17_c1_calendar_hashes.json sha256 d5e48579d2bd70b2e73d7583010e7c7ef61f94cc58fe68b07e7734a12911f6f8 |
| 7d C1 evaluate ONCE | done | 22:47:39 | 22:48:44 | reports/stage_e17_briefs/c1_evaluate.log; marker reports/stage_e14_c1_RUN_ONCE.json (22:47:44, sha256 8ff81f8d...); result reports/stage_e14_c1_result.json sha256 e5bbcaeb2520bdb07516814f268d98e73e0105d13d5d5e5c3a2947f75e76ee73: VERDICT STOPPED, exit 1: 'C10: features live in E.12 apply on no NG row: [g17_mbt (h60), g17_mbt (hF)]' (E.12 reference 87 / 84; MBT not listed 2010-2019, n/a by design); NG ok rows h60 5120, hF 4538; 1:05 wall, peak RSS 2.06 GB. No T1/T2 statistic. Attempt CLOSED, never rerun; N stays 473. Rulings C1-R1..R5 (reports/stage_e17_rulings.md): a freeze-internal contradiction (sections 2 vs 3) detectable before registration, missed by E.14's review, E.15 and this lead; A6 not triggered (NQ, ZN bought) so H2 stays; U1 met; the Fable check verifies the STOP |
| prep: run-manifest writer (step 12) | done | 19:30 | 19:31 | reports/stage_e17_briefs/write_run_manifest.py (schema stage_e16_run_manifest/1; ext2010/ext2010h from reports/hist/bars_<ROOT>_<plan>.json, step2 from reports/step2/bars_<ROOT>.json, each sha256 checked on disk; write-once); dry run with all 27 on fallback (scratchpad) OK; C1 verify brief drafted reports/stage_e17_briefs/brief_c1_verify.md |

## Tests

| Test | Status |
|---|---|
| C1 (T1, T2) | STOPPED (C10, g17_mbt) 22:48:44; registered 19:29:06 (N 471 -> 473); closed, not rerun; Fable verification pending |
| E16-H1..H5 | not registered |

## Next step

Commit 'E.17 C1 evaluated' (C1 artifacts, ledger lines); spawn VerdictVerifier-FableXHigh (reports/stage_e17_briefs/brief_c1_verify.md, rewritten for the STOP) and V12Coder-OpusXHigh (brief_v12.md, worktree) in parallel; then the v12 review.
