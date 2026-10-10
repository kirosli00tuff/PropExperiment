Four Fable checks ran, each worker-xhigh on fable, as the prompt names them. Every finding and its ruling is in
reports/stage_e17_review.md and reports/stage_e17_rulings.md.

| Check | When | Verdict | Findings | Rulings and fixes |
|---|---|---|---|---|
| v11 diff (HarnessReviewer) | 19:10-19:25 | APPROVE | 0 BLOCKING, 0 SHOULD FIX, 4 NOTE | V11-R1 line 196 within the freeze's words; R2 the dropped `funds >= cap` assertion (the invariant holds); R3 older sessions' room (pre-existing, no session ran); R4 stale names left (the freeze allows only assertions) |
| C1's verdict (VerdictVerifier) | 22:51-23:08 | VERIFIED WITH NOTES | 0 BLOCKING, 1 SHOULD FIX (F-1), 4 NOTE | C1-V1: F-1, the freeze contradiction (C10 vs section 2 for g17_mbt), decidable since 2026-10-05, goes to the user (section 7); V2-V4 recorded. The STOP stands, verified: reference 87/84 recomputed, run 0 of 5,137 NG rows, c10_check is the freeze's sentence, order and leakage 11/11, hashes 12/12 |
| v12 diff (HarnessReviewer) | 23:18-23:35; caps follow-up 00:07-00:12 | APPROVE WITH FIXES, then APPROVE | 0 BLOCKING, 2 SHOULD FIX (F-1, F-2), NOTEs N-1..N-8 | V12-R1 F-1 FIXED: an ext2010h buy needs --roots. V12-R2 F-2 FIXED: cap and session pins in the hashed test_e14_config_v10.py. V12-R3 the concurrency bound sets the session cap at 65.82. V12-R4/R5 the coder's points and the quote on the reviewed tree. V12-R6 the caps follow-up verified the selection, both caps (worst case $123.99), F-1 and manifest ece91ae8 |
| H1-H5 verdicts (VerdictVerifier) | 01:40-02:03 | H1-H4 VERIFIED, H5 VERIFIED WITH NOTES | 0 BLOCKING, 4 NOTE | H-V1 every verdict number verified (series to <= 2.8e-14; 714 units spot-checked against the stores, 0 mismatches); H-V2 H5's sd comes from four sparse-component dates (literal frozen wording; the verdict is unaffected; any reuse must guard sigma); H-V3 H3's flip cost accepted; H-V4 the unverifiable counters recorded; H-V5 the brief's focus points disclosed |

No BLOCKING finding arose on any verdict, so no verdict is reported as unverified. No fix touched a frozen file or a
registered parameter. The two code fixes (v12 F-1 and F-2) were made before v12's first use and before its commit.
