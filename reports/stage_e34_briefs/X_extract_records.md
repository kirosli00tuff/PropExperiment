# X_extract_records: earlier ZL exposure on the discovery dates (Stage E.34, ExposureExtract-HaikuMed)

Written 2026-10-29, from 12:10 PDT (TZ=America/Vancouver date at start). Extraction only: no conclusions.

Method and limits:
- No market-data file was opened or decoded by this worker. Sources were program reports (reports/*.md, reports/*.json read by grep or line range), ledger/trial_registrations.jsonl (10 lines, all printed as keys, notes and id counts), and ledger/databento_spend.jsonl (37,290 lines, read by reports/stage_e34_briefs/work/ExposureExtract-HaikuMed/spend_zl_summary.txt, counts and date ranges only).
- Numeric results of statistics computed on ZL data are not copied (rule 3). Outcomes are given as location (file:line) and, where it is a program verdict, the verdict word.
- Overlap column: "discovery" = 2020-12-01..2024-02-29. Where a row's data also touches the sealed window (2017-05-01..2020-11-30), that is stated as a separate fact in the overlap cell; it is not a judgment.
- Line references are to the file as it stands on 2026-10-29. Where a row cites a line only through X1_verify.md, that verification report is named.

## Table 1. Earlier reads or computations using ZL data, dated against the discovery window

| # | stage | trial or registration id | what was computed (verbatim phrase) | ZL data used (schema; dates) | overlaps 2020-12..2024-02 | labels | outcome recorded (where) | source file:line |
|---|---|---|---|---|---|---|---|---|
| EX-01 | E.0 (quotes) | none (metadata only) | "Quotes only ... nothing was bought" | ohlcv-1m metadata for ZL, request span 2019-05-01..2026-06-21 (record counts only, no prices) | yes (metadata span covers the discovery dates; no price read) | none | metadata row only | reports/stage_e0_quotes.md:73; reports/stage_e32_briefs/X1_verify.md:203 (M3) |
| EX-02 | E.8 (K6 screen, research window) | K6-cp1-01 ZL; K6-cp2-01 ZL; K6-cp3-01 ZL (baseline 471; not itemized in ledger) | "E.8 screen" on the K6 members (research window) | ZL, 2025-04-01..2026-06 ("Windows 264-287 dates from 2025-04-01") | no (2025-04 onward) | ZL own (K6 port mechanisms) | tier B on all three ZL rows | reports/stage_e32_briefs/X1_exposure.md:104, 107, 110; reports/E.8_RETURN.md:219, 226, 233; X1_verify.md:205 |
| EX-03 | E.22 Part A (K6 confirmation) | K6-cp1-01 ZL; K6-cp2-01 ZL; K6-cp3-01 ZL; K6-crushgap-01 ZS (legs ZM, ZL) | "E.22 confirmation (2019-05-06..2024-02-29)" (K6.md Facts section) | ZL step2 store, ohlcv-1m, 2019-05-06..2024-02-29 (reports/stage_e22_confirm_k6/K6_K6-cp{1,2,3}-01_ZL_confirmation_trips.json) | yes, full (2020-12-01..2024-02-29 inside 2019-05-06..2024-02-29); also overlaps the sealed window 2019-05-06..2020-11-30 | ZL own (cp1, cp2, cp3); ZL as an input leg (crushgap, ZS traded) | ZL rows: status null; K6 statement "no statement" | reports/E.22_RETURN.md:373, 380, 387, 390; reports/E.22_RETURN.md:398-402 (edge chain); reports/stage_e23_briefs/inventory/K6.md:12, 19, 26, 29; reports/stage_e32_briefs/X1_exposure.md:104, 107, 110, 111 |
| EX-04 | E.22 Part B (micro trend book design) | E22-F1 (registered, not evaluated) | "modelled" design study of MZL, extension span | ZL ext2010h store 2010-07-01..2019-04-30 and step2 store 2019-05-06..2024-02-29; cache reports/stage_e22_microbook/cache/ZL.parquet | yes (modelled span 2010-07-01..2024-02-29 covers the discovery dates); also covers the sealed window | none (design: weekly correlations, returns, costs) | "registered, not evaluated" (E22-F1); "design study" | reports/E.22_RETURN.md:432; reports/stage_e22_microbook.md:25-26; ledger/trial_registrations.jsonl:8 (r007-E22); reports/stage_e32_test_seal.md:130; X1_verify.md:69 (A8) |
| EX-05 | E.12 (Gate 0; in the 471 baseline) | gate0B_ZL_h60, gate0B_ZL_h120, gate0B_ZL_hF (family B, per root); ZL inside the family-A pool over 28 exposures | "Gate 0 ran once" | ZL step2 bars (reports/step2/bars_ZL.json), trade dates 2019-05-06..2024-02-29 (first and last trade date as recorded); c/sigma admissibility filter over the same panel | yes, full (2020-12-01..2024-02-29 inside); also overlaps the sealed window 2019-05-06..2020-11-30 | ZL own (family B per-root ML ridge pairs); ZL inside the pooled family-A K6-derived signal tests | verdict FAIL (reports/stage_e12_gate0.json verdict field); ZL family-B rows FAIL | reports/E.12_RETURN.md:543 (Gate 0 ran once; verdict FAIL); reports/E.12_RETURN.md:490 (ZL purchase row); reports/stage_e32_briefs/X1_exposure.md:129-131 (B2 ZL rows); reports/stage_e32_briefs/X1_verify.md:62-63 (A1, A2) |
| EX-06 | E.14 (test C1, M1 fit) and E.18 (test C1b) | C1-T1, C1-T2 (r001-C1, ledger line 2); C1b-T1, C1b-T2 (r003-C1b, ledger line 4) | "the E.12 phase-1 panel, 2019-05-06..2024-02-29, all 27 Gate 0 products" (stage_e14_prereg_C1.md:37-38) | E.12 panel including ZL rows (ZL as training input; the panel is built from the step2 stores) | yes, full (2020-12-01..2024-02-29 inside); also overlaps the sealed window 2019-05-06..2020-11-30 | ZL as training input (E.12 panel labels; ZL rows included); test window of C1 and C1b holds NG, NQ, ZN, 6E, GC, ZC only | "C1 stopped at C10 (no statistic); C1b FAIL" | reports/stage_e14_c1_model.md:33; reports/E.14_RETURN.md:171; reports/stage_e32_test_seal.md:124; X1_verify.md:81, 201 (M1); X1_exposure.md:201-203 area (B7) |
| EX-07 | E.17 (base-rule batch, r002-E16) | E16-H1, E16-H4, E16-H5 | "pooled" settlement-window and next-day products (table lines 14-22) | ZL ext2010h store 2010-07-01..2019-04-30 (reports/hist/bars_ZL_ext2010h.json) and ZL step2 store 2019-05-06..2024-02-29; ZL is not in the fallback list ("Fallback window 2019-05-06..2024-02-29, not funded: YM, HG, 6S, 6J, 6A, 6B, 6N, ZM, ZW, 6C") | yes, full (2020-12-01..2024-02-29 inside); the pool also spans the sealed window 2010-07-01..2020-11-30 | pooled over price paths; ZL own units recorded per product | H1 FAIL, H4 FAIL, H5 FAIL (table lines 14-22) | reports/E.17_RETURN.md:14-22, 26; reports/stage_e17_runs/H1_result.json (per_product ZL, as read by X1_verify); X1_verify.md:65 (A4 correction: pool window and roots) |
| EX-08 | E.20 (search, r005-E20S) | E20S-01..E20S-45 (45 trials) | "run on 17 roots with late-session features" | ZL step2 store, ZL among 17 vehicles; training-calendar dates 2019-05..2024-02 (1,248 dates); ZL closure bars counted (line 314) | yes (training span 2019-05-06..2024-02-29 includes the discovery dates); also overlaps the sealed window 2019-05-06..2020-11-30 | ZL own (ML search; ZL rows entered every fit, per X1_verify A5) | screen FAIL; all 45 negative (reports/E.20_RETURN.md:308-335); ZL "never traded" out of sample (341-342) | reports/E.20_RETURN.md:29, 268, 308-315, 341-342; reports/stage_e32_briefs/X1_exposure.md:178 (B4) |
| EX-09 | E.21 (multi-day round, r006-E21) | E21-T1, E21-T2 (T4 through T2) | "### Per root, T1 (base case)"; per-root contributions for ZL | ZL ext2010h and step2 stores, 17 roots, span 2010-07..2024-02 | yes (span 2010-07-01..2024-02-29 covers the discovery dates); also overlaps the sealed window | ZL own (per-root TSMOM 12 month; trend blend) | FAIL (E21-T1, T2 per reports/E.21_RETURN.md:8-16) | reports/E.21_RETURN.md:8-16, 385, 412; reports/stage_e32_briefs/X1_exposure.md:187-188 (B5); X1_verify.md:67 (A6) |
| EX-10 | E.23 (inventory, no registration) | K6-cp1-01 ZL; K6-cp2-01 ZL; K6-cp3-01 ZL; K6-crushgap-01 ZS (signal legs ZM, ZL) | membership and mechanism rows (inventory, no computation) | ZL W_ext store 2010-07-01..2019-04-30 (inventory facts); the W_ext span is recorded as never run on for any K6 member | no for the inventory itself (W_ext ends 2019-04-30); the E.22 and E.8 uses are in EX-02 and EX-03 | ZL own; ZL leg for crushgap | none in the inventory (membership only) | reports/stage_e23_briefs/inventory/K6.md:12, 19, 26, 29, 38, 44 (Facts section: "No stage ran a K6 member on W_ext"); reports/stage_e23_briefs/inventory_compact.txt:81, 84, 87 |
| EX-11 | E.25 (NM1 near-miss table, derived figures) | K6-cp2-01 ZL (E.22 row); gate0B_ZL_h120, gate0B_ZL_hF (E.12 rows) | "Derived figures (marked d) are computed from recorded per-trip gross_cents in the trips files" (NM1 header, per X1_verify M2) | E.22 trip files for the ZL members, 2019-05-06..2024-02-29; ZL Gate 0 family-B rows over 2019-05..2024-02 | yes (inside 2019-05-06..2024-02-29); also overlaps the sealed window | ZL own trades (gross per trade, derived) | descriptive; NM1 378 rows, NM2 triage (reports/E.25_RETURN.md:240) | reports/stage_e25_briefs/NM1_nearmiss_table.md:109, 180-181 (ZL rows); reports/E.25_RETURN.md:240; reports/stage_e32_test_seal.md:129 |
| EX-12 | E.28 (A0 contract statistics) | none (descriptive counts) | "whose range ends on or before 2023-11-01 were opened" (A0 data rule) | ZL ohlcv-1m raw files ending on or before 2023-11-01 (file inventory row ZL: 2010-07-01 to 2026-06-21 in the inventory; files opened are those ending on or before 2023-11-01) | yes (opened files include 2020-12..2023-10); also includes files spanning the sealed window | none | descriptive counts of big-move days per calendar year (seal table row) | reports/stage_e28_briefs/A0_contract_stats.md:12-14, 202; reports/stage_e32_test_seal.md:131; X1_verify.md:71 (A10) |
| EX-13 | E.31 (passive order-book pilot, ZM with ZL conditioning) | none (E.31 pilot; no registration; ledger has no E.31 line) | "ZS / ZL moves: sign of s x d, d = mid(t_f) - mid(t_f - L) in that contract's ticks" (stats31.md:1073) | ZL MBP-1 front month, 2020-12..2024-02 ("ZL MBP-1 (front)"); 816 trade dates measured, 764 DAY dates usable for the front month | yes, full (2020-12-01..2024-02-29) | ZM markouts (1 s, 10 s, 60 s) are the labels; ZL only as a conditioning split (ZL move over L = 1 s and 10 s; joint ZS+ZL) | verdict FAIL on K1 (reports/E.31_RETURN.md:18-24); conditioning statements verbatim at reports/E.31_RETURN.md:183-206 | reports/E.31_RETURN.md:25-28, 121, 183-206, 196-197; reports/stage_e31_briefs/work/pilot/runs/stats31.md:1073; reports/stage_e32_briefs/X1_exposure.md:213-217 (C1), 280-283 (C4) |
| EX-14 | E.31 follow-up V49 (ZL trade-through) | none | "V49's ZL follow-up" (planned, not run) | ZL MBP-1 front month, 2020-12..2024-02 (on disk) | would overlap; not computed | n/a | not run: R1-20 "ZL follow-up (skipped)" | reports/E.31_RETURN.md:312, 327-329, 336; reports/stage_e32b_briefs/R1_closed_lines.md:139-143 |
| EX-15 | E.32b (F3 volatility, owned ZL bars) | none (inputs to the E.32b ranking and holding) | "Table 1. Volatility per code ... (window 2022-11-01..2023-10-31, regular trade dates)" | ZL ohlcv-1m, 12 months 2022-11..2023-10, opened through the bar guard (reports/stage_e32b_briefs/F3_vol.md:16-19) | yes, full (2022-11-01..2023-10-31 inside 2020-12-01..2024-02-29) | none (volatility per horizon) | sigma values recorded (ZL row) and used by E.32b; values not copied | reports/stage_e32b_briefs/F3_vol.md:16-19, 111, 163; reports/stage_e32b_briefs/F5_holding.md:471-476 (ZL block sigma column matches F3 ZL row) |
| EX-16 | E.32b (F5 holding, ZL) | none | "### ZL (c_RT 1.50 u, L_main 290, min G_RT at 30)" (holding table, sigma from F3) | ZL via F3 sigma, window 2022-11-01..2023-10-31 | yes (inside discovery) | none | "topstep|ZL: B = 15, 30, 60; prior holds" (reports/stage_e32b_briefs/F5_holding.md:905); ibkr|ZL row at 966 | reports/stage_e32b_briefs/F5_holding.md:471, 905, 966 |
| EX-17 | E.32b (landing, ranking, build recommendation) | C140 ZL F10 order-book state; C138 ZL F09 soy-complex lead-lag (recommended, one registration) | "ZL ranks 15 (Topstep), the only top-15 product with a clean (sealed) test window" (ranking recorded; no value copied) | ZL inputs via EX-15 and EX-16 and the E.28 A1 tick sizes; no separate ZL bar read recorded in E.32b | indirect (inputs 2022-11..2023-10 inside discovery) | n/a | ranking and build recommendations (not an evaluation): reports/E.32b_RETURN.md:25, 194, 209, 238 | reports/E.32b_RETURN.md:21-25, 186-200, 209, 238, 252, 365 (OC-19, G17 null on ZL cited without value) |
| EX-18 | E.33 (search, r009-E33, 300 configurations) | E33-S*: feature set S2 (cross-asset propagation from ZS and ZL) and S5 (all four pooled, includes S2) | "cross-asset propagation from ZS and ZL, ZM order flow and book state, ZM's own price path, and all four pooled" | ZL MBP-1 front, split over the 816 dates 2020-12-01..2024-02-29 (E.33_RETURN.md:136); search on 796 out-of-fold dates 2020-12-30..2024-02-29 (E.33c_RETURN.md:209-211) | yes, full | labels on ZM (fixed horizons 5, 15, 30, 60 min; triple barrier 15, 30); ZL as input (S2 and S5) | "(vii) No candidate; the test window stays sealed; no test data purchase." (E.33c_RETURN.md:205); section 3.8 "clean negative" (E.33c_RETURN.md:207) | ledger/trial_registrations.jsonl:10 (r009-E33, 300 ids); reports/E.33c_RETURN.md:205-211; reports/E.33_RETURN.md:136 |
| EX-19 | E.33 and E.33b (data and label integrity checks on ZL) | none (checks) | "in sigma_ZM, sigma_ZS and sigma_ZL on 20 of 20 dates" (E.33b_RETURN.md:67) | ZL MBP-1 front, 2020-12..2024-02; B3 check on 20 out-of-fold dates (2021-01-19..2024-02-15, E.33_RETURN.md section 3.2) | yes, full | none | checks agree on the 20 dates; residual items listed in E.33 section 3.2 | reports/E.33_RETURN.md:136, 160, 166; reports/E.33b_RETURN.md:66-67 |
| EX-20 | E.33 (guard dry check, not a read) | none | "REFUSED" dry check of a sealed ZL path and of a test-window date | refused path data/sealed/SOY_test_v1/.../ZL/ohlcv-1m_ZL_v_0_2010-07-01_2019-04-30_ext2010h.parquet.sealed (no read) | no (refused; sealed window dates) | n/a | refusal recorded | reports/E.33_RETURN.md:76-81 (log reports/stage_e33_briefs/guard_dry_check_start.txt) |
| EX-21 | acquisition (spend ledger, not a computation) | none | purchase commits and quote events for ZL (summary in spend_zl_summary.txt) | ZL ohlcv-1m (2010-07-01..2026-06-21), ZL mbp-1 (2020-11-30..2026-04-15), definitions ZM.FUT, ZS.FUT, ZL.FUT (2020-11-30..2024-02-29) | yes for the purchase windows listed in the summary (counts in the summary file) | n/a | n/a | ledger/databento_spend.jsonl (lines per group in reports/stage_e34_briefs/work/ExposureExtract-HaikuMed/spend_zl_summary.txt) |

## Row count per stage (Table 1)

| stage | rows |
|---|---|
| E.0 | 1 |
| E.8 | 1 |
| E.12 | 1 |
| E.14 / E.18 | 1 |
| E.17 | 1 |
| E.20 | 1 |
| E.21 | 1 |
| E.22 | 2 |
| E.23 | 1 |
| E.25 | 1 |
| E.28 | 1 |
| E.31 | 2 |
| E.32b | 3 |
| E.33 | 3 |
| acquisition (ledger) | 1 |
| Table 1 total | 21 |

## Table 2. Earlier ZL rows that do not overlap the discovery dates (checked, for completeness)

| stage | ZL use | dates | source |
|---|---|---|---|
| E.8 | K6 ZL research screen | 2025-04-01..2026-06 | X1_exposure.md:104, 107, 110 (EX-02) |
| E.16 | grain settlement-window calendar (no bars) | calendar only | reports/E.16_RETURN.md:208 |
| E.23 | K6 W_ext membership | W_ext 2010-07-01..2019-04-30 (no run on W_ext) | K6.md:38, 44 (EX-10) |
| E.24 | IDM from F1's frozen correlation without MZL (no new ZL read recorded) | not applicable | reports/E.24_RETURN.md:370, 453; X1_verify.md:70 (A9) |
| E.32 | sealing of ZL files (sealed window only; no discovery read) | ZS and ZL 2017-04..2020-11 | reports/E.32_RETURN.md:135-136 |

## Notes on the sealed window (facts, for the lead)

These rows also touch the sealed window 2017-05-01..2020-11-30 (dates as recorded in the cited sources; no judgment made):
- EX-03 (E.22 Part A, W_cf 2019-05-06..2024-02-29), EX-04 (E.22 Part B, modelled span 2010-07-01..2024-02-29), EX-05 (E.12 Gate 0, step2 from 2019-05-06), EX-06 (E.14 M1 fit, panel from 2019-05-06), EX-07 (E.17, ext2010h and step2 pools), EX-08 (E.20, 2019-05-06..2024-02-29), EX-09 (E.21, 2010-07..2024-02), EX-11 (E.25, E.22 trips from 2019-05-06), EX-12 (E.28 A0, opened files through 2023-10-31), EX-01 (E.0 metadata from 2019-05-01).
- The X1 seal section (reports/stage_e32_test_seal.md:123-131) lists the same stages.
- X1_verify.md:81 and X1_verify.md:201 record that E.14 M1 was fitted on a panel that includes the sealed-window dates 2019-05-06..2020-11-30 (X1_verify M1 gives this overlap explicitly).

## Corrections to X1 that touch these rows (from X1_verify.md, not re-verified here)

- A4 (X1_verify.md:65): the E.17 pool window and roots as run differ from the pre-registered plan; ZM is on the fallback window from 2019-05-06 (ZL is not a fallback root).
- A6 (X1_verify.md:67): the E.21 per-calendar-year table runs from 2010 (T3 only) to 2024.
- B2 (X1_verify.md:123): "the other 174 family-A tests" should read 183; family-A K6-signal tests are 9 (3 signals x 3 horizons) in X1 B2.
- B3 (X1_verify.md:130): E.17 H4 hold is the "entering at the open of the bar at the day-session open O_p + 1 minute" wording; X1's "settlement-window exit next day" is wrong.
- B7 and B8 (X1_verify.md:144-146): C1 and C1b are not soy-free (M1 fitted on the panel with ZS, ZL, ZM rows); family-A pooled tests are 192, so the soy-involving Gate 0 tests are 201 of 273 (9 family B plus 192 family A).

## Not finished or not verified

- E.8 rows (EX-02) are cited from X1 and X1_verify, not from the E.8 file itself beyond the lines quoted there.
- E.12 family-A pooling: which of the 28 exposures take ZL values for each K6-derived signal was not extracted (X1_exposure.md, section "Not finished or not verified", item on E.12 Gate 0 family-A pooling).
- Per-product unit counts for ZL in reports/stage_e17_runs/H1_result.json and the E.21 per-root JSON were not read directly; EX-07 and EX-09 rely on the verify report and the returns.
- reports/stage_e21_runs/per_root/ZL.json, reports/stage_e20_search/ CSVs, ~/.cache/propexp_e12_phase1/, ~/.cache/propexp_e14_c1/ and ~/.cache/propexp_e20_search/ (listed in X1_verify M4) were not opened; they are named only.
- stats31.json and stage_e31_volume.md were not opened (per X1 "Not finished").
- The 471 baseline trials are not itemized in the ledger; K6 and Gate 0 members are cited from X1 tables and the E.23 inventory, not trial by trial.
- The ledger spend-line counts are in reports/stage_e34_briefs/work/ExposureExtract-HaikuMed/spend_zl_summary.txt (11 groups). Ledger rows for ZL with event type "refused" (one line, 2025-08-01..2025-09-01) are outside the discovery window and are included in that summary only.
- Stage E.12 family-A K6 signal details, the E.14 M1 coefficient file and the E.33 feature code were not read; no values from them are in this table.
