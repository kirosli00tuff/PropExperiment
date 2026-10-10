# Stage E.17 rulings (the lead's rulings on Fable's findings and on the lead's own open points)

All times PDT, from `date`. Findings are in reports/stage_e17_review.md.

## Budget (before any quote)

- B-1 The stage budget (A1) is $124.00 in total billed spend: the planning chat's third message (18:38, commit 8e5707c,
  "final budget from the user") supersedes $122.50 (5f9671d) and $126.30 (7447677). A3's greedy selection uses each
  root's fresh quote x 1.03 against $124.00 minus what Part 1 billed.

## Harness v11 (review: APPROVE, 0 BLOCKING, 0 SHOULD FIX, 4 NOTE; ruled 19:26)

- V11-R1 (lead, 19:09; Fable NOTE 1 agrees) tests/test_e14_pull_hist.py:196 pins E14_EXT2010_SESSION_CAP_USD through
  buy_gate/buy_policy (`== ("stage-E.14-ext2010", 0.0)`) and failed on v11. C1's freeze lists the pinning assertions
  as tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64,
  under the governing words "the test assertions that pin those two values". Line 196 is such an assertion, so it is
  changed to 59.47 and the citation gap is recorded (open choice). Likewise test_stage_e_config_v8.py's cap-pinning
  assertions are lines 64-65, not 62-64 (E.15_RETURN.md section 6 item 14).
- V11-R2 (Fable NOTE 2) the dropped `funds >= config.ACCOUNT_2_CAP_USD` (test_stage_e_config_v8.py:65) pinned the v8
  cap to v8's funds; it is replaced by the v11 value pin. The invariant it guarded (the cap never above the funds)
  holds: acct-2's headroom under 291.08 is $59.480270 against a $130.23 balance (V30 amendment). Accepted, no change.
- V11-R3 (Fable NOTE 3) raising ACCOUNT_2_CAP_USD also raises the room of the older acct-2 sessions (E.12 step 2,
  E.1) until C1's buy uses the headroom; settle deltas are not capped per session. Pre-existing design; no older
  session runs in E.17 and the buy is run only by the lead. Recorded, no change.
- V11-R4 (Fable NOTE 4) historical comments and test names that now read stale (for example "stays refused at a zero
  cap") are left as they are: the freeze allows only the assertions and the comments beside the two constants.

## C1's evaluation (STOPPED at C10; ruled 22:50)

- C1-R1 The single evaluation (marker 22:47:44, finished 22:48:44, exit 1) returned verdict STOPPED: "C10: features
  live in E.12 apply on no NG row: ['g17_mbt (h60)', 'g17_mbt (hF)']". E.12's reference counts on NG rows
  (reports/stage_e14_c1_model.json c10_reference) are g17_mbt 87 (h60) and 84 (hF); in 2010-2019 MBT is not listed
  (C1 freeze section 2: "MBT is not listed (n/a by design)"; ruling C7's sentinel frame dated 2019-05-31), so the
  feature applies on 0 rows. Every other feature with 0 applicable rows now also had 0 in E.12. The frozen code
  applies the freeze's C10 rule (section 3: "The run stops if any feature live in E.12 has 0 applicable rows")
  literally; the freeze's own sections 2 and 3 contradict each other for g17_mbt, so C1 as frozen could not complete
  on 2010-2019 data. The contradiction was detectable from frozen inputs before registration and purchase; E.14's
  freeze review, E.15 and this lead did not catch it.
- C1-R2 Per the freeze (section 3: "A C10 stop therefore CLOSES this registered attempt. Any calendar correction and
  rerun is a new registration, with its tests counted in N again") and the prompt (no test runs twice), C1 is
  reported STOPPED and is not rerun. N stays 473 (C1's +2 counted at registration). No T1 or T2 statistic exists;
  nothing is learned about the NG hypothesis. Any rerun needs a new pre-registration (for example exempting a leg
  that is n/a by design from C10) and adds to N again: a decision for the user (return section 7).
- C1-R3 The purchase completed (NG, NQ, ZN, 6E, GC, ZC, 642 chunks; $57.817332 billed including the orphan commit),
  so amendment A6 does not apply: H2 stays and H1-H5 are registered together (N + 5). The six ext2010 stores are the
  2010-2019 stores of those roots for the base-rule batch (hand-off section 2).
- C1-R4 U1 ("C1's evaluation completes before step 8") is met: the evaluation ran once and returned its verdict.
  Part 2 proceeds.
- C1-R5 The Fable check after step 7 verifies the STOPPED verdict itself (the C10 counts, the reference counts, that
  the stop is the freeze's rule applied as written and not a code error, that no statistic or bar-derived number was
  printed before the marker), since no verdict statistic exists to recompute.

## C1 STOPPED verdict verification (VerdictVerifier-FableXHigh: VERIFIED WITH NOTES, 22:51-23:08; ruled 23:08)

- C1-V1 (F-1, SHOULD FIX, for any new registration) accepted and carried to the user (return section 7): the freeze's
  C10 rule and its section 2 contradict each other for g17_mbt, and the stop was decidable from frozen artefacts
  since 2026-10-05 03:29:57 (tests/test_c1_world.py:96 asserts app_g17_mbt == 0 on every replication NG row; the
  model JSON records 87/84 > 0; c10_check stops on that combination). A new C1 freeze, if the user wants one, must
  name the n/a-by-design legs exempt from C10 in the same sentence as the stop, and run c10_check on the frozen
  reference against the sentinel frames before registering. Lead's addition: E.17's own pre-registration checks
  did not include such a dry run; for H1-H5 the lead ran one before registration (STATE, "H pre-marker dry check").
- C1-V2 (N-1) the annex's liveness table understates g17_mbt (29 live signals listed, 30 by count; g17_mbt live on
  29 NG trade dates 2024-01-04..2024-02-29). Recorded; the freeze rules over the annex and has no exemption.
- C1-V3 (N-2) the C10 unit test used a synthetic reference, so the frozen reference was never exercised against the
  frozen sentinel frames. Recorded with C1-V1 as the gap that let the contradiction through.
- C1-V4 (N-3, N-4) no action: both sides hold the same 64 signals; the pre-marker store hashing reads bytes, not bars.
- Verdict stands: C1 STOPPED (C10), verified.

## Harness v12 (review: APPROVE WITH FIXES, 0 BLOCKING, 2 SHOULD FIX, NOTEs; ruled 23:36)

- V12-R1 (F-1, SHOULD FIX) accepted and fixed before any use: data/pull_hist.py `_check_args` refuses
  `--buy --plan ext2010h` without `--roots` (RC_REFUSED before the preflight, any gate or vendor call); test
  tests/test_e17_v12_pull_hist.py::test_an_ext2010h_buy_without_roots_is_refused_before_the_preflight, and the zero-cap
  test no longer calls a roots-less buy. 70 passed (23:35).
- V12-R2 (F-2, SHOULD FIX) accepted: when the caps are set from the fresh quote, tests/test_e14_config_v10.py (hashed
  by the manifest) also pins STAGE_E17_EXT2010H_SESSION_ID and E17_EXT2010H_SESSION_CAP_USD.
- V12-R3 (N-1, concurrency) the caps are global and the ledger is re-read at every authorize, so k concurrent buy
  processes can overshoot the session cap by at most (k - 1) in-flight chunks. The lead bounds that by the largest
  fresh chunk quote of the selection, not the $3.00 request cap: k is chosen after the quote so that (k - 1) x the
  largest chunk quote x 1.03 fits in the budget left after the selection (A1's $124.00 is the hard bound), else the
  buy runs with fewer processes.
- V12-R4 the coder's points: the new v12 test files are not in the manifest's test patterns (changing the patterns is
  a screening/ edit outside step 8's list; the hashed test_e14_config_v10.py carries the cap pins, V12-R2); the
  ext2010h quote and buy run through `python -m data.pull_hist` (data/pull_step2.py is outside the diff list); the
  pre-listing symbology of TN, RTY and HE cannot be exercised with fakes (fail-closed: a failed metadata fetch or
  store build puts the root on the fallback list with its reason, A5); the "E.14 ... harness v10" labels in ledger
  notes and ext2010h store metadata are cosmetic and left (step 8's list fixes the diff).
- V12-R5 the ext2010h quote ran on the uncommitted, reviewed v12 tree with the caps at 0.00 (quote-only takes no
  harness sha; E.12's open choice 7 is the precedent), so that the caps go into the single v12 commit the prompt names.
- V12-R6 (caps follow-up, Fable APPROVE 00:12) the selection, the caps (355.38, 65.82), the F-1 fix and the manifest
  ece91ae8... verified from the ledger lines; NOTE N-8 (a uniform +3% overage would stop the buy $0.14 short,
  fail-closed: a stopped root's store cannot be built and it joins the fallback list with its reason) accepted.

## The user's message during the Part 2 buy (about 01:21 on 2026-10-10; ruled 01:22)

- B-2 The user wrote "theres 125 total on the account. use all if needed" while the four ext2010h buy processes were
  running (registration r002-E16 at 00:30:15). A3's greedy rule rerun with $125.00 in place of $124.00 gives
  B = $67.182668 and the same 11 roots (after UB $9.747611 left: YM $10.817687 skipped; TN, RTY, LE taken; HG and 6S
  skipped; HE taken; $1.222668 left; ZM, the cheapest skipped root, needs $5.829681). Nothing changes: the selection
  and the fallback list were fixed and registered before the purchase (A3, A5; the list may only grow afterwards),
  the caps stay as committed in v12 (worst case $123.99), and the expected total is $121.86.

## H1-H5 verdict recomputation (VerdictVerifier-FableXHigh: H1-H4 VERIFIED, H5 VERIFIED WITH NOTES, 01:40-02:03; ruled 02:05)

- H-V1 Every number entering the five verdicts is verified: series rebuilt from the units files (sigma and the
  risk-unit values reproduced on all 107,506 traded rows), every statistic, Holm step, pass-bar check and DSR equal
  to <= 2.8e-14; 714 units spot-checked against the stores with 0 mismatches (fills, prices, signals, gross, base,
  stress and slip150 costs). All five FAIL; N = 478. The verdicts stand as written in reports/stage_e17_runs/verdict.json.
- H-V2 (NOTE 1) H5's base sd 5.97 comes from four grid dates where a sparse component (H2 or H3) switches on against a
  near-zero trailing-60 sigma (59 zeros and one entry cost): the pre-registration's wording applied literally. Without
  the top 5 dates the sd is 0.63 and t about -13; the mean is negative in every variant, so the verdict is unaffected.
  Recorded for the user: the frozen H5 scaling is fragile for sparse components, and any reuse of the H5 form must
  guard sigma (for example a floor or a minimum count of non-zero entries) in a new pre-registration.
- H-V3 (NOTE 2) H3's flip costed per contract (2 x ceil) follows the spec's "per side ... at size one"; at most 1 cent
  on 317 units; accepted.
- H-V4 (NOTE 3, NOTE 4) the uncalibrated-bucket and event-window counts are explained and reproduced on the sampled
  units; the exclusion counters other than traded and warm-up, and the calendars themselves, cannot be verified from
  the outputs (no excluded candidate is written to the units files). Recorded; no change.
- H-V5 (open choice 17) the lead's focus points quoted three run numbers before the recomputation; Fable rebuilt every
  number from the units and the stores before reading the result statistics or verdict.json, so the verification is
  independent in its computation.
