Every reviewer ran in a fresh context on a different model from the author (authors: Opus 5.5; reviewers: Fable
5.1), and each model is confirmed from its own transcript (section 4).

| Check | Object | Reviewer(s) | Result |
|---|---|---|---|
| MathReviewer A | M2, R3a arithmetic | MathReviewerA-FableXHigh | 0 BLOCKING, 5 SHOULD FIX, 11 NOTE; 118 M2 and 71 R3a numbers recomputed, all agree |
| MathReviewer B | M1, M3 | MathReviewerB-FableXHigh | 0 / 5 / 14; every worked example recomputed; 127 quote segments found in saved pages |
| MathReviewer C | M5a, M5b, p7_thresholds.py | MathReviewerC-FableXHigh | 1 (C-10: power table used z 2.128 while the bar was DSR at N) / 7 / 8; about 450 closed-form numbers; 905 test dates confirmed |
| MathReviewer D | M4, M6, R5 (b) | MathReviewerD-FableXHigh | 0 / 7 / 12; M6's payout funnel reproduced cell by cell |
| X1 re-verification | X1_exposure.md (a Sonnet worker's) | X1Verifier-OpusHigh | 311 rows: 303 confirmed, 8 corrected, 0 unsourced; 4 missing rows added |
| ProtocolReviewer (4 lenses) | protocol v0.2 | Leakage, Dof, Arithmetic, Feasibility -FableXHigh | 6 BLOCKING, 39 SHOULD FIX, 44 NOTE; 122 numbers reproduced, p7_final.py re-run byte-identical |
| FixVerifier (4 workers) | v0.3 against the 45 items | FixVerifierLeakArith, DofA, DofB, Feas -FableXHigh | 29 CORRECT, 14 PARTIAL, 2 WRONG; 0 new BLOCKING, 17 SHOULD FIX, 25 NOTE |
| FixSpotCheck (2 workers) | the v0.3 to v0.4 diff (37 hunks) | FixSpotCheckA, FixSpotCheckB -FableXHigh | 32 CORRECT, 2 UNTAGGED-OK, 2 PARTIAL, 1 WRONG (one number); 0 BLOCKING, 4 SHOULD FIX, 12 NOTE; 0 findings uncovered |
| FinalDiffCheck | the v0.4 to v0.5 diff (15 hunks) | FinalDiffCheck-FableXHigh | {{FINAL_RESULT}} |

Rulings: every BLOCKING and SHOULD FIX item at every round was accepted and applied before the freeze; NOTE items of
the re-check rounds (FixVerifier, FixSpotCheck, FinalDiffCheck) were applied too; ProtocolReviewer NOTEs were
applied only where the lead chose (others, such as AR-15's sign, came back through the re-check) and MathReviewer
NOTEs were not (all are listed in the review files). Where a
reviewer left options open, the lead's choice is logged in reports/stage_e32_STATE.md and in section 6. Files:
reports/stage_e32_briefs/review/ (MathReview_A..D.md, ProtocolReview_*.md, fix_log.md) and review/recheck/
(Recheck_W1..W4.md, SpotCheck_A.md, SpotCheck_B.md, FinalDiffCheck.md).

Numbers entering the verdict thresholds: p7_final.py's outputs (N 838, T_disc 796, T_test 870, G3 0.1724, b_test
0.164882, G4 0.2007, drop branch 0.1017 / 0.1373 / 0.1724) were reproduced by ArithmeticReviewer, FixVerifier W1
and FixSpotCheck B independently. No trading verdict number exists in E.32 (nothing was run).

Tests: tests/test_e32_soy_test_seal.py 26 passed (Part 0); the store-test subset before and after the seal (1,840
passed 1 skipped; 1,866 passed 1 skipped); the full suite at 09:01 PDT: 8,116 passed, 1 failed, 5 skipped, 3
xfailed in 1,175.65 s (reports/stage_e32_briefs/pytest_end.log). The one failure,
tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha, predates E.32: it fails
identically at HEAD 3a75f3b in a clean worktree (reports/stage_e32_briefs/h6_single.log; decision D7).

Process gaps (stated, not hidden; methods brief Part V.5): 18 cftc.gov reference fetches before the terms check
(terms allow reference use); M2's 9 failed fetches without the Scrapling fallback; R2's FAS page not retried;
abstract-only sources marked [unverified]; M5b's Lo (2002) copy from a host of unknown authorisation; X1 ran on
Sonnet before the never-Sonnet rule and printed one E.17 pooled daily series to its context; the first session's
workflow journal could not be resumed (byte-identical continuation script); three usage limits and one planned
context wipe (section 8).
