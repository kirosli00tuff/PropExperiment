# Stage E.20 rulings (lead)

All times PDT. One section per review or verification, in the order they happened.

## 1. Lead rulings on the H6 build's stop items (h6_build.md section 1; ruled 11:10-11:12)

- S1 (registry names): the frozen registry (screening/trial_registry.py lines 48-49) allows no hyphen
  in a label. The prompt's E20-H6-T1..T3 are registered as label E20H6, ids E20H6-T1, E20H6-T2,
  E20H6-T3 (the E16 pattern). Prereg section 8 and h6_rod/constants.py changed together.
- S2 (shortened days): the frozen engine's flatten on an early-close date is the early close minus
  Topstep's 30-minute lead in 2019-2025 (rules/sessions.py TOPSTEP_EARLY_CLOSE_LEAD), so F = C-30 and
  every shortened-day entry is refused by the engine. The prereg text (section 3, 7a) was corrected
  to say so; the code already followed the engine.
- S3 (engine lead-in): ENGINE_LEAD_IN_DATES = 1. Each engine run begins one equity trade date before
  its window, with no entry on it, so the first window date has the D9.7 prior-settlement reference
  like every other date. The text was silent; this reading makes every eligible date tradeable alike.
- T3_REGISTERED = True (the NQ reader's GEX ruling, accepted); GEX_CSV_SHA256 = E.14's copy.
- Two tests in tests/test_h6_rod_run.py that pinned the "as shipped" refusals were updated to the
  ruled state (the ruled names accepted, a hyphenated label refused; the CLI refuses a wrong freeze
  sha256 and no longer for T3_REGISTERED).

## 2. Rulings on the H6 review (reports/stage_e20_review_h6.md: APPROVE WITH FIXES; 0 BLOCKING, 3 SHOULD FIX, 7 NOTE; review file 15:29, returned 15:30; rulings 15:31-15:33)

The first H6Reviewer spawn (11:12) stopped at 11:21 on the session usage limit with no output; the
review was re-spawned fresh at 15:12 after the limit reset (pause 11:21-15:10).

| Finding | Severity | Ruling | Fix |
|---|---|---|---|
| H6R-1 post-marker exceptions leave the marker and no result | SHOULD FIX | accepted | h6_rod/run.py: a catch-all after the marker writes every test STOPPED with the traceback, then the result file; a test injects a RuntimeError after the marker (H6Coder follow-up) |
| H6R-2 header says GEX values unread; section 6 has a sign count | SHOULD FIX | accepted | header amended; section 6 records who (lead), when (10:56:48 PDT), what was read (date and gex columns, sign only) and the count's inputs |
| H6R-3 section 7a omits two of the NQ reader's differences | SHOULD FIX | accepted | 7a adds the prior close after an early-close day, the roll difference, and shortened days in T2's median |
| H6R-4 day after a futures-only holiday has no GEX row | NOTE | accepted (text) | section 3 names the case and its approximate count |
| H6R-5 T2 warm-up reading is literal | NOTE | no change | the literal reading stands (F2 allows only the 60 trade dates) |
| H6R-6 registry names differ from the prompt's | NOTE | no change | the mapping is stated in prereg section 8 and will be in the return and progress entry |
| H6R-7 manifest need not list the tests | NOTE | accepted | the lead's manifest builder lists tests/test_h6_rod_*.py and tests/_h6_rod_synth.py |
| H6R-8 two wording points | NOTE | accepted (first point) | section 1 now separates the paper's window (C-30 to C) from the traded window; the T2 attribution stays as F5 words it, corrected in 7a |
| H6R-9 member.trading_windows unused | NOTE | accepted | comment added (H6Coder follow-up) |
| H6R-10 weak CLI refusal test | NOTE | accepted | the test also asserts "freeze manifest" in stderr (H6Coder follow-up) |

Fixes applied and checked by the lead at 15:33: H6R-1, H6R-9, H6R-10 in h6_rod/run.py, member.py and tests/test_h6_rod_run.py (h6_build.md section 7); the text fixes in the prereg; `uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py`: 85 passed; ruff clean. No BLOCKING finding; no re-review needed: the lead read the H6R-1 change (run.py evaluate, the post-marker try block), the member.py comment, the new and changed tests, and wrote the text fixes.

## 3. Rulings on the H6 verification (reports/stage_e20_review.md "H6 verification": VERIFIED WITH NOTES; 0 BLOCKING, 1 SHOULD FIX, 5 NOTE; returned 15:55, rulings 15:56)

- Verdict stands as evaluated and independently reproduced: E20-H6-T1 FAIL, T2 FAIL, T3 FAIL; no Holm
  rejection. The verifier's bar-level reconstruction matches every trade to the cent except the two
  MLL liquidations (T1 2023-11-30, T2 2021-10-07), which the prereg allows (section 3) and which
  fully explain the small t differences (T1 -0.528 lead vs -0.543 with C-2 exits; T2 -0.948 vs
  -1.010). Order of events verified (prereg 15:33:45, freeze 15:35:17, commit 15:35:53, registration
  15:36:20, marker 15:36:38, result 15:38:15).
- H6V-2 (SHOULD FIX, descriptive only): accepted as a reading note. The result's mll.breach_dates is
  empty because h6_rod/report.py fills it from DayClose events only; the MLL breach dates are the
  result's mll_liquidation_fill_dates: T1 2023-11-30, T2 2021-10-07 (T3 none). No code change (the
  code is frozen and the evaluation ran once); the return and progress entry carry this note.
- H6V-1, H6V-3 to H6V-6 (NOTE): accepted as recorded; no action.

## 4. Rulings on the plan review (reports/stage_e20_review_plan.md: BLOCK on PR-1; 6 SHOULD FIX, 8 NOTE; returned 16:18; rulings 16:19-16:41)

| Finding | Severity | Ruling | Fix (reports/stage_e20_plan.md) |
|---|---|---|---|
| PR-1 2010-2019 member-table swaps unspecified | BLOCKING | accepted | BackwardTables-OpusXHigh built the swap table (backward_swap_table.md/.json); section 10.1 lists the sources, mechanisms and verdicts (no feature NO-SOURCE) and the lead's seven rulings on its open items; the Step 6 sentinel dry check (section 13) runs before the search freeze and drops any feature that fails |
| PR-2 k2_fomc_mto not-applicable by design for 2010-2013 FOMC days | SHOULD FIX | accepted | dropped: KEPT 34, DROPPED 33 (section 5.1; product summary 1.6) |
| PR-3 above-4.0 rule self-contradictory | SHOULD FIX | accepted, reading (a) | above 4.0 fails item 3; the audit runs for the record; a clean audit does not convert it (section 9) |
| PR-4 composed builder bypasses frozen checks | SHOULD FIX | accepted | section 6 names every re-applied check; section 13 plants a shifted root |
| PR-5 B1 construction and price-limit convention | SHOULD FIX | accepted | section 10: the fixed-D score_split construction (the screen's), the excluded engine mechanics named, E.16 F-07's single-price-bar diagnostic kept in the statistic |
| PR-6 ruin deferral decided after the screen | SHOULD FIX (low) | accepted | section 9: not computed on a fail; on a pass the adapter is written and hashed before the B1 registration |
| PR-7 acceptance rule as applied | SHOULD FIX (low) | accepted | section 5.3: (c) carries the instrument-and-hold and governing-subsample conditions; RTY's ground (d) withdrawn |
| PR-8 backward start and end dates | NOTE | accepted | section 2 |
| PR-9 t4 structure | NOTE | accepted | section 4 |
| PR-10 guard details | NOTE | accepted | section 3 |
| PR-11 three definitions | NOTE | accepted | section 9 (PBO degenerate or NaN; V2.9's no-model rule cited; the DSR call with 528) |
| PR-12 normalization state and carried objects | NOTE | accepted | section 10 |
| PR-13 when the first search bar is read | NOTE | accepted | sections 6 and 15: the real panel is built only after the 45 registrations |
| PR-14 two test gaps | NOTE | accepted | section 13: a t4 planted-edge canary, the composed-panel shuffle null, assert_causal on the rod frames |
| PR-15 declare the row-loss sizes | NOTE | accepted | section 10.1's table |

Process: the SearchCoder (Step 6) was started at 16:21, before the PR-1 table existed, to build the parts the
plan had already fixed; it builds the swap context and the dry check from section 10.1. No fit happens before
the reviewer's recheck of the BLOCKING fix and the Step 6 dry check.

## 4b. Rulings on the plan recheck (reports/stage_e20_review_plan.md "Recheck": APPROVE WITH FIXES, BLOCK lifted; 1 SHOULD FIX (low), 2 NOTE; rulings 16:47)

- PR-1 to PR-15: FIXED per the recheck; rulings 1-7 of section 10.1 ACCEPTED-AS-RULED.
- PR-16 (SHOULD FIX, low): accepted. Ruling 4's daily cost fallback stays (E.16's convention under F2; conservative). Its reach is
  stated in 10.1 (t1 of ten vehicles, t3 of five, some exits); the Step 6 dry check computes the exact table before the search freeze;
  B1 reports the share of trades paying it.
- PR-17 (NOTE): accepted; 10.1 states the R-B1 post-step on the targets frame, its test and its separate reporting.
- PR-18 (NOTE): accepted; the dry check and B1 report ruling 2's excluded rows per root and t_index.

## 5. Rulings on the search build's open items (reports/stage_e20_briefs/search_build.md section 3; 17:13)

- Item 1, criterion 6's reading: per-product round trips per path on the nested record, flagged when the median over the 5
  paths is below 30 (the median path, as criterion 2); the other readings are reported. Not gating. Plan section 9 updated.
- Item 2: registration through the frozen CLI (screening.trial_registry register), as H6's was through h6_rod.
- Item 3: check hashes the 17 store files as bytes before the registration (no bar decoded), as H6's did. Accepted.
- Item 4: each root's first backward window date loses its rows (no prior-day bars); added to plan 10.1's declared table.
- Item 5: the frozen ports._cp3 edge case cannot arise on B1's full windows; noted.
- Item 6: PR-16's exact table copied into plan 10.1.
- Item 7: real_world and the store hashing run for the first time at the real check; any failure there is a pre-registration
  failure (nothing fitted), fixed before the registration.

## 6. Rulings on the search code review (reports/stage_e20_review_search_code.md: APPROVE WITH FIXES; 0 BLOCKING, 1 SHOULD FIX, 8 NOTE; 17:29)

- SC-1 (SHOULD FIX): accepted. `python -m pattern_search check --world` loads the real 17-root world through the frozen loaders
  (sha256, booking, holdout, embargo, store-range and roll checks, refuse_late, the grid check) before the registration, and
  computes no row, feature, panel, statistic or fit (F9: registration before any fit). Plan sections 6 and 15 record it.
- SC-2 (rod_ret across a roll, G5's frozen behaviour): accepted as stated in plan 5.2 (the G5 pattern).
- SC-3, SC-4, SC-5, SC-7, SC-9 (NOTE): accepted as recorded.
- SC-6: the search freeze manifest is built after the last plan edit; check then verifies it.
- SC-8 (B1 order of session_end_exits before apply_fallback_costs): to be enforced in the composed B1 targets step at Step 8
  (only on a passed screen).

SC-1 fix applied by SearchCoder (search_build.md section 7): check --world; 116 tests pass; ruff clean (17:35).

## 7. Ruling on the first real check --world (17:37; before any registration)

check --world refused: "REFUSED (BarGridError): NQ: 7 bars outside the open intervals, 0 with another trade date (first at
1573161300000000000)" (2019-11-07 15:15 CT). The grid assertion on real bars was the lead's PR-4 addition; it conflicts with
the frozen V2.2b text ("On real bars the session-grid check of the synthetic pipeline is replaced by the frozen loader's own
L-3 booking check") and E.12's phase-1 world (closure bars counted and kept, harness v9). Ruling: follow V2.2b; on real bars
the grid assertion is not applied and closure bars are counted (world_check.json, run results); the assertion stays for
synthetic worlds. Plan section 6 corrected; the freeze manifest (first build, sha256 66436234...) was deleted unregistered
and will be rebuilt after the code fix.

## 8. Rulings on the search screen verification (reports/stage_e20_review.md "Search screen verification": VERIFIED; 0 BLOCKING, 0 SHOULD FIX, 3 NOTE; 20:25)

- The screen verdict stands: FAIL (median-path t -1.334, PBO 0.596, annualized net Sharpe -0.826; DSR at 528 1.4e-5), recomputed
  independently from cpcv_units.jsonl to within 1e-9; one outer split and the final model refit reproduced exactly; order of
  events verified (freeze 17:42:47, check --world 17:43:36, registration 17:43:59, run 17:44:15, first unit after 17:45:10).
- SV-1 (179 structural zero dates dilute |t|), SV-2 (the DSR is uninformative for a negative Sharpe), SV-3 (no per-unit
  timestamps in cpcv_units.jsonl): accepted as notes; no action (the screen fails on all three items regardless).
