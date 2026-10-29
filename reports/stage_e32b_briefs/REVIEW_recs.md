# REVIEW_recs: RV2 RecsReviewer-FableXHigh, Stage E.32b step 3b (R5) and the holding scope (F5)

Reviewer: Fable 5.1 (claude-fable-5-1), xhigh, read-only. 2026-10-29 06:58-07:20 PDT. Scope: briefs/brief_review.md
section RV2, checks 1-5; the ranking (Step 4) is RV1's and is not reviewed here. Helpers and recomputations in
briefs/work/rv2/ (r3_summary.py, combo_show.py, f5_show.py, recompute_r3.py, f5_recompute.py, q3_scenarios.py,
r3_out_ts150_v2_rerun.json). Files reviewed in their state after the lead's 07:07:40 edits (work/R4/fix_lead_text.py);
findings against the earlier wording that those edits already fix are listed under "Fixed at 07:07" and not repeated.

VERDICT: PASS WITH ONE RULING NEEDED. The R3 arithmetic, the ordering, the R4 selection and the F5 bands and verdicts
all reproduce exactly from their inputs in every run (primary and four sensitivities); the lead's text appears verbatim
in the assembled file. One BLOCKING item: the Q3 = 2 ratings of the F09 candidates rest on a closed-line fact that R1
and the dossiers omitted (E.12 and E.20 searched cross-market lead returns on RTY/M2K and ZL at h60); under the spec's
Q3 = 1 text, which the rater itself applied to ZL F11 and ZL F01, RTY F09 leaves the R4 and the EQ3 F08 pool enters.
That is a lead ruling, not a recomputation. Counts: BLOCKING 1, SHOULD FIX 6, NOTE 7.

## Findings

### BLOCKING

B1. Q3 of the F09 candidates (RTY|F09 C112-C116, ZL|F09 C138-C139) rests on an incomplete closed-line fact; an R4
candidate changes under the spec-literal reading.
- Where: briefs/R2_Q_ratings.md RTY|F09 Q3 reason ("Family overlap only ...; no cross-market configuration closed on RTY
  or M2K") and ZL|F09 Q3 reason (no mention of R1-11/R1-15); briefs/R1_closed_lines.md R1-11 ("64 generic signals",
  "64-feature library") and R1-15 ("r_ROD features", "36 features"); R2_dossiers_for_rating.md lines 797-798, 995-996
  ("Gate 0 ML over 64 bar features", "E20S ML, 36 bar features"); work/R4/draft_sections.md:316-319 ("no cross-market
  configuration on RTY or M2K"; "E.20's 36 late-session features").
- Evidence: both ML libraries contain the G17 cross-market leads, "the 60-minute log return (x 1e4) of each other
  cluster's lead price path" (ml_route_v2/signals/generic.py:22; names g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc,
  plus g17_mes, g17_mbt in E.12). E.12 Gate 0 (R1-11) tested them pooled over the 27 products including M2K and ZL at
  h60, h120, hF (reports/stage_e12_gate0.md:158-164, rows gate0A_g17_*_h60; :222 h120) and inside Family B's per-product
  models; E.20 (R1-15) kept all six in its 36 frozen features on the 17 roots including RTY and ZL
  (pattern_search/constants.py:59; reports/stage_e20_search_freeze.json feature_names), decision times t1-t4 (t4 = F_X -
  60 = 14:08 CT for equity), horizons h60, h120, hF, 2019-05-06..2024-02-29. Caveat that the lead needs: G17 "never
  applies on its own cluster's rows" (c1_replication/c1b.py:53; generic.py SignalSpec legs), so on RTY the live leads
  were ZN, 6E, CL, GC, ZC (not NQ), and on ZL they were NQ, ZN, 6E, CL, GC (not ZC, and never the crush legs ZS, ZM).
- Two readings. (a) Family level, spec 8.3 Q3 = 1 "same family and product at a neighbouring horizon": F09 is
  "cross-market lead-lag"; h60 neighbours RTY's band {15, 30} and is a member of ZL's {15, 30, 60}. The rater used this
  reading for ZL|F11 ("R1-11 ZL Gate 0 (64 bar features) and R1-15 ZL E20S (36 bar features) at h60, a band member ...
  are closed" -> Q3 1) and for ZL|F01's 60-minute member, so consistency points to 1 here. (b) Leg level: the dossiers'
  leader (NQ for RTY; ZS and ZM for ZL) was never a live feature on that product, so Q3 = 2 "family overlap only" stands.
- Effect (work/rv2/q3_scenarios.py, in memory): RTY F09 Q3 1 -> C113, C112, C115 2.50, C114 2.35, C116 2.05; R4 becomes
  C138 ZL F09 2.75, C140 ZL F10 2.75, C072 MNQ F08 2.55, C021 YM F08 2.55, C147 EQ3 F08 topstep 2.55 (RTY F09 out);
  best own-broker C139 unchanged. RTY and ZL F09 both 1 -> C138 2.65, C139 2.50; R4 = C140, C138, C072, C021, C147;
  best own-broker C141 ZL F10 ibkr 2.60. Under (b) nothing changes.
- Fix: a lead ruling in RULINGS.md (as LR-Q3a), applied by a documented patch and an r3 rerun (seconds) if (a); either
  way R1-11 and R1-15 (R1 file and the dossier catalog) name the G17 leads and the own-cluster exclusion, and the
  RTY|F09 Q3 reason "no cross-market configuration closed on RTY or M2K" is corrected (cross-market leads from five other
  asset classes were searched on RTY and M2K at h60-hF). The lead's RTY case text already lists R1-15 as negative
  evidence, so the case paragraph needs only the feature fact.

### SHOULD FIX

S1. work/R4/lead_sections.md:60 and :66; reports/stage_e32b_recommendations.md:633 (and its K2 line): "12.3 ticks on
YM". e80_test = SR80_test x sigma_30 = 0.193625 x 63.2336 = 12.24 ticks; the drafter's 6(a) and 6(d) and the assembled
fact table give 12.24. Fix: 12.2 (MNQ's 28.5 is right: 28.48).

S2. lead_sections.md:50 / recommendations.md:553: "the dossier's evidence (F09.E06) has the Russell leading ES, so the
family's direction is an open question, not a small-cap lag". F09.E06 (R2_dossiers_for_rating.md:1300): "NQ leads ES by
about 9-12 min and Russell by 8-11 min; Russell leads ES by about 5 min": the Russell lags NQ and leads ES. Fix: state
both lags and that the leader and side are pre-registered; drop "not a small-cap lag".

S3. lead_sections.md:89 / recommendations.md:841 (stop rule, "Why"): "priors of 1.5-4%" is stale after the 07:07
edits (RTY F09 and MNQ F08 are now "under 1%"; YM 1.5% only if V31 were narrowed). Fix: "under 1% to about 4%".

S4. recommendations.md Summary (section 0, drafter's text, lines about 17-21): "RTY F09 and YM F08 about 1.5% each,
MNQ F08 about 1%" and "(RTY F09 is the final build only if the user opens data from 2024-03 onward)" contradict the
edited lead text (priors under 1%; stop rule item 1: "RTY F09, MNQ F08 and YM F08 are not fallbacks"). Fix: regenerate
the summary from the current lead sections.

S5. reports/stage_e32b_holding_scope.md:1348: "80% power at the test needs a gross of 5.0-13.2 ticks a trade at 30
minutes (c_f + e80 test)". Over the 15 pairs the minimum is 4.19 (topstep|ZL: 2.38 + 1.81; F5_holding.json
pairs."topstep|ZL".rows."30".gross_detect_test); 5.04 is topstep|RTY. Fix: "4.2-13.2".

S6. briefs/R1_closed_lines.md/.json R1-11 and R1-15 (and the dossier catalog rows copied from them): the feature
libraries are described without their cross-market content (see B1 evidence). The brief's check 1 asks for overlap
checks against the frozen code, not R1's summaries, and this is where the summaries fall short. Fix: add to both lines
"includes G17: 60-minute log returns of the other clusters' leads (NQ, ZN, 6E, CL, GC, ZC; E.12 also MES, MBT), not
applied on the lead's own cluster", with the file references above.

### NOTE

N1. ts150_v2 "fewer than 3 reach 2.0" (STATE L8 row, brief RV2 context): r3_score.py's last printed line is always the
label "fewer than 3 reach 2.00: <bool>"; the run printed "False" (work/R2/r3_run_topstep150.log shows the same form).
work/R2/r3_out_ts150_v2.json has fewer_than_3_reach_2 = false, n_reaching_2 = 5, and my rerun on the same input
(work/rv2/r3_out_ts150_v2_rerun.json) is identical apart from generated_pdt. No defect; the STATE wording is a misread
of the label. The ts150_v2 R4 is C138, C140, C113, C021 YM F08 topstep, C075 MNQ F08 lucid (C072 falls to 2.40, Q6 3).

N2. STATE D1-done row: "E.29 measured no correlation between members" (EQ3, EQ3m). E.29 3.2 measured only the CL, ZM,
GC, NQ pairs; none of YM-MNQ, YM-RTY, MNQ-RTY. rho_measured = {} and the spec default rho 0.5 within a class is the
right application. No score effect: an F08 pool's Q5 is 2 for any rho (K_total 2610 is below the 3262 trades Q5 = 3
needs), and the F10 pools' 4 holds for any rho below 1. Wording only.

N3. Q6 news count for continuous families at Topstep: RTY F09 carries 0.8348 events a week = NFP 0.2266 + CPI 0.2306 +
PPI 0.2306 + FOMC 0.1471, which counts the 07:30 CT releases although the family trades the 08:30-15:00 CT main session
only; a session-restricted count is about 0.15 (FOMC decision and press conference). Below the 2-a-week deduction either
way; no score effect.

N4. Q2 scale reading for ZL|F09 (C138, C139): F09.E01 is peer-reviewed, in sample, on ZL as a crush leg; the scale's 3
reads "peer-reviewed in sample ... on this product"; the rater gave 2 because the study tests cointegration, not a
lead-lag at any horizon. Defensible and explained. If the lead read the scale literally, C138 2.85 and C139 2.70; the
R4 membership and C138's first place would not change.

N5. Base rate (lead_sections.md:14): the Laplace estimate (0 + 1) / (23 + 2) counts all 23 R1 lines, of which R1-02,
R1-17, R1-19, R1-20, R1-22 and R1-23 carry no registered test outcome (trials 0 or none run); on the 17 lines with
outcomes the same estimate is 1/19, about 5%. The text states its base, so this is a note on the choice, not an error.

N6. Holding scope section 4 (E_dir): the placeholder table (15 PENDING rows) stands, as the brief said; not waited for.
The scope text expects the pass-2 run to end "about 10:30-11:00 PDT" while the brief says 07:30-08:00; one of the two
expectations is stale. Section 4's flagged zero mu*_mkt for topstep|YM and topstep|RTY is an E.28-model property as the
scope says; not re-derived here (econ is outside this review).

N7. F08 overlap readings confirmed from the frozen code and the inventory: K1-cp3-01 enters on the 08:30 bar (fill 08:31)
and exits at C-2 = 14:58 (strategy/members/k1/cp3.py:21-25, 64-65; K1.md rows 7-9); E16-H4 takes its side from d-1's
settlement-window move and enters at the open (CDE.md row 60). A 15-30 minute hold at the open on the same signals is a
shorter hold of closed signals, Q3 = 1 as rated, not a re-test; E.12/E.20's g05_gap, g08_prev_ret and cp3_clv at h60 on
NQ, RTY, M2K, MYM, MNQ give the same reading. ZL|F10 Q3 = 2 stands: neither ML library had order-book features and
R1-21 S3 was on ZM.

### Fixed at 07:07 (observed in the earlier text, now corrected; not counted above)

- "F09 asks whether crude oil, heating oil and the rest of the soy complex lead ZL": the dossier's legs are ZS and ZM.
- Stop rule item 1's RTY F09 fallback versus item 2's 2% floor (RTY's prior was 1.5%): the fallback is gone.
- "raises the test's per-trade hurdle from 0.165 to 0.296": these are daily-Sharpe bars; now "daily hurdle".
- "cuts the chance of detecting a real edge to about half": now "power ... about 0.05" (drafter's p7 power at 273 dates).
- "E16-H4 ... failed on YM" and "already read on YM (E16-H1)": now stated as pooled tests that included YM.
- "Baltussen et al.'s full-sample estimate": now "out-of-sample estimate" (F01.E02 recursive OOS R2).

## Checks performed and results

1. Closed lines. R1: 23 lines; trials_by_line sums to 838 = n_total; ledger_ladder (471 -> 838 over r001-r009)
   matches the 10 lines of ledger/trial_registrations.jsonl. Readings against the decision texts: LR-R1 against V38
   (DECISIONS:677-684, "nothing in 528 trials passed, and no published post-2015 intraday effect on the 17 roots exceeds
   1.5 x") and V56 (:1146-1152, "stays sealed for a future hypothesis family"; item 2 "Order-book direction is not closed
   for other products") agree; LR-V31 against V31 (:562-576, "no rerun or variant on these windows, no purchase of the
   10 fallback roots") is the literal reading as stated; LR-ZLW against V56 item 1 agrees; V50 item 4 (ZM MBO plus ZS
   and ZL MBP-1 2020-12..2024-02 "not a clean holdout") and V51 item 2 ("2024-03 onward stays closed unless the user
   approves") as cited. V45 item 4 checked only through R1-15/R1-19's quotes. LR-Q3a (F01 gate) checked against CDE.md
   row 59 (E16-H1: signal at S_p-31, entry S_p-30, exit S_p, pooled 27 roots incl. YM and RTY) and K1-cp1-01's constants
   as the drafter quotes them (L1). F08, F09, F10 overlaps for the R4 candidates and the next ten (C112, C115, C139,
   C141, C075, C074, C019, C023, C022, C020; also C147, C108): see B1 and N7.
2. R3 arithmetic. work/rv2/recompute_r3.py (written from the spec text, not from r3_score.py's helpers): 185/185
   combinations agree on Q4-Q7, C, C_rounded (half-up), gates, G(h_c), K_used (pools: K_eff with rho 0.5 within a
   class), the full eligible order, the R4 list and the best own-broker, for r3_out.json and r3_out_ts150_v2, q3only,
   nozlw, v1. Inputs checked: c_f = S + 0.5 + fee/v with F4 fees 5.28 (ZL), 3.78 (RTY, YM), 1.22 (MNQ), IBKR 6.02 (ZL);
   sigma_30 from F3 (ZL 28.10, RTY 51.75, YM 63.23, MNQ 147.10); K_test = n_cap(30) x 870 (ZL 9, RTY 13) or 870 for the
   daily family; MLL 2000 used for DLL "none" (LR-DLL); Topstep payout 0 (LR-Q6p), Tradeify 150; clean test windows
   from F2_data_access (ZL sealed 43.04 months; RTY p_all_read 1 -> 0; MNQ via NQ 0.82 -> deduction 2; YM 106.97
   unread -> 0 under LR-V31); data costs C140 19.48 / 40.96 (census k 0.4995 x 39, x 43 + MBP-1), C021 4.26. Ties:
   2.75 by family name; 2.60 by G then family name; 2.55 by G, venue, product code (all as the file's "ties").
3. Q1-Q3. 36 ratings read against the catalog rows and the spec 8.3 scales: ZL F09, ZL F10, RTY F09, YM F08, MNQ F08,
   EQ3 F08, YM F01, MNQ F01, ZL F01, ZL F03, ZL F11 (Q1, Q2, Q3 each). Consistent with the scales and with the evidence
   rows F09.E01-E03, E06, E10, F08.E03, F01.E02, E05, E14, E15, F10.E01, E03, E04, E07, F03.E01, E03, F11.E01, E05, E10,
   except the fact gap in B1 and the scale ambiguity in N4.
4. R4. Numbers in the lead text verified: 23 lines / 838 / 4%; H6 T1 1.25 vs 4.08, t -0.53 (R1-14); ZL 28.1, 2.38,
   0.085, nine holds, 4.2 ticks = 0.15 sigma, K2 1.8; RTY 0.044, 13 a day, 2.8 ticks, 51.8, 273 dates, 0.165 -> 0.296;
   MNQ 28.5 (YM 12.3: S1); 0.19 sigma; Standard Path 2.40; non-prop 2.60 vs 2.75, 2.50 vs 2.38, Q6 3 (sigma_cc 116.84
   x 6 = 701 > 120; margin 4661.63 < 6000), V32 quote; gated F01 1.25 / 147 under 1%; D1 2.85 (q3only). Priors'
   arithmetic as stated (0.07 x 0.7 x 0.7 = 3.4%; 0.04 x 0.49 = 2%). Kill criteria K0-K4 and the stop rule are
   coherent after 07:07 (S3, S4 are leftovers). No outcome read: r3_score.py reads only the combinations file; f5 reads
   F3 (volatility statistics), F4 and SR80; the thresholds use p7_final.py's functions with no data; every trade result
   quoted is a closed line's recorded figure (OC-13). No sealed or spent window was opened by any script reviewed.
5. F5 and the scope. work/rv2/f5_recompute.py from F3 sigma, F4 fees and limits, SR80.json: topstep|ZL, topstep|RTY,
   topstep|YM, topstep|MNQ, mffu|MYM and ibkr|ZL, ibkr|MNQ, ibkr|YM all reproduce c_f, min G (at 30 in each), B and the
   verdict (holds). Scope statements checked against F5_holding.json: 15/15 holds; B 15-30 for 13 pairs, 30-60
   mffu|MYM, 15-60 topstep|ZL; G(120)/minG 1.13-1.56, G(240)/minG 1.50-2.53, G(1,2)/minG 1.79-3.52 ("1.8-3.5"),
   c_f/sigma_1 0.14-0.44; DLL excludes h on 6 pairs exactly as listed (OC 6, 240 5, 120 2); DLL below 2 sigma_cc v on 8
   of 15; no firm allows overnight; ibkr 20 holds / 1 partly / 14 fails (8 "min G lies only at cc", 6 also B empty),
   19 of 35 reach 120, the five top-15 codes hold with the stated bands; p_be at 30 0.518-0.558. One wrong range (S5).
   The "15-60 minutes, not hours" finding and the E_dir placeholder are as stated (N6).
6. Assembled file. reports/stage_e32b_recommendations.md (86,261 bytes, 07:07): the 18 lead paragraphs of
   lead_sections.md appear verbatim; the R3 top-20 table and the R4 table match r3_out.json; the "Lead check" list's
   items 2-10 are answered by the 07:07 edits; item 1 (D2 b counts) is RV1's scope. Remaining: S1-S4.

## Could not check

- V45 item 4's text in DECISIONS.md directly (grep on the 844-872 block found no item text; checked via R1's quote).
- E.20's t1-t3 decision times (only t4 = 14:08 CT located), which bear on how "late-session" the G17 search on RTY was.
- The E_dir 30/120/240 columns (run pending) and the econ zeros in scope section 4.
- The drafter's published-effect translations (F10.E01 R2 -> 0.058 sigma; F01.E02 -> 15.5%) and the p7 power 0.05 at
  273 dates: arithmetic under stated assumptions, not re-derived here.
- D2 a/b counts in the base-rate paragraph (ranking scope, RV1).
- Full texts behind the evidence rows (no web access); the rows were taken as the dossiers record them.

## Log

- 06:58 start; brief (common, RV2), Common rules, spec 7-8 (sha256 verified), RULINGS.md, STATE rulings, r3_score.py,
  s32b_common.py, both lead patches, F5 README, SR80.json, lead_sections.md (first version), draft_sections.md.
- 07:00-07:06 r3 summaries of six outputs; combination records; F5 pair and F4 fee records; recompute_r3.py (5 runs,
  0 mismatches); ts150_v2 rerun identical; f5_recompute.py (8 rows match).
- 07:07 lead note received: 14 passages corrected; current lead_sections.md and recommendations.md re-read.
- 07:08-07:16 closed-line checks: R1 ladder, decision texts, cp3.py, CDE/K1/K8 inventory rows, E.20 freeze features and
  E.12 Gate 0 rows (G17), generic.py G17 definition and own-cluster rule; scope-file statements recomputed; Q1-Q3
  spot checks; q3_scenarios.py.
- 07:20 this file written. Holdout not touched; no file outside briefs/REVIEW_recs.md and briefs/work/rv2/ written.
