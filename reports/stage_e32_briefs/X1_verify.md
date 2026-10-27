# X1 verification (Stage E.32, X1Verifier-OpusHigh)

Started 2026-10-27 00:18 PDT (from `date`). Object: reports/stage_e32_briefs/X1_exposure.md (written by
ExposureInventory-SonnetMed). Method: every row's cited source opened at the cited line, section or JSON field, by grep,
line ranges or a short field-printing script under reports/stage_e32_briefs/work/X1_verify/ (all scripts written by this
worker; outputs saved beside them as .txt). No market data file opened; no daily or bar-level series printed; no web
access; no key printed. Verdicts: CONFIRMED, CORRECTED (correct value, verbatim quote, reference), UNSOURCED (the source
does not say it). A row with several claims is CONFIRMED only when every claim checks; otherwise the row is CORRECTED and
the specific claim is named. "NOTE" marks a precision remark that does not change a value.

## Ledger script check (done first)

- X1's script reports/stage_e32_briefs/work/X1_exposure/X1_ledger_summary.py (40 lines) read in full: it prints only
  (dataset, schema, symbols, event), a count, min start date and max end date per group, and merged committed ranges.
  The Python variable named `key` is a group tuple, not a credential. No other field is printed. CONFIRMED safe.
- My own script work/X1_verify/X1_verify_ledger.py (output X1_verify_ledger.txt) and a second check X1_verify_ledger2.py
  (X1_verify_ledger2.txt): ledger 37,290 lines, 0 lines without a request object; field names only (no values) were
  listed. Every group line (31) and every merged committed range (9 symbol sets) is identical to
  work/X1_exposure/X1_ledger_summary.txt. A broad match (symbol containing ZM/ZS/ZL anywhere) adds 0 lines beyond X1's
  root-prefix filter.
- Additional fact X1 did not state: requests whose requested date range touches 2017-05-01..2020-11-30 (by date) are
  44 ZS, 44 ZL and 19 ZM ohlcv-1m commits (the sealed chunks), plus 1 commit each for mbo, mbp-1 ZS, mbp-1 ZL and
  definition (the first chunk, start 2020-11-30T22:00Z, i.e. at the window's UTC end) and 4 quote lines per schema
  starting 2020-10-31 (quotes only; no data delivered by a quote). Source: X1_verify_ledger.txt, "intersects" block.

## Section 0. Owned files (sealed set)

| X1 row | Claim | Verdict | Evidence |
|---|---|---|---|
| intro | registry 9 lines, N 538, baseline 471, +67 split r001 2, r002 5, r003 2, r004 3, r005 45, r006 4, r007 1, r008 5 | see section T (registry) | |
| 0-1 | ZS raw ohlcv-1m chunks 44, 2017-04-01_2017-05-01 .. 2020-11-01_2020-12-01 | CONFIRMED | docs/soy_test/SOY_TEST_MANIFEST.json expected_targets (114): script count ZS 44, first ('2017-04-01','2017-05-01'), last ('2020-11-01','2020-12-01') |
| 0-2 | ZL 44, same span | CONFIRMED | same: ZL 44, same first and last |
| 0-3 | ZM 19, 2019-05-01_2019-06-01 .. 2020-11-01_2020-12-01 | CONFIRMED | same: ZM 19, first ('2019-05-01','2019-06-01'), last ('2020-11-01','2020-12-01') |
| 0-4 | ext2010h stores ZS, ZL 2010-07-01..2019-04-30 | CONFIRMED | manifest: data/processed_hist/ext2010h/{ZL,ZS}/ohlcv-1m_Z?_v_0_2010-07-01_2019-04-30_ext2010h.parquet |
| 0-5 | step2 stores ZS, ZL, ZM 2019-05-06..2024-02-29 | CONFIRMED | manifest: data/processed_step2/{ZL,ZM,ZS}/ohlcv-1m_Z?_v_0_2019-05-06_2024-02-29_step2.parquet |
| 0-6 | E.22 microbook caches ZS, ZL | CONFIRMED | manifest: reports/stage_e22_microbook/cache/{ZL,ZS}.parquet |
| 0-7 | total 114 = 107 raw + 7 | CONFIRMED | 44+44+19 = 107; 2+3+2 = 7 |
| 0-8 | no ZM store before 2019-05 ("manifest ext2010 null", K6.md line 38) | CONFIRMED | K6.md line 38: "ZW and ZM: no W_ext store (manifest ext2010 null)." NOTE: "manifest" there is the store manifest, not the soy manifest |
| 0-9 | window under test 2017-05-01..2020-11-30 | CONFIRMED | manifest first_trade_date 2017-05-01, last_trade_date 2020-11-30, window_utc ['2017-04-30T21:00:00+00:00', '2020-11-30T22:00:00+00:00'] |
| L1 | ohlcv-1m ZS.v.0: 179 commits, merged 2010-07-01..2024-03-01; 2025-04-01..2026-06-21 | CONFIRMED | X1_verify_ledger.txt: "('ohlcv-1m', 'ZS.v.0') 179 [['2010-07-01', '2024-03-01'], ['2025-04-01', '2026-06-21']]" |
| L2 | ohlcv-1m ZL.v.0: 179 (+1 refused 2025-08-01..2025-09-01), same ranges | CONFIRMED | "GLBX.MDP3 \| ohlcv-1m \| ZL.v.0 \| refused \| n=1 \| min_start=2025-08-01 \| max_end=2025-09-01"; ZL merged ranges identical |
| L3 | ohlcv-1m ZM.v.0: 73, 2019-05-01..2024-03-01; 2025-04-01..2026-06-21 | CONFIRMED | "('ohlcv-1m', 'ZM.v.0') 73 [['2019-05-01', '2024-03-01'], ['2025-04-01', '2026-06-21']]" |
| L4 | mbo ZM.v.0, ZM.v.1: 39, 2020-11-30..2024-02-29 | CONFIRMED | "('mbo', 'ZM.v.0,ZM.v.1') 39 [['2020-11-30', '2024-02-29']]" (the T22:00Z start is X1's extra check; not re-printed by me, consistent with date 2020-11-30) |
| L5 | mbp-1 ZS.v.0: 44, 2020-11-30..2024-02-29 plus five single days | CONFIRMED | "('mbp-1', 'ZS.v.0') 44 [['2020-11-30', '2024-02-29'], ['2025-05-13', '2025-05-14'], ... ['2026-04-14', '2026-04-15']]" |
| L6 | mbp-1 ZL.v.0: 44, same | CONFIRMED | identical line for ZL.v.0 |
| L7 | mbp-1 ZM.v.0: 5, the five days | CONFIRMED | "('mbp-1', 'ZM.v.0') 5 [...]" five one-day ranges |
| L8 | definition ZL.FUT, ZM.FUT, ZS.FUT: 39, 2020-11-30..2024-02-29 | CONFIRMED | "('definition', 'ZL.FUT,ZM.FUT,ZS.FUT') 39 [['2020-11-30', '2024-02-29']]" |
| L9 | ohlcv-1d QM.FUT, ZM.FUT: 1, 2023-01-01..2026-10-22 | CONFIRMED | "('ohlcv-1d', 'QM.FUT,ZM.FUT') 1 [['2023-01-01', '2026-10-22']]" |
| L10 | 2020-11-30T22:00Z start equals the exclusive upper bound of WINDOW_UTC | CONFIRMED | reports/stage_e32_briefs/seal/soy_test_seal.py line 57: "WINDOW_UTC = (datetime(2017, 4, 30, 21, tzinfo=UTC), datetime(2020, 11, 30, 22, tzinfo=UTC))"; line 148 "return start < WINDOW_UTC[1] and end > WINDOW_UTC[0]" (exclusive) |
| L-omit | (not in X1) tbbo quotes ZS/ZL/ZM n=5 each, no commit | NOTE | X1's table lists committed requests only, as it says; quotes deliver no data |

## Registry (X1 intro lines 10-12)

| Claim | Verdict | Evidence |
|---|---|---|
| ledger/trial_registrations.jsonl 9 lines, N 538; line 1 baseline 471 "N after Stage E.12", source reports/E.12_RETURN.md:561; lines 2-9: r001-C1 2 (471->473), r002-E16 5 (473->478), r003-C1b 2 (478->480), r004-E20H6 3 (480->483), r005-E20S 45 (483->528), r006-E21 4 (528->532), r007-E22 1 (532->533), r008-E23 5 (533->538) | CONFIRMED | `uv run python -m screening.trial_registry status`: "N = 538 (9 lines)", e.g. "r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00"; line 1 fields: entry_id 'baseline', n_after 471, source 'reports/E.12_RETURN.md:561'. E.12_RETURN.md line 561: "- **New program N = 198 + 273 = 471.**" K6's 27 members are inside the 198: E.8_RETURN.md line 20 "**Program N = 167 + 27 =" (194) |

## Table A verdicts

| Row | Verdict | Evidence (verbatim where a value is at stake) |
|---|---|---|
| A1 E.12 step 2 build | CONFIRMED | reports/step2/bars_{ZS,ZL,ZM}.json (mtimes 2026-10-03 10:54:47, 11:09:37, 11:26:45 PDT): bars 1143451 / 1085571 / 975302; trade_dates 1214 each; raw_checks all 0 for the six named checks; bars_in_scheduled_closure 3 / 3 / 1; closure_bars ZS first two "2020-04-13 Mon 07:45", "2020-04-17 Fri 07:45"; ZM "2019-07-09 Tue 13:20"; degraded_utc_dates 8 each, first two '2020-02-27', '2020-02-28'; first/last trade date 2019-05-06 / 2024-02-29; input_files 58. Stage label: E.12_RETURN.md line 523 "### Task 6: bars, filter and Gate 0"; NOTE: the three files were written during the phase-1 buy window (E.12 line 517 "Buy (10:03-11:57)"), i.e. the soy stores were among the "15 built under v8" (line 524) |
| A2 E.12 Gate 0 | CONFIRMED | reports/stage_e12_gate0.json: verdict FAIL, n_a 192, n_b 81, n_holm_family 273, passing_pairs []; family-A n_dates 1068 on every test; soy family-B n_dates min 330, max 425 (script X1_verify_gate0.py). E.12 line 543 "Gate 0 ran **once**, 12:15:41-12:15:54"; lines 490, 491, 510 are the ZL, ZS, ZM rows of the purchase table; K6.md line 44 as cited. NOTE 1: the 330-425 range is for the nine soy pairs; over all 81 family-B pairs n_dates runs 128-425. NOTE 2 (missing detail): the same panel also fed the c/sigma admissibility filter, E.12 line 538 "c/sigma filter (tau 0.167, volatility only): 81 pairs, **81 admissible, 0 dropped**" (reports/stage_e12_c_sigma.json), and the Fable recomputation of all 273 tests (line 15) |
| A3 E.17 ext2010h build | CONFIRMED | reports/hist/bars_{ZS,ZL}_ext2010h.json (mtimes 2026-10-10 01:29:42 / 01:29:22): bars 1898620 / 1704606; trade_dates 2223 each; 2010-07-01..2019-04-30; non-zero raw checks only bars_in_scheduled_closure 177 / 100; degraded 14 each. E.17 lines 555-560 ("Eleven ext2010h stores built (3:15; 1.37 GB)"). NOTE: the stores' calendar_check reads 'passed': False (grains group) for both; X1 says only "calendar check" |
| A4 E.17 H1, H4, H5 | CORRECTED (three claims) | (a) "27 price paths (24 from 2010-07 plus RTY, TN, HE)" is the pre-registered plan (stage_e16_prereg_H1.md line 32: "the 27 price paths (24 from 2010-07-01; RTY from listing 2017-07-10; TN from listing 2016-01-11; HE from 2017-07-03)"), not what ran. As run: reports/stage_e17_runs/H1_result.json notes.window_starts gives 14 roots from '2010-07-01', TN '2016-01-01', RTY '2017-06-01', HE '2017-07-01' and 10 roots (YM 6A 6B 6C 6J 6S 6N HG ZW ZM) from '2019-05-06'; E.17_RETURN.md line 26: "Fallback window 2019-05-06..2024-02-29, not funded: YM, HG, 6S, 6J, 6A, 6B, 6N, ZM, ZW, 6C." (b) "per-root series not in the result files" and X1's open item "that ZM actually entered the pooled series ... rests on" the fallback file: the result files DO carry per-product counts (no per-root returns). H1_result.json per_product.ZM: 'eligible': 1075, 'traded': 1043, 'outside window': 2246; traded units by year ZM {'2019': 116, '2020': 207, ...}; ZS traded 3095, ZL 3065 (2017: 229 / 226; 2018: 231 / 221; 2019: 225 / 216; 2020: 225 / 226). H4: ZM traded 998, ZS 3001, ZL 2977. So ZM entered H1 and H4 directly. (c) H5 read no bars: E.17 line 562 "H5 in 0:03 (no bar read)"; H5_result.json components = the H1-H4 result files. Run times (result files): H1 2026-10-10 01:31:43-01:34:41, H4 01:36:28-01:39:22, H5 01:39:39. Other claims (stores, manifest 27 stores with ZM ext2010 null, fallback rule A5, registration r002-E16) CONFIRMED |
| A5 E.20 Part C | CONFIRMED | E.20_RETURN.md lines 308-315: "Registered 17:43:59 as r005-E20S (N 483 -> 528), before any panel or fit; run 17:44:15-17:52:20"; "Panel: 57,775 decision rows (13,587 at t4) on 17 vehicles over 1,248 training-calendar dates"; "36 features (34 frozen + rod_ret, rod_absratio)"; "Closure bars counted and kept: 30 in all (NQ 7, RTY 6, LE 3, ZS 3, ZL 3, ...)"; "Nested CPCV: 15 outer splits, 4 inner folds, 45 configurations"; no backward read (lines 344-345). The 17 vehicles (line 341-342 list) exclude ZM. NOTE: E.20 lines 341-342: "the other eight vehicles (NG, TN, ZB, UB, ZS, ZL, HE, LE) never traded" out of sample; ZS and ZL rows still entered every fit |
| A6 E.21 | CORRECTED (one claim) | "yearly pooled table (2016-2024 rows)" -> the per-calendar-year table runs 2010 (T3 only) and 2011-2024: E.21_RETURN.md line 355 "### Per calendar year (base case)", line 359 "\| 2010 \|  \|  \|  \|  \| 44 \| 2.80 \|", line 373 "\| 2024 \| 43 \| 3.22 \|". Everything else CONFIRMED: run 03:04-04:40 (line 3), 17 roots, T1-T4, ZL/ZS rows lines 385, 394, 412, 416; ZM "never read by E.21" (stage_e22_microbook.md line 34) |
| A7 E.22 Part A K6 | CONFIRMED | E.22_RETURN.md line 262 "K6 marker; run; verdict \| 18:50:00; -18:59:17; 18:59:25"; line 286 "DSR at N = 533"; table lines 366-395; soy days 1028-1136. NOTE: VerdictVerifier-K6 (Fable) recomputed the K6 verdict from member records and trip lists, "No bar store was opened" (stage_e22_verify_k6.md line 14); the E.22 dry run counted "crushgap 1028" supply dates (stage_e22_list_review.md line 190). Both same span, no new trial |
| A8 E.22 Part B | CONFIRMED | stage_e22_microbook.md line 25 "MZS \| Soybeans \| ZS \| ... \| 2010-07-01..2024-02-29 \| modelled"; lines 240-241 MZS/MZL "2011-07-11"; line 122 MZS correlation row; data counters "MZS \| ZS \| 3402" and "MZL \| ZL \| 3400"; MZM line 34 "not modelled". Run 2026-10-16T01:34:27-01:35:04 (line 5) |
| A9 E.24 | CONFIRMED | E.24_RETURN.md line 370 "IDM \| 2.3293791420997985: F1's frozen correlation without MZL"; line 453. NOTE: E.24's E22-F2 draft (not registered; line 20) lists SOYB and reads ETF daily bars only "from 2024-03-01" (line 393) |
| A10 E.28 A0 | CONFIRMED | A0_contract_stats.md lines 12-14 (files ending on or before 2023-11-01 only); Table 3 lines 202, 203, 205: ZL 160, ZM 54, ZS 160 files opened; C4 method lines 50-56 |
| A10 value lines (3) | CONFIRMED | lines 151, 152, 154 match X1 lines 66-68 character for character in every number |
| A11 E.26 | CONFIRMED | E.26_RETURN.md lines 4 (2026-10-21) and 9-12 ("Every file's sha256, mode, owner and mtime were verified at the destination") |
| A12 E.32 Part 0 | CONFIRMED | stage_e32_STATE.md line 15-23 ("Seal run 22:54:51-22:55:11: 114 files sealed"); soy_test_seal.py docstring line 27 "no script ever reads in-window rows to split it" |

### Completeness list ("no soy data in the sealed window")

| Row | Verdict | Evidence |
|---|---|---|
| E.1, E.2a, E.2b, E.8 (2025-04..2026-06 data) | CONFIRMED | stage_e1_purchase.md line 15 "Allowed dates 2025-04-01..2026-06-21 (UTC)"; E.2a lines 380-382 ZL/ZM/ZS "2025-04-01 \| 2026-06-18"; E.8 line 205 "Windows 264-287 dates from 2025-04-01" |
| E.17 C1, E.18 C1b | CORRECTED | Their TEST window holds only NG NQ ZN 6E GC ZC (stage_e18_c1b_result.json world keys), but their model M1 was FITTED on soy rows in the sealed window: stage_e14_prereg_C1.md lines 37-38 "Training (already read, used only to fit the frozen model and reproduce q): the E.12 phase-1 panel, 2019-05-06..2024-02-29, all 27 Gate 0 products"; stage_e14_c1_model.md line 33 "M1 ... one ridge per horizon, lambda 0.1, on E.12's whole training panel", rows h60 67,797 and hF 64,695 ("81 admissible pairs, pooled"). See missing row M1 |
| E.20 H6 | CONFIRMED | E.20 line 7 "H6 (... on NQ at MNQ cost, 2020-06-01..2024-02-29)" |
| E.20 dry check step 6 | CONFIRMED | stage_e20_dry_check_step6.md line 1 "(synthetic sentinel frames, no store)" |
| E.23 | CONFIRMED | E.23 lines 354-356, 388 ("K6-crushgap-01 \| M10 \| ... dropped (ZM not owned on W_ext)"), 403-407 (ZF ZN ZB NQ); E.23 prereg line 78-79 lists ZL, ZS among W_ext-readable roots but no E23 trial uses them |
| E.13 | CONFIRMED | progress.md line 3453 "(research and scoping; no market data, no purchase)"; stage_e13_trend_carry.md lines 215 (header "Price 2026-10-02 (T-22) \| Ann. vol % (T-22)", external sources), 250-252 |
| E.16 Part A | CONFIRMED | progress.md line 3662 "(no Databento, no bar read, nothing registered)" |
| E.29 | CONFIRMED | E.29_RETURN.md line 113 "owned one-minute bars of CL, ZM, GC and NQ dated 2022-10-01 to 2023-11-01" |
| E.31 | CONFIRMED | E.31 lines 25-28, 121 ("No ZM, ZS or ZL record dated on or after 2024-03-01 was quoted, bought or read"), 128-142; ledger: first mbo/mbp-1/definition commit start 2020-11-30T22:00:00Z (X1_verify_ledger3.txt), equal to WINDOW_UTC's exclusive end; 2020-11 was quoted only (start 2020-10-31T21:00:00Z, "quote" lines), E.31 line 297 "2020-11 would make 124.340118" |

## Table B verdicts

### B1 (15 rows) and its notes

All 15 rows checked cell by cell against E.8_RETURN.md lines 217-241 (trips, days, mean ticks/day, daily t, tier),
E.22_RETURN.md lines 371-395 (tier, status, days, trips, theta_hat, UCB95, p_upper) and K6.md lines 10-34 (decision,
hold). Every number matches.

| Row | Verdict | Spot quote |
|---|---|---|
| K6-cp1-01 ZS | CONFIRMED | E.8 217 "\| 3 \| K6-cp1-01 ZS \| run \| 280 \| 285 \| -2.5301 \| -5.756"; E.22 371 "\| 1136 \| 1109 \| -1.7015 \| -1.1732 \| ... \| +1.0000"; K6.md 10 "fill 12:45 to exit fill nominally 13:14 (about 29 minutes)" |
| K6-cp1-01 ZM | CONFIRMED | E.8 218 "270 \| 278 \| -1.4134 \| -3.820"; E.22 372 "1106 \| 1075 \| -1.2097 \| -0.6902 ... +0.9999" |
| K6-cp1-01 ZL | CONFIRMED | E.8 219 "271 \| 287 \| -1.1361 \| -1.235"; E.22 373 "1129 \| 1076 \| -2.4878 \| -1.6296 ... +1.0000" |
| K6-cp2-01 ZS | CONFIRMED | E.8 224 "272 \| 285 \| -1.9418 \| -1.803"; E.22 378 "1136 \| 1077 \| -1.7164 \| -0.4434 ... +0.9845"; K6.md 17 "75 bars after the entry decision bar, or F (13:18) if earlier" |
| K6-cp2-01 ZM | CONFIRMED | E.8 225 "262 \| 278 \| -3.2959 \| -3.458"; E.22 379 "1106 \| 1033 \| -1.3235 \| -0.1204 ... +0.9666" |
| K6-cp2-01 ZL | CONFIRMED | E.8 226 "276 \| 287 \| -0.5481 \| -0.262"; E.22 380 "1129 \| 1081 \| -2.0867 \| -0.1249 ... +0.9531" |
| K6-cp3-01 ZS | CONFIRMED | E.8 231 "136 \| 285 \| -0.5618 \| -0.475"; E.22 385 "1136 \| 511 \| -1.9350 \| -0.3332 ... +0.9770" |
| K6-cp3-01 ZM | CONFIRMED | E.8 232 "119 \| 278 \| +0.4725 \| 0.495"; E.22 386 "1106 \| 515 \| -1.4151 \| +0.0896 ... +0.9452" |
| K6-cp3-01 ZL | CONFIRMED | E.8 233 "143 \| 287 \| -1.9353 \| -0.723"; E.22 387 "1129 \| 482 \| -1.1039 \| +1.3205 ... +0.7683" |
| K6-crushgap-01 ZS | CONFIRMED | E.8 236 "137 \| 264 \| -3.4807 \| -2.708"; E.22 390 "1028 \| 516 \| -2.5773 \| -0.6257 ... +0.9822"; K6.json trigger_event "G(d) = GPM_open(d) - GPM_close(d-1) <= -0.02 or >= +0.02 USD/bu, GPM = 0.022 P_ZM + 11 P_ZL - P_ZS" |
| K6-wasdepre-01 ZS | CONFIRMED | E.8 240 "13 \| 285 \| -0.7410 \| -1.288"; E.22 394 "1136 \| 57 \| -0.4458 \| +0.1724 ... +0.8782"; K6.md 33 "fill 10:30 to exit fill 11:15 (45 minutes, through the 11:00 CT release)" |
| K6-wasdepre-01 ZC | CONFIRMED | E.8 239; E.22 393 "1130 \| 55 \| -0.2534 \| +0.0387 ... +0.9264" |
| K6-wasdepost-01 ZC | CONFIRMED | E.8 241; E.22 395 "1130 \| 54 \| -0.0691 \| +0.1482 ... +0.7068" |
| K6-limitcont-01 HE | CONFIRMED | E.8 237 "1 \| 273 \| +0.1869 \| 1.002 ... A"; E.22 391 "A \| null by inactivity \| 1104 \| 10 \| +0.0495 \| +0.3869 ... +0.4088" |
| K6-limitcont-01 LE | CONFIRMED | E.8 238 "0 \| 266 \| +0.0000 \| undefined"; E.22 392 "inconclusive \| 1109 \| 0 \| +0.0000 \| +0.0000 ... +1.0000" |
| B1 notes (freeze sha a6f8b497, 27 members; 12 non-listed members on ZC ZW HE LE; edge chain lines 399-400; E.8 Tier A limitcont HE only) | CONFIRMED | K6.md line 3; E.22 line 400 "Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K6-limitcont-01 HE p 0.4088 vs 0.00556; DSR variance 0.0035193 over 27 series; PBO +0.5571 over 27 series."; K6.md line 45 |

### B2 (18 itemized rows plus the not-itemized statement)

| Row | Verdict | Evidence |
|---|---|---|
| 9 family-B rows (gate0B_Z{L,M,S}_{h60,h120,hF}) | CONFIRMED (9) | X1_verify_gate0.txt prints every field from reports/stage_e12_gate0.json tests[]; all 13 columns identical to X1 lines 129-137 to the last printed digit |
| 9 family-A K6-signal rows | CONFIRMED (9) | same script, X1 lines 145-153 identical |
| "the other 174 family-A tests" (X1 lines 157-158) | CORRECTED | 192 - 9 = 183, not 174. Script: "A non-k6 count 183"; 64 signals x 3 horizons = 192 ("A signals 64") |

### B3 (3 rows plus notes)

| Row | Verdict | Evidence |
|---|---|---|
| E16-H1 | CONFIRMED | E.17_RETURN.md line 18 "\| H1 \| -0.161 \| -20.0 \| 1.0 \| 3,380 \|"; hold: stage_e16_prereg_H1.md lines 27-28 "Entry: open of bar(p,d,S_p-30), direction s. Exit: open of bar(p,d,S_p)". Data span: see the A4 correction (10 roots incl. ZM from 2019-05-06) |
| E16-H4 | CORRECTED (hold) | X1 "settlement-window exit next day (per prereg H4)" is wrong. stage_e16_prereg_H4.md lines 27-28: "m = 0: no trade. Direction -sign(m). Entry: open of bar(p,d,O_p+1); exit: open of bar(p,d,S_p-31)." and lines 16-17 "entering at the open of the bar at the day-session open O_p + 1 minute on d, exiting at the open of the bar at S_p - 31 on d (so H4 never overlaps H1's window)": an intraday hold on the day after the H1 move, from the day-session open +1 min to 31 min before settlement. Statistics CONFIRMED (E.17 line 21 "\| H4 \| -0.048 \| -6.7 \| 1.0 \| 3,381 \|") |
| E16-H5 | CONFIRMED | E.17 line 22 "\| H5 \| -0.149 \| -1.46 \| 0.93 \| 3,400 \|". NOTE: no bar read (A4 (c)) |
| H2, H3 values, no soy roots | CONFIRMED | E.17 lines 19-20 "\| H2 \| +0.344 \| +1.52 \| 0.068 \| 56 \|", "\| H3 \| -0.015 \| -0.26 \| 0.60 \| 405 \|"; prereg titles "month-end NQ/ZN rebalancing pair", "Treasury auction cycle" |

### B4-B8

| Row | Verdict | Evidence |
|---|---|---|
| B4 E20S-01..45 | CONFIRMED | E.20 lines 323-333: "-1.334 \| >= 2.0", "PBO ... 0.596", "-0.826", "ridge_l0.1_k2_h60 (E20-S13)", "DSR at N = 528: 0.00001", "best: E20-S13 ridge_l0.1_k2_h60, -0.33"; line 29 "run on 17 roots with late-session features" |
| B5 E21-T1 | CONFIRMED | E.21 line 333 "\| T1 \| 3205 \| ... \| 1.776 \| ... \| 0.0419 \| 0.498 \| [-0.063, 1.053]"; fills 4,081 (line 13); ZL line 385, ZS line 394 identical |
| B5 E21-T2 | CONFIRMED | line 334 "1.557 ... 0.0637 ... 0.436 \| [-0.109, 0.982]"; ZL line 412, ZS line 416 identical |
| B5 E21-T3 | CONFIRMED | line 15 "\| T3 turn of month \| 0.15 [-0.40, 0.71] \| 0.53 \| 0.30 \| 454"; hold line 249 "days -1, +1, +2, +3, close to close" |
| B5 E21-T4 | CONFIRMED | line 16 "\| T4 combined book \| 0.12 [-0.37, 0.60] \| 0.43 \| 0.34" |
| B6 E22-F1 | CONFIRMED | registry line 8 note "E22-F1 forward test of the micro trend book at $25,000 (simple rounding; 36 months from the first ledger record after the user approves a daily settlement source; p <= 0.05 one-sided NW lag 10 and net Sharpe >= 0.3)" |
| B7 non-soy trials (12) | CORRECTED | E23 x5, E20H6 x3 CONFIRMED. C1-T1, C1-T2, C1b-T1, C1b-T2 are not free of soy: tested on NG only, but with model M1 fitted on the E.12 panel that includes ZS, ZL and ZM rows 2019-05-06..2024-02-29 (missing row M1 below) |
| B8 totals | CORRECTED | "B2 9 + 3 (family A, K6 signals)" -> 9 family-A K6-signal tests (3 signals x 3 horizons; X1's own B2 lists 9). Moreover every one of the 192 family-A tests is pooled over the 28 exposures, which include ZS, ZL and ZM, so the soy-involving Gate 0 tests are 9 (B) + 192 (A) = 201 of 273. Add C1-T1/T2 and C1b-T1/T2 (4 registered trials, through M1's training rows) |

## Table C verdicts

| Row | Verdict | Evidence |
|---|---|---|
| Scope line (stats31.md 1,595 lines, generated 2026-10-23 12:46:58 PDT, 816 dates 2020-12-01..2024-02-29, bootstrap) | CONFIRMED | stats31.md line 3 "Generated 2026-10-23 12:46:58 PDT by stats31.py from ... measure31: 816 trade dates with a done marker (2020-12-01 to 2024-02-29)"; wc 1595 |
| C1 Verdict 5-19, 4 tests + 2 info | CONFIRMED | lines 11-19 as quoted by X1 ("lower bound -1.2524; mean -1.2339 [-1.2524, -1.2142]", "111.5681; interval 111.5681 [109.5533, 113.4611]", "lower bound -1.5164; mean -1.4979 [-1.5164, -1.4782]") |
| C1 Primary population 21-80, 55 rows | CONFIRMED | row counter X1_verify_stats31_rows.txt "21 ... data_rows 55" |
| C1 Net results 81-102, 15 rows, fees | CONFIRMED | 15 rows; lines 87-91 "Topstep (0.264)", "Lucid (0.280)", "Bulenox (0.286)", "MFFU (0.306)", "Tradeify (0.460)" |
| C1 All cells 103-824, 12 headings at the listed lines, 55 each | CONFIRMED | headings at 105, 165, ..., 765, each 55 rows. NOTE: the source heading is "## All cells (model x symbol x session; pooled, buy, sell)"; X1's heading text is its own paraphrase |
| C1 2023-11-01 blocks 825-1070, 4 x 55, 82 dates | CONFIRMED | line 827 "82 trade dates; intervals resample trade dates on or after 2023-11-01 only." |
| C1 Splits 1071-1554, 12 x 35 | CONFIRMED | headings 1075 ... 1515, each 35 rows; families and buckets as X1 lists (line 1073 definitions) |
| C1 Loop 1555-1564, 3 rows | CONFIRMED | "207.662 [204.612, 210.449]", "215.137 [212.001, 218.005]", "111.568 [109.553, 113.461]"; durations 80.75, 77.94, 150.02 |
| C1 Implied liquidity 1565-1575, 4 rows | CONFIRMED | "7823934 / 19702332 \| 0.0552 ... \| 0.0360 ... \| 0.1180 ... \| 0.2600 ... \| 0.0905" |
| C1 Exclusions 1576-1582, 2 rows | CONFIRMED | "ZM.v.0 \| 816 \| 764 \| 52 \| after_roll_day: 20; cme_holiday_or_early_close: 4; roll_day: 23; scheduled_late_open: 5 \| 414363576"; "ZM.v.1 \| 816 \| 684 \| 132" |
| C1 Consistency checks 1583-1595, "9" rows | CORRECTED | 8 data rows (lines 1587-1594: placement_rows_on_dates_not_included ... fills_with_nan_c_half), all 0 or empty |
| C1 absence statement (grep "month", "by session", "hour") | CONFIRMED | grep -ci on stats31.md: month 0, by session 0, hour 0 |
| C2 35 rows (stats31 1395-1434) | CONFIRMED (35) | X1_verify_c2.py compares every cell: "rows identical 35 rows differing 0" |
| C3 verbatim E.31 lines 183-206 | CONFIRMED | diff of X1 lines 287-310 against E.31_RETURN.md lines 183-206: identical |
| C4 Volume check | CONFIRMED | E.31 line 137 "\| ZM \| 78,281.5 \| 79,512.0 \| 5,000 \| PASS \|"; line 10 "2025-10-01 to 2026-09-30"; lines 139-140 "(about 0.08)" |
| C4 USDA calendar | CONFIRMED | E.31 lines 304-305 "88 FAS rows are rule-derived or uncertain; NOPA is not USDA and is not used; three 2022 FAS outage weeks are skipped"; lines 226-227 |
| C4 Pilot spec definitions | CONFIRMED | stats31.md line 1073 "ZS / ZL moves: sign of s x d, d = mid(t_f) - mid(t_f - L) in that contract's ticks" |
| C4 Kill rule | CONFIRMED | E.31 lines 18-21 "**-1.234 ticks**, 95% day-block interval [-1.252, -1.214]", "gross -0.970 [-0.988, -0.950]" |
| C4 Data on disk | CONFIRMED | E.31 lines 25-28 "39 whole months, 2020-12 to 2024-02 ... 156 files, 24.2 GB ... 816 trade dates measured; 764 DAY dates usable"; lines 336-337 |
| C4 Reviewer deviation | CONFIRMED | E.31 lines 29-33 "ran on **claude-sonnet-5-5** at xhigh ... checked again by an Opus 5.5 xhigh fresh-context worker: CONFIRMED" |
| Appendix X1_tableC_appendix.md (982 lines) | CONFIRMED | 20% systematic sample: every 5th table data row in appendix order, 166 of 829 data rows, appendix lines 11, 16, 21, ..., 971 (full list with their stats31 line in work/X1_verify/X1_verify_appendix.txt); 0 mismatches. A full check of all 954 mapped lines also gives 0 mismatches. NOTE: the appendix copies 8 of the 16 all-cells blocks (all four (c) blocks, (a) and (b) ZM.v.0 DAY), all 12 split blocks, the loop, implied-liquidity and exclusions blocks; it omits the verdict block, the other eight all-cells blocks, the four 2023-11-01 blocks and the consistency checks (all in stats31.md itself) |
| X1 "Not finished" item 1 (ZM entry into E.17 pooled series unverified) | RESOLVED | see A4 (b): H1/H4 result files record ZM traded 1,043 / 998 units |
| X1 "Not finished" items 2-6 | CONFIRMED as open | not needed for the exposure statement except item 3 (hold of H4, resolved in B3) |

## (2) Completeness sweep

### Searches run (terms T = `\bZ[MSL]\b|[Ss]oy|[Cc]rush|WASDE|USDA|NOPA`; dates D = `201[7-9]|2020`; hit = a line with T and D)

| Search | Hits |
|---|---|
| progress.md: lines with T / lines with T and D | 28 / 0 |
| docs/STAGES.md | 3 / 1 (line 232, E.31 2020-12..2024-02: known) |
| docs/DECISIONS.md | 19 / 3 (lines 1046, 1062, 1064: V51 text about the E.31 data and this seal: known) |
| reports/*.md (360 files): files with T / files with T and D | 128 / 31 (list: work/X1_verify/X1_verify_sweep_reports.txt) |
| reports/stage_e*_briefs/**/*.md excluding stage_e32_briefs (896 files incl. E.32): files with T and D | 52 (list: work/X1_verify/X1_verify_sweep_briefs.txt); file names with soy terms: 37 |
| reports/stage_e23_briefs/inventory/ | K6.json 10, K6.md 2, CDE.json 2 (E16-H1, E16-H4 rows), all other K and H6 files 0 |
| trial registry (status and JSON fields) | 9 lines; soy appears only in r002's note (ZM on the fallback list) |
| store-set terms without soy names (`28 exposures`, `27 price paths`, `17 roots`, `W_cf`, `step 2 store`, `processed_step2`, `ext2010h`, `training panel`, `E.12 panel`) in the 21 stage returns X1 did not cite | E.2b 11, E.5 6, E.16 4, E.25 3, E.3/E.4/E.6/E.9/E.11/E.13 1 each; read: all are build code, ls output, plan text or NQ-only (E.25 line 221) except the E.14 hit found through the C1 prereg |

Each hit outside X1 was opened. Most are literature windows (stage_e2a_source_windows, stage_e0_research_K6,
stage_e10_research_commodity, stage_e13_info_sources, M10_USDA pages), calendars and settlement tables
(stage_e16_prereg_common lines 116-118, stage_e2a_calendar_sources*), E.20 Part A product readers ("No data store was
opened; no bar was read", product_ZS.md line 5), or further detail inside stages X1 already lists (E.21 prereg and
review roll-splice diagnostics, E.17 review, E.22 list review and verifier). Those are folded into the NOTES of
A4-A7 above. The hits that are new exposure:

### Missing rows to add

| # | Stage (date, time) | File | Span | What was computed | Trials | Reference |
|---|---|---|---|---|---|---|
| M1 | E.14 Task 5 (2026-10-05 03:29:54-03:29:57 PDT) | E.12 persisted state copy (~/.cache/propexp_e14_c1/e12_state_copy; the E.12 phase-1 panel built from the step 2 stores) | 2019-05-06..2024-02-29, all 27 Gate 0 products incl. ZS, ZL, ZM (overlap 2019-05-06..2020-11-30) | M1: one ridge per horizon (h60, hF), lambda 0.1, fitted once on E.12's whole training panel, 67,797 rows (h60) and 64,695 (hF), 150 features; plus the q reproduction from E.12's out-of-fold predictions (NG rows only). M1 was then applied to NG 2010-2019 by C1 (E.17, stopped at C10, no statistic) and C1b (E.18, FAIL) | C1-T1, C1-T2 (r001-C1, N 471 -> 473); C1b-T1, C1b-T2 (r003-C1b, N 478 -> 480) | stage_e14_prereg_C1.md lines 37-38 ("the E.12 phase-1 panel, 2019-05-06..2024-02-29, all 27 Gate 0 products") and 52-55; stage_e14_c1_model.md lines 1-5, 33-38; E.14_RETURN.md line 171 "\| C1 \| M1 fit and q (before any 2010-2019 byte; none exists) \| 03:29:54-03:29:57"; stage_e18_prereg_C1b.md lines 48-55 (reuses M1) |
| M2 | E.25 NM1 and NM2 (2026-10-18, NM1 06:2x PDT; NM2 11:16-12:0x PDT) | reports/stage_e22_confirm_k6/K6_*_Z{S,L,M}*_confirmation_trips.json (E.22 trip records); stage_e12_gate0.json | 2019-05-06..2024-02-29 | NEW derived statistics: mean gross per trade and iid gross t for the 11 soy K6 members' E.22 confirmation trips (e.g. K6-cp1-01 ZM 1,075 trips, +0.3665 ticks, gross t 1.138; K6-cp2-01 ZL 1,081, +0.0046, 0.004; K6-cp2-01 ZM 1,033, +0.1985, 0.256; K6-crushgap-01 ZS 516, -3.6531, -1.503; K6-wasdepre-01 ZS 57, -7.3333, -0.969), plus the 9 Gate 0 soy family-B rows copied; NM2 then classified each by failure cause (cost versus non-cost) | none (research triage) | NM1_nearmiss_table.md lines 3-7 ("Derived figures (marked d) are computed from recorded per-trip gross_cents in the trips files"), 106, 109, 110; NM1_nearmiss_table.json rows (11 soy confirmation rows, field window_read first '2019-05-06'); NM2_exec_triage.md lines 1-8, 146-153 |
| M3 | E.0 quotes (2026-09-23) | Databento free metadata endpoints | ohlcv-1m 2019-05-01..2026-06-21 | quote metadata only: record counts ZS 1,675,690, ZM 1,443,823, ZL 1,619,993 over "86/86" months (bar counts, no price) | none | stage_e0_quotes.md lines 3-5 ("Quotes only ... nothing was bought"), 71-73 |
| M4 | E.0-E.31, derived files on disk (not a stage) | trip files and units files beside the reports; ML caches | in-window soy content | per-trip and per-unit records and fitted states that hold window information and are NOT among the 114 sealed files: reports/stage_e22_confirm_k6/ (soy confirmation and trips JSON), reports/stage_e17_runs/H1_units.jsonl and H4_units.jsonl (H1: 1,063 lines contain "ZM", by grep count only), reports/stage_e21_runs/per_root/ZS.json and ZL.json, reports/stage_e20_search/ (path and config daily CSVs), ~/.cache/propexp_e12_phase1/, ~/.cache/propexp_e14_c1/, ~/.cache/propexp_e20_search/. Names listed only; no content opened | n/a | `ls` of those paths (this worker, 00:30 PDT) |

Not missing (checked): E.15 (C1 stopped before registration, nothing bought; E.15_RETURN.md has 0 soy hits), E.19 (0 soy
hits; prop economics), E.24 (A9), E.16 Part A (power priors, "priors only, no bars": CDE.json E16-H1 stages_read),
E.20 Part A product readers ZS/ZL (no bar read), E.22 power re-runs (research window 2025-04..2026-06, K6.json
stages_read), E.28 ranking (uses A0's 2022-11..2023-10 standard window), E.29 (2022-10..2023-11).

## (3) Seal document section 4 (reports/stage_e32_test_seal.md lines 103-142): corrections needed

Not edited here; the lead applies them.

1. Line 104-105, source sentence. Old: "Source: reports/stage_e32_briefs/X1_exposure.md (ExposureInventory-SonnetMed, pure
   extraction ...)". New: add "re-verified row by row by X1Verifier-OpusHigh (reports/stage_e32_briefs/X1_verify.md),
   with the corrections below". Source: this file.
2. Lines 109-111, "Only one-minute bars (and stores and caches built from them) ...". Old: "Only one-minute bars (and
   stores and caches built from them), for ZS and ZL from 2017-05 ... and for ZM, ZS and ZL from 2019-05-06 (through the
   step 2 store)." New: keep, and add: "Records derived from them also remain unsealed on disk: E.22 K6 trip files, the
   E.17 H1/H4 units files, E.21 per-root results, the E.20 search outputs and the E.12/E.14/E.20 ML caches (M4)."
   Source: M4. The order-book sentence is CONFIRMED: first mbo/mbp-1/definition commit start 2020-11-30T22:00:00Z
   (X1_verify_ledger3.txt), equal to WINDOW_UTC's exclusive end (soy_test_seal.py line 57); 2020-11 was quoted, never bought.
3. E.12 row, column "What was computed". Old: "store build and raw checks; Gate 0: 273 IC and mean-ticks tests on 28
   exposures, including three K6-derived signals ...". New: "store build and raw checks; c/sigma admissibility filter
   (81 pairs); Gate 0: 273 tests, of which 201 use soy rows (all 192 family-A pooled tests, including the three
   K6-derived signals x 3 horizons, and the 9 ZS/ZL/ZM family-B pairs); ridge models fitted out of fold on the panel".
   Sources: E.12_RETURN.md line 538; X1_verify_gate0.txt; NM2 line 146 "(ridge model sign, top 20% \|z\|)".
4. New row after E.12. "E.14 \| E.12 panel (step 2, 2019-05-06..) \| M1: one ridge per horizon (h60, hF) fitted once
   on the whole panel (27 products incl. ZS, ZL, ZM; 67,797 and 64,695 rows), later applied to NG 2010-2019 \| C1-T1/T2,
   C1b-T1/T2 \| C1 stopped at C10 (no statistic); C1b FAIL". Source: M1.
5. E.17 row. Old: "ext2010h (ZS, ZL 2010-07..2019-04) and step 2 \| store build; H1 settlement-window momentum, H4
   next-day reversal, H5 combination, pooled over 27 price paths". New: "ext2010h (ZS, ZL 2010-07..2019-04) and step 2
   (ZS, ZL; ZM on the fallback window from 2019-05-06) \| store build; H1 settlement-window momentum (S_p-30 to S_p), H4
   intraday reversal of the prior day's H1 move (O_p+1 to S_p-31), pooled over 27 price paths (14 from 2010-07, 10
   incl. ZM from 2019-05-06, TN, RTY, HE later); ZM traded 1,043 units in H1 and 998 in H4; H5 combines the H1-H4
   result files (no bar read)". Sources: A4 (a)-(c), B3 H4.
6. E.20 row. Old: "ML search ... nested CPCV". New: append "; ZS and ZL never traded out of sample". Source: E.20_RETURN.md
   lines 341-342.
7. E.22 Part A row. Old: "CP1 and CP2 momentum into the close, CP3 prior-close location at the 08:30 open". New: "CP1
   momentum into the close (12:45 to 13:14), CP2 opening-range breakout (08:45..13:14, 75-bar hold), CP3 prior-close
   location at the 08:30 open". Source: K6.md lines 10, 17, 24; K6.json trigger_event for K6-cp2-01 "first bar in
   [08:45, C) of CT date d whose close is >= OR_high + 4 ticks or <= OR_low - 4 ticks, OR = [08:30, 08:45)".
   The outcome cell "all null (theta_hat negative on every soy member)" is CONFIRMED (11 of 11 negative, E.22 lines 371-394).
8. New row after E.22. "E.25 \| E.22 K6 trip files (2019-05-06..2024-02-29) \| derived gross per trade and gross t for
   the 11 soy K6 members; execution triage \| none \| descriptive (e.g. K6-cp1-01 ZM +0.37 ticks gross, t 1.14)".
   Source: M2.
9. "What this means" paragraph. Old: "... WASDE pre-release drift (close to a post-USDA family), and an ML search on
   late-session bar features." New: "... and two pooled ML passes on bar features (the E.12 Gate 0 ridge with its M1
   refit, 64 signals; the E.20 search, 36 late-session features)." Source: M1, A2, A5.
10. "Disclosure" paragraph. Old: "X1 did not open the bar-level units file." New: keep, and add: "X1's re-verification
    read only per-product exclusion and traded-unit counts from the H1 and H4 result files (no series)". Source: this
    file, A4 (b).

## (4) Counts and fitness

| Part | Rows checked | CONFIRMED | CORRECTED | UNSOURCED |
|---|---|---|---|---|
| Registry statement | 1 | 1 | 0 | 0 |
| Section 0 (9 file rows, 10 ledger rows) | 19 | 19 | 0 | 0 |
| Table A (A1-A12) | 12 | 10 | 2 (A4, A6) | 0 |
| A10 value lines | 3 | 3 | 0 | 0 |
| Table A completeness list | 9 | 8 | 1 (C1/C1b) | 0 |
| B1 (15 rows + notes row) | 16 | 16 | 0 | 0 |
| B2 (18 rows + count statement) | 19 | 18 | 1 (174 -> 183) | 0 |
| B3 (3 rows + H2/H3 note) | 4 | 3 | 1 (H4 hold) | 0 |
| B4-B8 (B4 1, B5 4, B6 1, B7 1, B8 1) | 8 | 6 | 2 (B7, B8) | 0 |
| C1 (scope + 10 sections + absence statement) | 12 | 11 | 1 (consistency rows 8) | 0 |
| C2 rows | 35 | 35 | 0 | 0 |
| C3 block | 1 | 1 | 0 | 0 |
| C4 rows | 6 | 6 | 0 | 0 |
| Appendix (20% systematic sample) | 166 | 166 | 0 | 0 |
| **Total** | **311** | **303** | **8** | **0** |

Missing rows added: 4 (M1 E.14 M1 fit with C1/C1b; M2 E.25 derived statistics; M3 E.0 quote metadata; M4 unsealed
derived files). Seal section 4 corrections: 10.

**Fitness for P1's exposure statement.** X1 is accurate where it copies numbers: every K6, Gate 0, E.17, E.20, E.21,
E.22, E.28 and E.31 figure checked matches its source, the ledger summary reproduces exactly, and no row is unsourced.
Its errors are in description and coverage, not in values: the E.17 window composition (it repeated the
pre-registered "24 from 2010-07" instead of the as-run 14 plus 10 fallback roots), the H4 hold, two counts (183, 8)
and the B8 tally. The coverage gap matters more for P1: X1 lists C1/C1b as soy-free although their model M1 was fitted
on the E.12 panel's soy rows, it misses E.25's derived per-trip statistics on the soy K6 confirmation trips, and it
does not say that trip files, units files and ML caches carrying window information remain outside the seal. With the
eight corrections and the four added rows, X1 is fit to support P1's exposure statement. The overall reading does not
change: every earlier use of the window was one-minute bar work or derived from it, all results null or negative, no
order-book data from the window was ever bought, and no E.33 configuration was selected on it.
