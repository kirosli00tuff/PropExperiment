# Stage E.18 STATE (C1b: C1 re-registered with the C10 contradiction fixed, evaluated once)

Prompt docs/prompts/STAGE_E.18.md. Lead Opus 5.5 xhigh, session a6f2d97b-f5fc-4d95-a054-c5010e1ff6d0. All times PDT
(America/Vancouver), from `date`. On resume: read this file first and skip finished steps.

## In force

- Harness: v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32 (preflight OK at start, 11:47).
- C1 freeze (base text): reports/stage_e14_prereg_C1.md afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
  (tracked, no diff vs HEAD, touched only by 1680982).
- Trial registry at start: N = 478, 3 lines, sha256 851f18218bc22d76ae16b9c8ceee49cbe764af6e3c4e19de3b66b0abd0210e9f.
- Spend ledger at start: 36,402 lines, sha256 034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
  (must be unchanged at end: no purchase, no Databento call).
- Holdout at start: all_ok True, unlocks_logged 0 (top, holdout_2, MCL, MGC, MHG, NG).
- C1b freeze (12:17:07): reports/stage_e18_prereg_C1b.md sha256 35b936fb33c32f29365cdd77ce1f8642330270a827795dac4059403d78075dcd;
  manifest reports/stage_e18_freeze.json sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03 (13 C1b files,
  35 C1 inputs re-hashed against the pins, 10 external: both M1 payloads, the six ext2010 stores against
  reports/stage_e17_c1_store_hashes.json, the E.12 state copy 51 files, q h60 0.033735277284776724, hF 0.0831931045522869);
  c1_replication/c1b.py 4f8ce49b...; tests/test_c1b.py 4d9394fb....
  Section 11 (1)-(3) of the C1b text: (1) E.14 freeze-inputs list verified at start (only the harness manifest differs,
  the allowed exception), the E.12 state copy, model JSON and payloads by the manifest; (2) v12 preflight at start and
  again at registration; (3) stores and calendars by the manifest. Git state of both freezes checked after the commit.
- E.14 C1 freeze-inputs list (3356d676..., 43 entries): 1 mismatch, reports/stage_e2b_harness_freeze.json (the harness
  manifest, v10 -> v11 -> v12 in E.17; expected); every c1_replication/*.py and test file matches.

## Steps

| Step | Status | Start | End | Artifacts / notes |
|---|---|---|---|---|
| 0 read prompt and context | done | 11:41 | 11:47 | |
| 0 start checks | done | 11:47:18 | 11:47:30 | reports/stage_e18_briefs/start_checks.txt (checks.sh = E.17's with E.18 paths) |
| 0 start suite | done | 11:47:32 | 12:05:36 | reports/stage_e18_briefs/pytest_start.out: 6913 passed, 3 failed, 3 skipped, 3 xfailed (18:00). The 3 failures (tests/test_harness_freeze.py bytecode tests) are an artifact of the lead's invocation: PYTHONPYCACHEPREFIX was set for the suite, so bytecode left the tmp_path the tests inspect. Rerun of that file without it: 17 passed (12:16, reports/stage_e18_briefs/pytest_start_rerun_harness_freeze.out). The end suite runs the prompt's exact command, no prefix. |
| 1 C1b text, diff, code, test | done | 11:48 | 11:57 | reports/stage_e18_prereg_C1b.md (generator reports/stage_e18_briefs/make_c1b_text.py: 15 replacements + section 13); reports/stage_e18_c1b_diff.md; c1_replication/c1b.py; tests/test_c1b.py (74 passed, 11.6 s; ruff clean); listing evidence reports/stage_e18_briefs/pages/LOG.md (MBT 2021-05-03, BTC 2017-12-18, verbatim) |
| 2 DiffReviewer-FableXHigh | done | 11:58:43 | 12:14 | reports/stage_e18_review.md: APPROVE WITH FIXES (0 BLOCKING, S-1 SHOULD FIX, N-1..N-9); all six checks PASS. Rulings R-1..R-5 (reports/stage_e18_rulings.md); fixes in make_c1b_text.py, text regenerated (sha256 35b936fb...), diff regenerated via reports/stage_e18_briefs/make_diff_doc.py (12:15) |
| 3 dry check | done | 12:16:02 | 12:16:05 | PASS, every case as expected (expectation written 12:00:19). reports/stage_e18_dry_check.json (8b98a628...), .md; log reports/stage_e18_briefs/dry_check.log. Earlier smoke run on SYNTHETIC calendars only (mechanics, scratch, 12:00:07). |
| 4 freeze manifest + commit "C1b freeze" | done | 12:17:07 | 12:17:35 | manifest 5ed208a2... (write 12:17:07, verify OK 12:17:22); COMMIT b714751 "C1b freeze" 12:17:35 (37 files, explicit paths); both freezes tracked, no diff vs HEAD |
| 5 register (N 478 -> 480) + evaluate once | done | 12:17:46 | 12:18:38 | preflight OK (v12); REGISTERED r003-C1b 12:17:48, N 478 -> 480, registry sha256 55b1d24c... (reports/stage_e18_briefs/c1b_register.log). Evaluation launched detached 12:18:03 (setsid nohup, nice 10) -> reports/stage_e18_briefs/c1b_evaluate.log ; marker 12:18:05, result 12:18:38 (34.7 s wall, 2.05 GB peak, rc 0). VERDICT FAIL: T1 h60 n 814, mean 0.585 ticks vs bar 2.562, t_B -0.831, p 0.797; T2 hF n 627, mean -0.113 vs bar 2.649, t_B -0.410, p 0.659. Result reports/stage_e18_c1b_result.json sha256 0b820919... |
| 6 VerdictVerifier-FableXHigh | done | 12:19:13 | 12:29:08 | VERIFIED WITH NOTES (0 BLOCKING, 0 SHOULD FIX; NOTE 1 trade-level vs per-date mean, T1 +0.585 / -0.914, both fail; NOTE 2 harness manifest v12). recompute.json on disk 12:23:48 before the result was opened; 66 items, 0 unequal at 1e-9. reports/stage_e18_review.md lines 245-366; reports/stage_e18_verify/. Rulings V-1, V-2 |
| 7 return, progress, STAGES, end checks, end suite, commit | done | 12:29 | 12:48:04 | end checks 12:29:55 (reports/stage_e18_briefs/end_checks.txt: all pass, N 480, spend ledger unchanged, C1b freeze verify OK); end suite 12:30:09-12:46:32: 6990 passed, 3 skipped, 3 xfailed, rc 0 (reports/stage_e18_briefs/pytest_end.out); docs/STAGES.md line; progress.md entry; tokens to 12:46:58: 45,253,221 (lead 88.1%); reports/E.18_RETURN.md assembled; memory no-pycache-prefix-for-suite.md; final commit "Stage E.18 C1b evaluated" |

## Lead decisions so far (copied into the return's Open choices)

- D-1 (by 11:47): C1b's code goes in a NEW module c1_replication/c1b.py (plus tests/test_c1b.py); every C1 file stays
  byte-identical. Reason: C1's closed attempt stays reproducible from its frozen code, and the E.14 freeze-inputs
  verification (an end check this prompt requires) stays clean for c1_replication/. c10_check lives in
  c1_replication/evaluate.py; c1b runs the frozen evaluate.run inside a context that swaps the C1 attributes C1b
  changes (the ids, the C10 check) and restores them, the pattern c1_replication.context.hist_tables already uses.
- D-2 (by 11:57): the exempt list is g17_mbt and g17_cl (V31 names MBT and CL). g17_cl is listed in 2010-2019, so it is
  exempt under section 2 ("CL is never live on NG rows": NG's own cluster lead), not under "no listed contract"; its E.12
  reference is 0, so the exemption is a no-op for it. The text says so rather than claiming CL was unlisted.
- D-3 (by 11:57): C1's section 2 "Never read before the test" became false in E.17 (store builds; C1's stopped run printed
  C10 counts; the base-rule batch H1-H5 used these six stores, with per-product H1/H4 results including NG). C1b's text
  states this (change 3 of the diff) instead of copying a false sentence. The lead did not open the H1/H4 per-product
  values.
- D-4 (by 11:57): C1's section 11 required the evaluating session's harness to differ from v10 only in data/config.py; v12
  (the prompt's fixed harness) also changes data/pull_hist.py, hist_store.py, hist_calendar.py and adds livestock.json.
  C1b's section 11 names v12 and lists its differences; the review checks that none touches the ext2010 evaluation path.
