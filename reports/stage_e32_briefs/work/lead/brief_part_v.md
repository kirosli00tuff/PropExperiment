# Part V. Verification: the reviewers, the lead's rulings and the fixes

## V.1 Reviewers (each model confirmed from its own transcript, message.model; V50 item 5)

| Reviewer | Files | Model (transcript) | BLOCKING | SHOULD FIX | NOTE | Verdict |
|---|---|---|---|---|---|---|
| MathReviewerA-FableXHigh | M2 (all), R3a arithmetic (1, 2.3, 3.2, 4.2, 6.2, 7.2, 8.2) | claude-fable-5-1 | 0 | 5 (A-1 to A-4, A-12) | 11 | sound with fixes |
| MathReviewerB-FableXHigh | M1, M3 | claude-fable-5-1 | 0 | 5 (B-1, B-3, B-6, B-13, B-27) | 14 | sound with fixes |
| MathReviewerC-FableXHigh | M5a, M5b, p7_thresholds.py | claude-fable-5-1 | 1 (C-10) | 7 (C-1, C-2, C-3, C-7, C-8, C-9, C-11) | 8 | sound with fixes; p7 bar to fix |
| MathReviewerD-FableXHigh | M4, M6, R5 section B and E table | claude-fable-5-1 | 0 | 7 (D-1 to D-3, D-8 to D-11) | 12 | sound with fixes |
| X1Verifier-OpusHigh | X1_exposure.md (a Sonnet worker's inventory, re-verified under the user's never-Sonnet rule) | claude-opus-5-5 | - | 8 corrected rows, 4 missing rows | - | fit for P1 as corrected |

Reports: reports/stage_e32_briefs/review/MathReview_A.md to _D.md (scripts under review/work_A to work_D);
reports/stage_e32_briefs/X1_verify.md. The ProtocolReviewer's four lenses are in V.4.

Coverage (from the reviewers' own counts): A recomputed 118 M2 numbers and 71 R3a numbers and two Monte Carlos; B
recomputed every worked example in M1 and M3 and found all 127 evidence-quote segments in the saved pages; C
recomputed about 450 closed-form numbers, all simulated tables, 20 program file:line references and 68 quotes; D
reproduced every worked example of M4, M6 and R5 B, M6's payout funnel cell by cell, and found 58 quote substrings.

## V.2 The lead's rulings

Every BLOCKING and SHOULD FIX finding is accepted as the reviewer proposed it, with these specific rulings:
- C-10 (BLOCKING): p7_thresholds.py's power table used z 2.128 while its own binding test bar was the DSR at N.
  Resolved by reports/stage_e32_briefs/protocol/p7_final.py, which uses one bar everywhere; p7_thresholds.py is kept
  unchanged as the reviewed record, with a superseding note on its output.
- C-6, C-9, C-11 (the test bar): the protocol freezes the test bar as the program verdict exactly as coded
  (screening/stage_e_verdict.py: Holm at K = 9, DSR > 0.95 at the list's N with the population variance of the
  tested Sharpes, t > 3.0, PBO < 0.5) plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1). M5a's point
  that N-deflation at a fresh test is not needed for validity is right; the addition is the conservative reading of
  V43's "DSR at N", independent of how similar the tested candidates are. Dropping it is a user decision (return
  section 7) with its power cost shown both ways (P7.2).
- C-1 and C-7 (trade-date counts): 905 for 2017-05-01..2020-11-30 is right (31 closures); the protocol uses the
  MBO-feasible span 2017-05-22..2020-11-30 = 890, minus a 20-date burn-in = 870 (Part F's saved Databento page).
- A-2 and A-3 (clock offsets across feeds; bid-ask bounce and stale legs): taken into protocol G6 (per-month
  ts_recv - ts_event comparison across the three feeds; mids and executable touch prices only).
- D-1 (1.59 as a per-round-trip cost): E.28's 1.59 is a cycle-EV threshold; the per-trade market cost is 1.528 plus
  the firm's fee difference. The protocol uses executable prices and the fee directly, so no 1.59 enters a label.
- D-11 (M6 5.6's measurement plan): taken into protocol P6.4 (one common signal set, ts_recv clock, P3.6 rules).
- NOTE items: no edit; they are listed in the review files.

## V.3 The fixes

Each accepted correction is a bracketed note "[MathReview X-n (lead: accepted): ...]" in the reader file at the line
it corrects; nothing the reader wrote was deleted. Log: reports/stage_e32_briefs/review/fix_log.md. Applied by
FixApplier-OpusHigh (claude-opus-5-5): 25 accepted findings plus the C-6/C-9 ruling, 0 not applied, 32 notes inserted
(A 5, B 5, C 14 including the ruling at 7 places and the two superseding notes on p7_thresholds_budget500.md, D 8 with
D-1 in both M4 and R5), 0 lines deleted (diff against pre-edit copies). C-9's own figures (t-equivalent 4.92 at N
1,038) are superseded by the ruling's figures at N 838 (t about 4.86).

## V.4 ProtocolReviewer (the frozen protocol)

Four independent ProtocolReviewer lenses (Fable xhigh, worker-xhigh, workflow wf_30d7118e-f81, 07:32-07:57 PDT)
reviewed protocol DRAFT v0.2; each model was confirmed from its own transcript (claude-fable-5-1). A first run
(wf_3d631049-c34, 03:05) was stopped by a usage limit before any lens wrote a file and was re-run in full.

| Lens | File | Model (transcript) | BLOCKING | SHOULD FIX | NOTE |
|---|---|---|---|---|---|
| LeakageReviewer-FableXHigh | review/ProtocolReview_leakage.md | claude-fable-5-1 | 1 (LE-1) | 6 (LE-2 to LE-7) | 11 |
| DofReviewer-FableXHigh | review/ProtocolReview_dof.md | claude-fable-5-1 | 2 (DO-1, DO-2) | 20 (DO-3 to DO-22) | 14 |
| ArithmeticReviewer-FableXHigh | review/ProtocolReview_arithmetic.md | claude-fable-5-1 | 1 (AR-1) | 4 (AR-2 to AR-5) | 11 |
| FeasibilityReviewer-FableXHigh | review/ProtocolReview_feasibility.md | claude-fable-5-1 | 2 (FE-1, FE-2) | 9 (FE-3 to FE-11) | 8 |

The ArithmeticReviewer reproduced 122 numbers and re-ran p7_final.py byte-identically. All 45 BLOCKING and SHOULD
FIX items were accepted and applied by the lead (v0.3); the AR-1 finding (the program verdict as coded, V14 c,
makes the test's power depend on the list's composition) is disclosed in P7.2 and left to the user as a reserved
decision in P9 (amend V14 c to V = 1/(T_test - 1) for this test), since E.32 does not amend a user decision.

Re-check (FixVerifier, four Fable xhigh workers split by item and protocol section, workflow wf_6418603c-1ef,
08:42-08:56 PDT, all claude-fable-5-1; review/recheck/Recheck_W1.md to _W4.md): of the 45 items, 29 CORRECT, 14
PARTIAL, 2 WRONG (AR-1's disclosure overstated the weaker-companion case; DO-19's deadlines were stale against the
E.33 prompt as amended at 08:16); 0 new BLOCKING, 17 new SHOULD FIX, 25 NOTE. The lead applied every item, SHOULD
FIX and NOTE (v0.4; rulings and the options the lead chose in reports/stage_e32_STATE.md, 12:38-12:41).

Spot-check of the v0.3 to v0.4 diff (FixSpotCheck, two Fable xhigh workers by section, workflow wf_22487789-c6a,
both claude-fable-5-1; review/recheck/SpotCheck_A.md and _B.md): 37 hunks: 32 CORRECT, 2 UNTAGGED-OK, 2 PARTIAL, 1 WRONG (one number); no finding left uncovered; 0 BLOCKING, 4 SHOULD FIX, 12 NOTE, all applied (v0.5). A final check of the v0.4 to v0.5 diff (FinalDiffCheck-FableXHigh, claude-fable-5-1; review/recheck/FinalDiffCheck.md): 15 hunks, 11 CORRECT, 2 PARTIAL, 2 UNTAGGED-OK, 0 WRONG; 0 BLOCKING, 3 SHOULD FIX, 5 NOTE, all applied with the checker's own texts (v0.6), plus one consistency edit in P10. Frozen 2026-10-27 13:08 PDT as v1.0.

The frozen text is v1.0, sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05
(reports/stage_e32_discovery_protocol.sha256).

## V.5 Process gaps and source hygiene (stated, not hidden)

- cftc.gov: R3a, R3b and R4 fetched 18 single documents before a terms decision was logged; the lead's check at 00:40
  found robots.txt allows reference use for user-agent * ("ai-train=no, use=reference") while blocking named training
  crawlers; the fetches were consistent with the terms, but the order (fetch, then terms) breaks the reader rules.
- M2 logged 9 failed fetches without trying the Scrapling fallback; Hasbrouck (1995) and Hayashi-Yoshida (2005) are
  cited second-hand. R2 did not retry the FAS export-sales page (403) because no terms check was done. R5 treated
  Kaggle as closed (reCAPTCHA); competition metrics there are [unverified]. Several sources are abstract-only and
  marked [unverified] (Kolm-Turiel-Westray, Stoikov 2018, Ma-Serra, Jin et al., Volkenand et al., Chordia-Roll-
  Subrahmanyam 2008); none of them carries a verdict alone.
- M5b's Lo (2002) copy came from a student-organisation host (authorisation unknown); Newey-West and one Sinica
  quote were typed from page images.
- X1 (the exposure inventory) ran on Sonnet before the user's 23:15 never-Sonnet rule reached the run; X1Verifier
  re-verified all 311 rows on Opus. X1 printed one E.17 pooled daily result series to its context once (disclosed).
- The first lead session stopped at a usage limit (00:51-02:32); its workflow journal could not be resumed in the
  new session, so the three unfinished readers ran from a byte-identical continuation script. A second usage limit
  (about 03:12-07:31) stopped the ProtocolReviewer and FixApplier before either wrote anything; both were re-run.
