# Pre-registration DRAFT: backward NG replication of the E.12 Gate 0 near-miss (C1)

Status: DRAFT for the user, written by the lead in Stage E.13 on 2026-10-03, revised 2026-10-04 after the Fable review
(reports/stage_e13_rulings.md). Ranked first in reports/stage_e13_ranking.md (v3). Nothing here is frozen, run or bought.
A later stage freezes it only after the user's decisions in section 10, writes its sha256 into that stage's STATE
file before any computation, and registers N = 473 before the evaluation.

Source of the design: reports/stage_e13_ng_replication_draft.md (ReplicationDesigner-OpusXHigh, every code claim
cited by file:line), with the lead's rulings C1-C21 in its section 10. That file is the technical annex. Where
this draft and the annex differ, this draft rules. The annex's sha256 at the time this draft was written is
recorded in reports/stage_e13_STATE.md.

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
  applicable" (0 plus its flag) as in training. A listed leg is never set to n/a (L4-3). The CL and MBT frames
  are empty, with an equality test (ruling C7).
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

N goes from 471 to 473 at registration, whatever the outcome (ruling C21). The q reproduction and the M1 fit are
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

## 9. Order of events (rulings C9, C20; amends L4-7)

1. Freeze this pre-registration, its harness (v10, with an "ext2010" store type and buy plan, Fable-reviewed;
   ruling C18) and the hashes of E.12's persisted state (45 .npy files, meta, 2 pickles and the build JSON, with a
   read-only copy; ruling C17).
2. Build the calendars from official pages (no prices).
3. Fit M1 and reproduce q. Write M1's coefficient hash and q into STATE, before any 2010-2019 byte is bought.
4. Quote fresh (logged first), then buy NG and the five legs (top-up per section 10). The store builds print
   counts only.
5. Compute the replication features and run the evaluation once, behind a run-once marker (gate0_stage.py:260-264
   pattern).
6. Report the verdict, then the descriptive outputs.

## 10. Decisions the user must make before any freeze

1. **V24, two computations on the 2019-2024 training panel** (Fable R-04). Does the user allow both?
   (a) Reloading E.12's persisted out-of-fold predictions and reproducing NG's rows to 1e-9 to fix q (ruling C4).
   (b) The single full-panel fit of M1 on the E.12 training panel, a new fit that Gate 0 never ran (Gate 0 used 15
   CPCV split fits; annex section 4).
   Both read already-bought training data. Neither reruns Gate 0's decision or tests anything on 2019-2024. V24
   rules out "re-mining the 2019-2024 stores", so the user confirms both before the freeze.
2. **Funding:** one acct-2 cap raise covering $59.03 plus the June-2010 chunks and the margin. The lead's
   recommendation is about $45-$50, after the calendar probe, and only if C1 is chosen (ruling C19).
3. **Keep ~/.cache/propexp_e12_phase1** (107 MB, outside the repository) until step 1 hashes and copies it. It is
   the only source of q.
4. **The calendar probe first:** one session that sources one year (for example 2012) of the energy calendar and
   the NGS table at evidence grade. If more than a few dates cannot be sourced at "cme" grade, drop the
   replication (annex section 11).
