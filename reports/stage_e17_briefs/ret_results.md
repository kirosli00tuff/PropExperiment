### Part 1: C1 (hand-off steps 1-7)

1. **Start checks and suite (step 1).** All pass at harness v10: holdout all_ok with 0 unlocks, REGISTRATION.md
   0 bytes, check_frozen ALL_OK, cluster freezes K1-K8, v2 freeze (91 files), N = 471, the ledger 29,040 lines.
   acct-2 had spent 231.599730 against a 249.67 cap. Suite: 6815 passed.
2. **C1's freeze verified by script (step 2).** reports/stage_e17_briefs/verify_freeze.py (E.15's, output path changed)
   gave ALL_OK; verify_freeze.json sha256 5029b5c7... It checked:
   - the 43 inputs of reports/stage_e14_c1_freeze_inputs.json (list sha256 3356d676...);
   - the freeze file afc5c10f..., tracked, with no diff and touched only by 1680982;
   - the E.12 state copy (51 files);
   - the model JSON c6075306..., both M1 payloads and q;
   - the v10 preflight.
3. **E.16 freeze verified (step 3).** freeze_manifest.py verify OK (97 files, 5274aa97...), and
   `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md` exited 0.
4. **Fresh quote, which was also the access check (steps 4-5; A2).** acct-2 was unlocked.
   - 642 of 642 chunks were quoted with 0 failed, 18:54:50-19:06:57, under session stage-E.14-2026-10-05.
   - The guard (reports/stage_e17_briefs/fresh_quote_guard.py: E.15's, generalized and dry-run against E.15's failed
     lines, which it refused) summed the run's own 642 ledger lines: $57.742330.
   - Per root: NG 8.570392, NQ 10.625886, ZN 10.106134, 6E 11.072096, GC 11.182294, ZC 6.185528. That equals E.14's
     quote and the tool's JSON.
   - x 1.03 = $59.474600, within the $124.00 budget; the session cap of $59.47 is within V27's $60.00.
5. **Harness v11 (step 6).**
   - The diff: ACCOUNT_2_CAP_USD 249.67 -> 291.08 (231.599730 + 59.474600, rounded up) and E14_EXT2010_SESSION_CAP_USD
     0.00 -> 59.47 (rounded down), each with a comment.
   - The pinning assertions changed: test_e14_config_v10.py:20,32-33; test_e14_pull_hist.py:300, and :196, which
     also pins the cap (V11-R1); test_stage_e_config_v8.py:64-65, cited 62-64.
   - Manifest ba1ce996... Only those four file entries changed, plus the creation time and head fields.
   - Fable APPROVE (0 BLOCKING, 0 SHOULD FIX, 4 NOTE). Suite 6815 passed. Commit a21d82d.
6. **Registration, buy, stores and evaluation (step 7).**
   - Registered r001-C1 at 19:29:06 (N 471 -> 473).
   - Bought all 642 chunks: $57.817332 billed, i.e. the quote plus one orphan commit of $0.075002. The first buy process
     died with the Claude session at 19:37:46, during NG 2013-03's download; that chunk was committed but not settled,
     with no file. The identical command resumed at 19:42:33, skipped the 33 settled chunks and finished at 22:40:40
     with no chunk billed above its quote.
   - Built six ext2010 stores, 2010-06-07..2019-04-30, 2,241-2,287 trade dates each, 0 unsourced rows.
   - Hash files: stores b77bfc18..., calendars d5e48579... (byte-identical to E.15's).
   - Evaluated once: marker 22:47:44, STOPPED at C10 at 22:48:44 (exit 1; 1:05 wall; 2.06 GB peak). Result
     reports/stage_e14_c1_result.json, sha256 e5bbcaeb...
   - NG ok rows were h60 5,120 and hF 4,538. The only feature that was live on NG rows in E.12 and dead now is
     g17_mbt (E.12 87 and 84; now 0).
   - Rulings C1-R1..R5; Fable verification C1-V1..V4.

### Part 2: the base-rule batch (hand-off steps 8-15)

7. **Harness v12 (step 8).**
   - V12Coder-OpusXHigh wrote the diff in an isolated worktree, and the lead applied it on main. It covers:
     - plan "ext2010h" (label E16, ids E16-H1..H5, the 21 roots with per-root chunk lists, 1,993 chunks, store trade
       dates 2010-07-01..2019-04-30);
     - its own quote and buy session stage-E.17-ext2010h;
     - `--roots` (A4), which the lead made required for an ext2010h buy (review F-1);
     - the livestock hist calendar, a byte copy (802a4dd9...);
     - the ext2010h store builder;
     - tests.
   - No file of the E.16 freeze changed.
   - Fable: APPROVE WITH FIXES (F-1, F-2 fixed), then caps follow-up APPROVE.
   - Caps: ACCOUNT_2_CAP_USD 355.38; E17_EXT2010H_SESSION_CAP_USD 65.82 (V12-R3).
   - Manifest ece91ae8... Suite 6916 passed. Commit d30f50c.
8. **Fresh ext2010h quote (step 9).**
   - 1993 of 1993 chunks quoted with 0 failed, 23:36:08-00:01:54, under the new session.
   - The guard summed the run's own 1,993 lines: $153.965349, equal per root to E.12's quote.
9. **A3 selection (fixed before any quote).**
   - B = $124.00 - $57.817332 = $66.182668.
   - Order: ZT, ZF, ZB, then E.12's ranking mapped to price-path roots, skipping C1's six. Greedy on each root's fresh
     quote x 1.03, with the budget left falling by each taken root's quote x 1.03.

| Priority | Root | Quote x 1.03 ($) | Budget left before ($) | Taken? |
|---|---|---|---|---|
| 1 | ZT | 6.222467 | 66.182668 | taken |
| 2 | ZF | 9.364551 | 59.960200 | taken |
| 3 | ZB | 9.509736 | 50.595650 | taken |
| 4 | CL | 11.353945 | 41.085913 | taken |
| 5 | ZL | 6.409844 | 29.731968 | taken |
| 6 | ZS | 7.139396 | 23.322124 | taken |
| 7 | UB | 7.435118 | 16.182728 | taken |
| 8 | TN | 2.875335 | 8.747611 | taken |
| 9 | YM | 10.817687 | 5.872276 | skipped |
| 10 | RTY | 1.959305 | 5.872276 | taken |
| 11 | LE | 3.221091 | 3.912971 | taken |
| 12 | HG | 10.386760 | 0.691880 | skipped |
| 13 | 6S | 8.929036 | 0.691880 | skipped |
| 14 | HE | 0.468523 | 0.691880 | taken |
| 15-21 | 6J, 6A, 6B, 6N, ZM, ZW, 6C | 5.83-11.19 | 0.223357 | skipped |

   - Selected: 11 roots, 933 chunks, quote $64.038166 (x 1.03 $65.959311), with $0.223357 left. Selection
     reports/stage_e17_a3_selection.json, sha256 488b58f9...
10. **Fallback list and registration (step 10).**
    - reports/stage_e17_fallback.json (sha256 1acf1d96...): the 10 skipped roots, "not funded", window
      2019-05-06..2024-02-29. It was in STATE before any Part 2 purchase.
    - Registered r002-E16 at 00:30:15 (E16-H1..H5 against the E.16 freeze under v12; N 473 -> 478). The note records
      both sha256s.
11. **Buy (step 11).** Four detached processes over disjoint roots (CL ZT HE; ZB ZF RTY; UB ZS TN; ZL LE), 00:30:28 to
    01:26:30, all rc=0.
    - 933 chunks for $64.038166, equal to the quote, with no billed-above-quote stop.
    - Symbology was fetched for all 11 roots, including TN, RTY and HE. The condition file was written once.
    - acct-2 has now spent $353.455228; the stage total is $121.855498.
12. **Stores and run manifest (step 12).**
    - Eleven ext2010h stores built (3:15; 1.37 GB). LE and HE dropped 6,081 and 1,084 rows booked to unsourced
      livestock dates (R-C3). No purchase or build failed, so the fallback list is unchanged.
    - Run manifest reports/stage_e17_run_manifest.json, sha256 256a5410...: 6 ext2010 stores, 11 ext2010h and
      10 fallback.
    - Pre-marker dry check on it: context OK, 0 preflight refusals.
13. **The five runs, once each (step 13).**
    - H1 complete in 3:02 (1.58 GB). H2 in 0:24. H3 in 0:35. H4 in 2:59. H5 in 0:03 (no bar read).
    - Every marker was written before any bar was read, and every result records the registry path and sha256 (R-2).
14. **Verdict (step 14).** reports/stage_e17_runs/verdict.json, sha256 0c1777da..., N 478. Base case, Holm 0.05 over
    the five, with the stress and 1.5 x slippage cases reported.

| Test | Base n | mean | t | p | Holm | mean > 0 | n >= 30 | Years (qualifying / positive) | Pass | Stress mean / p | 1.5x slip mean / p |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 3,380 | -0.161 | -20.01 | 1.0 | no | no | yes | 15 / 0 | FAIL | -0.424 / 1.0 | -0.236 / 1.0 |
| H2 | 56 | +0.344 | +1.52 | 0.0677 | no | yes | yes | 6 / 5 (passes) | FAIL | +0.287 / 0.105 | +0.329 / 0.076 |
| H3 | 405 | -0.015 | -0.26 | 0.604 | no | no | yes | 12 / 5 | FAIL | -0.084 / 0.926 | -0.033 / 0.712 |
| H4 | 3,381 | -0.048 | -6.72 | 1.0 | no | no | yes | 15 / 0 | FAIL | -0.112 / 1.0 | -0.067 / 1.0 |
| H5 | 3,400 | -0.149 | -1.46 | 0.929 | no | no | yes | 15 / 2 | FAIL | -0.373 / 1.0 | -0.213 / 0.998 |

    - DSR at N = 478: H1 0.0, H2 0.0064, H3 0.0, H4 0.0, H5 0.0.
    - Descriptive only (the lead's sum over H1's 55,070 traded units with a sigma, after its run; adds nothing to N):
      mean gross_cents/sigma 5.22 against mean base costs_cents/sigma 20.83. The mean gross per traded unit is
      positive but about a quarter of the mean base cost.
15. **Fable recomputation (step 15).** See section 5.
