# Stage E.18: C1b's text and code against C1's freeze (line-by-line diff)

Lead, Stage E.18 Step 1 (revised after the Step 2 review), 2026-10-10 (PDT). Inputs: C1's freeze reports/stage_e14_prereg_C1.md (sha256
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b); C1b's text reports/stage_e18_prereg_C1b.md (sha256 35b936fb33c32f29365cdd77ce1f8642330270a827795dac4059403d78075dcd at the time of this diff; the freeze manifest
reports/stage_e18_freeze.json records the final one). Generator: reports/stage_e18_briefs/make_c1b_text.py (sha256 f26bc780d4ea57b292997db69f2ce86907296c07085815084b9911c7ef5d0ea0), 15 exact replacements on
C1's freeze, each required to match exactly once, plus section 13 appended. This file's generator:
reports/stage_e18_briefs/make_diff_doc.py.

Revision after DiffReviewer-FableXHigh (reports/stage_e18_review.md; rulings reports/stage_e18_rulings.md R-1..R-5):
section 3's exempt criterion no longer says "as in training" (S-1) and says why CL qualifies (N-1); section 2 names
H5 beside H1 and H4 (N-2); section 11 names E.17's ext2010h session constants in data/config.py (N-3); section 9
step 7 names the result path (N-6). No code changed in the revision.

## 1. What each change is (the prompt's THE ONE FIX: item 1 ids and registration, item 2 the C10 clause, item 3 every other feature unchanged)

| # | Where | Item | Change |
|---|---|---|---|
| 1 | title | 1 | "(C1)" -> "(C1b, C1 re-registered)" |
| 2 | status block | 1 | C1b's provenance (C1's freeze sha256, the draft's), C1's closed attempt cited, new registration N 478 -> 480, harness v12, no purchase; the 2010-2019 bytes now on disk were read in E.17 (section 2) |
| 3 | section 2, "Never read before the test" | 1 | C1's sentence "no program file has read NG or any leg before 2019-05" became false in E.17 (store builds, C1's stopped run, the base-rule batch on these stores: H1, H4 and the composite H5 cover NG); the bullet now says what was read and why none of it changes C1b. Without this, C1b's text would assert something false. |
| 4 | section 3, C10 bullet | 2, 3 | "unless the feature is on the exempt list below"; the criterion (section 2's not-applicable-by-design treatment of an unlisted or own-cluster leg); the exempt list g17_mbt (MBT not listed; BTC is not a leg) and g17_cl (own cluster lead; reference 0, so a no-op); "every other feature keeps C10 exactly as C1 had it"; the other legs' listing state |
| 5 | section 5 | 1 | T1, T2 "registered as C1b-T1 and C1b-T2" |
| 6 | section 6 | 1 | N 478 -> 480 in Stage E.18; C1's registration stays counted |
| 7 | section 8, pass | 1 | DSR at N = 480 |
| 8 | section 8, fail | 1 | N is 480 |
| 9 | section 9 heading | 1 | "C1b's steps as the Stage E.18 prompt orders them" |
| 10 | section 9 later-session steps | 1 | C1's steps 5-8 as done in E.17; C1b's steps 5-8 (review, dry check, freeze commit; register; evaluate once behind a new marker, result path named; verdict then descriptive); no quote, no purchase |
| 11 | section 10 heading | 1 | "(V25, V26; C1b: V31)" |
| 12 | section 10 item 5 | 1 | V31 |
| 13 | section 11 heading | 1 | "what Stage E.18 verifies first" |
| 14 | section 11, new bullet | 1 | C1b's code (c1_replication/c1b.py, tests/test_c1b.py); every C1 file unchanged |
| 15 | section 11, last paragraph | 1 | what Stage E.18 verifies before registering: C1's freeze inputs except the harness manifest (replaced by v11 and v12 in E.17), C1's freeze and this file in git, the E.12 state copy, the model and payloads; harness v12 by its preflight and the list of its differences from v10; the stores and calendars against E.17's hash files; no quote, no purchase |
| 16 | section 13 (new) | 1 | the list of changes |

Unchanged byte for byte: sections 1, 4, 7 and 12, and in sections 2, 3, 5 and 8 every line not listed above (the
model M1, q, the windows, the vehicle and legs, the C7 sentinel frames, the trade rule and exclusions, the calendars
and C12, the costs, the pass bar, the power and prior, the outcome readings apart from N).

## 2. The exempt list: listing dates and section 2 only

The applicable-row counts that E.17's stopped run printed (reports/stage_e14_c1_result.json, guards.C10; counts only,
no values) are known to the lead. C1b's design change does not use them: the exempt list follows from the listing
state of each leg in 2010-06-07..2019-04-30 and from section 2's text, and would be the same whatever those counts
were. Every leg and non-leg input of the 30 features live on NG rows in E.12 (reference counts from
reports/stage_e14_c1_model.json, E.12's training panel, not the test window):

| Input | Features live on NG rows in E.12 that read it (E.12 reference h60 / hF) | State on every date of 2010-06-07..2019-04-30 | C10 in C1b |
|---|---|---|---|
| NG (own path) | cp1_ret, cp2_brk, cp2_range, cp3_clv, g01-g11, k4_ovr_pct, k4_ovr_ret, k4_ngpre_* (with the NGS table) | listed (the vehicle; annex ruling C5) [launch date unverified] | applies |
| NQ | g17_nq (2453 / 2345) | listed [launch date unverified; annex C5] | applies |
| ZN | g17_zn (2457 / 2341) | listed [unverified; annex C5] | applies |
| 6E | g17_6e (2450 / 2354) | listed [unverified; annex C5] | applies |
| GC | g17_gc (2423 / 2311) | listed [unverified; annex C5] | applies |
| ZC | g17_zc (2468 / 2351) | listed [unverified; annex C5] | applies |
| MBT | g17_mbt (87 / 84; 29 trade dates 2024-01-04..2024-02-29, Fable E.17 C1 check 1) | NOT listed: CME Micro Bitcoin futures launched 2021-05-03 (verbatim quote, reports/stage_e18_briefs/pages/LOG.md). BTC (from the trade date 2017-12-18) is not a leg: no feature reads BTC | exempt (section 2: "MBT is not listed (n/a by design)") |
| CL | g17_cl (0 / 0) | listed, but NG's own cluster lead (K4): generic.py `_lead` sets app 0 on own-cluster rows | exempt; a no-op (reference 0; section 2: "CL is never live on NG rows") |
| MES | none (no covered signal reads it; P-1a) | n/a | n/a |
| Release calendar (NGS, WPSR, FOMC) | g13_min_to_rel, g14_min_since_rel, g15_rel_day, k4_ngpre_msince, k4_ngpre_mto | published on every week of the window; sourced in E.14 (NGS 470, WPSR 470, FOMC 72; reports/stage_e14_calendars.md) | applies |
| Group calendars, D6 sessions, energy full sessions | g12_dow, g16_month_end, the clock, g09, k4_ovr_* reference dates | sourced in E.14, 0 unsourced trade dates in the window; energy full sessions 2,250 | applies |

No other input of a live feature is absent by design in the window, so no third feature can meet C1's
contradiction (live in E.12, absent by design in 2010-2019). Features with a zero E.12 reference (34 of 64, g17_cl
among them) are never reached by C10 under C1's rule or C1b's. DiffReviewer-FableXHigh traced all 30 independently
(reports/stage_e18_review.md, check 3).

## 3. The code change

- New: c1_replication/c1b.py (runs the frozen c1_replication.evaluate.run inside `c1b_profile()`, which swaps
  evaluate's TEST, TEST_IDS, HORIZON_OF, c10_check and preconditions for C1b's and restores them; c10_check is C1's
  function called on the reference less C10_EXEMPT; preconditions is C1's plus the C1b record in the marker and
  result; the CLI defaults to C1b's freeze and marker paths). New: tests/test_c1b.py (74 tests).
- Every C1 file is unchanged (c1_replication/*.py other than c1b.py, tests/test_c1_*.py, tests/_c1_*.py): the E.14
  freeze-inputs list still verifies them (start checks, reports/stage_e18_briefs/start_checks.txt).
- Why not an edit in place (c10_check lives in c1_replication/evaluate.py): editing evaluate.py or constants.py
  would change C1's frozen code (hashed in the E.14 freeze-inputs list and in C1's result), break C1's own tests
  (which pin C1's ids and marker) and make C1's closed attempt irreproducible from its files. The new module leaves
  all of that intact and confines C1b's difference to one file. Lead decision D-1.
- git status of code paths at the time of this diff:
```
?? c1_replication/c1b.py
?? tests/test_c1b.py
```

## 4. The text diff (`diff -u reports/stage_e14_prereg_C1.md reports/stage_e18_prereg_C1b.md`)

```diff
--- reports/stage_e14_prereg_C1.md	2026-10-05 03:28:19.127546490 -0700
+++ reports/stage_e18_prereg_C1b.md	2026-10-10 12:14:38.558454057 -0700
@@ -1,13 +1,16 @@
-# Pre-registration FROZEN: backward NG replication of the E.12 Gate 0 near-miss (C1)
+# Pre-registration FROZEN: backward NG replication of the E.12 Gate 0 near-miss (C1b, C1 re-registered)
 
-Status: FROZEN by the Stage E.14 lead on 2026-10-05, from the draft reports/stage_e13_prereg_ngrepl.md (sha256
-a16e860003a80806d97ff32e08e1265ae8feb1acb236153064bf32fb60714f43) with the user's decisions V25 item 1 and V26
-applied, the Stage E.14 Task 1-2 results recorded (section 11) and the FreezeReviewer's required changes (listed
-in section 12). Nothing else changed. FROZEN, AWAITING FUNDS: this test is NOT registered in Stage E.14. Its
-registration (+2 on whatever N then is: 471 -> 473 if nothing else registers first), fresh quote, purchase, store builds and single evaluation happen in a later session,
-under this freeze, with harness v10 or a later harness that changes only ACCOUNT_2_CAP_USD and the session caps
-(section 11). This file's sha256 is written into reports/stage_e14_STATE.md. No 2010-2019 byte of any root exists
-on disk or was read to write it.
+Status: FROZEN by the Stage E.18 lead on 2026-10-10. This file is C1's freeze reports/stage_e14_prereg_C1.md (sha256
+afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b), which the Stage E.14 lead froze on 2026-10-05 from
+the draft reports/stage_e13_prereg_ngrepl.md (sha256 a16e860003a80806d97ff32e08e1265ae8feb1acb236153064bf32fb60714f43),
+with exactly the Stage E.18 prompt's one fix (the user's decision V31) and the bookkeeping a new registration needs.
+Section 13 lists every change; reports/stage_e18_c1b_diff.md shows them line by line. C1's registered attempt
+(r001-C1, N 471 -> 473, Stage E.17) stopped at its guard C10 before any statistic existed and stays closed
+(reports/stage_e14_c1_result.json; reports/E.17_RETURN.md section 3). C1b is a new registration (N 478 -> 480) in
+Stage E.18, evaluated once on the six stores bought and built in Stage E.17, with harness v12; nothing is bought.
+This file's sha256 is written into reports/stage_e18_freeze.json and reports/stage_e18_STATE.md. The 2010-2019
+bytes now on disk were read in Stage E.17 as section 2 states; C1b's one change does not depend on anything read
+there (section 3).
 
 Source of the design: reports/stage_e13_ng_replication_draft.md (ReplicationDesigner-OpusXHigh, every code claim
 cited by file:line; sha256 9685fe802ee36b534b32171fdfb8d7def78c2ddba8d48c263c4dab0ff50d20bf), with the lead's
@@ -32,8 +35,16 @@
   ledger's error text). The fixed start applies to every root, with no volume read (ruling C5). The end is the
   quote end, with no May-2019 splice (ruling C6). First rows come after the warm-up, about late December 2010 to
   January 2011: sigma_X,d needs 20 dates, G9 120, z-scores 60 (annex section 5).
-- Never read before the test: no program file has read NG or any leg before 2019-05 (annex section 5, evidence
-  list). The test window is never summarized, plotted or printed before the single evaluation (section 9).
+- Never read before the test (C1, Stage E.14): no program file had read NG or any leg before 2019-05 (annex
+  section 5, evidence list). Read since, in Stage E.17, before C1b's evaluation: the store builds (counts only:
+  bars, trade dates, exclusions); C1's stopped run, which built the test window's features and printed every
+  feature's applicable-row count and the panel's row counts, with no value, no return and no statistic
+  (reports/stage_e17_review.md, C1 check 4); and the base-rule batch E16-H1..H5, whose own frozen rules read these
+  six stores (H1 and H4 report per-product results, and their composite H5 a combined one, whose windows include
+  NG's 2010-07..2019-04 bars). None of it
+  changes C1b: every parameter of sections 3 to 5 was frozen on 2026-10-05, before any 2010-2019 byte was bought,
+  and C1b's one change (section 3, C10) follows from listing dates and section 2 alone. Beyond those reads, the
+  test window is never summarized, plotted or printed before the single evaluation (section 9).
 - Training (already read, used only to fit the frozen model and reproduce q): the E.12 phase-1 panel,
   2019-05-06..2024-02-29, all 27 Gate 0 products, from E.12's persisted state (annex sections 2 and 4).
 
@@ -62,10 +73,29 @@
   holiday or session status cannot be sourced at "cme" or "secondary" grade is excluded and counted. The run
   stops if more than 2% of dates are excluded this way (ruling C12). NGS drop rules as in E.5 (ruling C13).
 - Guard against silently n/a features: applicable-row counts per feature, printed without values. The run stops
-  if any feature live in E.12 has 0 applicable rows (ruling C10). These counts are computed from the test window's
-  features, so they read the test bars (no values printed). A C10 stop therefore CLOSES this registered attempt.
-  Any calendar correction and rerun is a new registration, with its tests counted in N again (Fable R-12, lead
-  ruling).
+  if any feature live in E.12 has 0 applicable rows (ruling C10), unless the feature is on the exempt list below.
+  These counts are computed from the test window's features, so they read the test bars (no values printed). A C10
+  stop therefore CLOSES this registered attempt. Any calendar correction and rerun is a new registration, with its
+  tests counted in N again (Fable R-12, lead ruling).
+  Exempt (C1b, V31): a feature whose leg section 2 already makes "not applicable" on every NG row of the test
+  window, the treatment section 2 gives an unlisted or own-cluster leg, as training gave MBT before its listing.
+  The list is decided from listing dates and section 2 alone, never from a count of the test window, and holds
+  exactly two features (the Stage E.18 prompt and V31 name both; CL is listed, so for CL the operative test is
+  section 2's "not applicable by design", the prompt's stated reason):
+  - g17_mbt, leg MBT: no MBT contract was listed on any date of 2010-06-07..2019-04-30. CME launched Micro Bitcoin
+    futures on 2021-05-03 ("today launched Micro Bitcoin futures", CME press release of May 3, 2021) and its
+    Bitcoin futures (BTC) for the trade date 2017-12-18 ("effective on Sunday, December 17, 2017 for a trade date of
+    December 18", CME press release of December 1, 2017). BTC is not a leg of the model: no feature reads it, and
+    E.12 never read it for g17_mbt, so BTC's listing does not make MBT listed. Section 2: "MBT is not listed (n/a by
+    design)".
+  - g17_cl, leg CL: listed throughout the window, but CL is the lead of NG's own cluster K4, and G17 never applies
+    a cluster's own lead on that cluster's rows (ml_route_v2/signals/generic.py, ``_lead``). Section 2: "CL is never
+    live on NG rows". Its E.12 reference count is 0 on both horizons, so C1's rule never reached it and this
+    exemption changes nothing for it.
+  Every other feature keeps C10 exactly as C1 had it: 0 applicable rows stops the attempt and closes it. Every
+  other leg read by a feature live on NG rows in E.12 (NQ, ZN, 6E, GC, ZC) was a listed CME Group contract on every
+  date of the window (launch dates before 2010 [unverified]; annex ruling C5: "all six were mature contracts in
+  2010").
 
 ## 4. Costs
 
@@ -76,7 +106,7 @@
 
 ## 5. Pass bar (fixed)
 
-Two tests, T1 = NG h60 and T2 = NG hF, each with Gate 0's own statistic (gate0._b_test: per-date mean of the gross
+Two tests, T1 = NG h60 and T2 = NG hF (registered as C1b-T1 and C1b-T2), each with Gate 0's own statistic (gate0._b_test: per-date mean of the gross
 P&L in vehicle ticks, t_B = mean / (sd / sqrt(n_dates)), one-sided p from Student's t with n_dates - 1 degrees of
 freedom). A test passes iff:
 1. mean gross g >= 1.5 x c(NG,h);
@@ -89,9 +119,8 @@
 ## 6. Trial count
 
 +2 at registration, whatever the outcome (ruling C21), in the append-only trial registry
-ledger/trial_registrations.jsonl, in the later session. Test C2 stopped in Stage E.14 before its registration
-(its power rule), so N is still 471 and C1's registration takes it to 473 unless another test registers first
-(then +2 on that N). The q reproduction and the M1 fit are
+ledger/trial_registrations.jsonl, in Stage E.18: N 478 -> 480. C1's own registration (r001-C1, N 471 -> 473,
+Stage E.17) stays counted; its attempt is closed. The q reproduction and the M1 fit are
 not tests. The descriptive outputs (the realized share above q, the long/short split, trades per year), printed
 after the verdict, add nothing to N (ruling C15).
 
@@ -112,14 +141,15 @@
 - **Pass:** the frozen model's NG predictions carried a gross edge of at least 1.5x D8 cost at p <= 0.025 in a
   disjoint decade with a different supply regime. That is real evidence the near-miss was not only selection
   (joint null probability about 0.018). It is still not tradeable: the bar is gross, the costs are 2025-26
-  calibrations, it clears none of the verdict bars (t >= 3, DSR at N = 473, PBO), and only one NG contract at h60
+  calibrations, it clears none of the verdict bars (t >= 3, DSR at N = 480, PBO), and only one NG contract at h60
   on a 150K XFA fits. A pass justifies one more pre-registered, net, NG-only design with its own N and a forward
   or holdout test before any money. NG's holdout-2 chunks are owned and sealed, and are opened only under a
   registered Stage D.2.
 - **Fail:** the NG near-miss is closed. Gate 0's reading stands, nothing more is built on v2's model, and N is
-  473. A fail cannot separate "never real" from "real only in the 2019-2024 LNG-era regime".
+  480. A fail cannot separate "never real" from "real only in the 2019-2024 LNG-era regime".
 
-## 9. Order of events (rulings C9, C20; amends L4-7; as the Stage E.14 prompt orders them)
+## 9. Order of events (rulings C9, C20; amends L4-7; as the Stage E.14 prompt orders them; C1b's steps as the
+Stage E.18 prompt orders them)
 
 In Stage E.14 (done before this file was committed, except step 4, which follows the commit):
 1. The calendar probe: 2012's energy calendar and EIA NGS table at evidence grade; C1 is dropped if more than 2%
@@ -131,15 +161,22 @@
    pickles and the build JSON, with a read-only copy; ruling C17).
 4. Fit M1 and reproduce q (c1_replication.q_m1). Write M1's coefficient hash and q into Stage E.14's STATE and
    reports/stage_e14_c1_model.json, before any 2010-2019 byte is bought.
-In a later session, under this freeze (section 11 lists what it verifies first):
-5. Register T1 and T2 (N 471 -> 473, or +2 on N then) with this file's sha256.
-6. Quote fresh (logged first), then buy NG and the five legs after the user's acct-2 top-up and a harness that
-   differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else. The store builds print counts only.
-7. Compute the replication features and run the evaluation once, behind a run-once marker
-   (c1_replication.evaluate; the gate0_stage.py:260-264 pattern).
+In Stage E.17, under C1's freeze, C1's steps 5-8: registration r001-C1 (N 471 -> 473); the fresh quote and the
+purchase of NG and the five legs under harness v11, as C1's step 6 allowed; the store builds (counts only); the one
+evaluation, STOPPED at C10, the attempt closed.
+In Stage E.18, under this freeze (section 11 lists what it verifies first), in this order:
+5. Before the freeze: a Fable review of this file's diff against C1's freeze; the dry check (the amended C10 on
+   E.12's reference counts against synthetic sentinel frames with MBT and CL absent and every other leg present,
+   then with one non-exempt leg removed; no test-window bar read; reports/stage_e18_dry_check.md); the freeze
+   commit.
+6. Register C1b-T1 and C1b-T2 (N 478 -> 480) with this file's sha256. No quote and no purchase: the six ext2010
+   stores of Stage E.17 are used.
+7. Compute the replication features and run the evaluation once, behind a new run-once marker
+   (reports/stage_e18_c1b_RUN_ONCE.json; the result reports/stage_e18_c1b_result.json; c1_replication.c1b, which
+   runs c1_replication.evaluate with C1b's ids and the amended C10; the gate0_stage.py:260-264 pattern).
 8. Report the verdict, then the descriptive outputs.
 
-## 10. Decisions made by the user before the freeze (V25, V26)
+## 10. Decisions made by the user before the freeze (V25, V26; C1b: V31)
 
 1. **V24, two computations on the 2019-2024 training panel** (V25 item 1): both allowed. (a) Reloading E.12's
    persisted out-of-fold predictions and reproducing NG's rows to 1e-9 to fix q (ruling C4). (b) The single
@@ -150,9 +187,12 @@
    funds. Stage E.14 quotes C1's set only ($0.00 ledger lines) so the user knows the top-up.
 3. **~/.cache/propexp_e12_phase1** was kept; Stage E.14 hashed it and made a read-only copy (section 11).
 4. **The calendar probe first** (V25 item 4): run inside Stage E.14 with the rule of section 9 step 1.
+5. **V31** (2026-10-10, after Stage E.17): C1 stopped at C10 on g17_mbt. The user chose this re-registration,
+   C1b, identical to C1 except that C10 exempts legs with no listed contract in the test window (MBT; CL),
+   which section 2 already treats as not applicable; N 478 -> 480; no purchase.
 
 
-## 11. Frozen inputs, Stage E.14 results, and what the later session verifies first
+## 11. Frozen inputs, Stage E.14 results, and what Stage E.18 verifies first
 
 Recorded in Stage E.14 (reports/stage_e14_STATE.md holds the times):
 - **Probe (section 9 step 1):** 2012 energy 0 of 258 trade dates unsourced; 2012 NGS 0 of 52 release dates
@@ -190,14 +230,21 @@
   is unsourced, or that holds an unsourced release. Rule H-1 is applied literally (rules/sessions.py lines
   20-40), so the equity halts of 2012-10-29/30 and 2018-12-05 give Topstep rows. The hist calendar loader accepts
   a Friday-to-Monday session handover and a day holding both an early halt and a late open (grains).
+- **C1b's code (Stage E.18):** c1_replication/c1b.py and tests/test_c1b.py, hashed in reports/stage_e18_freeze.json.
+  Every C1 file is unchanged: c1b runs the frozen c1_replication.evaluate with C1b's ids and the amended C10.
 
-The later session, before anything else: (1) verify, by script, every entry of reports/stage_e14_c1_freeze_inputs.json (recording the result in its STATE
-before registering), that this file is committed and unchanged in git (`git ls-files --error-unmatch` and
-`git diff --quiet HEAD --` on it), the
-E.12 state copy against its manifest, the model JSON and both M1 payloads against the hashes recorded in Stage
-E.14's return; (2) verify that its harness differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else; (3) quote fresh, and stop if the
-quote x 1.03 exceeds acct-2's headroom; then register, buy, build and evaluate once, in that order
-(c1_replication/README.md gives the commands).
+Stage E.18, before registering: (1) verify, by script, every entry of reports/stage_e14_c1_freeze_inputs.json
+(recording the result in its STATE) except reports/stage_e2b_harness_freeze.json, the harness manifest that
+harnesses v11 and v12 replaced in Stage E.17 (item 2); that C1's freeze and this file are committed and unchanged in
+git (`git ls-files --error-unmatch` and `git diff --quiet HEAD --` on each); the E.12 state copy against its
+manifest; the model JSON and both M1 payloads against the hashes recorded in Stage E.14's return; (2) verify harness
+v12 (ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32, Stage E.17) by its preflight. v12 differs
+from v10 in data/config.py (the caps and E.17's ext2010h session constants), data/pull_hist.py (plan ext2010h), data/hist_store.py (its docstring and the
+ext2010h choice of its CLI), data/hist_calendar.py (a seventh group, livestock, and its docstring), the livestock
+calendar file and tests; none of these changes the code C1b's evaluation calls for plan ext2010 (c1_replication
+names its six groups itself); (3) verify the six ext2010 stores against reports/stage_e17_c1_store_hashes.json and
+the calendars against reports/stage_e17_c1_calendar_hashes.json (Stage E.17's files). Then register and evaluate
+once, in that order (c1_replication/c1b.py gives the command). No quote and no purchase.
 
 ## 12. Changes from the draft (every one)
 
@@ -214,3 +261,25 @@
 8. Sections 9 and 11: the later harness may also change the test assertions that pin the two caps
    (FreezeReviewer F-01); section 11 step (1) checks the inputs by script and the freeze file's git state
    (F-04, F-05).
+
+## 13. Changes from C1's freeze (C1b; every one)
+
+The Stage E.18 prompt's one fix has three items: (1) the ids C1b-T1 and C1b-T2 and a new registration (N 478 ->
+480), C1's closed attempt cited; (2) C10's exemption clause; (3) every other feature keeps C10 as C1 had it.
+1. Title: C1b (item 1).
+2. Status block: C1b's provenance, C1's closed attempt, the new registration, no purchase (item 1).
+3. Section 2, "Never read before the test": what Stage E.17 read since C1's freeze, so the statement stays true
+   (item 1: C1's attempt and E.17 are cited).
+4. Section 3, C10: the exempt list, g17_mbt and g17_cl (item 2), and "every other feature keeps C10 exactly as C1
+   had it" with the listing state of the other legs (item 3).
+5. Section 5: T1 and T2 are registered as C1b-T1 and C1b-T2 (item 1).
+6. Section 6: N 478 -> 480 in Stage E.18; C1's registration stays counted (item 1).
+7. Section 8: N = 480 in the pass and fail readings (item 1).
+8. Section 9: C1's steps 5-8 as done in Stage E.17; C1b's steps 5-8 in Stage E.18, with no quote or purchase and a
+   new marker (item 1).
+9. Section 10: the user's decision V31 (item 1).
+10. Section 11: C1b's code; what Stage E.18 verifies first, with harness v12 as the Stage E.18 prompt fixes it and
+    no quote (item 1).
+11. Section 13 added: this list.
+Nothing else changed: sections 1, 4, 7 and 12, the model M1, q, the windows, the calendars, the trade rule, the
+exclusions, the costs and the pass bar are C1's, byte for byte.
```
