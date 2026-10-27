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
