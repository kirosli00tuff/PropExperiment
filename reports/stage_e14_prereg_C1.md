# Pre-registration FROZEN: backward NG replication of the E.12 Gate 0 near-miss (C1)

Status: FROZEN by the Stage E.14 lead on 2026-10-05, from the draft reports/stage_e13_prereg_ngrepl.md (sha256
a16e860003a80806d97ff32e08e1265ae8feb1acb236153064bf32fb60714f43) with the user's decisions V25 item 1 and V26
applied, the Stage E.14 Task 1-2 results recorded (section 11) and the FreezeReviewer's required changes (listed
in section 12). Nothing else changed. FROZEN, AWAITING FUNDS: this test is NOT registered in Stage E.14. Its
registration (+2 on whatever N then is: 471 -> 473 if nothing else registers first), fresh quote, purchase, store builds and single evaluation happen in a later session,
under this freeze, with harness v10 or a later harness that changes only ACCOUNT_2_CAP_USD and the session caps
(section 11). This file's sha256 is written into reports/stage_e14_STATE.md. No 2010-2019 byte of any root exists
on disk or was read to write it.

Source of the design: reports/stage_e13_ng_replication_draft.md (ReplicationDesigner-OpusXHigh, every code claim
cited by file:line; sha256 9685fe802ee36b534b32171fdfb8d7def78c2ddba8d48c263c4dab0ff50d20bf), with the lead's
rulings C1-C21 in its section 10. That file is the technical annex. Where this file and the annex differ, this
file rules.

## 1. Hypothesis (fixed by the Stage E.13 prompt)

The Gate 0 family B result for NG at h60 (E.12: mean gross 5.569 ticks, c 1.713, t_B 2.51, 518 trades), and at
hF as the second of exactly two tests (13.921 ticks, c 1.766, t_B 2.33, 494 trades), reflects an edge that also
holds on 2010-2019 NG data, a period no part of the program has read (E.12_RETURN.md lines 10-11 and the family B
table). Sign: the trade is sign(r_hat), as in Gate 0. No other product, horizon or model is tested.

## 2. Data and windows

- Price path and vehicle: NG.v.0 (Databento GLBX.MDP3, ohlcv-1m, volume-ranked continuous, splices from
  Databento's symbology), NG's own vehicle (annex sections 5-6).
- Legs read by features live on NG rows: NQ, ZN, 6E, GC and ZC (G17 leads), bought for the same window. CL is
  never live on NG rows. MBT is not listed (n/a by design). MES gets no feature (P-1a). (Annex section 3;
  generic.py:342-352.)
- Test window: trade dates 2010-06-07..2019-04-30. Databento's GLBX.MDP3 starts on 2010-06-06 (annex R01; the E.12
  ledger's error text). The fixed start applies to every root, with no volume read (ruling C5). The end is the
  quote end, with no May-2019 splice (ruling C6). First rows come after the warm-up, about late December 2010 to
  January 2011: sigma_X,d needs 20 dates, G9 120, z-scores 60 (annex section 5).
- Never read before the test: no program file has read NG or any leg before 2019-05 (annex section 5, evidence
  list). The test window is never summarized, plotted or printed before the single evaluation (section 9).
- Training (already read, used only to fit the frozen model and reproduce q): the E.12 phase-1 panel,
  2019-05-06..2024-02-29, all 27 Gate 0 products, from E.12's persisted state (annex sections 2 and 4).

## 3. Model and rule: every parameter fixed

- Model M1: the frozen Gate 0 family B ridge (lambda 0.1), with every feature the E.12 build computed plus product
  and cluster identifiers, pooled over the E.12 panel, one model per horizon. It is fitted ONCE on the whole E.12
  training panel with the frozen code, ml_route_v2/constants.py byte-identical (rulings C1, C2). The rule's
  fallback M2 does not apply: annex section 2 shows that neither condition (a) nor condition (b) holds.
- Features on replication rows: exactly E.12's feature_cols, in E.12's order (ruling C11). Features are computed
  on NG rows only, with per-product causal z-scores (normalize.py:88-93; ruling C8). Unlisted legs get "not
  applicable" (0 plus its flag) as in training. A listed leg is never set to n/a (L4-3). The CL and MBT frames are empty within the window (ruling C7, as
  implemented): each holds one sentinel bar dated 2019-05-31, after the window, because a frame with no row crashes the frozen g17
  code; no lead bar is ever closed at an NG decision time, and an equality test
  (tests/test_c1_world.py::test_c7_ng_rows_equal_those_with_synthetic_cl_bars) shows the NG rows equal those built
  with synthetic CL bars.
- Threshold q, per horizon: Gate 0's exact cutoff, the smallest |r_hat| among NG's E.12 Gate 0 trades (ruling
  C3; gate0.py:301-306). It comes from reloading E.12's persisted out-of-fold predictions. The run must reproduce
  E.12's NG h60 and hF rows (trades, mean, t_B) to 1e-9 and stops on any mismatch. Nothing is refitted (ruling C4).
- Trade rule: on each NG decision row of the test window (the frozen decision clock: energy t1 08:30, t2 10:30,
  t3 13:00 CT; h60 and the flatten F), trade sign(r_hat) iff |r_hat| >= q, 1 contract. All of V2.2's exclusions
  apply: roll blackout, early close and halt, and the release-window rule.
- Calendars (built from official pages before the purchase, no prices): the energy, equity, rates, FX, metals and
  grains group calendars for 2010-06..2019-05; Topstep flatten rows by Rule H-1; the release calendar for NG's D8
  list (EIA NGS, WPSR, FOMC); the regenerated K4 literal tables (annex section 5, C-1 to C-5). A date whose
  holiday or session status cannot be sourced at "cme" or "secondary" grade is excluded and counted. The run
  stops if more than 2% of dates are excluded this way (ruling C12). NGS drop rules as in E.5 (ruling C13).
- Guard against silently n/a features: applicable-row counts per feature, printed without values. The run stops
  if any feature live in E.12 has 0 applicable rows (ruling C10). These counts are computed from the test window's
  features, so they read the test bars (no values printed). A C10 stop therefore CLOSES this registered attempt.
  Any calendar correction and rerun is a new registration, with its tests counted in N again (Fable R-12, lead
  ruling).

## 4. Costs

D8 at the vehicle, the frozen cost table unchanged. c(NG,h) is the mean D8 round trip of the sides taken over the
test's trades (gate0.py:332-357). D8 was calibrated on 2025-2026 samples and understates thinner early-era costs
(reports/stage_e2a_costs.md line 100). The bar is gross, so cost enters only through the 1.5c threshold.
Descriptive after the verdict only: the 1.5x slippage case (ruling C14).

## 5. Pass bar (fixed)

Two tests, T1 = NG h60 and T2 = NG hF, each with Gate 0's own statistic (gate0._b_test: per-date mean of the gross
P&L in vehicle ticks, t_B = mean / (sd / sqrt(n_dates)), one-sided p from Student's t with n_dates - 1 degrees of
freedom). A test passes iff:
1. mean gross g >= 1.5 x c(NG,h);
2. one-sided p <= 0.025 (Bonferroni 0.05 / 2), in the direction mean g > 0;
3. at least 30 trades.

The replication passes iff at least one of T1 and T2 passes. Under no edge, the chance of at least one pass is
about 0.041-0.045 for a correlation of 0.5-0.7 between the two t's (annex section 7).

## 6. Trial count

+2 at registration, whatever the outcome (ruling C21), in the append-only trial registry
ledger/trial_registrations.jsonl, in the later session. Test C2 stopped in Stage E.14 before its registration
(its power rule), so N is still 471 and C1's registration takes it to 473 unless another test registers first
(then +2 on that N). The q reproduction and the M1 fit are
not tests. The descriptive outputs (the realized share above q, the long/short split, trades per year), printed
after the verdict, add nothing to N (ruling C15).

## 7. Power and prior

- Expected t at the observed effect: 3.41 (h60) and 3.17 (hF) over 8.90 years, about 957 and 913 trades. Power
  at 1 / 1/2 / 1/4 / 0 of the observed effect: 0.93 / 0.40 / 0.13 / 0.025 (h60). Including the 1.5c bar at a
  tick-volatility ratio of 0.7, h60 power is 0.88 / 0.29 / 0.08 / 0.012 (annex section 9). The span used is
  2010-06-07..2019-05-03. The ruled window ends 2019-04-30 and starts its rows after the warm-up, so the usable
  span is about 8.3 years and these figures are slightly optimistic. They scale by sqrt(8.3 / 8.9) = 0.97.
- Prior: under the global null, the best of 81 tests reaches t >= 2.51 with probability 0.396 if independent
  (Bonferroni bound 0.502). The 2010-2019 NG regime differs from 2019-2024: production up 59%, LNG exports from
  February 2016, and calmer volatility than 2022's (annex section 9, EIA sources R04-R20).
- The lead's odds of a pass: 12%, range 7-35% (annex section 9; ranking section 3).

## 8. What each outcome means

- **Pass:** the frozen model's NG predictions carried a gross edge of at least 1.5x D8 cost at p <= 0.025 in a
  disjoint decade with a different supply regime. That is real evidence the near-miss was not only selection
  (joint null probability about 0.018). It is still not tradeable: the bar is gross, the costs are 2025-26
  calibrations, it clears none of the verdict bars (t >= 3, DSR at N = 473, PBO), and only one NG contract at h60
  on a 150K XFA fits. A pass justifies one more pre-registered, net, NG-only design with its own N and a forward
  or holdout test before any money. NG's holdout-2 chunks are owned and sealed, and are opened only under a
  registered Stage D.2.
- **Fail:** the NG near-miss is closed. Gate 0's reading stands, nothing more is built on v2's model, and N is
  473. A fail cannot separate "never real" from "real only in the 2019-2024 LNG-era regime".

## 9. Order of events (rulings C9, C20; amends L4-7; as the Stage E.14 prompt orders them)

In Stage E.14 (done before this file was committed, except step 4, which follows the commit):
1. The calendar probe: 2012's energy calendar and EIA NGS table at evidence grade; C1 is dropped if more than 2%
   of 2012's energy trade dates or more than 2 NGS release dates are unsourced (E.14 Task 1; section 11).
2. The calendars from official pages, no prices (E.14 Task 2): the six group calendars, the release calendar
   for NG's D8 list, the energy full sessions; the 2% unsourced-date stop (ruling C12) checked here.
3. Freeze this pre-registration, its harness (v10, with the "ext2010" store type and buy plan, Fable-reviewed;
   ruling C18), C1's code (c1_replication/) and the hashes of E.12's persisted state (45 .npy files, meta, 2
   pickles and the build JSON, with a read-only copy; ruling C17).
4. Fit M1 and reproduce q (c1_replication.q_m1). Write M1's coefficient hash and q into Stage E.14's STATE and
   reports/stage_e14_c1_model.json, before any 2010-2019 byte is bought.
In a later session, under this freeze (section 11 lists what it verifies first):
5. Register T1 and T2 (N 471 -> 473, or +2 on N then) with this file's sha256.
6. Quote fresh (logged first), then buy NG and the five legs after the user's acct-2 top-up and a harness that
   differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else. The store builds print counts only.
7. Compute the replication features and run the evaluation once, behind a run-once marker
   (c1_replication.evaluate; the gate0_stage.py:260-264 pattern).
8. Report the verdict, then the descriptive outputs.

## 10. Decisions made by the user before the freeze (V25, V26)

1. **V24, two computations on the 2019-2024 training panel** (V25 item 1): both allowed. (a) Reloading E.12's
   persisted out-of-fold predictions and reproducing NG's rows to 1e-9 to fix q (ruling C4). (b) The single
   full-panel fit of M1 on the E.12 training panel. Neither reruns Gate 0's decision or tests anything on
   2019-2024.
2. **Funding** (V26): the acct-2 top-up did not go through. ACCOUNT_2_CAP_USD stays $249.67 and V25's approval
   lapsed. C1 is built, frozen and taken through its q reproduction and M1 fit, then waits, unregistered, for
   funds. Stage E.14 quotes C1's set only ($0.00 ledger lines) so the user knows the top-up.
3. **~/.cache/propexp_e12_phase1** was kept; Stage E.14 hashed it and made a read-only copy (section 11).
4. **The calendar probe first** (V25 item 4): run inside Stage E.14 with the rule of section 9 step 1.


## 11. Frozen inputs, Stage E.14 results, and what the later session verifies first

Recorded in Stage E.14 (reports/stage_e14_STATE.md holds the times):
- **Probe (section 9 step 1):** 2012 energy 0 of 258 trade dates unsourced; 2012 NGS 0 of 52 release dates
  unsourced (1 under the stricter actual-release reading, 2012-12-28); the rule does not fire
  (reports/stage_e14_probe.md).
- **Calendars (step 2):** six group calendars 2010-06-01..2019-05-31, 0 unsourced trade dates in each over
  2010-06-07..2019-04-30 (equity 0/2,298, rates 0/2,297, FX 0/2,298, energy 0/2,296, metals 0/2,296, grains
  0/2,243); the release calendar reports/stage_e14_cal_releases.json, sha256
  9a051211fe381cd2d1894180259624cc6729e8ddc89649e398b59e13666080a7 (NGS 470, WPSR 470, FOMC 72; C13's rule drops
  0 NGS rows; one WPSR time unsourced, 2012-11-01, whose NG date is excluded under ruling C12); the energy full sessions (2,250). Ruling C12's 2% stop does not fire
  (reports/stage_e14_calendars.md). Limits accepted by the lead: that file's "Limits" section.
- **Harness v10** (Fable-reviewed; commit "harness v10, E.14 caps and stores"): manifest sha256 fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b. It holds
  the ext2010 plan (NG, NQ, ZN, 6E, GC, ZC; the 2010-06-06..2010-07-01 chunk then 2010-07..2019-04, 107 chunks
  per root), the ext2010 store (trade dates 2010-06-07..2019-04-30), the hist calendar loader and the six
  calendar files, the trial registry, and E14_EXT2010_SESSION_CAP_USD = 0.00, so no C1 byte can be bought
  under v10.
- **C1's code** (c1_replication/, outside the harness directories) and every other input: the list
  reports/stage_e14_c1_freeze_inputs.json, sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e (design files, calendars, calendar reports, code,
  tests, the E.12 state manifest, E.12's v2 freeze, Gate 0 report and test list, ml_route_v2/constants.py, the
  harness manifest, the quote).
- **E.12's persisted state (ruling C17):** reports/stage_e14_c1_e12_state_manifest.json, sha256
  8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9: 51 files (45 OOF splits, gate0B_meta.json,
  phase1_filter.pkl, phase1_panel.pkl, phase1_build.json, gate0_run.json, gate0_DONE.json), copied byte-identical
  and read-only to ~/.cache/propexp_e14_c1/e12_state_copy.
- **Fresh quote (Stage E.14, $0.00 ledger lines):** $57.742330 for the 642 chunks (NG 8.570392, NQ 10.625886, ZN
  10.106134, 6E 11.072096, GC 11.182294, ZC 6.185528), x 1.03 = $59.474600; acct-2's headroom $18.070270, so the
  top-up needed is $41.404330 at that quote (reports/stage_e14_quotes_ext2010.json).
- **M1 and q (step 4, after this file's commit):** written to reports/stage_e14_c1_model.json and Stage E.14's
  STATE (q_h60, q_hF, both M1 payload sha256s, the model JSON's sha256), with the M1 payloads in
  ~/.cache/propexp_e14_c1/m1. They are fixed from then on.
- **Lead rulings on the code (Stage E.14):** CL and MBT are each given one sentinel bar dated 2019-05-31, after
  the window, because a truly empty frame crashes the frozen g17 code; the NG-row columns equal those built with
  synthetic CL bars (tested); this is ruling C7's "empty frames" within the window. Ruling C12 excludes an NG
  date that is unsourced in any of the six group calendars, whose prior energy trade date (or a weekday between)
  is unsourced, or that holds an unsourced release. Rule H-1 is applied literally (rules/sessions.py lines
  20-40), so the equity halts of 2012-10-29/30 and 2018-12-05 give Topstep rows. The hist calendar loader accepts
  a Friday-to-Monday session handover and a day holding both an early halt and a late open (grains).

The later session, before anything else: (1) verify, by script, every entry of reports/stage_e14_c1_freeze_inputs.json (recording the result in its STATE
before registering), that this file is committed and unchanged in git (`git ls-files --error-unmatch` and
`git diff --quiet HEAD --` on it), the
E.12 state copy against its manifest, the model JSON and both M1 payloads against the hashes recorded in Stage
E.14's return; (2) verify that its harness differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else; (3) quote fresh, and stop if the
quote x 1.03 exceeds acct-2's headroom; then register, buy, build and evaluate once, in that order
(c1_replication/README.md gives the commands).

## 12. Changes from the draft (every one)

1. Status block: FROZEN, AWAITING FUNDS (V26), with the hashes of the draft and annex.
2. Section 6: registration in the trial registry; N 471 -> 473 at the later registration, because C2 stopped
   before its registration in Stage E.14 (V26 had expected C2 first, 471 -> 473, then C1 473 -> 475).
3. Section 9: the order of events as the Stage E.14 prompt orders them (calendars before the freeze; M1 and q
   after the freeze commit, before any purchase; the later session's steps).
4. Section 10: the user's decisions (V25 item 1, V26) replace the open questions.
5. Section 11 added: the Stage E.14 results, the frozen inputs and what the later session verifies.
6. Section 12 added: this list.
7. Section 3: ruling C7's "empty frames" stated as implemented (one sentinel bar dated 2019-05-31, after the
   window; FreezeReviewer F-02).
8. Sections 9 and 11: the later harness may also change the test assertions that pin the two caps
   (FreezeReviewer F-01); section 11 step (1) checks the inputs by script and the freeze file's git state
   (F-04, F-05).
