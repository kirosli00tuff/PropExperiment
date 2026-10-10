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
