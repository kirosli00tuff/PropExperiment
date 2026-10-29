# Stages

Naming convention: `Stage X.Y : Task Z` (per program ways-of-working).
This doc tracks stage scope only. The exact prompt behind every stage is in
docs/prompts/ (index in docs/prompts/README.md), committed before it is sent.

- Stage A.1 — Data + rules engine offline build. No TopstepX credentials
  required. Port Databento adapter, pull MES ohlcv-1m, validate bars,
  calibrate cost model from existing ticks, build XFA rules engine with
  known-answer tests. (In progress.)
- Stage A.2 — TopstepX access and cost census, once Combine + API Access
  are purchased. Practice account, API key, measured rate limits,
  official fee table confirmation, written questions to Topstep support.
- Stage B — Funnel simulator (XFA branch only) and rules-engine
  integration tests against the Stage A.1 rules module. (Built 2026-09-17;
  see progress.md, reports/funnel_null_baseline.md, reports/power_gate.md.)
- Stage C — Backtest harness: strategy interface, fill model wired to
  Stage A.1 cost model, leakage suite with planted-future canaries,
  walk-forward splits with a sealed holdout. (Built 2026-09-17; see
  progress.md, reports/leakage_suite.md. Holdout sealed behind data/holdout.py;
  unlocks are logged in docs/HOLDOUT_UNLOCK_LOG.md and reserved for Stage D.2.)
- Stage D.1 — Strategy research. (Run 2026-09-18; see progress.md and
  reports/stage_d1_accounting.json. 23 hypotheses across 5 families screened on
  train dates; none cleared the robust power-gate verdict; shortlist empty.)
- Stage D.1a — Harness fixes: drift benchmark, passive/limit fills, shared
  screening runner. (Built 2026-09-18; see progress.md, docs/SCREENING.md and
  reports/stage_d1a_regression.json. Every future screen goes through
  `screening.screen_candidate`.)
- Stage D.1b — C-H4 (reversal with passive fills) and Family F, a bounded,
  declared-in-advance data-native exploration. (Run 2026-09-18; see progress.md,
  reports/stage_d1b_family_f_declaration.md and reports/stage_d1b_accounting.json.
  C-H4 failed; Family F's pre-declared selection rule admitted zero hypotheses;
  cumulative N = 24; shortlist still empty.)
- Stage D.1c — Constraint audit: the XFA flatten and the hypothesis space it
  excludes. Decision brief only; no code, no backtest, no registration. (Run
  2026-09-18; see progress.md. The 15:08/15:10 CT flatten is confirmed and applies
  to the Combine, XFA and LFA alike; no researched prop firm permits overnight.)
- Stage D.1d — Multi-timeframe audit and bounded coarser-bar sweep. (Run 2026-09-21; see
  progress.md, reports/stage_d1d_horizon_audit.md, reports/stage_d1d_timeframe_declaration.md
  and reports/stage_d1d_accounting.json. 7 of 24 trials were flagged as tested finer than
  their source's horizon; all 7 re-tests at the source's grid failed; the declared 28-statistic
  sweep at 5/15/30/60-minute bars admitted zero hypotheses; cumulative N = 31; shortlist
  still empty.)
- Stage D.1e — Defining the MES null: criteria, power and data quotes. Design only; nothing bought,
  nothing screened, N = 31. (Run 2026-09-22; see progress.md, docs/NULL_CRITERIA.md (hashed),
  reports/stage_d1f_confirmation_list.md (hashed, read-only), reports/stage_d1e_power.json and
  reports/stage_d1e_quotes.md. ε = 34 net ticks per micro per day from the power gate; the class null needs at most 566 days and the extension supplies 992–1,151 under a 2019–2020 start; 47 of 95 measured members resolvable below the cost bar, 48 not; second holdout 2024-04-01..2025-03-31 declared; frozen 58-test list with Family H declared and hashed.)
- Stage D.1f — Confirmation on the extended MES history (planned). Buys the 2019-05..2025-03 ohlcv-1m
  extension ($7.59 quoted), seals the second holdout (trade dates 2024-04-01..2025-03-31) on arrival,
  runs the frozen 58-test Tier A list and the 43 Tier B statistics under docs/NULL_CRITERIA.md, and
  returns per-class null / edge / inconclusive verdicts. Awaits the user's spend decision.
  Build session run 2026-09-23 (see progress.md): harness built, tested and hash-frozen with no purchase
  (reports/stage_d1f_harness_freeze.json, 129 files, sha256 ba5b34d5…847a; 355 new tests, 0 review blockers;
  N = 31); the purchase and run wait for the user's freeze commit.
  Run session 2026-09-23 (see progress.md): bought the history ($7.586199), sealed holdout-2 (13 chunks, all_ok), corrected the 2019–2023 Independence Day calendar entries through the step-4b path (commit 14c1007, manifest d3bd21e5…), S = 2020-02-03 (1,055 trade dates); no member passed confirmation (Holm rejects none of 58); C1–C5 and C7 null under docs/NULL_CRITERIA.md (C5 null by inactivity via E-H3), C6 awaits D.1g; independently verified with no discrepancy; N = 58.
- Stage D.1g — C6, passive execution: NOT RUN. It would have bought N_C6 = 181 full trade-date MBO days and
  applied a queue-position fill model to C-H4. Closed by the user's decision of 2026-09-23 as non-deployable
  on the XFA (TopstepX fills limit orders only on trade-through, the model D.1f already applied; better fills
  would rest on SIM queue position, which Topstep prohibits): see docs/DECISIONS.md, "C6 closed, Stage D.1g
  not run". A scope decision, not a null: no C6 null statement exists.
- Stage D.2 — Sealed holdout read under the pre-registered bar.
- Stage E — the CME universe program (planned; decided 2026-09-23). Every CME Group product Topstep permits,
  run as one program over one universe in eight clusters (K1 equity index, K2 rates, K3 FX, K4 energy,
  K5 metals, K6 agriculture and livestock, K7 crypto, K8 cross-cluster relationships), instead of one
  project per product. MES is closed and enters only as a leg. Design: docs/STAGE_E_DESIGN.md (draft).
  - Stage E.0 — research, hypothesis catalog and program design. No purchase, no data, no freeze.
    Run 2026-09-23/24 (see progress.md): 8 clusters researched; draft catalog of 61 members and 170 confirmation
    trials (projected N = 228; reports/stage_e0_catalog.md); draft design D1-D15 (docs/STAGE_E_DESIGN.md) and
    criteria (docs/NULL_CRITERIA_E.md); D1 keeps 31 exposures (NKD, 6M, MET out); $0.00 spent (5,050 free
    quotes); staged purchase quoted at $275-300, which needs the shared cap raised; Fable review READY WITH
    FIXES, all 10 should-fix findings ruled; C6 closed and D.1g not run. Awaits the user's review before E.1.
  - Stage E.1 — freeze the catalog and design after the user's review, and buy step 1 of the data.
    Run 2026-09-24 (see reports/E.1_RETURN.md): the user's decisions U1-U9 applied (docs/DECISIONS.md);
    platinum OUT, the ML members superseded by a separate ML route; 53 members, 158 trials, projected
    N = 216; Fable freeze audit READY WITH FIXES (0 blocking), all fixes ruled; design, criteria and
    catalog FROZEN under reports/stage_e1_freeze.json; acct-2 switch; step 1 bought (904 files, $103.16 settled,
    verified); ML route drafted (docs/STAGE_E_ML_DESIGN.md) for the user's review.
  - Stage E.2 — build: per-product rules, costs, calendars, bar builds, sealing, the ML pipeline (planned).
  - Stage E.2a — ML route freeze, then the build. Run 2026-09-25/26 (see reports/E.2a_RETURN.md): ML route FROZEN
    (commit ba67073, manifest 077a57e1...); source-window amendment removes 6 source-overlap labels (04c504f);
    rules engine, 8 cited group calendars, bars of all 45 contracts, frozen D8 costs, vehicles (28 traded, 3 not)
    and funnel epsilon for all 28 built and verified independently by Fable (0 discrepancies). Nothing bought.
  - Stage E.2b — screening runner, ML pipeline, canaries, step 2 path, Windows backend, harness freeze. Run
    2026-09-26 (see reports/E.2b_RETURN.md): Stage E harness FROZEN (commit 273c27b, manifest cf939270...,
    1,032 files) after an adversarial Fable review (1 blocking, 3 should-fix, all fixed). Nothing bought.
  - Stage E.3 — K2 rates screening. Run 2026-09-26/27 (see reports/E.3_RETURN.md): eight members (44 trials) coded,
    Fable-audited (0 blocking), FROZEN (commit a79b47e, cluster freeze 8815a775...) and screened once: all 44 Tier B,
    Tier A empty; N = 102. Nothing bought.
  - Stage E.4a — harness v4 and K4 energy screening. Run 2026-09-27 (see reports/E.4_RETURN.md): harness v4 FROZEN
    (commit b20163a, manifest 82ae8536...: C-1 fixed, per-trial trip lists; K2 replay identical); K4's eight members
    (12 trials) coded, Fable-audited, FROZEN (commit e0ccf63, cluster freeze cf066cb0...) and screened once: Tier A
    K4-ngpre-01 NG, 11 Tier B; N = 114. Nothing bought.
  - Stage E.4b — K5 metals screening. Run 2026-09-27 (see reports/E.4b_RETURN.md): seven members (11 trials) coded,
    Fable-audited, FROZEN (commit 09f1999, cluster freeze 1d0c974f...) and screened once: Tier A K5-fomc-01 MGC, 7 Tier B,
    3 excluded (two MHG ports on coverage, pmfix on the mean-hold floor); N = 123. Nothing bought.
  - Stage E.4c — K3 FX screening. Run 2026-09-27 (see reports/E.4c_RETURN.md): nine members (30 trials; K3-mehedge-01 on
    EUR not traded, no free index history) coded, Fable-audited, FROZEN (commit c5dfd5c, cluster freeze c4fb5da4...) and
    screened once: Tier A K3-ldnrev-01 6E, 26 Tier B, 3 excluded on coverage; N = 150. Nothing bought.
  - Stage E.5 — K4 and K5 confirmation. Run 2026-09-27 (see reports/E.5_RETURN.md): harness v5 (2c0bfe0) and v6 (ce3cb66),
    step 2 history of MCL, NG, MGC, MHG bought ($21.20) with holdout-2 sealed; K4 list hashed (4161032) and confirmed once: NULL
    (Tier A K4-ngpre-01 fails Holm); K5 stopped before its list (MGC's confirmation window is empty; U8 is the user's decision).
  - Stage E.6 — K7 bitcoin screening. Run 2026-09-27 (see reports/E.6_RETURN.md): six members (6 trials) coded, Fable-audited,
    FROZEN (commit d661eb6, cluster freeze 46cae308...) and screened once: all six Tier B, Tier A empty (K7-expiry-01 not traded:
    every research expiry day in a roll blackout); N = 156. Nothing bought.
  - Stage E.7 — K1 equity-index screening. Run 2026-09-28 (see reports/E.7_RETURN.md): five members (11 trials on MNQ, M2K,
    MYM) coded, Fable-audited, FROZEN (commit 9113abd, cluster freeze cf48f514...) and screened once: all eleven Tier B, Tier A
    empty (K1-cp3-01 MNQ's Tier B rests on four MLL-liquidated days); VXN read free from Cboe; N = 167. Nothing bought.
  - Stage E.8 — K6 grains, oilseeds and livestock screening. Run 2026-10-01 (see reports/E.8_RETURN.md): seven members
    (27 trials) coded, Fable-audited, FROZEN (commit 0a14a9a, cluster freeze a6f8b497...) and screened once: Tier A
    K6-limitcont-01 HE on a single trade (t 1.002, mechanical), 26 Tier B; N = 194. Nothing bought.
  - Stage E.9 — K8 cross-market screening. Run 2026-10-01/02 (see reports/E.9_RETURN.md): three members (4 trials:
    K8-flight-01 H30 and HEOD on MGC with MES, K8-oilcad-01 on 6C with MCL, K8-wkndbtc-01 on MNQ with MBT) coded,
    Fable-audited, FROZEN (commit 558a5dc, cluster freeze 99f5a6ce...) and screened once: Tier A flight HEOD (t 1.395) and
    wkndbtc (t 1.072, resting on one Monday), Tier B H30 and oilcad; N = 198. Nothing bought. Every cluster is screened.
  - Stage E.10 — K9 low-frequency full-session holds: literature research and a draft catalog. Run 2026-10-02/03
    (see reports/E.10_RETURN.md): 88 sources logged by four opus readers; draft K9 catalog of one member,
    K9-anncday-01 (macro-announcement-day premium, long MNQ, M2K, MYM, 3 trials, source-overlap), after the
    lead withdrew K9-vixback-01 and the Fable review (0 blocking, 8 should-fix) led to withdrawing
    K9-vixspike-01; design draft docs/STAGE_E_DESIGN_K9_DRAFT.md (K = 10, 30-trip floor, 40-trial budget).
    No market data, nothing bought, nothing frozen; N stays 198 (201 if screened). E.11 freezes after the
    user's decisions.
  - Stage E.11 — ML route v2: design draft and the pipeline built on synthetic data. Run 2026-10-03 (see
    reports/E.11_RETURN.md): draft docs/STAGE_E_ML_V2_DESIGN.md (Gate 0 first; ridge and shallow LightGBM, 45
    configurations, nested CPCV; drawdown-distance sizing, kill switches, payout simulation); ml_route_v2/ with 704
    synthetic tests, all leakage canaries caught; harness v7 (per-account Databento keys). No market data, nothing
    bought, frozen or trained; N stays 198. A freeze session follows the user's 19 decisions.
  - Stage E.12 — ML route v2 frozen, phase 1 bought, Gate 0 run once. Run 2026-10-03 (see
    reports/E.12_RETURN.md): v2 frozen (9466f2e) with V23; harness v8 and, by the user's decision on 24 held
    closure bars, v9; all 28 exposures' training windows bought for $133.72; Gate 0 FAIL (best NG h60, 3.25x
    cost, t 2.51, not Holm-rejected), verified by Fable; v2 stops; N = 471.
  - Stage E.13 — what is left to search: research and scoping, no market data, no purchase. Run 2026-10-03/04 (see
    reports/E.13_RETURN.md): venues for multi-day automated futures (only The Trading Pit Classic and, for a
    personal account, IBKR Canada permit it outright; Phidias human-in-the-loop), trend and carry after
    publication (SG Trend 0.24 net since 2010; carry gone since 2013; fails prop drawdowns), new information
    sources (dealer gamma, GFS revisions), a backward NG replication draft ($59 of data, 12% odds); ranking C1 NG
    replication > C2 GEX late-session momentum > C3 trend+carry personal; two pre-registration drafts, nothing
    frozen; Fable review BLOCK then R-01 closed; N stays 471.
  - Stage E.14 — C1 and C2 together, with the funds on hand (V25, V26). Run 2026-10-05 (see
    reports/E.14_RETURN.md): C2 (GEX-conditioned S&P late-session momentum) stopped at its power rule before its
    freeze (135 eligible GEX < 0 dates, under 200; Fable-verified); C1 (backward NG replication) frozen
    (1680982), its q reproduced exactly and M1 fitted, awaiting a $41.41 acct-2 top-up for its $57.74 of data;
    calendars 2010-2019 built from CME, EIA and Fed pages with 0 unsourced dates; harness v10 (dc93e9b);
    nothing bought, nothing registered; N stays 471.
  - Stage E.15 — complete C1 under its freeze (V27). Run 2026-10-07 (see reports/E.15_RETURN.md), two attempts:
    the freeze verified intact each time (43 inputs, E.12 state, model, q); both fresh quotes failed, Databento
    having locked acct-2 (403 auth_account_locked on 642, then 636 of 642 calls after the user's key update,
    $0.00); C1 stopped before registration both times; no v11, nothing bought, nothing registered; N stays 471;
    a lead-side quote guard added; the user gets Databento to unlock the account, then E.15 re-runs.
  - Stage E.16 Part A — base-rule batch H1-H5 built and frozen with no Databento (V28, V29). Run 2026-10-08/09
    (see reports/E.16_RETURN.md): five forced-flow tests (settlement-window momentum, month-end NQ/ZN pair,
    Treasury auction cycle, next-day reversal, their combination) frozen on 2010-07..2024-02 windows (freeze
    8f388c8, manifest 5274aa97...); nothing read, bought or registered; N stays 471. Stage E.17 completes C1, then
    buys the 21 remaining extension roots under harness v12, registers E16-H1..H5 and runs each once.
  - Stage E.17 — C1 completed and the base-rule batch run once, within $124.00 (V30 amended). Run 2026-10-09/10
    (see reports/E.17_RETURN.md): C1 registered, bought ($57.82) and evaluated, STOPPED at guard C10 (g17_mbt n/a
    by design in 2010-2019; a freeze contradiction; Fable-verified; not rerun); harness v11 and v12; 11 of the 21
    extension roots bought ($64.04; 10 on the fallback window); E16-H1..H5 registered and run once: all five
    FAIL (Holm rejects none, DSR about 0; Fable-verified); N 471 -> 478; no holdout-2 read, no meta-labeling.
  - Stage E.18 — C1b: C1 re-registered with guard C10's one fix (V31: g17_mbt and g17_cl exempt) and evaluated
    once on the stores bought in E.17, no purchase. Run 2026-10-10 (see reports/E.18_RETURN.md): Fable approved
    the diff, the dry check passed, freeze b714751; FAIL (T1 NG h60 mean 0.585 ticks vs bar 2.562, t_B -0.83;
    T2 NG hF -0.113 vs 2.649, t_B -0.41; Fable-verified); the NG near-miss is closed; N 478 -> 480.
  - Stage E.19 — Prop economics: the Topstep Combine-to-XFA funnel's cash value to the user, from sourced rules
    (214, help centre and terms), owned 2019-2024 return magnitudes (demeaned, fat-tailed) and D8 costs; no
    purchase, no edge test, N unchanged at 480. Run 2026-10-10 (see reports/E.19_RETURN.md): negative at zero edge
    for every size, path and sizing in the policy band (best 50K -$250 per cycle); break-even net Sharpe about 0
    (50K), 0.34-0.52 (100K), 0.54-0.86 (150K); Fable reproduced the headline; account stacking and excessive
    purchases are the binding terms.
  - Stage E.20 — Pattern search with per-product research: 17 literature readers (one per root with 2010-2019
    history), H6 (rest-of-day to last-half-hour momentum on NQ at MNQ cost, T1-T3) and the ML route's net pipeline
    on the 17 roots with a fourth decision time and the r_ROD features. Run 2026-10-11 (see reports/E.20_RETURN.md):
    no post-2015 effect cleared 1.5 x cost, 0 Part A features accepted; H6 FAIL on all three tests (T1 gross 1.25
    ticks vs 4.08 cost, t -0.53); search screen FAIL (median-path t -1.33, PBO 0.60, net Sharpe -0.83; all 45
    configurations negative out of sample), so no backward test; Fable verified; N 480 -> 528.
  - Stage E.21 — Multi-day round on 17 roots, 2010-2024 owned data: TSMOM-12 (MOP 2012), the 1/3/12-month trend
    blend (HOP 2017), the equity turn of the month on NQ/RTY (NYSE day numbering) and an equal-risk book with H2;
    literature-checked and Fable-reviewed before the freeze. Run 2026-10-14 (see reports/E.21_RETURN.md): all four
    FAIL (Holm 0.025); T1 net Sharpe 0.50 [-0.06, 1.05], t 1.78, p 0.042 and T2 0.44, both above the 0.3 bar but
    underpowered; T3 0.15, T4 0.12; Fable verified every number; PropEd automation not granted publicly; no
    purchase; N 528 -> 532.
  - Stage E.22 — Loose ends and the micro book. Part A: the five unconfirmed Tier A members confirmed once each on
    S_X..2024-02-29 under harness v13 (e40ca85: GC bars as MGC's price path by U8, MES leg, not-run trials, Holm K = 5,
    run-once marker), lists Fable-reviewed and committed (ccd7fa7). Run 2026-10-16 (paused 02:43-18:26; see
    reports/E.22_RETURN.md): K5-fomc-01 MGC null, K3-ldnrev-01 6E null, K6-limitcont-01 HE null by inactivity,
    K8-flight-01 HEOD null, K8-wkndbtc-01 inconclusive by design (not run); no Holm rejection, no edge; K8 statement null,
    K3/K5/K6 no statement (thin-product coverage at confirmation; LE zero trips); Fable recomputed every figure. Part B:
    the Carver micro trend book designed on 12 micros (simple rounding loses <= 0.07 Sharpe from $25K up; the published
    greedy loses more), forward/ paper runner, E22-F1 frozen (2a2bdd8) and registered at $25K; N 532 -> 533. Nothing
    bought; no data fetched.
  - Stage E.23 — The program's frozen intraday triggers at 5- and 20-trading-day holds, entered at the trigger day's
    settlement, measured as alpha over the same root's E.21 T1/T2 daily returns (NW lags h). 208 triggers inventoried,
    11 mechanism memos; 4 shortlisted and 5 trigger-holds registered (freeze 24dcf4dd..., r008-E23, N 533 -> 538):
    K2-monthend-01 long ZF/ZN/ZB at 5 days, E20H6-T1 reversal on NQ at 5 and 20 days. Run 2026-10-17 (see
    reports/E.23_RETURN.md): discovery on 2011-07-27..2019-04-30 read once, no survivor (alpha t 0.55/0.38/0.10/
    -1.61/-0.71; Holm smallest p 0.31; the month-end gain is the bonds' drift); confirmation on 2019-05..2024-02
    inconclusive by design (power 0.18) and not computed; all five null; Fable verified every figure. Nothing bought;
    no data fetched.
  - Stage E.25 — Untapped sources: a research-only pass (V42) for a prop-compatible intraday edge in sources the
    earlier passes did not cover, plus re-digs of E.13/E.20 sources and a near-miss execution triage (user addenda
    1-6). Run 2026-10-18 (see reports/E.25_RETURN.md): 47 worker spawns in three waves around two usage-limit
    pauses; four hypotheses clear 1.5 x D8 on published numbers and duplicate no trial (noise-area intraday momentum
    on MNQ; the 3rd-Friday price spike; pre-refunding and pre-FOMC ZN drifts) but none is confirmable on the
    research window (power 0.35 and 0.11-0.22 at published sizes; C1 not blind and weak after publication);
    Group A empty, Group B one weak candidate; re-dig supports nearly every closure, weakens V38's sentence; Fable
    review BLOCK, fixed, READY. Nothing read, bought or registered; N 538.
  - Stage E.24 — Forward plumbing (V41, V42). Run 2026-10-18 (see reports/E.24_RETURN.md), three usage-limit pauses
    and a reboot: the multi-day loader fix as a new package mdio/ (frozen files untouched; E.23 replay 79,207 values,
    0 mismatches; Fable APPROVE after fixes); IBKR paper adapter for E22-F1 built on mocks (IBKR's daily close is the
    last trade, only sometimes the settlement: nothing registered, the choice goes to the user); Alpaca paper adapter
    on raw bars plus corporate actions; E22-F2 (E22-F1's rule on 11 US ETFs, P&L in excess of BIL) drafted and revised
    for Fable's BLOCK, NOT frozen or registered (code fixes unverified, rechecks cut); warm-up declarations and the
    user checklist written. No broker contacted, no market data read; N 538.
  - Stage E.26 — Housekeeping (V44, V45). Run 2026-10-21 (see reports/E.26_RETURN.md), one usage-limit pause:
    data/sealed, processed_hist, processed_step2 and vendor/databento (4,579 files, 9.69 GB) moved to
    /mnt/large-storage/market_data/PropExperiment/ with symlinks at the old paths, sha256-verified from disk, the
    holdout, harness and freeze checks identical before and after (data/processed, release_pages and
    index_history stay); ACCOUNT_3 (DATABENTO_API_KEY3, pilot-only) as harness v14 2e908c81 (Fable APPROVE after
    fixes); V45 (the move, ACCOUNT_3, V34 corrected, V38 amended); the Topstep rules record refreshed for the Tier 1
    news window. Nothing bought or registered; N 538.
  - Stage E.28 — Methods brief, firm-contract ranking and order-book pilot (V44, V45, V46). Run 2026-10-21 in two
    sessions (Max, then E.28b on Pro; see reports/E.28_RETURN.md): the methods brief (costs and data granularity
    bound the program, not missing mathematics; phased design), the blind ranking (Topstep x QM first, the next four
    also QM; rests on CL-derived statistics), the pilot spec frozen for QM mbp-1 and its code GO after an Opus
    stand-in review. Nothing bought (DATABENTO_API_KEY3 absent by the 20:30 deadline; the pilot then put on hold, V47);
    acct-3 untouched and kept; N 538.
  - Stage E.29 — Basket simulation (V46): can 2 to 3 ranked contracts in one 50K account lower the break-even? Run
    2026-10-21/22 on Pro (see reports/E.29_RETURN.md), two usage-limit pauses and two reboots. E.28's model was run
    on the combined account's daily P&L; B0 equals E.28's QM exactly; all 470 thresholds were grid-confirmed. With a
    QM-only edge no basket beats QM alone (0 of 80 cells). The setting-(i) wins (27 of 76) come from MGC's inflated
    alone break-even, not diversification, and rho barely matters. E.28's firm order stands; N 538.
  - Stage E.31 — Volume check, then a ZM order-book pilot (V48): QM (median 4,480.5 a day) and ZM (78,281.5) pass the
    volume check; 39 months of ZM MBO with ZS and ZL top of book (2020-12..2024-02) bought on acct-3 for 121.65 USD, run
    2026-10-22/23 (see reports/E.31_RETURN.md), three usage-limit pauses and a reboot. Under the trade-through gate the
    front-month DAY 10 s edge net of fee is -1.234 ticks [-1.252, -1.214]: ZM FAILS (also at zero fee; K and FIFO models
    negative too). acct-3 safe to wipe; nothing registered; N 538.
  - Stage E.32 — ZM directional discovery design (V51): the 2017-05..2020-11 ZM/ZS/ZL test window sealed (114
    files), a methods brief (Parts R and M, 13 reader files, Fable-reviewed) and a frozen discovery protocol for
    E.33 (4 families, 300 configurations, N 838 after E.33; binding discovery daily Sharpe 0.2007, about 1.22
    ticks net per 15-minute trade at 4 a day; sha256 c4ffb9d7...), run 2026-10-26/27 (see reports/E.32_RETURN.md),
    three usage-limit pauses and a planned context wipe. Nothing trained or computed; nothing registered; N 538.
  - Stage E.33 — ZM directional discovery, run of the frozen E.32 protocol: Part A gates passed; Part B pipeline built
    twice (Coder-A production, Coder-B independent), B3 labels and sigma exact on 20 dates and 57 of 59 feature
    columns after rulings (F3_11, F3_9 open), B4 LT2-LT6 pass, B5 published examples reproduced, synthetic proofs
    partial (see reports/E.33_RETURN.md), B6 cost model matches E.28/E.31, B7 MathReviewer agrees, PipelineReviewer
    provisional NOT YET; stopped by the deadline after two usage limits (14 h 20 min), run 2026-10-27/28. No freeze,
    no registration, no search; N 538. Continuation (E.33b) recommended.
  - Stage E.33b — continuation of E.33 (V52): B3 0 cells on 59 features, 6 labels and sigma after the F3_11/F3_9
    rulings; LT1 (200 draws, both priors) and LT2-LT7 pass; proofs 40/40 (null 0/20, plant 20/20); PipelineReview
    GO; pipeline frozen (eb565a37) and registered (r009-E33, N 538 -> 838); search started 14:29 and stopped at 16:08
    by the protocol's P10 3x compute rule (synthetic probe 6.6 s vs real LOGIT fold 227 s): 72 of 300 configurations
    finished (S5 and 12 of S1), outcomes sealed, no selection; rule 5 removes minutes on 95-98 of 796 dates; run
    2026-10-28 (see reports/E.33b_RETURN.md). N 838. The user decides an amendment of the compute limit (D1).
  - Stage E.33c — completion of E.33 (V53): protocol 0.3 (a2a2856f; only the P5/P10 compute reference changed, re-set
    from measured fold times; AmendReview GO; amendment a001-E33) resumed r009-E33 from its DONE markers: 300 of 300
    configurations, 1,800 fits, 0 failed, at 0.39 of the new 3x stop. P8 on all 300: G1 61 (all lose more than 1.0
    tick a trade after costs), G2 8 (at most 55 trades each), G3-G5 0; Tier A empty; best daily Sharpe 0.0478 against
    the binding 0.2007, inside the synthetic null's per-seed maxima; PBO 0.14. Clean negative: no finalist, no E.34
    registration, the test window stays sealed, no purchase. VerifyWorker (Fable) CONFIRMED all 300 from the raw
    predictions; StatsReviewer (Fable) 0 BLOCKING; run 2026-10-28 (see reports/E.33c_RETURN.md). N 838.
  - Stage E.32b — directional rerank of the firm-contract pairs (V50 item 2, V51): a new two-layer spec (09ebe697,
    hashed before any lookup), eight family readers, F3 volatility in E.28's window only, a masked fact table rated
    blind (FactAuditor's two leaks patched first), E.28's economics rerun for market orders. 35 of 47 codes pass
    Layer 1 (QM fails on D4 = 0); 103 pairs ranked: Bulenox YM 3.113, Topstep MNQ 3.096, Tradeify MNQ 3.087; YM in
    the top 5 of all 28 variants; ZL 15, ZM 24. Holding scope: 15-30 minute bands (15-60 for Topstep ZL), not hours;
    no prop firm allows overnight holds. Build recommendations: one ZL program at Topstep (F10 order-book state +
    F09 soy-complex lead-lag, one registration on the single sealed read 2017-05..2020-11, prior about 4%); MNQ F08,
    YM F08 and the EQ3 F08 pool under 1%; stop rule at most one more registered build. RankingReviewer PASS,
    RecsReviewer PASS with one ruling (LR-Q3b), FixVerifier PASS (all Fable); run 2026-10-28/29 (see
    reports/E.32b_RETURN.md). N 838. The user decides D1-D5 (V31 scope, the ZL read, the cost gate, 2024-03+ data,
    the next stage).
  - Stage E.34 — ZL program design and frozen protocol (E.32b recs 4.5; no purchase, no registration): the E.32 seal
    covers every ZL, ZS and ZM file of 2017-05..2020-11; exposure audit (no F10 or F09 feature ever tested against a
    ZL outcome; 10 firewall rules, 6 exclusions); Part M (MBP-1 in both windows, 5-minute floor, the crush residual with
    ZL adjusting and ZS/ZM bar leads, CL out, labels FH15-FH60 and TB15-TB30; at N 1038 G4 0.2028, SR80_test 0.1957);
    data facts; protocol FROZEN v1.0 (46556059; 200 configurations, N_reg 1038; the test buys about USD 26.5, including
    ZM bars of 2017-05..2019-04 that are not owned). MathReviewer and ProtocolReviewer GO WITH FIXES, FixVerifier PASS
    WITH FIXES (all Fable); run 2026-10-29 (see reports/E.34_RETURN.md). N 838. The user decides E.32b-D2, E.32b-D3,
    E.32-D2 and the V43 reading (OC-5) before any registration.
  - Stage E.3b onward — SUPERSEDED (V57, 2026-10-29). This was the original E.0/E.1 plan line. Every cluster K1-K8
    was screened (E.3-E.9) and confirmed or closed (E.5, E.22); V38 and V40 closed the intraday clusters. There is no
    remaining Stage E cluster sequence. E.33c's return option (a) cited this line in error.
- Stage F — Practice-account forward test, then one 50K Combine. (Listed as "Stage E" until 2026-09-23;
  renumbered when the CME universe program took the E label. Runs only if an edge survives.)
