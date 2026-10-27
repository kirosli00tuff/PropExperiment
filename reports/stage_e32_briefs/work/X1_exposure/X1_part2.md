
## Table B. Overlap with the 538 trials

Scope applied (stated, not a judgment on results): every registered or screened trial whose universe includes ZM, ZS or ZL, plus trials
on other roots whose mechanism is named in the brief (WASDE or USDA release, limit moves). Baseline trials (K6 members, Gate 0 tests)
are in the 471 baseline and carry no registry ID line; registry lines are cited for the registered ones. Values copied as recorded.

### B1. K6 members on ZS, ZM, ZL (and adjacent K6 members on other roots for WASDE and limit-move mechanisms)

Family K6 (grains, oilseeds and livestock); freeze reports/stage_e_k6_member_freeze.json (sha256 a6f8b497..., 27 members). Mechanism and hold from
reports/stage_e23_briefs/inventory/K6.md (line in last column). Research window = E.8 screen on 2025-04-01..2026-06 (windows 264-287 dates);
confirmation = E.22 on W_cf 2019-05-06..2024-02-29. E.8 columns: trips, days, mean ticks/day, daily t, tier (reports/E.8_RETURN.md lines 217-240).
E.22 columns: tier, status, days, trips, theta_hat, UCB95, p_upper (reports/E.22_RETURN.md lines 371-394).

| Trial ID | Family | Mechanism | Hold | Data span (E.8 research; E.22 W_cf) | E.8 outcome and key statistic | E.22 outcome and key statistic | Source lines |
|---|---|---|---|---|---|---|---|
| K6-cp1-01 ZS | K6 | momentum port (CP1), decision 12:44 CT | fill 12:45 to 13:14 (about 29 min) | 2025-04..2026-06; 2019-05-06..2024-02-29 | trips 280, days 285, mean -2.5301 ticks/day, daily t -5.756, tier B | B, null, days 1136, trips 1109, theta_hat -1.7015, UCB95 -1.1732, p_upper +1.0000 | K6.md 10; E.8 217; E.22 371 |
| K6-cp1-01 ZM | K6 | same | same | same | trips 270, days 278, -1.4134, t -3.820, B | B, null, 1106, 1075, -1.2097, -0.6902, +0.9999 | K6.md 11; E.8 218; E.22 372 |
| K6-cp1-01 ZL | K6 | same | same | same | trips 271, days 287, -1.1361, t -1.235, B | B, null, 1129, 1076, -2.4878, -1.6296, +1.0000 | K6.md 12; E.8 219; E.22 373 |
| K6-cp2-01 ZS | K6 | momentum port (CP2 breakout), variable 08:45..13:14 | 75 bars after entry decision bar, or 13:18 | same | trips 272, days 285, -1.9418, t -1.803, B | B, null, 1136, 1077, -1.7164, -0.4434, +0.9845 | K6.md 17; E.8 224; E.22 378 |
| K6-cp2-01 ZM | K6 | same | same | same | trips 262, days 278, -3.2959, t -3.458, B | B, null, 1106, 1033, -1.3235, -0.1204, +0.9666 | K6.md 18; E.8 225; E.22 379 |
| K6-cp2-01 ZL | K6 | same | same | same | trips 276, days 287, -0.5481, t -0.262, B | B, null, 1129, 1081, -2.0867, -0.1249, +0.9531 | K6.md 19; E.8 226; E.22 380 |
| K6-cp3-01 ZS | K6 | prior-close location (CP3), decision 08:30 | fill 08:31 to 13:14 | same | trips 136, days 285, -0.5618, t -0.475, B | B, null, 1136, 511, -1.9350, -0.3332, +0.9770 | K6.md 24; E.8 231; E.22 385 |
| K6-cp3-01 ZM | K6 | same | same | same | trips 119, days 278, +0.4725, t 0.495, B | B, null, 1106, 515, -1.4151, +0.0896, +0.9452 | K6.md 25; E.8 232; E.22 386 |
| K6-cp3-01 ZL | K6 | same | same | same | trips 143, days 287, -1.9353, t -0.723, B | B, null, 1129, 482, -1.1039, +1.3205, +0.7683 | K6.md 26; E.8 233; E.22 387 |
| K6-crushgap-01 ZS (legs ZM, ZL) | K6 | overnight change in the soybean crush margin gap (ZS traded, ZM and ZL signal legs) | fill 08:31 to 13:14 | same (E.22 days 1028) | trips 137, days 264, -3.4807, t -2.708, B | B, null, 1028, 516, -2.5773, -0.6257, +0.9822 | K6.md 29; E.8 236; E.22 390 |
| K6-wasdepre-01 ZS | K6 | WASDE release pre-drift momentum, decision 10:29 CT | fill 10:30 to 11:15 (through the 11:00 CT release) | same | trips 13, days 285, -0.7410, t -1.288, B | B, null, 1136, 57, -0.4458, +0.1724, +0.8782 | K6.md 33; E.8 240; E.22 394 |
| K6-wasdepre-01 ZC (adjacent: WASDE mechanism, corn) | K6 | same mechanism, ZC | same | same | trips 12, days 276, -0.4729, t -1.315, B | B, null, 1130, 55, -0.2534, +0.0387, +0.9264 | K6.md 32; E.8 239; E.22 393 |
| K6-wasdepost-01 ZC (adjacent: WASDE mechanism, corn) | K6 | WASDE post-release momentum, decision 11:14 | fill 11:15 to 13:14 | same | trips 13, days 276, -0.1777, t -0.748, B | B, null, 1130, 54, -0.0691, +0.1482, +0.7068 | K6.md 34; E.8 241; E.22 395 |
| K6-limitcont-01 HE (adjacent: limit-move mechanism, lean hogs) | K6 | limit-move continuation, decision 08:44 | fill 08:45 to 12:59 or D9.7 forced exit | same | trips 1, days 273, +0.1869, t 1.002, tier A | A, null by inactivity, 1104, 10, +0.0495, +0.3869, +0.4088 | K6.md 30; E.8 237; E.22 391 |
| K6-limitcont-01 LE (adjacent: limit-move mechanism, live cattle) | K6 | same | same | same | trips 0, days 266, +0.0000, t undefined, B | B, inconclusive, 1109, 0, +0.0000, +0.0000, +1.0000 | K6.md 31; E.8 238; E.22 392 |
Row count B1: 15 (11 on ZS, ZM or ZL; 4 adjacent). The remaining 12 K6 members (K6-cp1-01, cp2-01, cp3-01 on ZC, ZW, HE, LE) are port mechanisms on non-soy roots and are not listed.
Edge chain recorded for K6 (reports/E.22_RETURN.md lines 399-402): Holm K = 5 (m = 1); descriptive K = 9: K6-limitcont-01 HE p 0.4088 vs 0.00556; DSR variance 0.0035193 over 27 series; PBO +0.5571 over 27 series. K6 statement: "no statement". E.8 Tier A: K6-limitcont-01 HE only (E.8_RETURN.md line 9 area; K6.md line 45 (Verdicts)).

### B2. E.12 Gate 0 (ML route v2; 273 tests in baseline N; roots pooled or per root)

Source file reports/stage_e12_gate0.json (verdict FAIL, n_a 192, n_b 81, n_holm_family 273, 0 passing pairs); generated by script from that file's tests[] (copied fields).
Data span: W_cf 2019-05-06..2024-02-29. Hold: horizons h60, h120 and hF as recorded in the test IDs (units and definitions not extracted).

Family B, per-root pairs (reports/stage_e12_gate0.json tests[], family B; field names as recorded):

| test_id | horizon | n_obs | n_dates | n_trades | mean_gross_ticks | cost_ticks | gross_cost_multiple | t_B | p | holm_rank (of 273) | holm_threshold | decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gate0B_ZL_h120 | h120 | 2781 | 391 | 556 | 1.1690647482014613 | 2.201245019727311 | 0.5310925125210662 | -1.1347565509031978 | 0.8714128581689435 | 215 | 0.0008474576271186442 | FAIL |
| gate0B_ZL_h60 | h60 | 2784 | 401 | 556 | -0.5323741007194157 | 2.197279411515097 | -0.2422878482952362 | -1.1148435613124679 | 0.8672065837487559 | 214 | 0.0008333333333333334 | FAIL |
| gate0B_ZL_hF | hF | 2784 | 344 | 556 | 0.008992805755378098 | 2.2144986783086877 | 0.004060876551186885 | -0.3142844946337256 | 0.6232519771453475 | 144 | 0.0003846153846153846 | FAIL |
| gate0B_ZM_h120 | h120 | 2728 | 391 | 545 | 0.8972477064220176 | 1.6152955228386219 | 0.5554696919144858 | -0.1578324612379251 | 0.5626647476696824 | 128 | 0.00034246575342465754 | FAIL |
| gate0B_ZM_h60 | h60 | 2729 | 403 | 545 | 0.4275229357798334 | 1.6154187749845865 | 0.2646514590521041 | -1.0909858902404852 | 0.8620337211167508 | 211 | 0.0007936507936507937 | FAIL |
| gate0B_ZM_hF | hF | 2731 | 330 | 546 | 0.8443223443223564 | 1.6218276997707735 | 0.5205992871139712 | 0.21367983164745186 | 0.41546454931253624 | 87 | 0.00026737967914438503 | FAIL |
| gate0B_ZS_h120 | h120 | 2851 | 412 | 570 | 0.5596491228070175 | 1.4760632892161627 | 0.3791498148458182 | -0.7174697193099201 | 0.763254057692144 | 181 | 0.0005376344086021505 | FAIL |
| gate0B_ZS_h60 | h60 | 2852 | 425 | 570 | 1.5 | 1.4754429717004265 | 1.0166438342725452 | 0.0010279995710780294 | 0.49959012931933616 | 107 | 0.0002994011976047904 | FAIL |
| gate0B_ZS_hF | hF | 2849 | 361 | 569 | 2.6678383128295255 | 1.4828277873927787 | 1.7991558665894192 | 0.6105584857455553 | 0.2709385845940024 | 58 | 0.0002314814814814815 | FAIL |

Row count: 9.

Family A, pooled over the 28 exposures, K6-derived signals (same file, family A):

| test_id | horizon | n_obs | n_dates | mean | t | p | holm_rank | holm_threshold | ic_spearman | decision |
|---|---|---|---|---|---|---|---|---|---|---|
| gate0A_k6_crushgap_gap_h60 | h60 | 67797 | 1068 | -0.0003487990347371341 | -0.6231830215936522 | 0.5332974350297579 | 114 | 0.0003125 | 0.0004597975411583521 | NOT REJECTED |
| gate0A_k6_limitcont_dir_h60 | h60 | 67797 | 1068 | 0.0004888728900922845 | 1.1117619168764858 | 0.2664909662938738 | 55 | 0.00022831050228310504 | 0.010575186413730535 | NOT REJECTED |
| gate0A_k6_wasdepre_drift_h60 | h60 | 67797 | 1068 | 7.134067561204716e-06 | 0.037507749864877114 | 0.9700871770164187 | 244 | 0.0016666666666666668 | -7.135524793264993e-05 | NOT REJECTED |
| gate0A_k6_crushgap_gap_h120 | h120 | 67646 | 1068 | -0.00037936557852565273 | -0.4015978050770428 | 0.6880604655407103 | 157 | 0.00042735042735042735 | 0.0012965344398423032 | NOT REJECTED |
| gate0A_k6_limitcont_dir_h120 | h120 | 67646 | 1068 | 0.0005249298242137638 | 1.1076913443704612 | 0.2682447750898166 | 57 | 0.0002304147465437788 | 0.006713887684682285 | NOT REJECTED |
| gate0A_k6_wasdepre_drift_h120 | h120 | 67646 | 1068 | 0.0001243968372220266 | 0.6456946172023428 | 0.5186159769866322 | 109 | 0.00030303030303030303 | 0.002883017817616065 | NOT REJECTED |
| gate0A_k6_crushgap_gap_hF | hF | 64695 | 1068 | -0.0008560171966234357 | -0.6019179130021609 | 0.5473566544001726 | 120 | 0.0003246753246753247 | -0.0013721702652494984 | NOT REJECTED |
| gate0A_k6_limitcont_dir_hF | hF | 64695 | 1068 | 6.46904105328334e-05 | 0.7590622385716671 | 0.4479829754530015 | 94 | 0.0002777777777777778 | 0.004645962692727101 | NOT REJECTED |
| gate0A_k6_wasdepre_drift_hF | hF | 64695 | 1068 | 0.0001725906317325895 | 0.7537183934210048 | 0.4511846205802573 | 96 | 0.0002808988764044944 | 0.002070719469802645 | NOT REJECTED |

Row count: 9.

Not itemized here: the other 174 family-A tests (generic signals g01-g17, cp1-cp3, k1-k5, k7-k9, pooled over all 28 exposures, which include ZS, ZL and ZM); they are in the same file (tests[] where family A and signal not starting k6_).
Row count B2: 18 itemized rows (9 B, 9 A); 174 pooled family-A tests not itemized.

### B3. E.17 base-rule batch (registered r002-E16, N 473 -> 478; run once, all five FAIL)

Source: reports/E.17_RETURN.md lines 14-22 (table, base case, Holm 0.05, N 478); window lines 22-24. Pooled over the 27 price paths; soy roots in the pool: ZS, ZL (2010-07-01..2024-02-29) and ZM (2019-05-06..2024-02-29).

| Trial ID | Family | Mechanism | Hold | Data span | Outcome | Key statistic as recorded (mean in risk units, t, p, n) |
|---|---|---|---|---|---|---|
| E16-H1 | base rules | settlement-window intraday momentum, pooled | 30 minutes (S_p-30 to S_p) | 2010-07..2024-02, TN from 2016-01, RTY from 2017-06, HE from 2017-07 | FAIL | -0.161, t -20.0, p 1.0, n 3,380 |
| E16-H4 | base rules | next-day reversal of the settlement-window move, pooled | settlement-window exit next day (per prereg H4) | same | FAIL | -0.048, t -6.7, p 1.0, n 3,381 |
| E16-H5 | base rules | equal-risk combination of H1 to H4 | per component | same | FAIL | -0.149, t -1.46, p 0.93, n 3,400 |
Row count B3: 3 (E16-H2 NQ/ZN and E16-H3 Treasury auctions do not include soy roots: reports/stage_e16_prereg_H2.md and _H3.md titles; H3 and H2 rows in E.17_RETURN.md lines 17-18: H2 +0.344, t +1.52, p 0.068, n 56; H3 -0.015, t -0.26, p 0.60, n 405).
Hold for H4 is the title wording of reports/stage_e16_prereg_H4.md line 1 ("next-day reversal of the settlement-window move"); exit rule text is in that file and was not extracted.

### B4. E.20 search (registered r005-E20S, N 483 -> 528; 45 configurations; 17 vehicles including ZS and ZL)

Source: reports/E.20_RETURN.md lines 308-335. Per-vehicle results are not recorded there.

| Trial IDs | Family | Mechanism | Hold | Data span | Outcome | Key statistics as recorded |
|---|---|---|---|---|---|---|
| E20S-01..E20S-45 (45) | ML search (ridge, LightGBM depth 2) | ML route net pipeline run on 17 roots with late-session features (E.20_RETURN.md line 29) | h60, h120, hF | 2019-05..2024-02, 1,248 training dates | screen FAIL | median-path daily t -1.334 (bar >= 2.0); PBO 0.596 (bar < 0.5); annualized net Sharpe at 50K -0.826 (bar 0.5 to 4.0); final selection ridge_l0.1_k2_h60 (E20-S13); DSR at N = 528 0.00001; best CPCV OOS daily t -0.33 (E20-S13); all 45 negative |
Row count B4: 1 row for 45 trials.

### B5. E.21 multi-day round (registered r006-E21, N 528 -> 532)

Source: reports/E.21_RETURN.md lines 8-16, 333-334, 385-416 (per-root tables). Roots: 17 including ZS and ZL (ZM not read). Data span 2010-07..2024-02.

| Trial ID | Family | Mechanism | Hold | Data span | Outcome | Key statistic as recorded | Soy-root rows as recorded (contribution sum, own t, fills, gross, costs base) |
|---|---|---|---|---|---|---|---|
| E21-T1 | multi-day trend | TSMOM-12 (MOP 2012), 17 roots | hold per MOP 2012 (E.21 line 243; day count not in the lines read) | 2010-07..2024-02 | FAIL | net Sharpe 0.498 [-0.063, 1.053], t 1.776, p (NW) 0.0419, n 3205, fills 4,081 | ZL 0.0627, 0.75, 225, 0.0681, 0.0054; ZS -0.0797, -0.95, 237, -0.0758, 0.0039 (E.21 lines 385, 394) |
| E21-T2 | multi-day trend | trend blend, 17 roots | as T1 | same | FAIL | net Sharpe 0.436 [-0.109, 0.982], t 1.557, p (NW) 0.0637, fills 4,081 | ZL 0.0283, 0.44, 225, 0.0330, 0.0047; ZS -0.0385, -0.65, 237, -0.0351, 0.0034 (lines 412, 416) |
| E21-T3 | calendar | turn of the month, NQ and RTY | days -1, +1, +2, +3 close to close (E.21 line 249) | same | FAIL | net Sharpe 0.15, t 0.53, p 0.30, fills 454 | no soy root |
| E21-T4 | combined book | equal-risk T2 + T3 + H2 | n/a | same | FAIL | net Sharpe 0.12 [-0.37, 0.60], t 0.43, p 0.34 | soy enters through T2 |
Row count B5: 4 (T3 and T4 included for completeness of the registry line; T1 and T2 carry soy roots, T4 through T2).

### B6. E.22 forward test (registered r007-E22, N 532 -> 533)

| Trial ID | Family | Mechanism | Hold | Data span | Outcome | Key statistic |
|---|---|---|---|---|---|---|
| E22-F1 | micro trend book, forward test at $25,000, 36 months from first ledger record after the user approves a daily settlement source; p <= 0.05 one-sided NW lag 10 and net Sharpe >= 0.3 | trend (EWMAC) across the micro universe, including MZS (ZS) and MZL (ZL) | multi-day | design on 2010-07-01..2024-02-29 (modelled); forward period not started | registered, not evaluated | none (design study values in A8) |
Source: ledger/trial_registrations.jsonl line 8 (note field); reports/stage_e22_microbook.md lines 25-26.
Row count B6: 1.

### B7. Registered trials with no soy involvement (checked)

E23-MEZFh5, E23-MEZNh5, E23-MEZBh5 (ZF, ZN, ZB), E23-H6NQh5, E23-H6NQh20 (NQ): reports/E.23_RETURN.md lines 403-407. E20H6-T1..T3 (NQ): reports/E.20_RETURN.md line 7. C1-T1, C1-T2 and C1b-T1, C1b-T2 (world roots NG NQ ZN 6E GC ZC): reports/stage_e18_c1b_result.json (world.roots). E16-H2, E16-H3: B3. Row count B7: 12 trials.

### B8. Trial totals for Table B

Itemized soy-involving trial IDs: B1 11 (plus 4 adjacent), B2 9 (family B per root) + 3 (family A, K6 signals) of the 273, E16-H1, H4, H5 (3), E20S 45, E21-T1, T2 (2; T4 via T2), E22-F1 (1). Not counted into a single total by me: the K6 and Gate 0 trials are inside the 471 baseline.
