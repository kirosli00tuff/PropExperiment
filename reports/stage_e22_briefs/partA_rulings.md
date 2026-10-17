# Stage E.22 Part A: lead rulings (before any confirmation read)

Written by the E.22 lead (Opus 5.5, xhigh), 2026-10-16 from ~01:10 PDT, against docs/prompts/STAGE_E.22.md
Part A, from reports/stage_e22_briefs/partA_facts_K5_K3.md, partA_facts_K6_K8.md, partA_decisions_scan.md
and partA_harness_audit.md. No confirmation-window bar has been read by anyone in this stage. Each ruling
is a lead decision and is listed under Open choices in reports/E.22_RETURN.md.

## A1. The member list against the records

The prompt's five Tier A members match the screening returns exactly (quotes in the facts files):
K5-fomc-01 MGC (E.4b:13, the only K5 Tier A; no other K5 Tier A trial exists), K3-ldnrev-01 6E (E.4c:14),
K6-limitcont-01 HE (E.8:12-15, 274), K8-flight-01 HEOD MGC and K8-wkndbtc-01 MNQ (E.9:15-18, 262-263).
No discrepancy. K4's Tier A (K4-ngpre-01 NG) was confirmed in E.5 (NULL) and is not re-run.

- **R-E22-A1 (scope of a run).** As E.5 did for K4, each cluster's single confirmation run covers every
  runnable trial of the cluster (Tier A and Tier B), so that V14 (c) (DSR variance over all of a
  one-member Tier A cluster's confirmation-window Sharpes) and L-E5-3 (PBO over every run trial) can be
  computed from the one run. OC-H-excluded trials (K5: cp1 MHG, cp2 MHG coverage, pmfix MGC hold floor;
  K3: cp1 6S, cp1 6N, cp2 6N coverage) are listed, not run, not covered (L-E5-5). K3-mehedge-01 on EUR
  is not a frozen trial (dropped at E.4c) and is not listed.
- **R-E22-A2 (K6 despite V18).** V18 said K6's confirmation is not planned (one-trade Tier A). V39 and
  this stage's prompt name K6-limitcont-01 for confirmation; the later instruction governs. Its "Tier A
  on a single trip" label is carried.

## A2. Windows and price paths (D2, D4, U8, V39)

- **R-E22-A3 (owned data only).** Owned: step 2 stores 2019-05-06..2024-02-29 of 6A 6B 6C 6E 6J 6N 6S CL
  GC HE HG LE MBT MCL MGC MHG NG NQ RTY TN UB YM ZB ZC ZF ZL ZM ZN ZS ZT ZW (E.5, E.12); MES's Stage D
  confirmation store (2019-05-01..2024-02-29). Not owned: MNQ's step 2 history, any full-size BTC history.
- **R-E22-A4 (MGC -> GC).** MGC's own start rule found no qualifying month (S_X none at 0.25; E.5), so
  every MGC trial's own supply is 0 and D4's power check fails; under U8 as met by V39's delegation, GC's
  bars are declared as the price path of every MGC-vehicle trial (K5's six MGC trials and K8's flight H30
  and HEOD), with MGC's cost table, tick value and q_c (D2), and GC's start rule (D4: "the start rule then
  runs on the full-size contract"). Declared per exposure (gold) in the list before any read.
- **R-E22-A5 (MNQ -> NQ).** MNQ's confirmation-window history is not owned. On owned data the vehicle's
  own confirmation window supplies 0 days, so D4's power check fails exactly as it does for MGC; NQ is the
  same underlying with the same quotes up to the multiplier (D2), owned, and named among this stage's
  owned stores by the prompt. NQ's bars are declared as K8-wkndbtc-01's traded-leg price path, with MNQ's
  cost table, tick value and q_c, and NQ's start rule. Alternative considered: label wkndbtc "untestable
  on owned data (missing leg MNQ)"; rejected because D2/D4 treat a micro with no usable own window and an
  owned full-size twin as the substitution case, and the choice is made by rule before any read.
  Flagged for ListReviewer as an adversarial item.
- **R-E22-A6 (MBT, BTC).** MBT's own step 2 store is owned (from 2021-05-03). MBT runs on its own bars
  and start rule. If wkndbtc's power check fails on the MBT-limited window, the U8 substitute (BTC) is not
  owned, and wkndbtc is labelled "untestable on owned data (missing leg: BTC full-size history for the
  MBT signal path)" and not run (A2: "not bought").
- **R-E22-A7 (MES leg).** MES (K8 flight's signal leg) reads its Stage D confirmation store with S = 2020-02-03
  (D.1f; D4: "MES as a leg starts 2020-02-03").
- **R-E22-A8 (start rule).** Every other root uses D4's start rule (0.25 V_ref; 0.15 and 0.40 descriptive)
  run on its owned step 2 store, with the research-window volumes for V_ref, by the frozen start-rule code.
  Cross-product members: the intersection of the legs' windows; the union of the legs' roll blackouts.

## A3. Power (D4)

- **R-E22-A9.** n_b per trial from its research-window daily series by the frozen power check (D.1e Task 3,
  at the operative eps_X; analytic, and the block-bootstrap simulation where they differ by more than
  15%, the larger), against the supply of its confirmation window; n_b > supply labels the trial
  "inconclusive by design" before the run, and it is not run. Computed as E.5 did (research re-runs under
  the harness in force, matched to the screening records in every field but `power`).

## A4. Verdicts (D5, V14, NULL_CRITERIA_E)

- **R-E22-A10 (K = 5).** Clusters with a non-empty Tier A in the program: K3, K4, K5, K6, K8 (K1, K2, K7
  empty; K9 folded into the ML route by V21 and never a cluster; the ML route has no Tier A: V23 left its
  slot unused, V24 stopped it at Gate 0, V38 closed the E.20 search). K = 5, alpha_k = 0.05 / 5 = 0.01.
  Source: the prompt A4, D5 (docs/STAGE_E_DESIGN.md:306-308), NULL_CRITERIA_E:70. V14 (b)'s K = 9 applied
  "until every cluster and the ML route have been screened"; that condition is met (V17: every cluster
  screened; V24: the ML route ended). The Holm result at K = 9 is reported beside it as a descriptive
  figure; t > 3.0 one-sided (p < 0.00135) is stricter than either threshold, so no edge verdict can differ.
- **R-E22-A11 (N for DSR).** N = 533: the program N after this stage's registration of E22-F1 (532 + 1),
  the larger of the two values the program holds tonight. Confirmations of already-counted members add
  nothing to N (E.5: N 150 at its list, 150 after its run; E.6 then added only its screened trials).
- **R-E22-A12 (eps_X).** The operative eps_X = min(translated, funnel) of reports/stage_e2a_epsilon.json
  (D3, U8), as E.5 used: MGC 71, MHG 27, 6E 12, 6A 11, 6B 8, 6C 9, 6J 10, 6S 13, 6N 10, ZC 4, ZW 4, ZS 5,
  ZM 5, ZL 11, HE 7, LE 8, MNQ 170 ticks per contract per day.
- **R-E22-A13 (a Tier A member with no record).** A Tier A trial labelled inconclusive by design or
  untestable on owned data has no confirmation p-value; it stays in its cluster's Holm family with p = 1
  (not rejected), so the family size is the screened Tier A size (conservative: the others' thresholds
  are not loosened). It is "not covered" for the null statement.
- **R-E22-A14 (DSR variance for K8).** If both K8 Tier A members are run, the variance is over their two
  confirmation-window daily Sharpes (D5); if only one is run, over all of K8's run trials (V14 (c)).
- **R-E22-A15 (open issues carried, nothing changed).** Each member runs exactly as frozen: K3's 14
  FX_FULL_SESSIONS dates that the harness flattens at 11:30 (R-A2-1) stay as frozen and the harness's
  rule applies; July 3 dates as Rule H-1 leaves them; K6's frozen limit tables, D9.7 settlement proxy and
  initial limits (K6-L-06/07) as frozen; wkndbtc's regime note and every source-overlap label carried.
  Tick history over the confirmation window (K3 N-4, K6 C7): every Part A root's step 2 bar report records
  off_tick_prices 0 at the frozen tick over 2019-05..2024-02 (reports/step2/bars_<ROOT>.json raw_checks);
  that is the record the audits asked for; unit history beyond the tick grid is not separately verified
  (label "unit history not separately verified").

## A5. Rulings after the power re-runs and ListReviewer-FableXHigh (reports/stage_e22_list_review.md), before any read

- **R-E22-A6 (revised, list review F3).** K8-wkndbtc-01 MNQ: the power re-run under v13 gives supply 34 (the
  window is limited by MBT's S_X 2024-01-02) against n_b 43, so D4's check fails: "inconclusive by design".
  U8's substitute for the short-history MBT signal path (full-size BTC) is not owned and is not bought (A2).
  Labelled consistently with the declared harness reading (MNQ on NQ, R-E22-A5, a v13 frozen input that this
  trial does not exercise): "inconclusive by design" only, declared not run by a reason-only entry in
  reports/stage_e22_notrun_K8.json (missing_leg null). The earlier draft declaration (reports/stage_e22_untestable_K8.json,
  label "untestable on owned data", missing leg MBT) was withdrawn before any list was committed. Alternative
  recorded as an open choice: under the strict reading of A2 (no NQ path for MNQ, which the reviewer prefers),
  the trial is "untestable on owned data (missing MNQ)". Not run either way; Holm m = 2 with wkndbtc at p = 1;
  DSR variance and PBO over K8's three run trials; no verdict changes.
- **R-E22-A9 (applied).** Every "inconclusive by design" trial is listed run: false and declared not run to the
  runner (list review N-1); the only one is K8-wkndbtc-01.
- **R-E22-A16 (list review F2).** K6-limitcont-01 LE: the research series has zero variance (0 trips), so the
  frozen power check is "undefined"; D4 labels by-design only when n_b > supply, so the trial is listed run and
  covered, as frozen. A zero-trip (or SE_boot = 0) confirmation outcome reads "inconclusive" (NULL_CRITERIA_E 3)
  and K6 then gets no cluster null statement (NULL_CRITERIA_E 1, 6). Accepted now, before any read.
- **N-2 (list review).** reports/stage_e_start_rule_K8.json was built at 01:41 under the working-tree manifest
  W1 (8cd39432...); W1 -> v13 changed only screening/stage_e_runner.py, screening/stage_e_verdict.py and two test
  files (reports/stage_e22_harness_change.md, Review fixes), so the start-rule code is the committed code; the file
  is kept (rebuilding would change its sha256 and every K8 power record's start_rule hash).
