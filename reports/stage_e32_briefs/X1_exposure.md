# X1 exposure inventory (Stage E.32, ExposureInventory-SonnetMed)

Written 2026-10-26 (PDT, from `date`). Pure extraction: no interpretation, no conclusions, no new statistic. Every row names its
source file and line or section. No market data file was opened (data/vendor, data/processed*, data/sealed, /mnt/large-storage);
only reports, inventories, JSON result files, and the spend ledger through a count-only script
(reports/stage_e32_briefs/work/X1_exposure/X1_ledger_summary.py, output X1_ledger_summary.txt: counts, dataset, schema, symbols,
requested date range; no other field printed, no key seen).

Window under test: ZM, ZS, ZL data for CME trade dates 2017-05-01..2020-11-30 (sealed, docs/soy_test/SOY_TEST_MANIFEST.json).
Trial registry: ledger/trial_registrations.jsonl, 9 lines, N = 538 (line 1 baseline 471, "N after Stage E.12", source
reports/E.12_RETURN.md:561; lines 2-9 add 67: r001-C1 2, r002-E16 5, r003-C1b 2, r004-E20H6 3, r005-E20S 45, r006-E21 4,
r007-E22 1, r008-E23 5). The 471 baseline trials are not itemized in the registry; they are itemized from the stage reports below.

## 0. What the owned files are (sealed set, by name and span only)

Source: docs/soy_test/SOY_TEST_MANIFEST.json (expected_targets, 114 entries; names only).

| Group | Files | Span by file name |
|---|---|---|
| Raw ohlcv-1m ZS_v_0 chunks | 44 | range=2017-04-01_2017-05-01 .. range=2020-11-01_2020-12-01 |
| Raw ohlcv-1m ZL_v_0 chunks | 44 | same span |
| Raw ohlcv-1m ZM_v_0 chunks | 19 | range=2019-05-01_2019-06-01 .. range=2020-11-01_2020-12-01 |
| ext2010h bar stores | 2 (ZS, ZL) | 2010-07-01..2019-04-30 (data/processed_hist/ext2010h/{ZS,ZL}/...) |
| step2 bar stores | 3 (ZS, ZL, ZM) | 2019-05-06..2024-02-29 (data/processed_step2/{ZS,ZL,ZM}/...) |
| E.22 microbook caches | 2 (ZS, ZL) | reports/stage_e22_microbook/cache/{ZS,ZL}.parquet |
Total 114 (107 raw + 7). There is no ZM store before 2019-05 (manifest ext2010 null: reports/stage_e23_briefs/inventory/K6.md line 38).

Spend-ledger summary (ledger/databento_spend.jsonl, 37,290 lines; lines naming ZM, ZS or ZL; output in
work/X1_exposure/X1_ledger_summary.txt, 31 lines). Committed requests, merged requested ranges (start..end as logged):

| Dataset | Schema | Symbols | Commit lines | Merged requested range(s) |
|---|---|---|---|---|
| GLBX.MDP3 | ohlcv-1m | ZS.v.0 | 179 | 2010-07-01..2024-03-01; 2025-04-01..2026-06-21 |
| GLBX.MDP3 | ohlcv-1m | ZL.v.0 | 179 (+1 refused, 2025-08-01..2025-09-01) | 2010-07-01..2024-03-01; 2025-04-01..2026-06-21 |
| GLBX.MDP3 | ohlcv-1m | ZM.v.0 | 73 | 2019-05-01..2024-03-01; 2025-04-01..2026-06-21 |
| GLBX.MDP3 | mbo | ZM.v.0, ZM.v.1 | 39 | 2020-11-30T22:00:00Z..2024-02-29 (first request start 2020-11-30T22:00:00Z, end 2020-12-31T22:00:00Z) |
| GLBX.MDP3 | mbp-1 | ZS.v.0 | 44 | 2020-11-30T22:00:00Z..2024-02-29; plus five single days 2025-05-13, 2025-08-12, 2025-11-11, 2026-02-10, 2026-04-14 |
| GLBX.MDP3 | mbp-1 | ZL.v.0 | 44 | same as ZS.v.0 |
| GLBX.MDP3 | mbp-1 | ZM.v.0 | 5 | the five single days above |
| GLBX.MDP3 | definition | ZL.FUT, ZM.FUT, ZS.FUT | 39 | 2020-11-30..2024-02-29 |
| GLBX.MDP3 | ohlcv-1d | QM.FUT, ZM.FUT | 1 | 2023-01-01..2026-10-22 |
The 2020-11-30T22:00:00Z start equals the exclusive upper bound of the sealed UTC window in work: reports/stage_e32_briefs/seal/soy_test_seal.py
(WINDOW_UTC ends 2020-11-30T22:00Z). Source lines: work/X1_exposure/X1_ledger_summary.txt, "union of committed ranges" block.
Row count of this table: 9.

## Table A. Earlier exposure to the sealed window (2017-05-01..2020-11-30)

Columns: stage; store or file; roots; date span read; what was computed; trial IDs registered; source.

| # | Stage | Store or file | Roots | Date span read (overlaps sealed window as stated) | What was computed | Trial IDs | Source (file, line or section) |
|---|---|---|---|---|---|---|---|
| A1 | E.12 Task 6 (2026-10-03 10:54-11:26 by file mtime) | data/processed_step2/{ZS,ZL,ZM} built from raw ohlcv-1m chunks 2019-05-01..2024-03-01 | ZS ZL ZM | trade dates 2019-05-06..2024-02-29 (overlap 2019-05-06..2020-11-30) | store build and raw checks: bars ZS 1,143,451, ZL 1,085,571, ZM 975,302; trade_dates 1,214 each; non_increasing_steps 0, duplicate_timestamps 0, negative_volume 0, zero_volume_bars 0, off_tick_prices 0, ohlc_inconsistent 0; closure bars ZS 3 (first two listed: 2020-04-13 07:45, 2020-04-17 07:45), ZL 3, ZM 1 (2019-07-09 13:20); degraded UTC dates 8 each (first two 2020-02-27, 2020-02-28); roll boundaries; no returns | none | reports/step2/bars_ZS.json, bars_ZL.json, bars_ZM.json (fields bars, trade_dates, raw_checks, closure_bars, degraded) |
| A2 | E.12 Gate 0 (run once 2026-10-03 12:15) | step2 stores, 28 exposures | ZS ZL ZM among 28 | W_cf 2019-05-06..2024-02-29; family-A n_dates 1,068; family-B per-root n_dates 330-425 (overlap 2019-05-06..2020-11-30) | 273 tests: 192 family A (64 signals x 3 horizons h60/h120/hF, pooled over the 28 exposures, Spearman IC, t, p, Holm) and 81 family B (per root-horizon pairs, mean gross ticks vs cost, t_B); verdict FAIL, 0 passing pairs; includes the K6-derived signals k6_crushgap_gap, k6_limitcont_dir, k6_wasdepre_drift | gate0A_*/gate0B_* (273, inside baseline 471 = 198 + 273) | reports/E.12_RETURN.md lines 1-30, 490-491, 510; reports/stage_e12_gate0.json (tests[], n_a 192, n_b 81, verdict FAIL); reports/stage_e23_briefs/inventory/K6.md line 44 |
| A3 | E.17 step 12 (2026-10-10 01:29 by file mtime) | data/processed_hist/ext2010h/{ZS,ZL} built from raw chunks 2010-07-01..2019-05-01 | ZS ZL | trade dates 2010-07-01..2019-04-30 (overlap 2017-05-01..2019-04-30) | store build and raw checks: bars ZS 1,898,620, ZL 1,704,606; trade_dates 2,223 each; all raw_checks counts 0 except bars_in_scheduled_closure ZS 177, ZL 100; degraded UTC dates 14 each; calendar check; no returns | none (E16 test label) | reports/hist/bars_ZS_ext2010h.json, bars_ZL_ext2010h.json; reports/E.17_RETURN.md lines 555-560 |
| A4 | E.17 step 13: H1, H4, H5 runs (once each) | ext2010h + step2 stores; run manifest | ZS ZL on both stores; ZM on step2 only (fallback list, "not funded") | ZS, ZL 2010-07-01..2024-02-29; ZM 2019-05-06..2024-02-29 | pooled settlement-window tests: H1 settlement-window momentum, H4 next-day reversal, H5 equal-risk combination, one pooled daily series each over the 27 price paths (24 from 2010-07 plus RTY, TN, HE), per-root series not in the result files; results in Table B | E16-H1, E16-H4, E16-H5 (registered r002-E16, N 473 -> 478) | reports/E.17_RETURN.md lines 6-26, 531-532, 555-562; reports/stage_e17_fallback.json (ZM "not funded", window 2019-05-06..2024-02-29, rule A5); reports/stage_e17_run_manifest.json (ZS, ZL stores listed); reports/stage_e16_prereg_H1.md lines 30-40; reports/stage_e23_briefs/inventory/CDE.json (E16-H1 inputs: step2 27 roots) |
| A5 | E.20 Part C search (run 2026-10-11 17:44-17:52) | step2 stores, 17 vehicles | ZS ZL (ZM not among the 17 W_ext roots) | 1,248 training-calendar dates, 2019-05..2024-02 (overlap 2019-05-06..2020-11-30); no backward (ext2010h) read | panel 57,775 decision rows on 17 vehicles, 36 features, closure bars counted and kept (ZS 3, ZL 3); nested CPCV 15 outer splits, 4 inner folds, 45 configurations (ridge, LightGBM; h60, h120, hF); screen FAIL (results in Table B) | E20S-01..E20S-45 (r005-E20S, N 483 -> 528) | reports/E.20_RETURN.md lines 20-26, 308-335, 551-554; reports/stage_e23_briefs/inventory/K6.md line 44 |
| A6 | E.21 (run 2026-10-14 03:04-04:40) | ext2010h + step2 stores (17 roots) | ZS ZL | 2010-07..2024-02 (overlap 2017-05..2020-11) | T1 TSMOM-12 and T2 trend blend on 17 roots, per-root contribution (sum, own t, fills, gross, costs), yearly pooled table (2016-2024 rows), T3 turn of month and T4 combined book; soy results in Table B | E21-T1..T4 (r006-E21, N 528 -> 532) | reports/E.21_RETURN.md lines 1-16, 365-420, 435-437, 538, 576-583; reports/stage_e22_microbook.md line 34 ("never read by E.21" for ZM) |
| A7 | E.22 Part A K6 confirmation (K6 run once 18:50, 2026-10-16) | step2 stores (W_cf) | ZS ZM ZL (+ ZC ZW HE LE) | 2019-05-06..2024-02-29 (days 1,028-1,136; overlap 2019-05-06..2020-11-30) | confirmation of 27 K6 members (trips, theta_hat, UCB95, SE_boot, eps_X, null power, p_upper), Holm K = 5, DSR at N = 533, PBO; the soy rows are in Table B | the 27 K6 members (inside baseline 471; no new registration) | reports/E.22_RETURN.md lines 270-300, 355-402; reports/stage_e23_briefs/inventory/K6.md lines 10-34, 44 |
| A8 | E.22 Part B micro trend book (design study, B2-B3) | ext2010h + step2 stores; caches reports/stage_e22_microbook/cache/{ZS,ZL}.parquet | ZS ZL (as MZS, MZL; MZM not modelled) | 2010-07-01..2024-02-29 ("extension" data); live from 2011-07-11 | constants and estimates (weekly-return correlation matrix incl. MZS, MZL), returns by capital and method, turnover and costs, drawdowns, instruments at zero, capital sweep, per-instrument table, sensitivities, data counters (Marks MZS 3402, MZL 3400) | E22-F1 (r007-E22, N 532 -> 533; forward test, no data run) | reports/stage_e22_microbook.md lines 9-35, 94-123, 125-275, 313-341; reports/E.22_RETURN.md lines 425-440 |
| A9 | E.24 (2026-10-18) | none (reuses E.22's frozen estimates) | MZL appears in E22-F1's frozen correlation | n/a (no new read) | IDM from F1's frozen correlation without MZL | none | reports/E.24_RETURN.md lines 370, 453 |
| A10 | E.28 Part A0 (2026-10-21) | raw data/vendor/databento/GLBX.MDP3/ohlcv-1m/{ZS,ZL,ZM}_v_0 chunks ending on or before 2023-11-01 (160 ZS files, 160 ZL files, 54 ZM files opened) | ZS ZL ZM | owned span to 2023-10-31 (ZS, ZL from 2010-07-01; ZM from 2019-05-01), overlap includes the sealed window | Table 2 C4 big-move days (|daily log return| > 4 x that year's daily SD), per calendar year, mean per full year, rate per 252 days (values copied below); Table 1 standard window 2022-11-01..2023-10-31 (outside the sealed window) | none | reports/stage_e28_briefs/A0_contract_stats.md lines 10-19, 52-58, 114-117, 121-154, 202-205 |
| A11 | E.26 data move (2026-10-21) | all stores and raw chunks | all | byte-level move; sha256 and mode verified at the destination | no decoding (hash, mode, owner, mtime) | none | reports/E.26_RETURN.md lines 11, 20 |
| A12 | E.32 Part 0 seal (2026-10-26 22:54-22:55) | 114 files | ZS ZL ZM | whole-file seal | encryption and checksums; no in-window row read (by the tool's design statement) | none | reports/stage_e32_STATE.md lines 15-23; reports/stage_e32_briefs/seal/soy_test_seal.py docstring |

A10 recorded values (reports/stage_e28_briefs/A0_contract_stats.md, Table 2, lines 151, 152, 154; columns: first trade date, full years, mean per full year, rate per 252 days owned span, rate per 252 days 2019..2023-10-31, per year big moves / returns):
- ZL: 2010-07-01, 12, 0.33, 0.31, 0.21; 2010: 0/123, 2011: 0/247, 2012: 0/247, 2013: 1/245, 2014: 0/243, 2015: 0/247, 2016: 1/247, 2017: 1/246, 2018: 0/245, 2019: 0/245, 2020: 0/248, 2021: 1/241, 2022: 0/244, 2023: 0/206
- ZM: 2019-05-01, 3, 0.33, 0.46, 0.46; 2019: 0/161, 2020: 0/239, 2021: 1/245, 2022: 0/242, 2023: 1/206
- ZS: 2010-07-01, 12, 0.58, 0.62, 0.63; 2010: 0/125, 2011: 0/247, 2012: 0/245, 2013: 0/241, 2014: 1/245, 2015: 2/245, 2016: 0/247, 2017: 1/244, 2018: 1/247, 2019: 0/247, 2020: 0/248, 2021: 2/245, 2022: 0/246, 2023: 1/205

Row count Table A: 12 rows (A1-A12), plus A10's three recorded value lines.

### Table A, read-checked stages with no soy data in the sealed window (for completeness, each with its reason)

| Stage | Reason it is not an exposure row | Source |
|---|---|---|
| E.1 step 1 purchase, E.2a funnel and epsilon, E.2b, E.8 K6 screen (27 trials), E.8 power runs | data dated 2025-04-01..2026-06-21 (E.2a bars built 2025-04-01..2026-06-18; E.8 windows 264-287 dates from 2025-04-01) | reports/stage_e1_purchase.md line 15; reports/E.2a_RETURN.md lines 380-382; reports/E.8_RETURN.md lines 202-206 (Windows 264-287 dates at line 205) |
| E.17 C1 (stopped at C10), E.18 C1b | world roots NG NQ ZN 6E GC ZC only (no ZS, ZM, ZL); K6-derived features had 0 applicable rows on W_ext | reports/stage_e18_c1b_result.json (world.roots); reports/stage_e23_briefs/inventory/K6.md line 44 |
| E.20 H6 | NQ only | reports/E.20_RETURN.md line 7 |
| E.20 dry check step 6 | synthetic sentinel frames, no store | reports/stage_e20_dry_check_step6.md line 1 |
| E.23 (five trials) | ZF ZN ZB and NQ only; K6 members on ZS, ZL, ZM dropped for data, mechanism and root reasons (inventory step read code and reports only) | reports/E.23_RETURN.md lines 222, 354-356, 388, 403-407; reports/stage_e23_briefs/inventory/K6.md lines 3-5, 77 (Sources read) |
| E.13 research | no market data | progress.md line 3453 header; reports/stage_e13_trend_carry.md lines 250-252 (contract spec figures only) |
| E.16 Part A | "no Databento, no bar read" | progress.md line 3662 header |
| E.29 | ZM bars dated 2022-10-01..2023-11-01 | reports/E.29_RETURN.md line 113 |
| E.31 | ZM MBO, ZS and ZL MBP-1 from 2020-12 to 2024-02 (discovery dates; first request start 2020-11-30T22:00:00Z); volume check ohlcv-1d 2023-01-01..2026-10-22; "No ZM, ZS or ZL record dated on or after 2024-03-01 was quoted, bought or read" | reports/E.31_RETURN.md lines 25-28, 121, 128-142, 160-174; ledger summary above |
Row count: 9 rows.

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

## Table C. E.31's prior exposure on the discovery dates 2020-12..2024-02

Scope: reports/E.31_RETURN.md and reports/stage_e31_briefs/work/pilot/runs/stats31.md (1,595 lines; generated 2026-10-23 12:46:58 PDT by stats31.py from
reports/stage_e31_briefs/work/pilot/runs/measure31: 816 trade dates 2020-12-01 to 2024-02-29; bootstrap 2000 replicates, seed 31, unit trade date; units ticks of
0.10 USD/short ton). Recorded values only; nothing computed. Full verbatim copies of the line ranges listed below are in
reports/stage_e32_briefs/work/X1_exposure/X1_tableC_appendix.md (982 lines, made by X1_tableC_copy.py, which only copies line ranges).
E.31 also wrote stats31.json (E.31_RETURN.md line 178: "the full tables"); it was not opened.

### C1. Statistics E.31 computed, by section name (stats31.md)

Splitting variables that exist in E.31's output: model (a) K, (b) FIFO back of queue, (c) trade-through; symbol ZM.v.0 (front) and ZM.v.1 (second month);
session DAY and OVERNIGHT; side (buy, sell, pooled); markout horizon 1 s, 10 s, 60 s; five firms (fee per fill); ZS move over the prior L = 1 s and 10 s;
ZL move over L = 1 s and 10 s; joint ZS+ZL move; USDA release window; queue imbalance at entry; trade dates from 2023-11-01 alone (model (a) only).

| Section name (stats31.md heading) | Lines | Data rows (excluding header) | Variables and statistics recorded | Steering-relevant content |
|---|---|---|---|---|
| ## Verdict: FAIL | 5-19 | 4 test rows + 2 info lines | K1 (lower bound -1.2524; mean -1.2339 [-1.2524, -1.2142], 44045 fills), K2 (44045), K3 (111.5681 [109.5533, 113.4611]); information-only full round-trip fee: lower bound -1.5164, mean -1.4979 [-1.5164, -1.4782] | fill and markout level for the primary population |
| ## Primary population, the three models side by side (ZM.v.0, DAY, sides pooled) | 21-80 | 55 | placements, fills, fill rate, touch rate, stale share, KM P(fill by 1, 10, 60 s), half-spread captured, markouts, E_1, E_10, E_60, N_10(Topstep), VPO, medians, share E_h > 0, per model | level of markout by horizon |
| ## Net results for the five firms (ZM.v.0, DAY, sides pooled) | 81-102 | 15 | N_h(firm) and VPO_h, h in {1, 10, 60} s, firms Topstep 0.264, Lucid 0.280, Bulenox 0.286, MFFU 0.306, Tradeify 0.460 ticks per fill, three models | firm split |
| ## All cells: (a) K, (b) FIFO, (c) trade-through; ZM.v.0 and ZM.v.1; DAY and OVERNIGHT (12 headings: lines 105, 165, 225, 285, 345, 405, 465, 525, 585, 645, 705, 765) | 103-824 | 55 per block, 660 in all | pooled, buy and sell columns for every statistic above | session, month-of-contract (front vs second), side split |
| ## Model (a), trade dates from 2023-11-01 alone (spec 3.1; decides nothing) (4 headings: lines 829, 889, 949, 1009) | 825-1070 | 55 per block, 220 in all; 82 trade dates | same statistics, dates on or after 2023-11-01 only | recent-period split (model a only) |
| ## Splits (spec 5; reported for every model, they decide nothing) (12 headings: lines 1075, 1115, 1155, 1195, 1235, 1275, 1315, 1355, 1395, 1435, 1475, 1515) | 1071-1554 | 35 per block, 420 in all | families: ZS L=1 s (against, flat, with, missing); ZL L=1 s; ZS L=10 s; ZL L=10 s; ZS+ZL L=1 s (both against, both with, other, missing); ZS+ZL L=10 s; USDA release (pre (-30, 0), post [0, 5), post [5, 30), other); queue imbalance (7 buckets: (-1,-0.6], (-0.6,-0.2], (-0.2,0.2), [0.2,0.6), [0.6,1), outside (-1,1), missing). Columns: placements (fill rate), fills, mean E_1, E_10, E_60, median E_10, share E_10 > 0, mean N_10(Topstep) with 95% interval and label | ZS and ZL moves at fill, USDA windows, queue imbalance at entry |
| ## Feasible round trips: the loop (spec 6; DAY session) | 1555-1564 | 3 | round trips per DAY date by model: (a) 207.662 [204.612, 210.449], (b) 215.137 [212.001, 218.005], (c) 111.568 [109.553, 113.461]; durations 80.75, 77.94, 150.02 s | trade frequency |
| ## Implied-liquidity check (spec 8) | 1565-1575 | 4 | ZM.v.0 DAY: A/B prints 7,823,934, volume 19,702,332; (i) share of prints 0.0552, of volume 0.0360; (ii) 0.1180, 0.2600; side N share 0.0905; OVERNIGHT, ZM.v.1 rows as recorded | displayed-liquidity facts |
| ## Exclusions (days.parquet, spec 2) | 1576-1582 | 2 | ZM.v.0: 816 dates, 764 included, 52 excluded (after_roll_day 20, cme_holiday_or_early_close 4, roll_day 23, scheduled_late_open 5), records 414,363,576; ZM.v.1: 684 included, 132 excluded | calendar facts |
| ## Consistency checks | 1583-1595 | 9 | all 0 or empty | none |

Search result for what is absent (grep, case-insensitive, in stats31.md for "month", "by session", "hour"): no match. No section of stats31.md splits by calendar month, hour of day, day of week, year, volatility state, or contract expiry other than front versus second month and the exclusions table. (Statement of what the file contains, not a conclusion.)
Row count C1: 10 section rows.

### C2. The model (c), ZM.v.0, DAY splits, as recorded (stats31.md lines 1395-1434; the other eleven blocks are in the appendix)

Columns as recorded: family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 [95% interval] label | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) [interval] label.

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 20710 | -1.0832 | -1.1004 [-1.1311, -1.0700] negative | -1.1333 | -1.0000 | 0.1746 [0.1692, 0.1797] | -1.3644 [-1.3951, -1.3340] negative |
| ZS L=1 s | flat | - | 20851 | -0.8540 | -0.8781 [-0.8984, -0.8568] negative | -0.8818 | -0.5000 | 0.1927 [0.1869, 0.1983] | -1.1421 [-1.1624, -1.1208] negative |
| ZS L=1 s | with | - | 2484 | -0.7091 | -0.6520 [-0.7240, -0.5776] negative | -0.5074 | -0.5000 | 0.2548 [0.2381, 0.2716] | -0.9160 [-0.9880, -0.8416] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 14006 | -1.0231 | -1.0435 [-1.0849, -1.0038] negative | -1.0840 | -1.0000 | 0.1907 [0.1836, 0.1974] | -1.3075 [-1.3489, -1.2678] negative |
| ZL L=1 s | flat | - | 21800 | -0.9135 | -0.9332 [-0.9588, -0.9072] negative | -0.9398 | -0.5000 | 0.1811 [0.1757, 0.1867] | -1.1972 [-1.2228, -1.1712] negative |
| ZL L=1 s | with | - | 8239 | -0.9417 | -0.9417 [-0.9816, -0.9011] negative | -0.9039 | -1.0000 | 0.2001 [0.1913, 0.2096] | -1.2057 [-1.2456, -1.1651] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 28876 | -1.0233 | -1.0416 [-1.0655, -1.0176] negative | -1.0487 | -1.0000 | 0.1776 [0.1730, 0.1820] | -1.3056 [-1.3295, -1.2816] negative |
| ZS L=10 s | flat | - | 9710 | -0.8376 | -0.8629 [-0.8926, -0.8315] negative | -0.8922 | -0.5000 | 0.1871 [0.1792, 0.1952] | -1.1269 [-1.1566, -1.0955] negative |
| ZS L=10 s | with | - | 5459 | -0.7909 | -0.7811 [-0.8343, -0.7316] negative | -0.7641 | -0.5000 | 0.2424 [0.2303, 0.2542] | -1.0451 [-1.0983, -0.9956] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 20854 | -0.9887 | -1.0138 [-1.0442, -0.9830] negative | -1.0163 | -1.0000 | 0.1863 [0.1810, 0.1917] | -1.2778 [-1.3082, -1.2470] negative |
| ZL L=10 s | flat | - | 7057 | -0.9055 | -0.8937 [-0.9272, -0.8617] negative | -0.8990 | -0.5000 | 0.1817 [0.1720, 0.1907] | -1.1577 [-1.1912, -1.1257] negative |
| ZL L=10 s | with | - | 16134 | -0.9293 | -0.9465 [-0.9769, -0.9158] negative | -0.9656 | -0.5000 | 0.1921 [0.1859, 0.1982] | -1.2105 [-1.2409, -1.1798] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 11067 | -1.0811 | -1.1036 [-1.1518, -1.0564] negative | -1.1764 | -1.0000 | 0.1799 [0.1724, 0.1870] | -1.3676 [-1.4158, -1.3204] negative |
| ZS+ZL L=1 s | both with | - | 1553 | -0.7595 | -0.7202 [-0.8031, -0.6348] negative | -0.6101 | -0.5000 | 0.2447 [0.2235, 0.2666] | -0.9842 [-1.0671, -0.8988] negative |
| ZS+ZL L=1 s | other | - | 31425 | -0.9183 | -0.9352 [-0.9567, -0.9137] negative | -0.9276 | -0.5000 | 0.1876 [0.1830, 0.1924] | -1.1992 [-1.2207, -1.1777] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 17946 | -1.0261 | -1.0452 [-1.0772, -1.0130] negative | -1.0419 | -1.0000 | 0.1789 [0.1733, 0.1848] | -1.3092 [-1.3412, -1.2770] negative |
| ZS+ZL L=10 s | both with | - | 4294 | -0.8121 | -0.8009 [-0.8561, -0.7458] negative | -0.7927 | -0.5000 | 0.2345 [0.2213, 0.2469] | -1.0649 [-1.1201, -1.0098] negative |
| ZS+ZL L=10 s | other | - | 21805 | -0.9218 | -0.9412 [-0.9657, -0.9175] negative | -0.9637 | -0.5000 | 0.1857 [0.1806, 0.1908] | -1.2052 [-1.2297, -1.1815] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 293 | -0.9454 | -0.9625 [-1.1514, -0.7846] negative | -0.8242 | -1.0000 | 0.1775 [0.1374, 0.2174] | -1.2265 [-1.4154, -1.0486] negative |
| USDA release | post [0, 5) | - | 68 | -7.8824 | -8.9779 [-15.2470, -4.2997] negative | -11.1176 | -9.0000 | 0.3824 [0.2769, 0.4789] | -9.2419 [-15.5110, -4.5637] negative |
| USDA release | post [5, 30) | - | 330 | -1.1606 | -1.2015 [-1.4984, -0.9169] negative | -1.2061 | -1.0000 | 0.2727 [0.2360, 0.3063] | -1.4655 [-1.7624, -1.1809] negative |
| USDA release | other | - | 43354 | -0.9412 | -0.9556 [-0.9724, -0.9384] negative | -0.9623 | -1.0000 | 0.1868 [0.1830, 0.1907] | -1.2196 [-1.2364, -1.2024] negative |
| queue imbalance | (-1, -0.6] | 8211 (0.6065 [0.5948, 0.6184]) | 4980 | -0.8965 | -0.9317 [-0.9798, -0.8844] negative | -0.9693 | -0.5000 | 0.1821 [0.1710, 0.1942] | -1.1957 [-1.2438, -1.1484] negative |
| queue imbalance | (-0.6, -0.2] | 20260 (0.5556 [0.5473, 0.5634]) | 11257 | -0.9490 | -0.9552 [-0.9946, -0.9175] negative | -0.9972 | -1.0000 | 0.1904 [0.1831, 0.1978] | -1.2192 [-1.2586, -1.1815] negative |
| queue imbalance | (-0.2, 0.2) | 28626 (0.4898 [0.4826, 0.4966]) | 14021 | -0.9707 | -0.9984 [-1.0302, -0.9668] negative | -0.9622 | -1.0000 | 0.1868 [0.1802, 0.1932] | -1.2624 [-1.2942, -1.2308] negative |
| queue imbalance | [0.2, 0.6) | 20260 (0.4921 [0.4837, 0.5001]) | 9969 | -0.9701 | -0.9601 [-1.0053, -0.9159] negative | -0.9925 | -1.0000 | 0.1909 [0.1834, 0.1986] | -1.2241 [-1.2693, -1.1799] negative |
| queue imbalance | [0.6, 1) | 8211 (0.4650 [0.4514, 0.4774]) | 3818 | -0.9358 | -0.9840 [-1.0360, -0.9340] negative | -0.9637 | -1.0000 | 0.1820 [0.1695, 0.1945] | -1.2480 [-1.3000, -1.1980] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |


Row count C2: 35 data rows (plus header).

### C3. E.31_RETURN.md statements about conditioning and levels (verbatim, lines 183-206)

```
Primary population (ZM.v.0, DAY session, buy and sell pooled; ticks; 95% day-block intervals):

| Statistic | (a) K | (b) FIFO, back of queue | (c) trade-through (gate) |
|---|---|---|---|
| placements | 85,568 | 85,568 | 85,568 |
| fills (rate) | 60,216 (0.704) | 61,078 (0.714) | 44,045 (0.515) |
| half-spread captured, mean | +0.341 | +0.359 | -0.425 |
| 10 s markout vs mid, mean | -0.629 | -0.611 | -0.545 |
| 10 s edge E_10, mean | -0.287 [-0.303, -0.273] | -0.252 [-0.267, -0.239] | -0.970 [-0.988, -0.950] |
| 10 s edge net of Topstep's fee per fill | -0.551 | -0.516 | **-1.234 [-1.252, -1.214]** |
| 60 s edge E_60, mean | -0.290 | -0.253 | -0.979 |
| loop round trips per DAY date, mean | 207.7 | 215.1 | 111.6 [109.6, 113.5] |

Kill rule (spec v2 section 7), model (c): K1 holds (FAIL): lower bound -1.2524 under both variants; information only,
at 0.528 per fill: -1.5164. K2 clear: 44,045 fills. K3 clear: 111.568 over 764 dates. **Verdict: FAIL.**

Reported beside, deciding nothing (gross 10 s edge, model (c)): overnight front month -0.997 (fill rate 0.132);
second month (ZM.v.1) DAY -1.186; model (a) from 2023-11-01 alone, front DAY -0.281. All five firms' nets are negative
for every model and horizon (Tradeify's 0.460 fee per fill makes it the worst). Conditioning, model (c), front DAY,
10 s edge: fills after a ZS move against the order in the prior 1 s average -1.100, after a ZS move with it -0.652;
fills 0-5 minutes after a USDA release -8.98 (68 fills); no imbalance, ZS, ZL or USDA bucket is positive for any
model. Implied liquidity, front DAY: 5.5% of aggressor prints (3.6% of their volume) found no displayed resting
quantity at their price, 11.8% (26.0% of volume) found less than their size, and 9.1% of prints carry no aggressor side.

```

Row count C3: 24 verbatim lines.

### C4. Other E.31 sources that carry steering-relevant facts (not statistics from the discovery dates)

| Item | Source | Recorded content |
|---|---|---|
| Volume check, ZM | reports/E.31_RETURN.md lines 128-141; reports/stage_e31_volume.md (not opened beyond the return) | window median 78,281.5 (own universe 79,512.0) over 2025-10-01..2026-09-30 (outside the discovery dates); per-quarter medians, 10th percentiles and front-month shares are in stage_e31_volume.md; "ZM's Q3 front-month share is low (about 0.08)" (E.31_RETURN.md line 139-140) |
| USDA calendar used for the splits | reports/E.31_RETURN.md lines 304-305; research/usda_releases.csv and usda_releases_ext.csv (E.31_RETURN.md lines 226-227) | WASDE, NASS and FAS rows; 88 FAS rows rule-derived or uncertain; NOPA not used; three 2022 FAS outage weeks skipped |
| Pilot spec definitions of the splits | reports/stage_e31_pilot_spec.md (not opened here); stats31.md line 1073 describes them | ZS and ZL move = sign of s x d, d = mid(t_f) - mid(t_f - L) in that contract's ticks; USDA = signed minutes from nearest release on the trade date; imbalance = s x I at j |
| Kill rule and verdict | reports/E.31_RETURN.md lines 18-24, 195-197 | ZM FAILS on K1 (model c, front, DAY, 10 s): -1.234 [-1.252, -1.214]; also fails at zero fee (gross -0.970 [-0.988, -0.950]) |
| Data on disk | reports/E.31_RETURN.md lines 25-28, 336-337 | 39 whole months 2020-12 to 2024-02, ZM MBO (ZM.v.0, ZM.v.1), ZS and ZL MBP-1 (front), definitions; 156 files, 24.2 GB; 816 trade dates measured; 764 DAY dates usable for the front month |
| Reviewer model deviation | reports/E.31_RETURN.md lines 29-33 | workers spawned as "Fable xhigh" ran on claude-sonnet-5-5 per transcript; verdict numbers rechecked by an Opus 5.5 xhigh worker: CONFIRMED |
Row count C4: 6.

## Not finished or not verified

- E.17 H1/H4/H5: that ZM actually entered the pooled series (on the fallback window) rests on reports/stage_e17_fallback.json rule A5 and reports/stage_e23_briefs/inventory/CDE.json (E16-H1 inputs: step2 27 roots); the pooled result files carry no per-root rows, and I did not open the bar-level units file (reports/stage_e17_runs/H1_units.jsonl).
- E.12 Gate 0 family-A pooling: whether the three K6-derived signals take values on all 28 exposures or only on soy and livestock legs was not extracted.
- Hold lengths for E16-H4 and E21-T1/T2, and the exact horizon units h60, h120, hF, were not extracted (named in Table B where so).
- The 471 baseline trials are not itemized in the registry; I itemized soy-involving ones from stage reports (K6 freeze, Gate 0 file). Other baseline trials (D.1 to D.1f MES families, K1-K5, K7-K9 members) were checked at cluster level in reports/stage_e16_overlap.md line 50 (roots list) and reports/stage_e23_briefs/inventory/CDE.json, not trial by trial.
- reports/stage_e12_gate0.json and the stage E.17 H result JSONs were read as result files (the H1 result printed daily pooled series once by mistake; no raw bars involved).
- stats31.json, stage_e31_volume.md and stage_e31_pilot_spec.md were not opened.
- Ledger summary prints only counts, dataset, schema, symbols, requested ranges (one extra check printed request start/end strings for the earliest mbo and mbp-1 lines). No key or other field was shown.
