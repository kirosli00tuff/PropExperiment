# Stage E.32b F3: volatility at horizons (spec section 2)

Worker VolCoder (Opus 5.5, xhigh), JSON generated 2026-10-28 23:14:46 PDT. Facts only: volatility statistics, no signed, conditional or
autocorrelation statistic, nothing about any strategy. Contract: reports/stage_e32b_ranking_spec.md sections 0 and 2
(sha256 09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635, matches the frozen hash: True). Machine-readable output: reports/stage_e32b_briefs/F3_vol.json
(schema of brief_wave_b.md "Shared data contract"; extra keys per root: family, tick_source, flags, and for owned roots
early_halt_dates_excluded_n, us_holiday_trade_dates, overnight_pairs_span_excluded_date). Code, tests and logs:
reports/stage_e32b_briefs/work/F3/ (f3_guard.py, f3_core.py, f3_vol.py, f3_md.py, test_f3.py, run.log, opens.log,
parts/<ROOT>.json, regression.json, holdout_before.txt, holdout_after.txt, time_run.txt).

Counts: 22 owned, 17 OC1, 8 unknown (47 codes). Owned: MCL CL NG MGC GC MHG HG 6E 6A MBT RTY YM NQ ZT ZF ZN ZB ZC ZS ZW ZL ZM. NQ is computed as MNQ's transfer
source and flagged "excluded from scoring (V49)".

## Data rule, as applied (spec 2.1)

- Every bar file was opened through f3_guard.BarGuard. It resolves the path (os.path.realpath; data/vendor/.../ohlcv-1m
  is a symlink to /mnt/large-storage/...) and refuses before opening unless the resolved path is exactly
  <resolved ohlcv-1m>/<ROOT>_v_0/range=YYYY-MM-01_YYYY-MM-01.dbn.zst with ROOT one of the 47 codes and the range one of
  the 12 months 2022-11 .. 2023-10, and the file is a regular file. Any given or resolved path containing mbo, mbp,
  tbbo, holdout, sealed or enc (case-insensitive) is refused first. The reader is called on the resolved (checked)
  path. Every open and refusal is logged with its PDT time in work/F3/opens.log.
- Files opened: 264 distinct (22 roots x 12 months); opens.log has 264 OPEN lines and 0 REFUSED lines
  (one probe run on ZC, then the full run, which skipped ZC's finished part; the re-assembly opened nothing). Nothing
  outside the 12 allow-listed months was opened: not the 2022-10 file E.28 A0 also read (so trade date 2022-11-01
  lacks its 17:00-19:00 CT evening bars; its main session is complete), no pilot, research, holdout-2 or embargo file,
  no mbo, mbp-1 or tbbo file, nothing of the E.32 soy test seal (2017-05 .. 2020-11).
- Guard unit tests (test_f3.py, synthetic file tree): allowed files pass and are logged; refused, with the reader never
  called: the months 2022-10, 2023-11 and 2024-03, a root outside the 47 (MES), a wrong suffix, an absent allowed
  name, a ../ traversal to MES, a path into mbp-1, a symlink whose given path contains each forbidden token, a symlink
  resolving into mbp-1 and one resolving outside the ohlcv-1m folder; on the real tree, 2024-03, 2023-11 and a 2019 ZS
  path are refused without opening.

Before the run (work/F3/holdout_before.txt):

    # E.32b F3 guard checks: before the F3 run
    $ date
    Wed Oct 28 23:13:18 PDT 2026
    $ uv run python -m data.holdout status (keys)
    top all_ok True unlocks_logged 0 unlock_log_ok True
    holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
    MCL all_ok True unlocks_logged 0 unlock_log_ok True
    MGC all_ok True unlocks_logged 0 unlock_log_ok True
    MHG all_ok True unlocks_logged 0 unlock_log_ok True
    NG all_ok True unlocks_logged 0 unlock_log_ok True
    $ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)  [the E.32 test seal]
    soy test {'state': 'sealed', 'files_sealed': 114, 'files_ok': 114, 'plaintext_in_window_present': [], 'unlocks_logged': 0, 'all_ok': True}
    $ guard33.py dry-check  [E.33 test-seal read guard: must refuse every forbidden read]
    dry-check: 4 of 4 refused
    rc=0

After the run (work/F3/holdout_after.txt; identical apart from the header and the date):

    # E.32b F3 guard checks: after the F3 run
    $ date
    Wed Oct 28 23:14:50 PDT 2026
    $ uv run python -m data.holdout status (keys)
    top all_ok True unlocks_logged 0 unlock_log_ok True
    holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
    MCL all_ok True unlocks_logged 0 unlock_log_ok True
    MGC all_ok True unlocks_logged 0 unlock_log_ok True
    MHG all_ok True unlocks_logged 0 unlock_log_ok True
    NG all_ok True unlocks_logged 0 unlock_log_ok True
    $ uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status (keys)  [the E.32 test seal]
    soy test {'state': 'sealed', 'files_sealed': 114, 'files_ok': 114, 'plaintext_in_window_present': [], 'unlocks_logged': 0, 'all_ok': True}
    $ guard33.py dry-check  [E.33 test-seal read guard: must refuse every forbidden read]
    dry-check: 4 of 4 refused
    rc=0

## Method (spec 2.2 to 2.4; E.28 A0 code reused)

- Trade dates, scheduled grid, main session and EARLY_HALT exclusion are A0's functions, copied unchanged into
  f3_core.py: trade date by the 17:00 CT rule (Saturday and Sunday roll to Monday); the grid is the group calendar's
  scheduled minutes (data/calendars/<group>.py SESSIONS) cut to the trade date's first and last bar; main session =
  grid minutes whose start is in [06:30, 13:00) America/Vancouver, which gives 06:30-13:00 (390 minutes) for equity,
  rates, fx, energy, metals and crypto and 06:30-11:20 (290 minutes) for grains; close carried forward from the last
  bar at or before each grid minute; the instrument at a grid minute is that bar's instrument_id. Dates in the group's
  EARLY_HALT list are excluded (data.cme_calendar for equity, data/calendars/<group>.py otherwise). L_main and
  main_session_pt are read off the group calendar on a regular date (2023-06-14); the most frequent number of main grid
  minutes per date in the data equals L_main for every owned root.
- Ticks: price changes in vendor fixed-point units divided by the vendor tick (rules/products.py tick_size x
  vendor_price_factor), so every change is an exact multiple of a tick. tick_size and median_close in the JSON are in
  the exchange units of rules/products.py (USD per bushel, pound, ton, barrel, MMBtu or ounce; index points; points of
  par; USD per foreign unit). Codes absent from rules/products.py (BTC, MET, ETH, 2YY, 5YY, 10Y, 30Y, MZC, MZS, MZW,
  MZL, MZM, XC, XK, XW) take E.28 A1_<family>.json tick_size, converted from US cents to USD where A1 states cents, and
  are flagged.
- D_h(t) = close(t+h) - close(t) for every main grid minute t whose t+h is a main grid minute of the same trade date,
  with the same instrument at both ends (overlapping starts), h in 1, 2, 5, 15, 30, 60, 120, 240. sigma_h = SD (ddof 1);
  m = mean |D_h|; median |D_h|; p99 |D_h| (numpy linear interpolation); n = count of pairs.
- OC = close at the last main grid minute minus close at the first main grid minute, same instrument at both ends
  (sigma, mean |OC|).
- Overnight: cc = last main close of a trade date minus that of the previous sample trade date; on = first main close of
  a trade date minus the previous sample trade date's last main close; each kept only with the same instrument at both
  ends. "Consecutive" = consecutive regular (non-excluded) trade dates in the data, so a pair can span an excluded
  EARLY_HALT date (counted per root in the holiday table; under CME's own convention the holiday session belongs to the
  next trade date anyway).
- R_d: E.28's definition, the full trade date's high minus low of the bars of the instrument traded in the day's last
  bar; median and p99 over regular dates. Main range: high minus low of the bars that start on a main grid minute, of the
  instrument of the last such bar; median over dates.
- median_close: the median over regular dates of the last main-session close (exchange units).
- OC-1 (spec 2.4): a code without the 12 window files takes its sibling's tick statistics (sigma, m, median |D|, p99,
  OC, cc, on, R_d, main range) times sibling tick / own tick; counts (n, n_dates) are the sibling's; median_close is
  the sibling's price (same price of the same underlying). L_main and main_session_pt come from the code's own group
  calendar where data.calendars lists the code, else from the sibling (flagged). Unknown: no transfer (SI, SIL, MET,
  ETH: no owned sibling; 2YY, 5YY, 10Y, 30Y: yield-quoted).

One property of the spec's D_h definition, reported for the lead (not changed): because both t and t+h must be main
minutes, the move of the first main bar itself (06:30-06:31 PT, the US cash open for equity index futures) is never
part of any D_h; OC starts at the same close. E.28 A0's sigma_1m counted it (the change from 06:29 to 06:30). See the
regression section.

## Table 1. Volatility per code, ticks of the code's own tick (window 2022-11-01..2023-10-31, regular trade dates)

s<h> = sigma of D_h. OC s (m) = SD (mean |OC|). cc, on = overnight SDs. R_d and main range in ticks. Median close in
exchange units.

| Code | Status | Transfer | Tick | Dates | L_main | s1 | s2 | s5 | s15 | s30 | s60 | s120 | s240 | OC s (m) | cc s | on s | R_d med (p99) | Main range med | Median close |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MCL | owned |  | 0.01 | 250 | 390 | 6.48 | 9.02 | 13.95 | 23.68 | 33.55 | 48.34 | 70.00 | 99.42 | 120.45 (94.00) | 170.57 | 124.50 | 245.5 (570.5) | 177.0 | 78.59 |
| QM | OC1 | CL x 0.4 | 0.025 | 250 | 390 | 2.52 | 3.53 | 5.52 | 9.44 | 13.40 | 19.31 | 27.98 | 39.74 | 48.38 (37.64) | 68.38 | 50.04 | 97.6 (227.8) | 70.2 | 78.585 |
| CL | owned |  | 0.01 | 250 | 390 | 6.29 | 8.84 | 13.80 | 23.61 | 33.51 | 48.28 | 69.95 | 99.34 | 120.95 (94.09) | 170.96 | 125.10 | 244.0 (569.5) | 175.5 | 78.585 |
| MNG | OC1 | NG x 1 | 0.001 | 250 | 390 | 6.27 | 8.75 | 13.59 | 22.84 | 32.54 | 47.26 | 66.03 | 92.35 | 105.61 (72.59) | 175.95 | 150.67 | 158.0 (704.7) | 113.5 | 2.6655 |
| QG | OC1 | NG x 0.2 | 0.005 | 250 | 390 | 1.25 | 1.75 | 2.72 | 4.57 | 6.51 | 9.45 | 13.21 | 18.47 | 21.12 (14.52) | 35.19 | 30.13 | 31.6 (140.9) | 22.7 | 2.6655 |
| NG | owned |  | 0.001 | 250 | 390 | 6.27 | 8.75 | 13.59 | 22.84 | 32.54 | 47.26 | 66.03 | 92.35 | 105.61 (72.59) | 175.95 | 150.67 | 158.0 (704.7) | 113.5 | 2.6655 |
| MGC | owned |  | 0.1 | 250 | 390 | 5.39 | 7.56 | 11.90 | 20.70 | 29.04 | 39.25 | 52.34 | 73.45 | 111.76 (82.54) | 168.97 | 113.34 | 220.0 (571.3) | 137.5 | 1935.7 |
| GC | owned |  | 0.1 | 250 | 390 | 5.29 | 7.45 | 11.79 | 20.52 | 28.84 | 39.09 | 52.23 | 73.40 | 111.60 (82.34) | 168.83 | 113.41 | 220.5 (567.7) | 139.5 | 1935.6 |
| SIL | unknown |  | 0.005 | 0 | 390 | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| SI | unknown |  | 0.005 | 0 | 390 | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| MHG | owned |  | 0.0005 | 250 | 390 | 3.38 | 4.75 | 7.34 | 12.26 | 16.92 | 23.07 | 31.57 | 43.53 | 56.25 (42.35) | 106.06 | 92.07 | 159.0 (351.2) | 85.0 | 3.8265 |
| HG | owned |  | 0.0005 | 250 | 390 | 3.14 | 4.41 | 6.90 | 11.80 | 16.50 | 22.74 | 31.37 | 43.23 | 56.37 (42.44) | 104.42 | 90.17 | 159.0 (354.7) | 85.5 | 3.82675 |
| M6E | OC1 | 6E x 0.5 | 0.0001 | 257 | 390 | 1.78 | 2.50 | 3.92 | 6.77 | 9.52 | 13.10 | 17.41 | 24.00 | 33.99 (25.02) | 54.67 | 42.72 | 76.5 (212.7) | 45.5 | 1.0778 |
| 6E | owned |  | 5e-05 | 257 | 390 | 3.56 | 4.99 | 7.84 | 13.53 | 19.04 | 26.19 | 34.82 | 48.00 | 67.98 (50.05) | 109.34 | 85.44 | 153.0 (425.4) | 91.0 | 1.0778 |
| M6A | OC1 | 6A x 0.5 | 0.0001 | 257 | 390 | 1.54 | 2.17 | 3.42 | 5.87 | 8.17 | 11.18 | 14.93 | 20.76 | 29.24 (21.70) | 50.34 | 41.44 | 69.0 (181.5) | 39.0 | 0.6692 |
| 6A | owned |  | 5e-05 | 257 | 390 | 3.09 | 4.34 | 6.83 | 11.73 | 16.35 | 22.36 | 29.86 | 41.53 | 58.48 (43.41) | 100.68 | 82.88 | 138.0 (363.0) | 78.0 | 0.6692 |
| MET | unknown |  | 0.5 | 0 | - | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| ETH | unknown |  | 0.5 | 0 | - | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| MBT | owned |  | 5 | 257 | 390 | 4.91 | 6.92 | 10.75 | 18.37 | 25.82 | 36.67 | 51.35 | 73.39 | 105.03 (69.11) | 164.31 | 119.85 | 169.0 (704.4) | 105.0 | 26635.0 |
| BTC | OC1 | MBT x 1 | 5 | 257 | 390 | 4.91 | 6.92 | 10.75 | 18.37 | 25.82 | 36.67 | 51.35 | 73.39 | 105.03 (69.11) | 164.31 | 119.85 | 169.0 (704.4) | 105.0 | 26635.0 |
| M2K | OC1 | RTY x 1 | 0.1 | 249 | 390 | 9.90 | 13.98 | 21.97 | 37.41 | 51.75 | 70.77 | 95.69 | 132.46 | 193.61 (157.72) | 237.81 | 142.40 | 341.0 (822.3) | 283.0 | 1838.5 |
| RTY | owned |  | 0.1 | 249 | 390 | 9.90 | 13.98 | 21.97 | 37.41 | 51.75 | 70.77 | 95.69 | 132.46 | 193.61 (157.72) | 237.81 | 142.40 | 341.0 (822.3) | 283.0 | 1838.5 |
| MYM | OC1 | YM x 1 | 1 | 249 | 390 | 12.04 | 16.95 | 26.54 | 45.24 | 63.23 | 88.56 | 122.94 | 166.20 | 226.31 (176.32) | 275.49 | 154.57 | 393.0 (1,049.5) | 326.0 | 33825.0 |
| YM | owned |  | 1 | 249 | 390 | 12.04 | 16.95 | 26.54 | 45.24 | 63.23 | 88.56 | 122.94 | 166.20 | 226.31 (176.32) | 275.49 | 154.57 | 393.0 (1,049.5) | 326.0 | 33825.0 |
| MNQ | OC1 | NQ x 1 | 0.25 | 249 | 390 | 27.68 | 39.09 | 61.54 | 105.64 | 147.10 | 202.67 | 283.31 | 389.76 | 576.05 (456.41) | 699.90 | 411.21 | 967.0 (2,265.9) | 789.0 | 13301.5 |
| NQ | owned |  | 0.25 | 249 | 390 | 27.68 | 39.09 | 61.54 | 105.64 | 147.10 | 202.67 | 283.31 | 389.76 | 576.05 (456.41) | 699.90 | 411.21 | 967.0 (2,265.9) | 789.0 | 13301.5 |
| 2YY | unknown |  | 0.001 | 0 | - | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| 5YY | unknown |  | 0.001 | 0 | - | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| 10Y | unknown |  | 0.001 | 0 | - | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| 30Y | unknown |  | 0.001 | 0 | - | - | - | - | - | - | - | - | - | - (-) | - | - | - (-) | - | - |
| ZT | owned |  | 0.00390625 | 250 | 390 | 1.58 | 2.17 | 3.36 | 5.75 | 8.00 | 11.00 | 15.02 | 20.88 | 30.51 (21.13) | 48.07 | 36.29 | 52.5 (265.2) | 32.0 | 102.16796875 |
| ZF | owned |  | 0.0078125 | 250 | 390 | 1.67 | 2.31 | 3.60 | 6.16 | 8.53 | 11.57 | 15.84 | 22.46 | 32.96 (23.91) | 50.48 | 38.43 | 63.0 (206.6) | 40.0 | 107.84765625 |
| ZN | owned |  | 0.015625 | 250 | 390 | 1.27 | 1.70 | 2.58 | 4.33 | 5.94 | 7.99 | 10.96 | 15.75 | 23.16 (17.24) | 35.74 | 27.28 | 46.5 (133.6) | 30.0 | 112.6875 |
| ZB | owned |  | 0.03125 | 250 | 390 | 1.21 | 1.64 | 2.50 | 4.19 | 5.77 | 7.80 | 10.73 | 15.39 | 22.58 (17.79) | 34.45 | 26.30 | 48.0 (120.7) | 31.0 | 126.703125 |
| MZC | OC1 | ZC x 0.5 | 0.005 | 250 | 290 | 0.86 | 1.17 | 1.77 | 2.99 | 4.18 | 5.91 | 8.50 | 12.19 | 13.97 (10.41) | 18.04 | 11.26 | 21.8 (72.1) | 18.5 | 6.07875 |
| MZS | OC1 | ZS x 0.5 | 0.005 | 250 | 290 | 1.55 | 2.17 | 3.36 | 5.69 | 7.99 | 11.35 | 16.28 | 22.20 | 25.69 (19.42) | 34.35 | 23.41 | 45.2 (103.5) | 36.0 | 14.185 |
| MZW | OC1 | ZW x 0.5 | 0.005 | 250 | 290 | 1.36 | 1.89 | 2.90 | 4.90 | 6.67 | 9.23 | 12.46 | 17.65 | 20.76 (16.20) | 29.85 | 19.78 | 38.8 (107.5) | 31.5 | 6.77 |
| MZL | OC1 | ZL x 0.5 | 0.0002 | 250 | 290 | 2.76 | 3.86 | 6.03 | 10.18 | 14.05 | 19.10 | 26.41 | 38.87 | 45.29 (36.15) | 58.42 | 35.06 | 83.0 (187.1) | 68.0 | 0.60185 |
| MZM | OC1 | ZM x 0.5 | 0.2 | 250 | 290 | 1.58 | 2.21 | 3.42 | 5.72 | 8.02 | 11.20 | 15.70 | 21.81 | 25.95 (20.57) | 33.81 | 22.24 | 48.0 (113.3) | 40.0 | 420.65 |
| XC | OC1 | ZC x 2 | 0.00125 | 250 | 290 | 3.43 | 4.67 | 7.10 | 11.97 | 16.70 | 23.66 | 33.99 | 48.75 | 55.89 (41.66) | 72.16 | 45.05 | 87.0 (288.4) | 74.0 | 6.07875 |
| XK | OC1 | ZS x 2 | 0.00125 | 250 | 290 | 6.21 | 8.69 | 13.44 | 22.74 | 31.96 | 45.42 | 65.12 | 88.79 | 102.76 (77.69) | 137.39 | 93.64 | 181.0 (414.2) | 144.0 | 14.185 |
| XW | OC1 | ZW x 2 | 0.00125 | 250 | 290 | 5.45 | 7.57 | 11.61 | 19.59 | 26.68 | 36.90 | 49.83 | 70.61 | 83.03 (64.79) | 119.39 | 79.11 | 155.0 (429.8) | 126.0 | 6.77 |
| ZC | owned |  | 0.0025 | 250 | 290 | 1.71 | 2.33 | 3.55 | 5.98 | 8.35 | 11.83 | 16.99 | 24.37 | 27.95 (20.83) | 36.08 | 22.52 | 43.5 (144.2) | 37.0 | 6.07875 |
| ZS | owned |  | 0.0025 | 250 | 290 | 3.11 | 4.34 | 6.72 | 11.37 | 15.98 | 22.71 | 32.56 | 44.40 | 51.38 (38.84) | 68.69 | 46.82 | 90.5 (207.1) | 72.0 | 14.185 |
| ZW | owned |  | 0.0025 | 250 | 290 | 2.72 | 3.78 | 5.80 | 9.79 | 13.34 | 18.45 | 24.91 | 35.30 | 41.52 (32.40) | 59.70 | 39.55 | 77.5 (214.9) | 63.0 | 6.77 |
| ZL | owned |  | 0.0001 | 250 | 290 | 5.52 | 7.72 | 12.05 | 20.37 | 28.10 | 38.21 | 52.82 | 77.74 | 90.58 (72.29) | 116.84 | 70.12 | 166.0 (374.1) | 136.0 | 0.60185 |
| ZM | owned |  | 0.1 | 250 | 290 | 3.15 | 4.42 | 6.84 | 11.45 | 16.03 | 22.40 | 31.41 | 43.63 | 51.90 (41.14) | 67.62 | 44.49 | 96.0 (226.5) | 80.0 | 420.65 |

## Table 2. Owned roots: mean |D_h| / median |D_h| / p99 |D_h| and pair counts at h = 5, 60, 240

| Code (owned) | m5 / med5 / p99_5 | m60 / med60 / p99_60 | m240 / med240 / p99_240 | n5 | n60 | n240 |
|---|---|---|---|---|---|---|
| MCL | 9.91 / 7.0 / 44.0 | 35.12 / 26.0 / 148.0 | 74.31 / 56.0 / 307.2 | 95428 | 81678 | 36678 |
| CL | 9.78 / 7.0 / 44.0 | 35.09 / 26.0 / 148.0 | 74.37 / 56.0 / 306.0 | 96250 | 82500 | 37500 |
| NG | 8.20 / 5.0 / 51.0 | 29.15 / 17.0 / 177.0 | 59.31 / 36.0 / 363.0 | 96250 | 82500 | 37500 |
| MGC | 7.81 / 5.0 / 42.0 | 26.57 / 18.0 / 136.0 | 54.28 / 40.0 / 234.0 | 96097 | 82347 | 37347 |
| GC | 7.78 / 5.0 / 42.0 | 26.44 / 18.0 / 135.0 | 54.22 / 40.0 / 234.0 | 96250 | 82500 | 37500 |
| MHG | 4.90 / 3.0 / 25.0 | 15.89 / 11.0 / 78.0 | 31.90 / 24.0 / 139.0 | 95347 | 81597 | 36750 |
| HG | 4.69 / 3.0 / 23.0 | 15.58 / 10.0 / 78.0 | 31.67 / 23.0 / 138.0 | 96250 | 82500 | 37500 |
| 6E | 5.16 / 4.0 / 27.0 | 17.92 / 13.0 / 91.2 | 35.08 / 26.0 / 156.0 | 98600 | 84480 | 38400 |
| 6A | 4.50 / 3.0 / 23.2 | 15.19 / 11.0 / 79.2 | 30.57 / 23.0 / 132.0 | 98582 | 84480 | 38400 |
| MBT | 6.57 / 4.0 / 39.0 | 22.74 / 14.0 / 143.0 | 48.00 / 30.0 / 255.0 | 95594 | 81459 | 36900 |
| RTY | 15.56 / 11.0 / 74.0 | 51.29 / 39.0 / 234.0 | 101.86 / 82.0 / 386.0 | 95865 | 82170 | 37350 |
| YM | 18.67 / 14.0 / 89.0 | 64.51 / 48.0 / 286.0 | 126.42 / 100.0 / 493.0 | 95865 | 82170 | 37350 |
| NQ | 44.23 / 33.0 / 201.0 | 150.24 / 116.0 / 639.0 | 302.62 / 249.0 / 1,108.0 | 95865 | 82170 | 37350 |
| ZT | 2.02 / 1.0 / 12.0 | 6.92 / 5.0 / 44.0 | 14.09 / 10.0 / 77.0 | 96250 | 82500 | 37500 |
| ZF | 2.33 / 2.0 / 13.0 | 7.74 / 5.0 / 44.0 | 16.01 / 12.0 / 79.0 | 96250 | 82500 | 37500 |
| ZN | 1.73 / 1.0 / 9.0 | 5.57 / 4.0 / 28.0 | 11.55 / 9.0 / 52.0 | 96250 | 82500 | 37500 |
| ZB | 1.73 / 1.0 / 8.0 | 5.64 / 4.0 / 25.0 | 11.54 / 9.0 / 45.0 | 96250 | 82500 | 37500 |
| ZC | 2.46 / 2.0 / 12.0 | 8.38 / 6.0 / 39.0 | 17.77 / 14.0 / 74.0 | 71250 | 57500 | 12500 |
| ZS | 4.73 / 4.0 / 19.0 | 16.18 / 13.0 / 67.0 | 32.70 / 26.0 / 143.0 | 71250 | 57500 | 12500 |
| ZW | 4.13 / 3.0 / 19.0 | 13.47 / 10.0 / 62.0 | 27.34 / 22.0 / 101.0 | 71250 | 57500 | 12500 |
| ZL | 8.77 / 7.0 / 38.0 | 28.54 / 22.0 / 117.0 | 60.44 / 47.0 / 202.0 | 71250 | 57500 | 12500 |
| ZM | 4.90 / 4.0 / 21.0 | 16.53 / 13.0 / 69.0 | 33.75 / 28.0 / 122.0 | 71250 | 57500 | 12500 |

## Table 3. OC-1 transfers

| Code | Source | Own tick | Source tick | Factor | Tick source | Session |
|---|---|---|---|---|---|---|
| QM | CL | 0.025 | 0.01 | 0.4 | rules/products.py | session from own group calendar (energy) |
| MNG | NG | 0.001 | 0.001 | 1 | rules/products.py | session from own group calendar (energy) |
| QG | NG | 0.005 | 0.001 | 0.2 | rules/products.py | session from own group calendar (energy) |
| M6E | 6E | 0.0001 | 5e-05 | 0.5 | rules/products.py | session from own group calendar (fx) |
| M6A | 6A | 0.0001 | 5e-05 | 0.5 | rules/products.py | session from own group calendar (fx) |
| BTC | MBT | 5 | 5 | 1 | reports/stage_e28_briefs/A1_crypto.json tick_size (5.0 USD per bitcoin) | session taken from MBT (code absent from data.calendars) |
| M2K | RTY | 0.1 | 0.1 | 1 | rules/products.py | session from own group calendar (equity) |
| MYM | YM | 1 | 1 | 1 | rules/products.py | session from own group calendar (equity) |
| MNQ | NQ | 0.25 | 0.25 | 1 | rules/products.py | session from own group calendar (equity) |
| MZC | ZC | 0.005 | 0.0025 | 0.5 | reports/stage_e28_briefs/A1_grains.json tick_size (0.5 US cents per bushel) | session taken from ZC (code absent from data.calendars) |
| MZS | ZS | 0.005 | 0.0025 | 0.5 | reports/stage_e28_briefs/A1_grains.json tick_size (0.5 US cents per bushel) | session taken from ZS (code absent from data.calendars) |
| MZW | ZW | 0.005 | 0.0025 | 0.5 | reports/stage_e28_briefs/A1_grains.json tick_size (0.5 US cents per bushel) | session taken from ZW (code absent from data.calendars) |
| MZL | ZL | 0.0002 | 0.0001 | 0.5 | reports/stage_e28_briefs/A1_grains.json tick_size (0.02 US cents per pound) | session taken from ZL (code absent from data.calendars) |
| MZM | ZM | 0.2 | 0.1 | 0.5 | reports/stage_e28_briefs/A1_grains.json tick_size (0.2 USD per short ton) | session taken from ZM (code absent from data.calendars) |
| XC | ZC | 0.00125 | 0.0025 | 2 | reports/stage_e28_briefs/A1_grains.json tick_size (0.125 US cents per bushel) | session taken from ZC (code absent from data.calendars) |
| XK | ZS | 0.00125 | 0.0025 | 2 | reports/stage_e28_briefs/A1_grains.json tick_size (0.125 US cents per bushel) | session taken from ZS (code absent from data.calendars) |
| XW | ZW | 0.00125 | 0.0025 | 2 | reports/stage_e28_briefs/A1_grains.json tick_size (0.125 US cents per bushel) | session taken from ZW (code absent from data.calendars) |

## Table 4. Unknown (no sigma)

| Code | Tick | Tick source | Reason |
|---|---|---|---|
| SIL | 0.005 | rules/products.py | no owned standard-window bars and no owned sibling (spec 2.4) |
| SI | 0.005 | rules/products.py | no owned standard-window bars and no owned sibling (spec 2.4) |
| MET | 0.5 | reports/stage_e28_briefs/A1_crypto.json tick_size (0.5 USD per ether (index points)) | no owned standard-window bars and no owned sibling (spec 2.4) |
| ETH | 0.5 | reports/stage_e28_briefs/A1_crypto.json tick_size (0.5 USD per ether (index points)) | no owned standard-window bars and no owned sibling (spec 2.4) |
| 2YY | 0.001 | reports/stage_e28_briefs/A1_rates.json tick_size (0.001 index points of yield (0.1 basis point)) | yield-quoted micro: no transfer from price-quoted Treasury futures (spec 2.4) |
| 5YY | 0.001 | reports/stage_e28_briefs/A1_rates.json tick_size (0.001 index points of yield (0.1 basis point)) | yield-quoted micro: no transfer from price-quoted Treasury futures (spec 2.4) |
| 10Y | 0.001 | reports/stage_e28_briefs/A1_rates.json tick_size (0.001 index points of yield (0.1 basis point)) | yield-quoted micro: no transfer from price-quoted Treasury futures (spec 2.4) |
| 30Y | 0.001 | reports/stage_e28_briefs/A1_rates.json tick_size (0.001 index points of yield (0.1 basis point)) | yield-quoted micro: no transfer from price-quoted Treasury futures (spec 2.4) |

## Table 5. Trade-date quirk (E.21): US holidays booked as trade dates, per owned root

A0's handling: EARLY_HALT dates of the group calendar are excluded. "US holidays booked as trade dates" counts trade
dates in the raw window data that appear in data.cme_calendar.HOLIDAYS (the US holiday list). Equity: all 10
excluded. Rates, energy and metals: all excluded except 2023-07-03 (the day before Independence Day), which their group
calendars do not list (energy and metals have no 2023-04-07 bars: full closure). Fx and crypto: their calendars list
only 2022-11-25 and 2023-04-07 as EARLY_HALT, so the other 8 US holiday sessions (2022-11-24, 2023-01-16, 2023-02-20,
2023-05-29, 2023-06-19, 2023-07-03, 2023-07-04, 2023-09-04) stay in the sample as short days (A0 caveat 3). Grains:
2023-07-03 stays.

| Root | Calendar | Trade dates in data | Regular (used) | EARLY_HALT excluded | US holidays booked as trade dates | of which excluded | kept | cc/on pairs spanning an excluded date |
|---|---|---|---|---|---|---|---|---|
| MCL | data.calendars.energy | 258 | 250 | 8 | 9 | 8 | 1 | 5 |
| CL | data.calendars.energy | 258 | 250 | 8 | 9 | 8 | 1 | 5 |
| NG | data.calendars.energy | 258 | 250 | 8 | 9 | 8 | 1 | 6 |
| MGC | data.calendars.metals | 258 | 250 | 8 | 9 | 8 | 1 | 7 |
| GC | data.calendars.metals | 258 | 250 | 8 | 9 | 8 | 1 | 7 |
| MHG | data.calendars.metals | 258 | 250 | 8 | 9 | 8 | 1 | 7 |
| HG | data.calendars.metals | 258 | 250 | 8 | 9 | 8 | 1 | 7 |
| 6E | data.calendars.fx | 259 | 257 | 2 | 10 | 2 | 8 | 2 |
| 6A | data.calendars.fx | 259 | 257 | 2 | 10 | 2 | 8 | 2 |
| MBT | data.calendars.crypto | 259 | 257 | 2 | 10 | 2 | 8 | 1 |
| RTY | data.cme_calendar | 259 | 249 | 10 | 10 | 10 | 0 | 8 |
| YM | data.cme_calendar | 259 | 249 | 10 | 10 | 10 | 0 | 8 |
| NQ | data.cme_calendar | 259 | 249 | 10 | 10 | 10 | 0 | 8 |
| ZT | data.calendars.rates | 259 | 250 | 9 | 10 | 9 | 1 | 7 |
| ZF | data.calendars.rates | 259 | 250 | 9 | 10 | 9 | 1 | 8 |
| ZN | data.calendars.rates | 259 | 250 | 9 | 10 | 9 | 1 | 8 |
| ZB | data.calendars.rates | 259 | 250 | 9 | 10 | 9 | 1 | 8 |
| ZC | data.calendars.grains | 251 | 250 | 1 | 2 | 1 | 1 | 0 |
| ZS | data.calendars.grains | 251 | 250 | 1 | 2 | 1 | 1 | 1 |
| ZW | data.calendars.grains | 251 | 250 | 1 | 2 | 1 | 1 | 1 |
| ZL | data.calendars.grains | 251 | 250 | 1 | 2 | 1 | 1 | 1 |
| ZM | data.calendars.grains | 251 | 250 | 1 | 2 | 1 | 1 | 1 |

## Regression against E.28 A0 (reports/stage_e28_briefs/A0_contract_stats.json), all 22 owned roots

Statistics both compute on the same window: the number of regular trade dates, the EARLY_HALT list, sigma_1m and its
count of changes, and the R_d median. F3 also computes A0's sigma_1m convention (the change ending at each main minute)
as a diagnostic only (not in F3_vol.json).

| Root | Dates F3 / A0 | Halt lists equal | sigma_1m A0-convention F3 / A0 (diff %) | changes F3 / A0 | sigma_1 spec F3 (diff % vs A0) | n_1 spec | R_d median F3 / A0 | implied RMS of the dropped open-minute changes (ticks, approx.) |
|---|---|---|---|---|---|---|---|---|
| MCL | 250 / 250 | True | 6.4912 / 6.4912 (+0.0000) | 96678 / 96678 | 6.4836 (-0.117) | 96428 | 245.5 / 245.5 | 8.9 (k = 250) |
| CL | 250 / 250 | True | 6.2998 / 6.2998 (+0.0000) | 97500 / 97500 | 6.2922 (-0.120) | 97250 | 244 / 244.0 | 8.8 (k = 250) |
| NG | 250 / 250 | True | 6.2803 / 6.2803 (+0.0000) | 97500 / 97500 | 6.2746 (-0.091) | 97250 | 158 / 158.0 | 8.2 (k = 250) |
| MGC | 250 / 250 | True | 5.4010 / 5.4010 (-0.0000) | 97347 / 97347 | 5.3932 (-0.146) | 97097 | 220 / 220.0 | 7.9 (k = 250) |
| GC | 250 / 250 | True | 5.2933 / 5.2933 (-0.0000) | 97500 / 97500 | 5.2852 (-0.153) | 97250 | 220.5 / 220.5 | 7.8 (k = 250) |
| MHG | 250 / 250 | True | 3.3834 / 3.3834 (+0.0000) | 96597 / 96597 | 3.3800 (-0.098) | 96347 | 159 / 159.0 | 4.5 (k = 250) |
| HG | 250 / 250 | True | 3.1420 / 3.1420 (+0.0000) | 97500 / 97500 | 3.1389 (-0.099) | 97250 | 159 / 159.0 | 4.2 (k = 250) |
| 6E | 257 / 257 | True | 3.5584 / 3.5584 (+0.0000) | 99885 / 99885 | 3.5558 (-0.073) | 99628 | 153 / 153.0 | 4.5 (k = 257) |
| 6A | 257 / 257 | True | 3.0931 / 3.0931 (-0.0000) | 99867 / 99867 | 3.0899 (-0.105) | 99610 | 138 / 138.0 | 4.2 (k = 257) |
| MBT | 257 / 257 | True | 4.9244 / 4.9244 (+0.0000) | 96879 / 96879 | 4.9145 (-0.201) | 96622 | 169 / 169.0 | 7.8 (k = 257) |
| RTY | 249 / 249 | True | 10.0077 / 10.0077 (-0.0000) | 97110 / 97110 | 9.9037 (-1.039) | 96861 | 341 / 341.0 | 30.1 (k = 249) |
| YM | 249 / 249 | True | 12.1364 / 12.1364 (+0.0000) | 97110 / 97110 | 12.0380 (-0.811) | 96861 | 393 / 393.0 | 32.8 (k = 249) |
| NQ | 249 / 249 | True | 27.8254 / 27.8254 (+0.0000) | 97110 / 97110 | 27.6822 (-0.515) | 96861 | 967 / 967.0 | 62.2 (k = 249) |
| ZT | 250 / 250 | True | 1.5809 / 1.5809 (+0.0000) | 97500 / 97500 | 1.5783 (-0.163) | 97250 | 52.5 / 52.5 | 2.4 (k = 250) |
| ZF | 250 / 250 | True | 1.6775 / 1.6775 (+0.0000) | 97500 / 97500 | 1.6744 (-0.188) | 97250 | 63 / 63.0 | 2.6 (k = 250) |
| ZN | 250 / 250 | True | 1.2765 / 1.2765 (+0.0000) | 97500 / 97500 | 1.2742 (-0.187) | 97250 | 46.5 / 46.5 | 2.0 (k = 250) |
| ZB | 250 / 250 | True | 1.2175 / 1.2175 (+0.0000) | 97500 / 97500 | 1.2146 (-0.245) | 97250 | 48 / 48.0 | 2.1 (k = 250) |
| ZC | 250 / 250 | True | 1.7141 / 1.7141 (+0.0000) | 72250 / 72250 | 1.7141 (+0.000) | 72250 | 43.5 / 43.5 | - (k = 0) |
| ZS | 250 / 250 | True | 3.1057 / 3.1057 (+0.0000) | 72250 / 72250 | 3.1057 (+0.000) | 72250 | 90.5 / 90.5 | - (k = 0) |
| ZW | 250 / 250 | True | 2.7250 / 2.7250 (+0.0000) | 72250 / 72250 | 2.7250 (+0.000) | 72250 | 77.5 / 77.5 | - (k = 0) |
| ZL | 250 / 250 | True | 5.5170 / 5.5170 (-0.0000) | 72250 / 72250 | 5.5170 (-0.000) | 72250 | 166 / 166.0 | - (k = 0) |
| ZM | 250 / 250 | True | 3.1522 / 3.1522 (+0.0000) | 72250 / 72250 | 3.1522 (+0.000) | 72250 | 96 / 96.0 | - (k = 0) |

- Under A0's convention every root matches exactly: same dates, same EARLY_HALT lists, same change counts, sigma_1m
  equal to at least 4 decimals, R_d medians equal (A0's values differ only by float rounding). Not opening the 2022-10
  file changes nothing here.
- The spec-literal sigma_1 is lower by 0.07% to 1.04% on the 17 roots whose 06:29 PT minute is on the grid, and equal
  for the 5 grain roots (06:29 PT is in the 07:45-08:30 CT break, so A0 also dropped that change). The count gap is
  exactly one change per trade date (k = n_dates). Above 1%: RTY (-1.04%). Explanation: the dropped change is the move
  of the 06:30 PT bar, the equity cash open; the implied RMS of those changes is 2.2 to 3.0 times sigma_1 for the
  three equity roots and 1.3 to 1.7 times for the others (last column, an approximation from the two SDs and counts),
  so dropping 249 of 97,110 changes lowers the SD by about 1.0% for RTY, 0.8% for YM and 0.5% for NQ. This follows
  from the spec's definition; it is not a bug.

## OC-1 check on owned pairs (micro vs full-size, same tick)

The three owned micro/full-size pairs on the same tick show how close a transferred statistic is to an owned one.

| Owned micro / owned full-size | s5 ratio | s30 ratio | s60 ratio | s240 ratio | R_d median ratio |
|---|---|---|---|---|---|
| MCL / CL | 1.011 | 1.001 | 1.001 | 1.001 | 1.006 |
| MGC / GC | 1.009 | 1.007 | 1.004 | 1.001 | 0.998 |
| MHG / HG | 1.064 | 1.026 | 1.014 | 1.007 | 1.000 |

## Run

`flock reports/stage_e32b_briefs/work/heavy.lock nice -n 10 uv run python reports/stage_e32b_briefs/work/F3/f3_vol.py`,
one process, resumable (one part per root). Free memory before: about 10.5 GB available. Probe on ZC: 0.8 s; full run
(21 roots plus assembly): 7.2 s wall, peak RSS 214 MB (/usr/bin/time, work/F3/time_run.txt). Unit tests:
`uv run pytest -q reports/stage_e32b_briefs/work/F3/test_f3.py` (29 passed).
