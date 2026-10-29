# R4 draft sections (Stage E.32b step 3b): RecsDrafter-OpusXHigh (D5), version 3

Version 1 worked 2026-10-29 06:21-06:46 PDT; version 2 from 06:49 PDT (Opus 5.5 xhigh), for the lead's decisions of
06:47-06:49 PDT; version 3 (this file) from 08:57 PDT in session 4 by RecsAssembler-OpusXHigh (Opus 5.5 xhigh), for
lead rulings LR-Q3b (07:19:57) and LR-OF (08:58), the RecsReviewer's SHOULD FIX items S1-S4 and S6
(briefs/REVIEW_recs.md) and R1Fixer's verified facts (work/fix4/r1/r1fix_report.md). Version 2 is kept as
work/R4/draft_sections_v2.md. Version 3 changes: the R4 list and its grouping (section 1: Program 1 = C140 ZL F10 and
C138 ZL F09 on one sealed read, then C072 MNQ F08, C021 YM F08 and the new Program 4, C147 EQ3 F08, in section 6); L11
(RV2 B1 and LR-Q3b); Program 1's fact table with C140 first and C138 at Q3 1; RTY F09 moved to Appendix B with its
overlap text corrected; the own-broker section is now C141 ZL F10 at IBKR (section 7); sections 2, 8, 9 and 10
updated; Programs 2 and 3 renumbered (version 2's 5 and 6). Draft for reports/stage_e32b_recommendations.md. Facts and
arithmetic only: no outcome of any strategy was computed or read, no Databento call, no market data. The lead writes
the case paragraphs, the kill-criteria choices, the priors with base rates, the non-prop paragraph and the stop rule;
this file offers facts for them. Anything labelled "draft" is a proposal for the lead.

Inputs (sha256, first 16 hex): briefs/r3_out.json d3812c4020cc32a3 (r3_score.py, 07:19:31 PDT, on
briefs/R2_combinations.json bdbce3ae91fd258b = work/R2/patch_v31_q3_lead.py primary: LR-Q3a, LR-Q3b and LR-V31);
work/R2/r3_out_q3only.json 08e1bf16c0c9e107 (narrow V31 reading); work/R2/r3_out_nozlw.json a3b5d54b315062c5 (no ZL
window); work/R2/r3_out_ts150_v2.json e84b024d47adf7e8 (Standard-Path $150 on the corrected base);
work/R2/r3_out_q3bleg.json 21ccabbb99777671 (08:48:48 PDT; the primary without LR-Q3b, the leg-level F09 reading) on
work/R2/R2_combinations_q3bleg.json bd9dad5a9c1ab69e; work/R2/r3_out_v1.json ed186d0a53a580c8 and
R2_combinations_v1.json (version 1 inputs, kept by the lead); work/R2/combos_detail.json d3982a4fa58e2f31;
briefs/F5_holding.json 212a29bbf4350cc3; work/F5/SR80.json 632f68e1886f1fbb; briefs/R1_closed_lines.md
b917868a41d7b5fe and .json 30471ef44cb12ea8 (session 4: R1-11 and R1-15 cross-market bullets); briefs/RULINGS.md
12bf874c236a3cd7; work/fix4/r1/r1fix_report.md a4c0cd202a00b343; briefs/REVIEW_recs.md e13af8a012600d6d. Kept from
version 2: briefs/R2_dossiers.md; briefs/R2_Q_ratings.md; briefs/F5_holding.md; briefs/F2_data_access.json
4bad06bd9d34c913 and .md; work/R2/groundwork.json; reports/stage_e16_windows.json; reports/stage_e32_discovery_protocol.md
(frozen v1.0, c4ffb9d79af4bbbf) with protocol/p7_final.py; reports/stage_e32_test_seal.md;
reports/stage_e23_briefs/inventory/K1.json, K8.json, CDE.json; strategy/members/k1/cp1.py; reports/E.33c_RETURN.md
sections 1 and 7; reports/E.31_RETURN.md sections 1 and 7; reports/E.29_RETURN.md section 1; docs/DECISIONS.md (V28,
V31, V32, V33, V43, V49, V50, V51, V52, V56); reports/stage_e32b_STATE.md; spec section 8. briefs/r3_out.md does not
exist (r3_score.py writes JSON only); every R3 number here is from the r3_out JSON files.

## 0. Facts for lead decisions (version 1 record and L11, with the lead's resolutions)

**L1. K1-cp1-01's frozen rule holds the last half hour, not the day.** strategy/members/k1/cp1.py:58-60 (member frozen
in reports/stage_e_k1_member_freeze.json, sha256 cf48f514dcf26490..., the hash the E.23 inventory cites):
`SIGNAL_AFTER_O_MIN = 29  # the bar at O+29 = 08:59`, `ENTRY_BEFORE_C_MIN = 31  # the bar at C-31 = 14:29`,
`EXIT_BEFORE_C_MIN = 2  # the first bar at or after C-2 = 14:58`. Verbatim rule (inventory K1.json, K1-cp1-01 MYM):
"Signal s = sign(close of the bar at O+29 = 08:59 minus open of the trade date's first bar)", the first bar being "the
bar opening 17:00 CT on the CT calendar date before d"; "Entry: market intent on the bar at C-31 = 14:29 of CT date d
(fills at the 14:30 open)"; "Exit: market intent on the first present bar of CT date d at or after C-2 = 14:58 (fills
nominally at the 14:59 open)". So K1-cp1-01 on MYM held 14:30 to 14:59 CT, the same window as an F01 member at h 30
(C-30 to C) and as H6, differing in the signal (overnight plus first half-hour) and by one minute at the exit. The
06:21:31 ruling (1) matched R1-03's line-level horizons field, not the member's code; the scorer's flag 2 named the
boundary.
- *Resolved by the lead (06:47-06:49, LR-Q3a):* F01 on YM, MYM and RTY re-tests closed configurations (E16-H1 on YM,
  R1-13; K1-cp1-01 on MYM and M2K, R1-03): Q3 = 0 (gate) for C001-C006, C043-C044, C092-C096; ruling (1) of 06:21
  withdrawn. F01 material is kept in Appendix A as "gated: re-test".

**L2. V31 and the YM windows.** V31 (docs/DECISIONS.md:568-576): "The base-rule batch H1 to H5 is closed: all five
failed ...; no rerun or variant on these windows, no purchase of the 10 fallback roots, no holdout-2 read." YM is a
fallback root (R1-13: "2019-05-06..2024-02-29 on the 10 fallback roots (YM 6A 6B 6C 6J 6S 6N HG ZW ZM)"). (i) E16-H1's
rule (inventory CDE.json) is F01's rest-of-day rule at h 30, read on YM over 2019-05-06..2024-02-29, which contains
every YM discovery date (2020-12-01..2024-02-29); E16-H4 (reversal of the prior day's settlement-window move, entry
at O_p + 1 minute, exit at S_p - 31) is an F08-type rule read on the same window. (ii) A YM test purchase (ohlcv-1m
2015-10..2019-04) is a purchase of a fallback root's data. V31 also sets the cost-feasibility gate: "every future
hypothesis states, before any data purchase or pre-registration, its expected gross per trade from published evidence
against the D8 round-trip cost of its vehicle, and is dropped if the expected gross does not clear the cost by its
pass multiple".
- *Resolved by the lead (LR-V31):* V31 is read literally (in force): YM has no buyable clean test window and its owned
  2019-05..2024-02 window was read by E.16, so every combination with a YM or MYM member has clean_test_window_months
  = 0 (Q7 -2). The narrow reading (V31 covers only H1-H5) is a sensitivity and a decision for the user
  (work/R2/r3_out_q3only.json). The cost-feasibility gate is still open for every program ((d) of each gives the
  published effect sizes; whether F5's c_f stands in for the D8 round trip, and the pass multiple, are the lead's).

**L3. The ZL window.** 2017-05-01..2020-11-30 is the soy test window, sealed for ZM, ZS and ZL, every schema
(reports/stage_e32_test_seal.md section 1 item 2: "No stage may buy, download or open ZM, ZS or ZL data of any schema
dated in that window until a registered test stage reads it once"; item 3: the only permitted steps before the test
are a cost quote, after a funded Databento account exists, then registration, then the one read). V56 item 1: "The
2017-05..2020-11 window stays sealed for a future hypothesis family." Earlier reads, all one-minute bars (seal section 4
table; F2_data_access.json codes.ZL.read_windows): ZL over the whole window by E.16/E.17 (H1/H4 pooled) and E.21 (TSMOM,
trend blend); from 2019-05-06 also E.12 Gate 0, E.20's 45-configuration search and E.22 Part A's K6 confirmation (CP1
momentum into the close, CP2, CP3, the overnight crush-margin-gap rule with ZM and ZL legs). Seal section 4: "No
order-book data (MBO, MBP, trades) for the window was ever bought or read." (i) The seal allows one read, so C138 and
C140 can use it only through one registration. (ii) Without it ZL has no unread unsealed stretch of 24 months or more
before 2024-03 (codes.ZL.read_windows: E.16 and E.21 read 2010-07-01..2024-02-29; p_unread_stretches empty), Q7 drops by
2 and C by 0.30 (2.45; confirmed by work/R2/r3_out_nozlw.json, C138 2.45).
- *Resolved by the lead (LR-ZLW):* V56 item 1 keeps 2017-05..2020-11 "sealed for a future hypothesis family", so ZL
  keeps its sealed test window; which family gets its single read is a user decision. The ZL F09 and F10 candidates
  are written below as one program on that one read.

**L4. Model rules (open fact, no decision asked).** V43 (DECISIONS:788-805) lets an ML model be the traded strategy
"for order-book and limit-order strategies" only; "V28 stands unchanged for every other line (no ML layer on an
untested rule set elsewhere; meta-labeling only after a base rule passes)". Bar price-path families (F08 on MNQ and
YM, F09 on RTY, F09 on ZL on bars) are rule-based under V28 unless the lead reads one as an order-book strategy; ZL F10
can be ML under V43's conditions. E.33 ran its crush and propagation sets as ML because the ZM program was an
order-book program (V51 item 1: "ML is a core tool, under V43").

**L5. MYM data (open fact).** F2_data_access.json codes.MYM.owned lists MYM ohlcv-1m only for 2025-04..2026-06; the
combinations use YM's price path for MYM (groundwork.json for_lead). Relevant now only to the q3only alternatives
(C049) and Appendix A.

**L6. Carried notes (open fact, no score effect).** combos_detail.json lists "leader leg bars: NQ ohlcv-1m for RTY
(owned 2010-06..2024-02)" and "crush legs: ZS and ZM bars for ZL" under unpriced_extras of both C113 (RTY F09) and
C138/C139 (ZL F09): one F09 list carried into every F09 row; each row's own leg is the relevant item. R2_dossiers.md
RTY|F09's "Participant flow" line reads "Hedgers and spread traders anchoring an economic relation (crush margin)",
the F09 template text; RTY's stated mechanism is NQ leading Russell (F09.E06).

**L7. Shared test windows (open fact).** One registered read spends a window (protocol P9: "No re-run: a bug found
after the read voids the test; the window is spent"). ZL: C138 and C140 share the sealed window (L3 (i)). Nasdaq and
Russell: C113 (RTY F09, NQ leader bars) and C072 (MNQ F08, NQ path) would both need post-2024-03 data (Appendix B and
section 4); their longest unread post-2024-03 span today is 2024-03-01..2025-03-31 (13 months; the dates after 2026-06-17,
about 4 months to date, is also neither owned nor read), so two programs reading it would share it. [Version 3: C113
left the R4 under LR-Q3b (L11); the EQ3 pool C147 (section 6) would read the same NQ and RTY span through its MNQ
and RTY members.]

**L8. Drafts.** Every trial count, grid and threshold below is a draft for the lead's pre-registration.

**L9. F12.** The lead's ruling (4) at 06:21:31: MNQ F12 and the F12 pools keep Q3 = 1 only if the pre-registration
excludes R1-14 H6 T3 (negative-GEX momentum into the close). F12 appears below only in the q3only alternatives (C039 YM
F12, section 9) and is carried there.

**L10. New in version 2 (open facts).** (i) MNQ and RTY have no clean pre-2024-03 test window (F2_data_access p_basis:
RTY "history 2017-07-10..2024-02-29 (79.7 months): no unread unsealed stretch of 36 months or more, no pre-2024-03
window sealed"; MNQ, through NQ, the same over 2010-06-06..2024-02-29), so their tests would read 2024-03 onward, which
V51 item 2 keeps closed unless the user approves; seal section 1 item 4: "2024-03-01 onward stays closed to this
program (program embargo; V48 gives no approval)". (ii) C072 (MNQ F08) passes Q6 on Topstep's Consistency Path
(LR-Q6p, no per-day minimum); on the Standard Path its one-lot sqrt(n/day) sigma_hc v is USD 73.55 against the USD 150
winning-day threshold ("payout_threshold_exceeds": true), which deducts 1: Q6 3, C 2.40 (work/R2/r3_out_ts150_v2.json,
on the corrected base: C072 2.40, rank 22; C147 2.40 through its MNQ member). C021 (YM) and C113 (RTY) stay below the threshold
($316.17, $932.96). (iii) V49 (R1-22) drops NQ; MNQ trades NQ's path, and "NQ-based closed lines bind MNQ because the
price path is the same" (R2_dossiers MNQ head note); RTY F09 uses NQ only as a leader input.

**L11. RV2 B1: cross-market leads in R1-11 and R1-15 (new in version 3).** The RecsReviewer (briefs/REVIEW_recs.md,
B1) found that E.12's Gate 0 (R1-11) and E.20's search (R1-15) held G17 cross-market lead features, which R1's line
summaries left out. R1Fixer's check of the frozen code (work/fix4/r1/r1fix_report.md section 1, F1-F5): G17 is "the
60-minute log return (x 1e4) of each other cluster's lead price path" (ml_route_v2/signals/generic.py:22-25), never
applied on the row's own cluster (generic.py:343, 351-352). Live leads on M2K/RTY: ZN, 6E, CL, GC, ZC (NQ, its own
cluster's lead, excluded); on ZL: NQ, ZN, 6E, CL, GC (ZC excluded; ZS and ZM are cluster members, not G17 leads). E.12
also had g17_mbt, live only 2024-01-02..2024-02-29 (MBT's store start), and excluded g17_mes by rule P-1a
(reports/stage_e12_rulings.md:49). Horizons h60, h120, hF. E.12 tested G17 pooled over its 27 products (Family A) and
as inputs of Family B's ridge (one model per horizon pooled across products, tested per product and horizon); E.20
ran one pooled model per horizon over the 17 vehicles, 2019-05-06..2024-02-29, at decision times 09:00, 11:00 and
13:00 CT and t4 14:08 CT on equity (grains 09:00, 10:00, 11:00 and t4 12:18 CT). The rater's Q3 = 2 for RTY F09 and
ZL F09 rested on R1's summaries. Both R1 lines now carry the content (briefs/R1_closed_lines.md and .json, R1-11 and
R1-15, "cross-market [added 2026-10-29 (session 4, RV2 B1/S6)]").
- *Resolved by the lead (LR-Q3b, 07:19:57; RULINGS.md "Rulings (session 3 end and session 4)"):* RTY F09 (C112-C116)
  and ZL F09 (C138-C139) get Q3 = 1, "same family and product at a neighbouring horizon" (spec 8.3; h60-hF against
  bands of 15-30 and 15-60 minutes); the rater's 2 is kept as Q3_rater in R2_combinations.json; applied by
  work/R2/patch_v31_q3_lead.py in every mode, and r3 rerun. The leg-level reading (the dossier's leaders, NQ for RTY and
  ZS/ZM for ZL, were never live features there: Q3 = 2) is the sensitivity q3bleg (work/R2/r3_out_q3bleg.json), which
  reproduces the version 2 list. Effects: C138 2.75 -> 2.65, C139 2.60 -> 2.50, C113 2.60 -> 2.50 (leaves the R4;
  Appendix B), C112 and C115 2.60 -> 2.50, C114 2.45 -> 2.35, C116 2.15 -> 2.05; C147 EQ3 F08 enters the R4 at 2.55;
  the best own broker becomes C141, ZL F10 at IBKR (2.60). LR-OF (08:58): on ZL, R1-11 and R1-15 are the same family
  for F09 at a neighbouring horizon and other families for F10 (no order-book features in either library).

## 1. The R4 list (r3_out.json "R4", version 3 after LR-Q3b, verbatim) and its grouping

| R4 | id | product or pool | family | best venue | band B | h_c | C | weak | r3 rank |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C140 | ZL | F10 order-book state at 5 min and longer | topstep | 15, 30, 60 | 30 | 2.75 | no | 1 |
| 2 | C138 | ZL | F09 cross-market lead-lag | topstep | 15, 30, 60 | 30 | 2.65 | no | 2 |
| 3 | C072 | MNQ | F08 session and overnight-to-day handoff | topstep | 15, 30 | 30 | 2.55 | no | 4 |
| 4 | C021 | YM | F08 session and overnight-to-day handoff | topstep | 15, 30 | 30 | 2.55 | no | 5 |
| 5 | C147 | EQ3 {YM, MNQ, RTY} | F08 session and overnight-to-day handoff | topstep | 15, 30 | 30 | 2.55 | no | 12 |
| own broker | C141 | ZL | F10 order-book state at 5 min and longer | ibkr | 15, 30, 60 | 30 | 2.60 | no | 3 |

- n_reaching_2 = 5; fewer_than_3_reach_2 = false; "R4_prop_only" is the same five. None is weak.
- Ties (r3_out.json "ties"): none at 2.75, 2.65 or 2.60 (C140, C138 and C141 stand alone); at 2.55 C072 above C021 by
  G(h_c) 0.0805 < 0.0894, then C075, C074 (MNQ lucid, mffu), C019, C023, C022, C020 (YM), C147 (EQ3; G 0.0973, its
  worst member's), C108 (RTY, below C147 by product code), C107, C161, C110; at 2.50 C134 (ZL F03 topstep) above C113
  by Q1, then C112, C115 and C139 by G(h_c).
- Q3 under LR-Q3b (L11): C138 has Q3 1 (the rater's 2 is kept as Q3_rater); C140 and C141 keep the rater's 2.
- Q7 under LR-V31 and the census: C072, C021 and C147 carry the 24-month test-window deduction (Q7 2); C140, C138 and
  C141 keep Q7 4 on the sealed ZL window.
- Sensitivities (section 9): q3only puts C021 YM F08 first (2.85); nozlw puts C072 MNQ F08 first (2.55); q3bleg (the
  leg-level F09 reading) reproduces the version 2 list (C138 and C140 2.75, C113 2.60, C072 and C021 2.55).

Grouping:
- **Program 1, ZL (C140 F10 and C138 F09)**: one product, venue, band and sealed test window; one registration with two
  feature families on the one sealed read (L3), F10 first (the higher C). The best own-broker C141 (ZL F10 at IBKR) is
  an execution choice of the same program (section 7); C139 (ZL F09 at IBKR) is 2.50 under LR-Q3b.
- **Program 2, MNQ F08 (C072)** and **Program 3, YM F08 (C021)**: the same family at the cash open on two underlyings.
  Sections 4 and 5 keep them separate because their data constraints differ (post-2024-03 data for MNQ; V31 for YM).
- **Program 4, EQ3 F08 (C147)**: the same handoff pooled over YM, MNQ and RTY at Topstep, one registration (section 6).
  Under the decisions in force its YM member cannot enter (LR-V31), so the pool is cut to MNQ and RTY (6(b) P9).
- RTY F09 (C113, 2.50) left the R4 under LR-Q3b (L11); its tables are kept in Appendix B.

## 2. Outline skeleton shared by every program (reports/stage_e32_discovery_protocol.md P0-P10)

Items stated here are not repeated in the programs.
- P0 change control: frozen and hashed before any outcome read; nothing chosen by looking at an outcome.
- P1 data: files with sha256, data allowlist and refusals, sessions, trade dates, and P1.5 "Prior exposure of the
  discovery dates, and the firewall".
- P2 families: mechanism, evidence, overlap with closed lines and how the family differs.
- P3 labels, horizons (the pair's band B only, LR-R2b), executable prices, trade rule, exclusions, simulation.
- P4 features with exact definitions; leakage tests and synthetic proofs before any real-outcome fit.
- P5 models: rule-based (V28) or ML under V43's conditions (L4).
- P6 validation: E.33 used 6 blocked folds with a 21-date embargo and out-of-fold dates; PBO reported, not a gate.
- P7 budget: every configuration registered in one screening.trial_registry call before any real-outcome fit; every
  one counts into N whatever the outcome (N now 838, r009-E33); thresholds from p7_final.py at the registered N
  (section 8).
- P8 selection (mechanical): G1 activity, G2 edge, G3 DSR > 0.95 at N with V = 1/(T_disc - 1), G4
  SR_d - se(SR_d) >= b_test, G5 stability; Tier A at most 3 with OOF correlation <= 0.70; Tier B 2. ZM-specific
  numbers each program re-sets: G1 "at least 1.0 trade per OOF date on average (at least 796 trades)" (a once-a-day
  family trades at most once a date), G2 "mean net per trade >= 0.50 tick (Topstep, market, L = 1 s)" with its
  Tradeify 0.920 margin note, G5 (d)'s sigma_ZM terciles.
- P9 test: one read of a window that never selected anything; the frozen pipeline; verdict (1) as coded
  (screening/stage_e_verdict.py: Holm at K = 9, DSR > 0.95 at the program N with V14 (c)'s variance, daily t > 3.0,
  CSCV PBO < 0.5) and (2) the protocol-added DSR > 0.95 at the same N with V = 1/(T_test - 1) (kept by V52 item 1); a
  pass reads "edge candidate, composite pending" (V14 a); no re-run. E.32 D2 (amend V14 (c)) stays open until a test is
  registered (V56 item 4). Purchase only after a funded Databento account exists and a fresh quote is approved (V51
  item 4; seal section 1 item 3 for the soy window).
- P10 stops for integrity and feasibility only; the null report (funnel, best 10, null distribution and SR0, PBO,
  minimum detectable net edge per horizon, null statement or "no statement", and "No candidate; the test window stays
  sealed; no test data purchase.").
- After a pass, V33 item 1: "No Combine is bought until a strategy passes a registered test and its follow-up reads
  with a net Sharpe of about 0.5 or more."
- V51 item 2: "2024-03 onward stays closed unless the user approves it later, as a possible second confirmation."
  Program 2 (MNQ) and Program 4's MNQ and RTY members have no test window without that approval (L10 (i));
  Program 3 (YM) and Program 4's YM member have none under LR-V31 (section 5).
- T_disc 796 and T_test 870 are spec 8.2's values for every combination; a registration recomputes them on the
  product's calendar and burn-in (and on the actual test span, section 8).

## 3. Program 1: ZL F10 order-book state and ZL F09 cross-market lead-lag (C140, C138; one sealed read)

### 3(a) Fact table

| item | C140 ZL F10 topstep | C138 ZL F09 topstep | source |
|---|---|---|---|
| band B; h_c | 15, 30, 60; 30 | 15, 30, 60; 30 | F5 pair 15 |
| documented horizon vs B | [5, 15, 30]: "documented horizon(s) [5] min lie outside B" | [15, 240]: "documented horizon(s) [240] min lie outside B (15-60 min)"; h_c 30 is not a documented horizon | combos_detail |
| C (r3 rank) | 2.75 (1) | 2.65 (2; Q3 1 under LR-Q3b; 2.75 under q3bleg) | r3_out.json |
| Q1 | 2: "Plausible participant story but forward predictability decays by 5-30 min (F10.E01); grain evidence is a drift-burst reversal with look-ahead (F10.E03, ZC) and an abstract with unknown horizon (F10.E04); the ZM order-flow and book test with ZL MBP-1 input fails net (F10.E07)." | 2: "Identified economic anchor (crush margin) but no evidence at the horizon: cointegration on 180 of 243 days in 2015 with no half-life or trading test (F09.E01); the crush-residual and propagation test on ZM finds nothing net (F09.E02); spillovers within 30 s (F09.E03, abstract)." | R2_combinations Q1 |
| Q2 | 2: "Cousin peer-reviewed in sample (F10.E03, ZC, full text via E.32, look-ahead to remove) and other-asset evidence (F10.E01); sibling program test net negative (F10.E07); nothing on ZL." | 2: "Peer-reviewed in sample on this product but of cointegration only, with no horizon or trading test (F09.E01, full text), so below 3; sibling-leg program test net negative (F09.E02)." | Q2 |
| Q3 | 2: "Family overlap: R1-21 S3 order flow and book state closed on ZM with ZL MBP-1 as an input; R1-20 ZL passive follow-up skipped (execution line); R1-11 ZL bar-feature ML (other family); V50 item 4: ZL MBP-1 2020-12..2024-02 is not a clean holdout." [R1-11 and R1-15 also held G17 cross-market leads on ZL (R1 file, session 4): other families for F10 (LR-OF: no order-book features in either library)] | 1: "LR-Q3b: R1-11 and R1-15 searched G17 cross-market lead features (60-minute lead-path returns of NQ, ZN, 6E, CL, GC, ZC; never the own cluster) on M2K/RTY and ZL at h60-hF: same family and product at a neighbouring horizon (RV2 B1)" (live on ZL: NQ, ZN, 6E, CL, GC; r1fix_report F3-F4). The rater's 2, kept as Q3_rater: "Family overlap: R1-21 S1 crush residual and S2 propagation closed on ZM with ZL as an input leg (LR-R1: family overlap on other products); R1-08 K6-crushgap-01 on ZS; trading ZL on the same residual is the mirror leg (1 if read as a close variant)." | R2_combinations Q3 (LR-Q3b), Q3_rater; ruling (5) 06:21 (rater's value) |
| Q4; Q5; Q6; Q7 | 2 (x 0.0847); 3 (q 0.0645); 4; 4 (discovery USD 19.48, all USD 40.96, estimates; clean 43.04 months, sealed) | 2; 3; 4; 4 (discovery USD 0, all USD 0, clean 43.04 months, sealed) | r3_out.json |
| c_f | 2.38 = S 1.0 (u) + 0.5 + fee 0.88 (USD 5.28 a round trip, stated); USD 14.28 | same | combos_detail |
| sigma_hc; m_hc; G(h_c) | 28.10; 20.90; 0.1492 | same | idem |
| p_be (emp / norm); p_1 at 1 tick net | 0.5569 / 0.5531; 0.5809 / 0.5754 | same | idem |
| K_year; K_disc; K_test; n/day | 2268 (n_cap(30) 9 x 252); 7164; 7830; 9 | same | idem |
| e80 discovery G3+G4 / G3; test | 2.16 / 1.90; 1.81 ticks (USD 10.88) | same | idem |
| c_f + e80_test | 4.19 | 4.19 | idem |
| prop fit | no DLL (Topstep 50K; MLL $2,000 trailing on end-of-day balance, used as the DLL, LR-DLL); MLL/(sigma_30 v) 11.86 a trade, 3.95 a day of 9 trades (2000 / 505.85); flat-by-close 13:10 PT; ZL day session 06:30-11:20 PT, latest start 10:50 PT at h 30; no overnight; payout Consistency Path 0, Standard Path $150 vs $505.85 (below); "Topstep Tier 1 windows do not name this product"; gates none | same | combos_detail prop_fit |
| queue-limit variant | not computed (Topstep) | not computed (Topstep) | dossier conventions |
| same pair elsewhere | C141 ibkr 2.60 (section 7, best own broker); MZL: no combination (not a top-15 code) | C139 ibkr 2.50 (LR-Q3b) | r3_out.json |

Closed-line overlap (R1_closed_lines.md):
- R1-21 (r009-E33, N 538 -> 838): ZM traded, ZS and ZL inputs; S1 crush residual, S2 propagation from ZS and ZL, S3
  ZM order flow and book state, 5-60 minutes; "Tier A empty; best loses 1.098 ticks/trade"; "61 of 300 met G1 (all
  lose over 1.0 tick/trade)"; V56 closes ZM's route; V56 item 2: "Order-book direction is not closed for other
  products."
- R1-08 K6-crushgap-01: ZS traded at 08:30 CT once a day with ZM bars as the signal leg (seal section 4: "the
  overnight crush-margin-gap change (ZS traded, ZM and ZL legs)"); E.22 confirmation null on 2019-05..2024-02.
- R1-20 / V50: passive spread capture closed; V49's ZL follow-up skipped; V50 item 4 on ZL MBP-1 2020-12..2024-02.
- Same family for F09 at a neighbouring horizon (LR-Q3b): R1-11, R1-15 (G17 leads NQ, ZN, 6E, CL, GC at h60-hF).
- Other families: R1-08 CP ports (ZL F01 gated at Q3 0), R1-13, R1-16; for F10 also R1-11 and R1-15 (no order-book
  features in either library).

### 3(b) Pre-registration outline (draft): one registration, two families, one sealed read

- **P1 data.** ZL MBO plus definitions (book) and ZL, ZS, ZM ohlcv-1m (crush legs). Discovery 2020-12-01..2024-02-29:
  bars owned (39 files each; seal section 3); ZL MBO not owned (buy) or the owned ZL MBP-1 front month (E.31). P1.5
  exposure of the discovery dates: E.33 computed the board-crush residual (its F1: "the board crush C = 11 ZL + 2.2 ZM
  - ZS") and ZS/ZL propagation features with ZM labels; E.31 read ZS and ZL MBP-1 for passive markouts with 1 s and
  10 s mid-move splits and queue-imbalance splits (V50 item 4: "Any test of an order-flow signal on these dates is
  therefore not a clean holdout"; a discovery use is disclosed exposure); bar trials on 2019-05-06..2024-02-29 (E.22 K6
  incl. the crush gap, E.12, E.17, E.20; E.12 and E.20 with G17 cross-market leads NQ, ZN, 6E, CL, GC on ZL
  at h60-hF, R1-11 and R1-15). Test 2017-05-01..2020-11-30, sealed (L3), bars inside the sealed files, MBO
  from 2017-05-21 (protocol P9: "On 2017-05-21, CME introduced full granularity for every order event (MBOFD)"; for ZM
  it used trade dates 2017-05-22..2020-11-30, 890 dates, 870 after a 20-date burn-in, and "The 15 trade dates
  2017-05-01..2017-05-19 stay sealed and untested"). Sessions: ZL day 08:30-13:20 CT (06:30-11:20 PT), pause 07:45-08:30
  CT.
- **P2 families.** F10 on ZL: E.32's F3 definitions (12 features: order-flow imbalance, aggressor imbalance, touch
  cancellations, sweeps, hidden-order refills; seasoned depth as the spoofing guard) on ZL's own book; "In no more
  than thirty minutes, order imbalances lose their predictive ability" (Chordia, Roll and Subrahmanyam, in the
  protocol's F3). F09 on ZL: crush legs cointegrated intraday on 180 of 243 day sessions in 2015, no fixed leader, no
  half-life (F09.E01); the E.32 protocol's F1 (crush residual; levels "normalised by causal rolling statistics, never
  fixed cents", because of the oil-share regime) and F2 (propagation, "minute look-backs only") mirrored with ZL as the
  traded leg. Stated differences: from R1-21, the traded leg and its label (ZL instead of ZM) and, for F10, ZL's own
  MBO instead of ZM MBO with ZL MBP-1 inputs; from K6-crushgap-01, minutes-scale and continuous against a once-a-day
  overnight gap traded in ZS; for F09, from R1-11 and R1-15's G17 features, the leaders (ZS and ZM, never G17 leads) and
  the 15-60 minute band against h60-hF. E.33's context block C (15 features) can enter every set, as in E.33.
- **P3.** Horizons {15, 30, 60} (B; E.33's F05 label, F10's documented 5 and F09's documented 240 lie outside B).
  Labels F15, F30, F60, T15, T30 (E.33's six minus F05); market orders; executable prices from the book with
  Topstep's 1 s latency (E.33 P3.2) where the book is used, bar opens otherwise.
- **P4-P5 (draft; L4 decides the model rule).** Option A, E.33-style ML under V43 for all sets: S_crush (F1 mirror),
  S_prop (F2 mirror), S_book (F3 on ZL), S_pool (all three), each with C, x 5 labels x 10 model settings (6 LOGIT,
  4 LGBM) = 200. Option B, rules for F09 on bars (V28) and ML for F10 (V43): F09 rules {reversion at |z| >= 1.5,
  reversion at |z| >= 2.0, ZS leads, ZM leads} x h {15, 30, 60} = 12, plus S_book 5 x 10 = 50: 62. V43's conditions
  for every ML set (DECISIONS:792-803): frozen and hashed before any outcome read; "every configuration searched counts
  into N"; "purged and embargoed cross-validation on the discovery data"; tested once "on data that never selected it
  ... with the program's bar (Holm, net Sharpe, DSR at N, PBO)"; "costs use the measured fill and adverse-selection
  model from the tick-data pilot, never touched-means-filled"; "no model trades, on paper or live, before it passes".
- **P6.** 6 blocked folds, 21-date embargo (E.33); rules have only the causal z to estimate.
- **P7 (draft).** Option A 200 -> N 1038 (binding 0.2028 daily, b_test 0.1670); option B 62 -> N 900 (binding about
  0.2014, between the 50 and 100 rows of section 8). One registration covers both families because the window
  allows one read (L3 (i)).
- **P8.** Section 2; G1's 1.0 trade a date fits continuous families; G2 re-set in ZL ticks (USD 6).
- **P9.** One read of ZL, ZS, ZM bars and ZL MBO (and definitions) over 2017-05..2020-11 under soy_test_seal.py's guard,
  after the user assigns the window's single read to this program (LR-ZLW). Regime differences E.32 P9 names: the
  oil-share regime (renewable diesel: discovery inside the high-oil-share regime, the test before it), the 2020 COVID
  liquidity collapse, the 2021-2022 change in federal position limits, lower volume in 2017-2019.
- **P10.** Section 2.

### 3(c) Data purchase plan

| use | schema | symbols | dates | status | approximate cost (estimate) |
|---|---|---|---|---|---|
| discovery, F10 | mbo | ZL.v.0 | 2020-12-01..2024-02-29 | not owned | USD 19.48 (census k USD 0.4995 a month, scaled from mbp-1, x 39) |
| discovery, F10 (alternative) | mbp-1 | ZL front month | 2020-12..2024-02 | owned (E.31); read by E.31 and E.33 (V50 item 4) | 0 |
| discovery, F09 | ohlcv-1m | ZL.v.0, ZS.v.0, ZM.v.0 | 2020-12-01..2024-02-29 | owned (39 files each); exposure in 3(b) P1 | 0 |
| test, F10 | mbo | ZL.v.0 | 2017-05-21..2020-11-30 (MBP-10 is the highest granularity before 2017-05-21) | sealed, never bought | USD 21.48 (0.4995 x 43) |
| test, F10 (alternative) | mbp-1 | ZL.v.0 | 2017-05..2020-11 | sealed, never bought | USD 23.36 (census mbp-1 USD 0.5432 a month x 43) |
| test, F09 | ohlcv-1m | ZL, ZS, ZM | 2017-05-01..2020-11-30 | owned inside the sealed soy files (ZL: 44 raw ohlcv-1m monthly chunks 2017-04..2020-11 plus stores and caches; docs/soy_test/SOY_TEST_MANIFEST.json); sealed | 0 |
| definitions | definition | ZL | both windows | E.31 bought 2020-12..2024-02 definitions; none for the test window | not priced |
| closed | any | ZL, ZS, ZM | 2024-03-01 onward | V51 item 2 | - |

Quote requests to obtain later (combos_detail): GLBX.MDP3, mbo, ZL.v.0, 2020-12-01..2024-02-29; GLBX.MDP3, mbo,
ZL.v.0, 2017-05-01..2020-11-30 (MBP-10 before 2017-05-21); plus ZL definitions for the test window (as E.32 P9 listed
for ZM). Drafter's notes: E.32 P9 requested ZM's test MBO "from 2017-05-21"; E.31's first discovery chunk starts at
2020-11-30T22:00Z, the soy window's exclusive end (seal section 1 items 5-6); the test quote is allowed only after a
funded Databento account exists (seal section 1 item 3). Program total (estimates): USD 0 for bars, USD 40.96 with MBO
in both windows, or USD 23.36 with owned MBP-1 discovery and an MBP-1 test.

### 3(d) Kill-criteria facts

- Power: e80 discovery 2.16 (G3+G4) / 1.90 (G3), test 1.81 ticks (USD 10.88); c_f + e80 4.19 ticks; q 0.0645 at
  K_test 7830. K counts every 30-minute slot of the 290-minute session (n_cap 9); e80 scales with 1/sqrt(K): a rule
  that trades once a day (K 870) has e80_test 0.1936 x 28.10 = 5.44 ticks.
- Thresholds (section 8): binding discovery SR_d about 0.2014 (N 900) to 0.2028 (N 1038); b_test about 0.1655 to
  0.1670.
- Published effect at the horizon. F09: none (F09.E01 cointegration only, no half-life or trading test; F09.E03
  spillovers within 30 s, abstract). F10 (arithmetic on F10.E01, NYSE stocks 1996; assumptions: bivariate normal
  predictor and return, R2 read as a squared correlation, a sign rule, gross): 30-minute forward R2 0.53% gives a
  correlation of 0.0728 and a gross edge of 0.058 sigma, 1.63 ZL ticks at sigma_30 28.10, below c_f 2.38; the 5-minute
  R2 3.32% is outside B.
- Program measurement on the sibling leg (R1-21, ZM): no configuration passes; best -1.098 ticks a trade; the median
  configuration loses 2.2 to 2.6 ticks a trade at every firm's fee; minimum detectable edges 1.5 to 4.4 ticks a trade
  at the trade rates seen (E.33c_RETURN section 7 item 2); S3's G1 configurations all lost more than 1.0 tick a trade.
- Prop limits by horizon (F5 pair 15; Q6 deducts 1 below 3 and 2 below 1.5; the F5 band needs >= 2): MLL/(sigma_h v)
  15: 16.36, 30: 11.86, 60: 8.72, 120: 6.31, 240: 4.29, OC: 3.68, cc: 2.85 (< 3); a day of 9 trades at h 30: 3.95.
  Payout below $150 on either path.
- Data: bars cost nothing; MBO about USD 40.96 (estimate); the window's single read is the user's assignment (LR-ZLW).

## 4. Program 2: MNQ F08 session and overnight-to-day handoff (C072, Topstep)

### 4(a) Fact table

| item | C072 MNQ topstep | source |
|---|---|---|
| band B; h_c | 15, 30; 30 | F5 pair 2 |
| documented horizon vs B | [30, 60]: "documented horizon(s) [60] min lie outside B (15-30 min)" | combos_detail |
| C (r3 rank) | 2.55 (4) | r3_out.json |
| Q1 | 3: "Identified carry-over of prior-US-close imbalances into the European open on the ES cousin (F08.E03, 1998-2020, gross Sharpe 1.1, -0.5 after spreads), documented at 60 min outside the 15-30 band and outside the main session; the cash-open handoff has only F01.E05 (SPY, to 2013)." | Q1 |
| Q2 | 2: "Peer-reviewed in sample on a cousin (F08.E03, ES, full text; negative after spreads) and other-venue SPY (F01.E05); nothing on this underlying." | Q2 |
| Q3 | 1: "Same family and underlying: R1-03 K1-cp3-01 prior-day close-location (MNQ traded, 08:30 CT to flat), R1-13 E16-H4 (pooled incl. NQ) and R1-10 K8-wkndbtc-01 (MNQ) are closed; a 15-30 min hold of these handoff signals is a close variant; R1-01 MES family overlap." | Q3 |
| Q4; Q5; Q6; Q7 | 3 (x 0.0268); 2 (q 0.1936); 4 (Consistency Path; Standard Path see L10 (ii)); 2 (clean window 0.82 months, 2010-06-06..2010-07-01) | r3_out.json |
| c_f | 3.94 = 1.0 (u) + 0.5 + fee 2.44 ticks (USD 1.22 a round trip, stated; tick USD 0.50); USD 1.97 | combos_detail |
| sigma_hc; m_hc; G(h_c) | 147.10 (NQ's F3, OC-1); 107.94; 0.0805 | idem |
| p_be (emp / norm); p_1 | 0.5183 / 0.5168; 0.5229 / 0.5210 | idem |
| K_year; K_disc; K_test; n/day | 252; 796; 870; 1 (daily family) | idem |
| e80 discovery G3+G4 / G3; test | 33.96 / 29.79; 28.48 ticks (USD 14.24) | idem |
| c_f + e80_test | 32.42 | idem |
| prop fit | no DLL (MLL $2,000, LR-DLL); MLL/(sigma_30 v) 27.19; flat-by-close 13:10 PT; gate note "documented exit 07:00 PT vs flat-by-close 13:10 PT"; no overnight; payout Consistency 0; Standard $150 vs $73.55 (exceeds); news: "Topstep Tier 1: micro capped, one lot allowed (not stopped)"; gates none | combos_detail prop_fit |
| same pair elsewhere | C075 lucid 2.55, C074 mffu 2.55, C073 tradeify 2.40 (Q6 3: Tradeify's $150 threshold), C076 ibkr 2.40 (Q6 3: sigma_day) | r3_out.json |

Closed-line overlap (inventory K1.json, K8.json; R1_closed_lines.md):
- R1-03 K1-cp3-01 (MNQ traded): "on the 08:30 bar of CT date d: prior COMPLETE day's CLV = (C - L)/(H - L) of its
  [08:30, 15:00) bars >= 0.8 (buy) or <= 0.2 (sell)"; fill at the 08:31 open; exit at the 14:59 open.
- R1-13 E16-H4 (pooled incl. NQ, 2010-07..2024-02): opposite to the prior date's S-30 to S move, entry at O_p + 1
  minute, exit at S_p - 31.
- R1-10 K8-wkndbtc-01 (MNQ traded): Monday trades on the weekend MBT move ("P_F Friday 14:59 bar close, P_S Sunday
  17:59 bar close"), "fill at the 18:00 MNQ open", exit "on the first present MNQ bar at or after 14:58 on CT date d";
  inconclusive by design, not run in confirmation.
- R1-01 MES families A (clock windows) and D (gaps), incl. European-open drift (MES outside the universe).
- NQ-path lines of other families: R1-14 (H6, F01), R1-15 (E.20 search), R1-18 (H6 reversal at 5 and 20 days).

### 4(b) Pre-registration outline (draft)

- **P1 data.** NQ ohlcv-1m (NQ.v.0) as MNQ's price path (OC-1; MNQ ohlcv-1m owned only 2025-04..2026-06). Discovery
  2020-12-01..2024-02-29, owned. P1.5 exposure: E.16 H1/H4 (NQ, 2010-07..2024-02), E.21, E.20's search, R1-14 H6
  (2020-06..2024-02), E.12 Gate 0 (MNQ vehicle, cp1_ret and cp3_clv features). Test: no clean pre-2024-03 window (L10
  (i)); post-2024-03 as in Appendix B(b) P1 (2024-03-01..2025-03-31 not owned and not read; 2025-04..2026-06 owned and read by
  E.7 K1 and E.9 K8 on MNQ); needs the user's approval (V51 item 2).
- **P2 F08 at the cash open.** Excluded: K1-cp3-01's rule (closed on MNQ at every venue), E16-H4's rule, K8-wkndbtc-01's
  rule. The documented European-open trade (02:00-03:00 ET = 01:00-02:00 CT, 60 minutes) lies outside B and outside
  the main session (LR-R2b).
- **P3 (draft).** Entry at the 08:31 open, exit at the open of the bar at 08:31 + h, h {15, 30}; one trade a trade
  date. On CPI, PPI and NFP days the overnight return contains the 07:30 CT release (F04's event): excluding those
  days is a declared choice. Topstep's Tier 1 window does not reach 08:31 CT, and micros are capped at one lot, not
  stopped.
- **P4 (draft).** ON = sign(close of the 08:29 bar minus open of the 17:00 CT bar of d-1); CLV of the prior complete day
  with K1-cp3-01's 0.8 / 0.2 thresholds; side {continuation, reversal}; grid 2 x 2 x 2 = 8. (CLV, continuation) shares
  K1-cp3-01's trigger, entry bar and side and differs only in the exit (08:31 + h against 14:59), the scorer's
  close-variant reading; without the CLV members: 4. K8-wkndbtc-01's Sunday-evening entry differs in time and signal.
- **P5-P6.** Rule-based (V28); nothing to fit.
- **P7 (draft).** 8 (or 4) -> N 846 (842): binding 0.2008 daily, b_test 0.1650 at 870 test dates.
- **P8.** Section 2, G1 for a once-a-day family, G2 in MNQ ticks (USD 0.50).
- **P9.** One read of NQ ohlcv-1m over the approved post-2024-03 span; at 13 months (about 273 dates) b_test 0.2964 and
  SR80_test 0.3485 (section 8).
- **P10.** Section 2.

### 4(c) Data purchase plan

| use | schema | symbols | dates | status | approximate cost (estimate) |
|---|---|---|---|---|---|
| discovery | ohlcv-1m | NQ.v.0 | 2020-12-01..2024-02-29 | owned (NQ 2010-06..2024-02); read (4(b) P1) | 0 |
| test (needs the user's approval, V51) | ohlcv-1m | NQ.v.0 | 2024-03-01..2025-03-31 | not owned, not read | about USD 1.29 (USD 0.0995 a month x 13; 2010-2019 quote rate) |
| owned after 2024-03 | ohlcv-1m | NQ, MNQ | 2025-04..2026-06 | owned; read by E.7 and E.9 (MNQ); closed by V51 | 0 |

Quote request to obtain later, after the V51 approval, a funded account and an approved fresh quote: GLBX.MDP3,
ohlcv-1m, NQ.v.0, 2024-03-01..2025-03-31 (ON on the first test date needs the 17:00 CT bar of 2024-02-29, inside the
discovery file). The same NQ request serves Program 4's MNQ member (section 6) and RTY F09 (Appendix B; L7).

### 4(d) Kill-criteria facts

- Power: e80 discovery 33.96 / 29.79, test 28.48 ticks (USD 14.24); c_f + e80 32.42; q 0.1936. At the 13-month span:
  0.3485 x 147.10 = 51.26 ticks.
- Published effect (arithmetic on F08.E03, ES, European open, outside B and the main session): Sharpe 1.1 a year gross
  is 0.069 daily; -0.5 a year after spreads is -0.031 daily; against 0.2008 daily (3.19 a year) at selection. No
  futures evidence at the cash open (scorer flag 13).
- Prop limits by horizon (F5 pair 2): MLL/(sigma_h v) 15: 37.87, 30: 27.19, 60: 19.74, 120: 14.12, 240: 10.26, OC:
  6.94, cc: 5.72: no breach at any horizon. Payout: the Standard Path's $150 exceeds the one-lot sqrt(n/day) sigma v of
  $73.55 (L10 (ii)); E.29 section 1: a one-lot micro rarely clears the $150 winning-day threshold (MGC).
- Data: about USD 1.29 (estimate), only with the V51 approval.

## 5. Program 3: YM F08 session and overnight-to-day handoff (C021, Topstep), under V31

**V31 constraint, stated plainly (LR-V31).** YM is one of V31's 10 fallback roots. Read literally, V31 forbids any
purchase of YM data ("no purchase of the 10 fallback roots") and any "rerun or variant" on YM's E.16 window
2019-05-06..2024-02-29, where E16-H1 and E16-H4 (an F08-type next-day reversal) were read. So C021 has no buyable clean
test window (Q7 2), every owned pre-2024-03 YM date was read by E.16, and the only owned YM data outside that window
is 2025-04..2026-06 ohlcv-1m, closed by V51 item 2 (needs the user's approval) and read through MYM by E.7 K1 (not
clean). Whether an F08 discovery search on 2020-12..2024-02 is itself a "variant on these windows" is part of the
same reading (the score applies V31 to the test window only). Under the narrow reading (the user's decision;
work/R2/r3_out_q3only.json), the test would be YM ohlcv-1m 2015-10-01..2019-04-30, never read, about USD 4.26.

### 5(a) Fact table

Every cost, power and prop number is YM-Topstep's at h 30: band 15, 30; h_c 30; c_f 2.256 (fee 0.756 = USD 3.78 a
round trip, stated; USD 11.28); sigma_30 63.23; m 45.42; G 0.0894; p_be 0.5248 / 0.5224; p_1 0.5358 / 0.5323; K 252 /
796 / 870, one a day; e80 14.60 / 12.80 / 12.24 ticks (USD 61.22); c_f + e80 14.50; MLL/(sigma v) 6.33; flat-by-close
13:10 PT; payout Consistency 0, Standard $150 vs $316.17 (below); 0 Tier 1 events a week; gates none.

| item | C021 YM topstep | source |
|---|---|---|
| documented horizon vs B | [30, 60]: 60 outside B | combos_detail |
| C (r3 rank) | 2.55 (5); 2.85 under q3only (rank 1) | r3_out.json; q3only |
| Q1; Q2; Q3 | 3; 2; 1 (reasons as C072's, with "R1-03 K1-cp3-01 prior-day close-location (MYM traded, 08:30 CT entry to flat) and R1-13 E16-H4 next-day reversal (pooled incl. YM, intraday) are closed") | R2_combinations |
| Q4; Q5; Q6; Q7 | 3 (x 0.0357); 2 (q 0.1936); 4; 2 (LR-V31: clean_test_window_months 0; 106.97 before V31) | r3_out.json; R2_combinations data |
| gate note | "flat-by-close gate: documented exit 07:00 PT vs flat-by-close 13:10 PT" | combos_detail |
| same pair elsewhere | C019 bulenox, C023 lucid, C022 mffu, C020 tradeify 2.55; C024 ibkr 2.10 (Q6 1: margin USD 12,699.91 > 6,000 u); MYM F08 C049 mffu (q3only 2.70); EQ3 pool C147 2.55 (section 6) | r3_out.json |

Closed-line overlap: R1-03 K1-cp3-01 (MYM traded; the CLV rule quoted in 4(a), 08:31 to 14:59); R1-13 E16-H4 (pooled
incl. YM, 2019-05-06..2024-02-29; V31); R1-01 MES families A and D; scorer flag 13: "a cash-open F08 test has no
direct evidence".

### 5(b) Pre-registration outline (draft)

- **P1 data.** YM ohlcv-1m (YM.v.0). Discovery 2020-12-01..2024-02-29 (owned, inside E.16's YM window). Test: none
  under LR-V31 (above); under the narrow reading 2015-10-01..2019-04-30 (43 months) or any 43-month span of the unread
  2010-06-06..2019-05-06 (107.0 months). YM settled at 15:15 CT before 2020-10-26 and at 15:00 CT after
  (reports/stage_e16_settlement.md, via the K1 inventory); the F08 trade at 08:31 CT is not affected.
- **P2-P10.** As Program 2 on YM's path: the same draft grid (ON and CLV x side x h {15, 30} = 8, or 4 without CLV),
  rule-based (V28), N 846 (842); excluded configurations K1-cp3-01 (on MYM; YM path) and E16-H4 (V31).

### 5(c) Data purchase plan

- Under LR-V31: no purchase is allowed; no test window; owned 2025-04..2026-06 YM bars only with the user's V51
  approval (read through MYM by E.7).
- Under the narrow reading (user's decision): GLBX.MDP3, ohlcv-1m, YM.v.0, 2015-10-01..2019-04-30, about USD 4.26
  (E.12 quote USD 10.50261 for 106 monthly chunks 2010-07..2019-04 = USD 0.0991 a month x 43); ON on the first test date
  needs the 17:00 CT bar of 2015-09-30, so the request starts one trade date earlier; the program's files use
  exclusive month ends (range=YYYY-MM-01_next-month-01, seal section 1 item 5).

### 5(d) Kill-criteria facts

- Power: e80 test 12.24 ticks (USD 61.22), c_f + e80 14.50; q 0.1936. Published effect: as 4(d) (F08.E03: 0.069 daily
  gross, -0.031 net). Prop limits by horizon (F5 pair 5): MLL/(sigma_h v) 15: 8.84, 30: 6.33, 60: 4.52, 120: 3.25,
  240: 2.41 (< 3), OC: 1.77 (< 2), cc: 1.45 (< 1.5). Data: none buyable under LR-V31; USD 4.26 under the narrow
  reading.

## 6. Program 4: EQ3 F08, the session and overnight-to-day handoff pooled over YM, MNQ and RTY (C147, Topstep)

### 6(a) Fact table

Pool facts (R2_combinations.json and r3_out.json C147): one registration over the members YM, MNQ and RTY, asset class
equity for all three. rho = 0.5, the spec 8.3 default within a class: E.29 section 3.2 measured only the CL-ZM, CL-GC,
CL-NQ, ZM-GC, ZM-NQ and GC-NQ pairs, none of YM-MNQ, YM-RTY or MNQ-RTY (R2_combinations.json rho_measured = {};
work/fix4/r1/r1fix_report.md F6). K_total = 3 x 870 = 2,610 test trades; K_eff = K_total / (1 + (m - 1) rho) =
2,610 / 2 = 1,305 (r3_out.json C147 K_used; work/score/r3_score.py k_eff); q = SR80_test x sqrt(870 / K_eff) =
0.1936 x 0.8165 = 0.1581 (C147 q; r3_score.py q5_score). K_eff falls if the true rho exceeds 0.5 (at rho 1 it
is 870, one member's count).

| item | YM | MNQ | RTY | source |
|---|---|---|---|---|
| band B; h_c | 15, 30; 30 | 15, 30; 30 | 15, 30; 30 | F5 pairs 5, 2, 9 |
| c_f (ticks); USD a round trip | 2.256 = 1.0 (u) + 0.5 + fee 0.756 (USD 3.78, stated); 11.28 | 3.94 = 1.0 (u) + 0.5 + fee 2.44 (USD 1.22, stated; tick USD 0.50); 1.97 | 2.256 = 1.0 (u) + 0.5 + fee 0.756 (USD 3.78, stated); 11.28 | combos_detail C147 members |
| sigma_30 (ticks) | 63.23 | 147.10 (NQ's F3, OC-1) | 51.75 | idem; F5_holding.json pairs rows."30".sigma |
| c_f / sigma_30 | 0.0357 | 0.0268 | 0.0436 (worst member: the pool's Q4 x) | idem; r3_out.json C147 x |
| K_year; K_disc; K_test; n/day | 252; 796; 870; 1 | 252; 796; 870; 1 | 252; 796; 870; 1 | combos_detail (daily family) |
| trades a year | 252 (one a trade date; F5's continuous cap at h 30, 13 a day or 3,276 a year, does not apply) | 252 | 252 | idem; F5 rows."30".n_cap, trades_per_year |
| e80 test, pooled (q 0.1581 x sigma_30) | 10.00 ticks (USD 49.98) | 23.26 ticks (USD 11.63) | 8.18 ticks (USD 40.91) | arithmetic |
| e80 test alone (q 0.1936, K 870) | 12.24 | 28.48 | 10.02 | combos_detail e80_ticks.test |
| c_f + e80 test, pooled | 12.25 | 27.20 | 10.44 | arithmetic |
| p_be (emp / norm) | 0.5248 / 0.5224 | 0.5183 / 0.5168 | 0.5304 / 0.5273 | combos_detail |
| Q6 (Consistency Path) | 4 (dll 0, payout 0, news 0) | 4 (dll 0, payout 0, news 0) | 4 (dll 0, payout 0, news 0) | r3_out.json C147 Q6_by_member |
| Standard Path $150 vs sqrt(n/day) sigma_30 v | $316.17: below | $73.55: exceeds (deducts 1) | $258.76: below | combos_detail prop_fit |
| MLL/(sigma_30 v) | 6.33 | 27.19 | 7.73 | idem |
| news (Topstep Tier 1) | "the family's fixed trade times lie outside every Tier 1 window" | "Topstep Tier 1: micro capped, one lot allowed (not stopped)" | as YM | idem |
| clean test window | 0 months under LR-V31 (106.97 before V31: 2010-06-06..2019-05-06, never read, unsealed) | 0.82 months (2010-06-06..2010-07-01) | 0.0 months (none) | R2_combinations.json C147 data.windows |
| data after 2024-03 | 2024-03..2025-03 not owned (a purchase, which V31 forbids); 2025-04..2026-06 owned, read through MYM by E.7 K1; 2026-06-18..2026-06-20 owned and unread (owned bars end 2026-06-20), later dates not owned | 2024-03-01..2025-03-31 not owned, not read (13 months, about 273 dates); 2025-04..2026-06 owned, read by E.7 K1 and E.9 K8 on MNQ; 2026-06-18..2026-06-20 owned and unread (owned bars end 2026-06-20), later dates not owned | 2024-03-01..2025-03-31 not owned, not read; 2025-04..2026-06 owned, read through M2K by E.7 K1; 2026-06-18..2026-06-20 owned and unread (owned bars end 2026-06-20), later dates not owned | F2_data_access; sections 4(b), 5 and Appendix B(b) P1 |
| data schema | ohlcv-1m (YM price path) | ohlcv-1m (NQ price path) | ohlcv-1m (RTY price path) | combos_detail members data |
| data cost (estimates) | discovery 0; test none under LR-V31 (USD 4.26 for 2015-10..2019-04 under the narrow reading) | discovery 0; test about USD 1.29 (2024-03..2025-03, needs V51 approval) | discovery 0; test about USD 1.08 (2024-03..2025-03, needs V51 approval) | combos_detail; 6(c) |

Every data period after 2024-03 is closed by V51 item 2 unless the user approves it.

| pool item | C147 EQ3 topstep | source |
|---|---|---|
| documented horizon vs B | [30, 60]: "documented horizon(s) [60] min lie outside B (15-30 min)" | combos_detail C147 |
| C (r3 rank; R4) | 2.55 (12; R4 5): at 2.55 below C020 by G(h_c) (0.0973, RTY's) and above C108 by product code | r3_out.json; ties |
| Q1; Q2; Q3 (weakest member) | 3: "identified imbalance carry-over at the European open on the ES cousin (F08.E03), 60 min outside the band; cash-open handoff only F01.E05"; 2: "cousin peer-reviewed in sample, negative after spreads (F08.E03) and SPY (F01.E05)"; 1: "R1-03 K1-cp3-01 closed on MYM, MNQ and M2K and R1-13 E16-H4 pooled incl. YM, NQ and RTY; 15-30 min holds of these handoff signals are close variants" | R2_combinations.json C147 Q1-Q3 |
| Q4; Q5; Q6; Q7 | 3 (x 0.0436, the worst member's; r3 for_lead: "Q4 pool: worst member's x used (spec names the worst member only for Q6)"); 2 (q 0.1581); 4 (each member 4); 2 (test-window deduction 2: clean_test_window_months 0) | r3_out.json C147 |
| K_total; K_eff; rho; q | 2,610; 1,305; 0.5 (default); 0.1581 | r3_out.json C147 |
| prop fit (one account) | no DLL (Topstep 50K, MLL $2,000 trailing, used as the DLL, LR-DLL); flat-by-close 13:10 PT; latest start 12:30 PT at h 30; no overnight; gate note "flat-by-close gate: documented exit 07:00 PT vs flat-by-close 13:10 PT"; gates none. The three positions open on the same bar: at rho 0.5 their combined daily P&L sigma at one lot each is USD 544.45 (from USD 316.17, 73.55 and 258.76), MLL / that 3.67; MNQ and RTY alone USD 302.32, 6.62 (arithmetic) | combos_detail prop_fit; arithmetic |
| same pool elsewhere | C161 mffu 2.55 (rank 15); C154 tradeify 2.25 (MNQ member Q6 3); C168 ibkr 2.10 (YM and RTY members Q6 1: margin); EQ3m {MYM, MNQ, RTY}: C175 mffu 2.40, C182 ibkr 1.80 | r3_out.json |
| sensitivities | ts150_v2 2.40 (rank 25; MNQ member Q6 3); q3only 2.55 (rank 32; Q7 stays 2, as MNQ and RTY have no clean pre-2024-03 window); nozlw 2.55 (R4 3rd); q3bleg 2.55 (rank 16, outside the R4); v1 2.55 (rank 46) | section 9 files |

Closed-line overlap (the members'; R1_closed_lines.md): R1-03 K1-cp3-01 (the CLV rule quoted in 4(a), MYM, MNQ and M2K
traded, 08:31 to 14:59); R1-13 E16-H4 (pooled incl. YM, NQ and RTY; V31 for YM's window); R1-10 K8-wkndbtc-01 (MNQ);
R1-01 MES families A and D; NQ-path lines of other families R1-14, R1-15, R1-18; R1-11 (E.12 Gate 0 on MNQ, MYM and
M2K) and R1-15 (E.20's search on NQ and RTY) are other families (bar-feature ML, G17 cross-market leads among the
features); scorer flag 13: "a cash-open F08 test has no direct evidence".

### 6(b) Pre-registration outline (draft)

- **P1 data.** YM ohlcv-1m (YM.v.0), NQ ohlcv-1m as MNQ's price path (NQ.v.0; OC-1) and RTY ohlcv-1m (RTY.v.0).
  Discovery 2020-12-01..2024-02-29, owned for all three. P1.5 exposure: E.16 H1/H4 pooled (YM 2019-05..2024-02, NQ
  2010-07..2024-02, RTY 2017-06..2024-02), E.21 (NQ, RTY), E.20's search (NQ, RTY), R1-14 H6 (NQ, 2020-06..2024-02),
  E.12 Gate 0 (MNQ, MYM and M2K vehicles), K1 (R1-03, MYM, MNQ and M2K traded). Test: none for YM under LR-V31
  (section 5); MNQ and RTY have no clean pre-2024-03 window (L10 (i)), so their test reads 2024-03 onward only with the
  user's approval (V51 item 2).
- **P2 F08 pooled.** One registration, members pooled, one mechanism (the handoff at the US cash open); excluded
  configurations as Programs 2 and 3: K1-cp3-01's rule (closed on MYM, MNQ and M2K), E16-H4's rule and K8-wkndbtc-01's
  rule (MNQ).
- **P3.** F08 at 15-30 minutes (B), h_c 30: entry at the 08:31 CT open on each member, exit at the open of the bar at
  08:31 + h, h {15, 30}; one trade per member a trade date, the members' positions opened on the same bar. The CPI,
  PPI and NFP note of 4(b) P3 applies to every member; full-size YM and RTY trade outside Topstep's Tier 1 windows and
  MNQ is capped at one lot, not stopped.
- **P4 (draft).** Program 2's grid (ON and CLV x side x h {15, 30} = 8, or 4 without the CLV members), each
  configuration run on the pool with the same parameters on every member: 8 (or 4) trials.
- **P5-P6.** Rule-based (V28); nothing to fit.
- **P7 (draft).** 8 (or 4) -> N 846 (842): binding 0.2008 daily, b_test 0.1650 at 870 test dates per member (section
  8); pooled per-trade test edge q 0.1581 at K_eff 1,305.
- **P8.** Section 2; G1 for a once-a-day family on each member, G2 in each member's ticks (YM and RTY USD 5, MNQ USD
  0.50).
- **P9. How the pool is cut under the decisions in force.** LR-V31 keeps YM out (no purchase, no variant on E.16's YM
  window), so the registration would cover MNQ and RTY only, on the post-2024-03 span the user approves. By the
  scorer's formulas the two-member pool has K_total 1,740 and K_eff 1,160 at rho 0.5, so q = 0.1936 x sqrt(870 /
  1,160) = 0.1677 (Q5 still 2; e80 test 24.67 ticks on MNQ, 8.68 on RTY) at the 870-date design; on the 13-month
  unread span (about 273 dates a member) K_eff is about 364 (2 x 273 / 1.5) and the test bars are section 8's
  short-window row (b_test 0.2964, SR80_test 0.3485 at N 846). The lead's K0: if only one of V31's narrowing and the
  2024-03+ approval is granted, the pool shrinks to its admissible members and is re-scored before any registration.
  With both granted, YM's test window (2015-10..2019-04) would not overlap MNQ's and RTY's (2024-03 onward), so the
  pooled test would be read over two disjoint spans.
- **P10.** Section 2.

### 6(c) Data purchase plan

| use | schema | symbols | dates | status | approximate cost (estimate) |
|---|---|---|---|---|---|
| discovery | ohlcv-1m | YM.v.0, NQ.v.0, RTY.v.0 | 2020-12-01..2024-02-29 | owned; read (6(b) P1; YM inside E.16's window, V31) | 0 |
| test, YM | ohlcv-1m | YM.v.0 | none under LR-V31; 2015-10-01..2019-04-30 under the narrow reading | not owned, never read; V31 forbids the purchase | USD 4.26 under the narrow reading only (combos_detail C147 all_data_cost_usd; E.12 quote rate USD 0.0991 a month x 43) |
| test, MNQ (needs the user's approval, V51) | ohlcv-1m | NQ.v.0 | 2024-03-01..2025-03-31 | not owned, not read | about USD 1.29 (USD 0.0995 a month x 13; 2010-2019 quote rate) |
| test, RTY (needs the user's approval, V51) | ohlcv-1m | RTY.v.0 | 2024-03-01..2025-03-31 | not owned, not read | about USD 1.08 (USD 0.0827 a month x 13; 2010-2019 quote rate) |
| owned after 2024-03 | ohlcv-1m | YM, NQ, RTY (MYM, MNQ, M2K) | 2025-04..2026-06 | owned; read by E.7 K1 (MYM, MNQ, M2K) and E.9 K8 (MNQ); closed by V51 | 0 |
| not owned | ohlcv-1m | YM, NQ, RTY | after 2026-06-20 | closed by V51 | not priced |

Quote requests to obtain later, only after the user approves 2024-03 onward (V51), a funded Databento account exists
and a fresh quote is approved: GLBX.MDP3, ohlcv-1m, NQ.v.0, 2024-03-01..2025-03-31; GLBX.MDP3, ohlcv-1m, RTY.v.0,
2024-03-01..2025-03-31 (the same two requests serve Program 2 and Appendix B; L7). No YM request under LR-V31
(combos_detail lists GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30, valid only under the narrow reading); the ON
signal on the first test date needs the 17:00 CT bar of the prior trade date, inside the discovery file for 2024-03-01.

### 6(d) Kill-criteria facts

- Power: q 0.1581 at K_eff 1,305; e80 test 10.00 ticks on YM (USD 49.98), 23.26 on MNQ (USD 11.63), 8.18 on RTY (USD
  40.91), that is 0.158 sigma_30 on each member; c_f + e80 12.25, 27.20, 10.44. Cut to MNQ and RTY (6(b) P9): q 0.1677,
  e80 24.67 and 8.68 ticks at the 870-date design.
- Published effect: as 4(d) (F08.E03, ES, European open: 0.069 daily gross, -0.031 net; no futures evidence at the cash
  open, scorer flag 13).
- Prop limits by horizon (F5 pairs 5, 2, 9; MLL/(sigma_h v)): YM 15: 8.84, 30: 6.33; MNQ 15: 37.87, 30: 27.19; RTY 15:
  10.69, 30: 7.73. The three positions at once: about 3.67 (rho 0.5, arithmetic above). Payout: the Standard Path's
  $150 exceeds MNQ's $73.55 (ts150_v2: C147 2.40).
- Data: none buyable for YM under LR-V31; MNQ and RTY about USD 2.37 (estimate), only with the V51 approval.

## 7. Best own-broker combination: C141 ZL F10 at IBKR (non-prop alternative)

### 7(a) Fact table

| item | C141 ZL F10 ibkr | source |
|---|---|---|
| band B; h_c | 15, 30, 60; 30 (LR-F5-IBKR: G <= 1.10 min G; no DLL or flat-by-close condition) | F5 ibkr|ZL |
| documented horizon vs B | [5, 15, 30]: "documented horizon(s) [5] min lie outside B (15-60 min)" | combos_detail |
| C (r3 rank) | 2.60 (3): best own broker; no tie at 2.60. C139 ZL F09 ibkr is 2.50 (rank 21) under LR-Q3b (2.60 under q3bleg) | r3_out.json |
| Q1 | 2: "Plausible participant story but forward predictability decays by 5-30 min (F10.E01); grain evidence is a drift-burst reversal with look-ahead (F10.E03, ZC) and an abstract with unknown horizon (F10.E04); the ZM order-flow and book test with ZL MBP-1 input fails net (F10.E07)." (as C140) | R2_combinations Q1 |
| Q2 | 2: "Cousin peer-reviewed in sample (F10.E03, ZC, full text via E.32, look-ahead to remove) and other-asset evidence (F10.E01); sibling program test net negative (F10.E07); nothing on ZL." | Q2 |
| Q3 | 2: "Family overlap: R1-21 S3 order flow and book state closed on ZM with ZL MBP-1 as an input; R1-20 ZL passive follow-up skipped (execution line); R1-11 ZL bar-feature ML (other family); V50 item 4: ZL MBP-1 2020-12..2024-02 is not a clean holdout." [R1-11 and R1-15 also held G17 cross-market leads on ZL (R1 file, session 4); other families for F10 (LR-OF: no order-book features in either library)] | Q3 |
| Q4; Q5 | 2 (x 0.0891); 3 (q 0.0645 at K 7,830) | r3_out.json |
| Q6 | 3: margin deduction 0 (intraday and overnight initial USD 4,661.63, below the USD 6,000 (u) ceiling); sigma_day deduction 1 (sigma_cc 116.84 ticks x USD 6 = USD 701.05 > 2% of USD 6,000 = USD 120; LR-Q6d); u: "Q6: own-account capital ceiling not recorded -> USD 6,000 (u)" | r3_out.json Q6_by_member; combos_detail own_broker_fit |
| Q7 | 4 (discovery USD 19.48, all USD 40.96, estimates; clean 43.04 months, the sealed ZL window) | r3_out.json; combos_detail data |
| c_f | 2.503 = 1.0 (u) + 0.5 + fee 1.003 ticks (USD 6.02 a round trip, published; LR-F5-IBKR 2 x all-in); USD 15.02 | combos_detail |
| sigma_hc; m_hc; G(h_c) | 28.10; 20.90; 0.1536 | idem |
| p_be (emp / norm); p_1 | 0.5599 / 0.5558; 0.5838 / 0.5781 | idem |
| K_year; K_disc; K_test; n/day | 2268; 7164; 7830; 9 | idem |
| e80 discovery G3+G4 / G3; test | 2.16 / 1.90; 1.81 ticks (USD 10.88) | idem |
| c_f + e80_test | 4.32 | idem |
| fit | own account: no DLL, MLL or flat-by-close; latest start 10:50 PT at h 30; fits the main session; overnight allowed (not needed); sigma_OC 90.58 ticks; queue-limit variant not computed ("the IBKR route is a real exchange order and no platform fact is recorded") | combos_detail own_broker_fit |
| data | as C140: ZL MBO (from 2017-05-21) for discovery 2020-12..2024-02 (USD 19.48) and test 2017-05..2020-11 (USD 21.48), or owned MBP-1 discovery and an MBP-1 test (USD 23.36); estimates | combos_detail data |
| other own-broker rows | C139 ZL F09 ibkr 2.50; C076 MNQ F08 ibkr 2.40; C024 YM F08 ibkr 2.10 (Q6 1: margin); C168 EQ3 F08 ibkr 2.10; C116 RTY F09 ibkr 2.05 (Q6 1: margin) | r3_out.json |
| capital | docs/DECISIONS.md records no own-account ceiling (USD 6,000 u); V32: "The user cannot fund a personal IBKR account yet and plans to build that capital from Topstep XFA payouts." | DECISIONS |

### 7(b)-(c) Outline and data

C141 is an execution choice of Program 1's F10 family (same product, family, band, data and sealed read): IBKR's c_f
2.503 against Topstep's 2.38. Draft: report it as an execution variant of the Topstep selection (E.33 P6.4 precedent:
variants select nothing, no added trials), or select at IBKR's cost separately (adds the F10 count again: S_book's 50
ML configurations, 5 labels x 10 model settings). No extra data beyond Program 1's (3(c)).

### 7(d) Kill-criteria facts

Power as Program 1 (e80 test 1.81 ticks; gross needed 4.32 at IBKR's cost). Account: no prop limit; one contract's
sigma_day USD 701.05 is 11.7% of the USD 6,000 (u) ceiling, the intraday margin 77.7% of it; the user cannot fund the
account yet (V32).

## 8. Thresholds (p7_final.py functions, no data read)

Computed 06:37 PDT (T_test 870) and 06:52 PDT (T_test 273) with protocol/p7_final.py's se_sharpe and g4_threshold,
p7_thresholds.required_sharpe and funnel.multiple_comparisons.expected_max_sharpe (scripts in
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/3860d0d1-cf19-46b3-a4da-6fda65b58c32/scratchpad/d5/:
hurdles.py, short_test.py); T_disc 796, normal moments, b_test = max(daily t 3.0, DSR 0.95 at N with V = 1/(T_test -
1)) as V52 item 1 keeps it. The N 838 row reproduces protocol P7.2 (SR0 0.1137, G3 0.1724, b_test 0.1649, G4 0.2007,
SR80_test 0.1936).

| trials added | N | SR0 (discovery) | G3 SR_d (t) | b_test (t), T_test 870 | G4 SR_d (t) | binding selection | SR80_test |
|---|---|---|---|---|---|---|---|
| 0 | 838 | 0.1137 | 0.1724 (4.86) | 0.1649 (4.86) | 0.2007 (5.66) | 0.2007 | 0.1936 |
| 4 | 842 | about 0.1137 | about 0.1725 | about 0.1650 | about 0.2008 | about 0.2008 | about 0.1937 |
| 8 | 846 | 0.1137 | 0.1725 (4.87) | 0.1650 (4.87) | 0.2008 (5.67) | 0.2008 | 0.1937 |
| 12 | 850 | 0.1138 | 0.1726 (4.87) | 0.1650 (4.87) | 0.2008 (5.67) | 0.2008 | 0.1938 |
| 50 | 888 | 0.1142 | 0.1730 (4.88) | 0.1654 (4.88) | 0.2013 (5.68) | 0.2013 | 0.1942 |
| 100 | 938 | 0.1148 | 0.1736 (4.90) | 0.1660 (4.90) | 0.2018 (5.69) | 0.2018 | 0.1947 |
| 120 | 958 | 0.1150 | 0.1738 (4.90) | 0.1662 (4.90) | 0.2020 (5.70) | 0.2020 | 0.1949 |
| 200 | 1038 | 0.1158 | 0.1746 (4.93) | 0.1670 (4.92) | 0.2028 (5.72) | 0.2028 | 0.1957 |
| 300 | 1138 | 0.1167 | 0.1755 (4.95) | 0.1679 (4.95) | 0.2037 (5.75) | 0.2037 | 0.1966 |

(The 4 row is read between the 0 and 6 rows of the 06:37 run, 0.2008 at 844; not computed separately.)

Short test window (Program 2, Program 4's MNQ and RTY members and RTY F09 in Appendix B, on the 13-month unread
post-2024-03 span, about 273 dates as an approximation):
N 846: b_test 0.2964 (t 4.90), SR80_test 0.3485; N 888: b_test 0.2972, SR80_test 0.3494.

Fact for every program: at N 838 the hurdle is set by the 838 earlier trials; adding 4 to 200 configurations raises
the binding discovery threshold by at most 0.0021 daily. The test window's length moves the test bar more: 870 to
about 273 dates raises b_test from 0.1650 to 0.2964.

## 9. Sensitivities: the alternatives (current files)

Every run is r3_score.py on one mode of work/R2/patch_v31_q3_lead.py applied to the version 1 combinations (the
ts150 mode starts from work/R2/R2_combinations_topstep150.json); v1 is the unpatched version 1 run. The table is
generated from the files' "R4" and "best_own_broker" keys.

| run | file (sha256, first 16) | rulings | R4 (1-5) | best own broker (r3 rank) | reach 2.00 |
|---|---|---|---|---|---|
| primary | r3_out.json (d3812c4020cc32a3) | LR-Q3a, LR-Q3b, LR-V31, LR-ZLW | C140 ZL F10 topstep 2.75; C138 ZL F09 topstep 2.65; C072 MNQ F08 topstep 2.55; C021 YM F08 topstep 2.55; C147 EQ3 F08 topstep 2.55 | C141 ZL F10 ibkr 2.60 (3) | 5 |
| q3only | work/R2/r3_out_q3only.json (08e1bf16c0c9e107) | LR-Q3a, LR-Q3b (V31 narrow reading; user decision D1) | C021 YM F08 topstep 2.85; C140 ZL F10 topstep 2.75; C049 MYM F08 mffu 2.70; C039 YM F12 topstep 2.65; C138 ZL F09 topstep 2.65 | C141 ZL F10 ibkr 2.60 (23) | 5 |
| nozlw | work/R2/r3_out_nozlw.json (a3b5d54b315062c5) | primary plus no ZL window (user decision D2) | C072 MNQ F08 topstep 2.55; C021 YM F08 topstep 2.55; C147 EQ3 F08 topstep 2.55; C108 RTY F08 topstep 2.55; C113 RTY F09 topstep 2.50 | C076 MNQ F08 ibkr 2.40 (21) | 5 |
| ts150_v2 | work/R2/r3_out_ts150_v2.json (e84b024d47adf7e8) | primary with Topstep's Standard Path $150 in Q6 | C140 ZL F10 topstep 2.75; C138 ZL F09 topstep 2.65; C021 YM F08 topstep 2.55; C075 MNQ F08 lucid 2.55; C108 RTY F08 topstep 2.55 | C141 ZL F10 ibkr 2.60 (3) | 5 |
| q3bleg | work/R2/r3_out_q3bleg.json (21ccabbb99777671) | primary without LR-Q3b (leg-level F09 reading) | C138 ZL F09 topstep 2.75; C140 ZL F10 topstep 2.75; C113 RTY F09 topstep 2.60; C072 MNQ F08 topstep 2.55; C021 YM F08 topstep 2.55 | C139 ZL F09 ibkr 2.60 (6) | 5 |
| v1 | work/R2/r3_out_v1.json (ed186d0a53a580c8) | before LR-Q3a, LR-Q3b and LR-V31 (LR-Q6p primary) | C003 YM F01 topstep 2.95; C021 YM F08 topstep 2.85; C043 MYM F01 mffu 2.80; C138 ZL F09 topstep 2.75; C140 ZL F10 topstep 2.75 | C044 MYM F01 ibkr 2.65 (22) | 5 |

**q3only (LR-Q3a and LR-Q3b, V31 narrow, the user's decision D1):** C021 YM F08 topstep 2.85 (Q7 4: YM test
2015-10..2019-04 buyable, about USD 4.26) leads; C049 MYM F08 mffu (30, 60; h_c 30) 2.70 and C039 YM F12 topstep (15,
30) 2.65 (Q 3, 2, 2, 3, 0, 4, 4; L9 applies: exclude R1-14 H6 T3) enter; C138 is fifth (2.65); best own-broker C141
2.60 (rank 23). The Dow candidates (C021, C049, C039) all rest on the narrow reading of V31: no YM purchase and no
variant on YM's 2019-05..2024-02 window is allowed under the literal reading. C049 uses YM's path (L5) and MFFU's costs
(c_f 5.30 MYM ticks, x 0.0838). C147 stays 2.55 with Q7 2 (MNQ and RTY have no clean pre-2024-03 window).

**nozlw (primary plus no ZL window, the user's decision D2):** C140 falls to 2.45 (rank 19) and C138 to 2.35 (rank
33); every R4 member has Q7 2 (no clean pre-2024-03 test window); the MNQ and RTY members need post-2024-03 data with
the user's approval (V51), and the YM member of C021 and C147 is bound by V31 read literally (section 5). RTY F09
(C113, 2.50) is fifth here.

**ts150_v2 (primary with Topstep's Standard Path $150 in Q6):** n_reaching_2 = 5 and fewer_than_3_reach_2 = false;
the run's last printed line "fewer than 3 reach 2.00: False" is r3_score.py's label with its value (RV2 N1), not a
finding that fewer than three reach 2.00. The Standard Path deducts 1 from Q6 where a one-lot sqrt(n/day) sigma_hc v
is below $150: C072 MNQ F08 topstep falls to 2.40 (rank 22) and C147 to 2.40 (rank 25, through its MNQ member), so MNQ
F08 enters at Lucid (C075, 2.55) and C108 RTY F08 topstep takes fifth. C140 and C138 ($505.85) and C021 ($316.17)
keep Q6 4: their one-lot sqrt(n/day) sigma v exceeds $150.

**q3bleg (primary without LR-Q3b: the leg-level F09 reading, Q3 2 as rated; LR-Q3b's sensitivity):** reproduces the
version 2 primary list and own broker (C138 and C140 2.75, C113 2.60, C072 and C021 2.55; C139 2.60).

**v1 (06:20, before LR-Q3a, LR-V31 and LR-Q3b; LR-Q6p primary):** its F01 leaders (C003, C043, C044) are gated now
(Appendix A).

## Appendix A. F01 (gated: re-test, LR-Q3a)

C001-C006 (YM F01 at all six venues), C043-C044 (MYM F01 at MFFU and IBKR) and C092-C096 (RTY F01) carry Q3 = 0 (gate)
in version 2: "LR-Q3a: re-tests E16-H1 (R1-13, rest-of-day rule at h 30 on YM, 2019-05..2024-02) and K1-cp1-01 (R1-03,
14:30-14:59 CT on MYM and M2K)". Their rater's values are kept beside as "Q3_rater" (1) in R2_combinations.json. Version
1 R4 positions: C003 1 (2.95), C043 3 (2.80), C044 best own-broker (2.65); r3_out_v1.json.

| item | C003 YM topstep | C043 MYM mffu | C044 MYM ibkr |
|---|---|---|---|
| band; h_c | 15, 30; 30 | 30, 60; 30 | 30, 60, 120; 60 |
| version 1 Q1-Q7; C | 3, 3, 1, 3, 2, 4, 4; 2.95 | 3, 3, 1, 2, 2, 4, 4; 2.80 | 3, 3, 1, 2, 2, 3, 4; 2.65 |
| c_f (ticks); USD | 2.256; 11.28 | 5.300; 2.65 | 6.34; 3.17 |
| sigma_hc; G | 63.23; 0.0894 | 63.23; 0.1375 | 88.56; 0.1506 |
| p_be emp / norm | 0.5248 / 0.5224 | 0.5583 / 0.5525 | 0.5491 / 0.5449 |
| e80 test; c_f + e80 | 12.24; 14.50 | 12.24; 17.54 | 17.15; 23.49 |

Facts behind the gate:
- E16-H1 (r002-E16, inventory CDE.json): "Signal s = sign(close of bar(p,d,S_p-31) - PS(p,d-1)) ... Entry: open of
  bar(p,d,S_p-30), direction s. Exit: open of bar(p,d,S_p)", pooled over 27 roots incl. YM on 2019-05-06..2024-02-29;
  "H1's gross is about a quarter of its D8 cost"; V31.
- K1-cp1-01 (E.7, MYM and M2K traded): L1 (entry fill 14:30, exit fill 14:59; signal 17:00 CT of d-1 to 08:59).
- R1-14 H6 on NQ at MNQ cost, entry 14:30 CT, 2020-06..2024-02: "T1 gross 1.25 ticks vs 4.08 cost, t -0.53".
- Published effect (version 1 arithmetic on F01.E02, assumptions as 3(d)): YM R2_OOS 2.18% gives a sign-rule daily
  Sharpe of 0.119 gross, 0.083 net at YM-Topstep and 0.034 at MYM-MFFU, against 0.2008 at selection.
- Mechanism quote: "Hedging short gamma exposure requires trading in the direction of price movements, thereby
  creating price momentum." (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md:84-85).

## Appendix B. Dropped by LR-Q3b: RTY F09 (C113, C 2.50)

RTY F09 (C113, Topstep) left the R4 under LR-Q3b (L11): Q3 2 -> 1, C 2.60 -> 2.50, r3 rank 3 -> 18; under the
leg-level reading (q3bleg) it is R4 3 at 2.60. Version 2's tables are kept below with the R3 values updated and the
closed-line overlap corrected from R1Fixer's code check (work/fix4/r1/r1fix_report.md F1-F5).

### B(a) Fact table

| item | C113 RTY topstep | source |
|---|---|---|
| band B; h_c | 15, 30; 30 | F5 pair 9 |
| documented horizon vs B | [10, 60]: "documented horizon(s) [10, 60] min lie outside B (15-30 min)" (no documented horizon inside B) | combos_detail |
| C (r3 rank) | 2.50 (18) under LR-Q3b; 2.60 (3) in version 2 and under q3bleg | r3_out.json; r3_out_q3bleg.json |
| Q1 | 2: "Plausible slow diffusion from the deeper market; the only evidence is a preprint on 60-min chart extrema 2004-2014 with no trading test (F09.E06: NQ leads Russell by 8-11 min); E.25 prices information within seconds on NQ; M2K-RTY is arbitrage-tight (F09.E10)." | Q1 |
| Q2 | 2: "Preprint in sample on this underlying (F09.E06, Russell futures on ICE, full text), not peer-reviewed and not a trading test, so below 3: other-venue evidence." | Q2 |
| Q3 | 1: "LR-Q3b: R1-11 and R1-15 searched G17 cross-market lead features (60-minute lead-path returns of NQ, ZN, 6E, CL, GC, ZC; never the own cluster) on M2K/RTY and ZL at h60-hF: same family and product at a neighbouring horizon (RV2 B1)" (live on M2K/RTY: ZN, 6E, CL, GC, ZC; E.12 also MBT from 2024-01-02; r1fix_report F3-F4). The rater's 2, kept as Q3_rater, named family overlap only (R1-10 K8 cross-market with MGC, 6C and MNQ legs, R1-13 E16-H2 NQ vs ZN pair, R1-21 S1/S2 on ZM); its statement that no closed line held a cross-market feature on RTY or M2K is corrected by LR-Q3b | R2_combinations Q3 (LR-Q3b), Q3_rater |
| Q4; Q5; Q6; Q7 | 3 (x 0.0436); 3 (q 0.0537); 4 (news 0.8348 events a week, below the 2-a-week deduction); 2 (test-window deduction 2: clean window 0.0 months) | r3_out.json |
| c_f | 2.256 = S 1.0 (u) + 0.5 + fee 0.756 (USD 3.78 a round trip, stated); USD 11.28 | combos_detail |
| sigma_hc; m_hc; G(h_c) | 51.75; 37.09; 0.0973 | idem |
| p_be (emp / norm); p_1 | 0.5304 / 0.5273; 0.5439 / 0.5394 | idem |
| K_year; K_disc; K_test; n/day | 3276 (n_cap(30) 13 x 252); 10348; 11310; 13 | idem |
| e80 discovery G3+G4 / G3; test | 3.31 / 2.91; 2.78 ticks (USD 13.90) | idem |
| c_f + e80_test | 5.04 | idem |
| prop fit | no DLL (MLL $2,000 used, LR-DLL); MLL/(sigma_30 v) 7.73 a trade, 2.14 a day of 13 trades (2000 / 932.96); flat-by-close 13:10 PT, latest start 12:30 PT at h 30; no overnight; payout Consistency 0, Standard $150 vs $932.96 (below); news: "Topstep Tier 1 blocks new openings 5 min before to 5 min after CPI, PPI, NFP, FOMC decision and press conference: a continuous family is stopped around each (frozen-calendar rate)" 0.8348 a week; gates none | combos_detail prop_fit |
| queue-limit variant | not computed (Topstep) | conventions |
| same pair elsewhere | C112 bulenox 2.50, C115 mffu 2.50, C114 tradeify 2.35, C116 ibkr 2.05 (Q6 1: margin); M2K: no combination (not a top-15 code) | r3_out.json |

Closed-line overlap (corrected in version 3 from R1Fixer's code check, work/fix4/r1/r1fix_report.md F1-F5; LR-Q3b).
Same family at a neighbouring horizon: R1-11 (E.12 Gate 0 on M2K: G17 60-minute log returns of the ZN, 6E, CL, GC and
ZC leads, and of MBT from 2024-01-02, at h60, h120 and hF, tested pooled over 27 products in Family A and as inputs of
Family B's pooled ridge; NQ, the lead of M2K's own cluster, never applied) and R1-15 (E.20's search on RTY through the
M2K vehicle: the same five G17 leads among its 36 frozen features, one pooled model per horizon over the 17 vehicles at
h60, h120 and hF, decision times 09:00, 11:00 and 13:00 CT and t4 14:08 CT on equity); both closed without a pass.
Family overlap: R1-10 K8 (equity flight into gold with an MES leg, oil/CAD, weekend bitcoin to MNQ); R1-13 E16-H2
(month-end NQ vs ZN pair); R1-21 S1/S2 (ZM). RTY and M2K in other families' lines: R1-03 K1 (M2K traded: CP1-CP3 ports;
CP1 F01 gated, LR-Q3a), R1-13 (RTY pooled H1/H4), R1-16 (E.21 trend). NQ as the leader: NQ is excluded as a candidate
(V49, R1-22), was never a live G17 feature on RTY or M2K (own cluster), and NQ-path lines R1-14, R1-15, R1-18 are
other families.

### B(b) Pre-registration outline (draft)

- **P1 data.** RTY ohlcv-1m (RTY.v.0, traded) and NQ ohlcv-1m (NQ.v.0, leader). Discovery 2020-12-01..2024-02-29,
  owned (RTY 2017-06..2024-02; NQ 2010-06..2024-02). P1.5 exposure of the discovery dates: E.16 H1/H4 pooled (RTY from
  2017-06, NQ from 2010-07), E.21, E.20's search (2019-05-06..2024-02-29, RTY and NQ searched), R1-14 H6 on NQ
  (2020-06..2024-02), E.12 Gate 0 (M2K); E.12 and E.20 held G17 cross-market leads ZN, 6E, CL, GC
  and ZC on M2K/RTY at h60-hF (R1-11, R1-15). Test: no clean pre-2024-03 window (L10 (i)); a test reads 2024-03 onward
  only with the user's approval (V51 item 2). Post-2024-03 facts (F2 owned lists; R1 windows): 2024-03-01..2025-03-31
  RTY and NQ neither owned nor read in any R1 line (13 months, buy); 2025-04..2026-06 RTY, NQ, M2K, MNQ ohlcv-1m owned,
  read by E.7 K1 (M2K and MNQ traded, 2025-04-01..2026-06-12) and E.9 K8 (MNQ, 2025-04-01..2026-06-16); not owned from
  2026-06-17. 2024-03-01 to 2026-10-28 is about 32 months, so no 43-month post-2024-03 window exists yet. R1-17
  (E22-F1, 12 micros, list not extracted in R1) had a V42-approved daily-settlement warm-up read "2024-03-01 to
  start"; whether M2K or MNQ are among the 12, and whether the read ran, was not checked.
- **P2 F09 NQ -> RTY.** Evidence: "NQ leads ES by about 9-12 min and Russell by 8-11 min; Russell leads ES by about 5
  min" at 60-minute chart extrema, 2004-09..2014-05, in sample, no trading test (F09.E06, Maier-Paape and Platen 2015,
  arXiv preprint). Against: E.25, information priced within 1 to 5 s on NQ; mini and full pairs (M2K-RTY) are
  arbitrage-tight (F09.E10), so M2K is not a leader. Stated difference from R1-10, R1-13 H2 and R1-21: the pair (NQ to
  RTY) and minutes-scale continuous trading; from R1-11 and R1-15's G17 features, the leader (NQ, never a
  live feature on RTY or M2K) and the 15-30 minute band against h60-hF (the leg-level reading, q3bleg).
- **P3.** h {15, 30} (B; the documented 10 and 60 lie outside); continuous, market orders, one contract. Exclusion:
  Topstep's Tier 1 window (5 minutes either side of CPI, PPI, NFP, FOMC decision and press conference) blocks new
  openings in full-size RTY (0.8348 events a week on the frozen calendar).
- **P4 (draft).** Gap_L = NQ return over the last L minutes minus a causal rolling beta times RTY's return over the
  same L; trade RTY in the gap's direction. Grid L {5, 15} x threshold {none, |gap| in its trailing top tercile} x h
  {15, 30} = 8.
- **P5-P6.** Rule-based (V28; bars). The beta and the tercile are trailing.
- **P7 (draft).** 8 -> N 846: binding 0.2008 daily, b_test 0.1650 at 870 test dates (section 8).
- **P8.** Section 2, G2 re-set in RTY ticks (USD 5).
- **P9.** One read of RTY and NQ ohlcv-1m over the approved post-2024-03 span. At the 13-month unread span (about 273
  dates at 21 a month, an approximation) b_test is 0.2964 daily (t 4.90) and the 80%-power true Sharpe 0.3485 (N 846;
  section 8), against 0.1650 and 0.1937 at 870 dates.
- **P10.** Section 2.

### B(c) Data purchase plan

| use | schema | symbols | dates | status | approximate cost (estimate) |
|---|---|---|---|---|---|
| discovery | ohlcv-1m | RTY.v.0, NQ.v.0 | 2020-12-01..2024-02-29 | owned; read (B(b) P1) | 0 |
| test (needs the user's approval, V51) | ohlcv-1m | RTY.v.0, NQ.v.0 | 2024-03-01..2025-03-31 | not owned, not read | RTY about USD 1.08 (E.12 quote USD 1.902238 for 23 chunks = USD 0.0827 a month x 13); NQ about USD 1.29 (USD 10.544864 for 106 chunks = USD 0.0995 a month x 13); 2010-2019 quote rates (reports/stage_e16_windows.json), no post-2024 quote exists |
| owned after 2024-03 | ohlcv-1m | RTY, NQ (M2K, MNQ) | 2025-04..2026-06 | owned; read by E.7 and E.9 through M2K and MNQ; closed by V51 | 0 |

Quote requests to obtain later, only after the user approves 2024-03 onward (V51), a funded account exists and a fresh
quote is approved: GLBX.MDP3, ohlcv-1m, RTY.v.0, 2024-03-01..2025-03-31; GLBX.MDP3, ohlcv-1m, NQ.v.0,
2024-03-01..2025-03-31. combos_detail lists none ("no clean pre-2024-03 test window: nothing to buy before 2024-03").

### B(d) Kill-criteria facts

- Power: e80 discovery 3.31 / 2.91, test 2.78 ticks (USD 13.90); c_f + e80 5.04; q 0.0537 at K_test 11310 (every
  30-minute slot, 13 a day); a rule trading once a day has e80_test 0.1936 x 51.75 = 10.02 ticks. At the 13-month
  span: 0.3485 x 51.75 / sqrt(13) = 5.00 ticks a trade at 13 a day, 18.04 at one a day.
- Published effect: F09.E06 gives a lag (8-11 minutes at 60-minute extrema) and no return or trading statistic, so no
  per-trade size to set against c_f.
- Prop limits by horizon (F5 pair 9): MLL/(sigma_h v) 15: 10.69, 30: 7.73, 60: 5.65, 120: 4.18, 240: 3.02, OC: 2.07
  (< 3), cc: 1.68 (< 2); a full day of 13 trades at h 30: 2.14. News stops 0.8348 events a week.
- Data: about USD 2.37 (estimate), only with the V51 approval.

## 10. Not done, limits

- briefs/r3_out.md does not exist; the r3_out JSON files were used throughout.
- Costs are census or quote-scaled estimates (labelled); post-2024 ohlcv-1m months have no quote in the files (2010-2019
  rates used); no Databento price was checked (no call allowed).
- The published-effect translations (3(d), 4(d), 6(d), Appendix A) are arithmetic under stated assumptions; no second model
  has checked them.
- T_disc and T_test are spec 8.2's 796 and 870; the short-window rows use about 273 dates (21 a month), not a
  calendar count. The N 842 row is read from neighbouring rows.
- Not checked: whether E22-F1's 12 micros include M2K or MNQ and whether its V42 warm-up read ran (Appendix B(b) P1).
- The draft grids name configurations from the evidence rows and the frozen protocol; they are not a design review.
- Version 3: the EQ3 pool's cut to MNQ and RTY (6(b) P9), its K_eff on 273 dates and the members' combined one-day
  sigma (6(a)) are arithmetic by the scorer's formulas at rho 0.5, not a re-score; how a pooled test would be read over
  disjoint member windows (YM before 2019-05, MNQ and RTY after 2024-03) is not worked out.
