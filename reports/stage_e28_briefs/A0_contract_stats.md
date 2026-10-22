# Stage E.28 A0: owned-data magnitude statistics per owned root

Worker A0 (Opus 5.5), 2026-10-21 02:40 PDT. Facts only: no scores. Definitions from
reports/stage_e28_ranking_spec.md section 1. Machine-readable output, one object per root with units in the
field names: reports/stage_e28_briefs/A0_contract_stats.json. Script:
reports/stage_e28_briefs/work/A0/A0_stats.py (tables below generated from the JSON by
reports/stage_e28_briefs/work/A0/A0_md.py; per-root intermediate files in work/A0/A0_roots/; run log
work/A0/A0_run.log). Full run: about 1 minute, peak RSS about 170 MB on a test root, nice 10, one process.

## Data rule, as applied

- Only files under data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/ whose range ends on or before
  2023-11-01 were opened. The script refuses any other file before opening it (open_store) and refuses any
  resolved path containing mbp-1. Paths were resolved with os.path.realpath at each open; no file vanished
  during the run, so the 60-second retry never fired.
- Pilot-window coverage (2023-11-01..2024-02-29) is decided from file names only. No such file was opened.
- Nothing was written under data/. No Databento API call, no keys.
- The sealed holdout chunks (2024-03..2025-03) are absent from every root's folder (the gap 2024-03-01..2025-04-01
  in Table 3); nothing about them was read. `data.holdout status` was not run by this worker (the lead runs it).

## Method

- Tick size and tick value: rules/products.py (the `_p("<ROOT>", ...)` line cited per root, sourced there to
  reports/stage_e0_liquidity.json, CME contract specifications). Prices in the files are vendor units: ZC, ZW,
  ZS, ZL, HE and LE are quoted in US cents by Databento, so their vendor tick is 100 x the exchange tick
  (rules/products.py, `vendor_price_factor`). All tick counts here divide vendor-unit prices by the vendor tick.
- Trade date: bar start time (ts_event) in America/Chicago; at or after 17:00 CT it belongs to the next day;
  Saturday and Sunday roll to Monday. Holiday sessions are therefore booked on the holiday's own date, not merged
  into the next day as CME does. To handle this, the primary statistics exclude every EARLY_HALT date in the
  group's repo calendar (data/cme_calendar.py for equity, data/calendars/<group>.py otherwise); the excluded
  dates are listed per root in the JSON (`early_halt_dates_excluded`), and the JSON also carries an
  `all_trade_dates_variant` (all dates kept). The two differ by at most about 3% on any median.
- Main session: bar start in [06:30, 13:00) America/Vancouver on the trade date. Overnight: every other scheduled
  minute of the trade date. Scheduled minutes come from the group's `SESSIONS` segments in the repo calendars
  (CT), cut to the span from the trade date's first bar to its last bar (which handles early closes). For grains
  the main session is therefore 06:30-11:20 PT (290 minutes) and for livestock 06:30-11:05 PT (275 minutes), as
  those products close at 13:20 and 13:05 CT; livestock has no overnight session.
- sigma_1m: on that minute grid, the close is carried forward from the last bar at or before each minute (a
  minute with no trade has an unchanged price). The change for main-session minute t is close(t) - close(t-1),
  kept only when t-1 is exactly one minute earlier on the scheduled grid and both minutes carry the same
  instrument_id (so roll jumps are dropped). SD with ddof 1, in ticks. A variant from consecutive actual bars
  only (no carried-forward minutes) is shown beside it; they differ materially only for MBT (4.92 vs 6.29) and
  MHG (3.38 vs 4.21), the two thinnest books.
- R_d: per trade date, high minus low of the bars of the instrument traded in the day's last bar (on days with two
  instrument_ids in the v_0 series, the other instrument's bars are left out); median over the window, in ticks.
- ADV: median of the per-trade-date sum of volume in the v_0 series. This is the v_0 continuous front contract
  (Databento's volume-ranked front) only, not all expiries as the spec asks; it understates all-expiry ADV,
  most for products whose volume is spread over several expiries (rates around rolls, energy, grains).
- Volume per minute: over the grid minutes of each session (a minute with no bar counts 0), median and mean.
- C4: daily close = close of the last 1-minute bar of the trade date (not the CME settlement price). Daily
  return = ln(close_t / close_t-1) between consecutive owned trade dates, dropped when the two days' last bars
  are different instrument_ids (rolls; counted per year as `roll_returns_skipped`). Per calendar year of the trade
  date: SD of that year's returns (ddof 1); a big move is |return| > 4 SD. A non-positive close would have been
  counted as a big move; none occurred (CL's v_0 series had already rolled before the 2020-04-20 negative
  settlement). Span: the first owned file to the trade date 2023-10-31, all trade dates kept (early-halt dates
  included). Reported three ways: the mean per full calendar year (>= 240 trade dates), and a rate per 252
  returns over the whole owned span and over 2019-01-01..2023-10-31 (the spec's window is 2019-2024; 2024 is not
  available under the data rule).

## Caveats

1. MNQ, the baseline, has no owned bars before 2025-04-01, so nothing here is MNQ's own. The same holds for M2K,
   MYM, QM, QG, MNG, SI, SIL, M6E and M6A. As a fact for the lead (not applied here): MNQ and NQ share the
   0.25 tick, M2K and RTY the 0.10 tick, MYM and YM the 1.00 tick, MNG and NG the 0.001 tick, so price-based
   statistics in ticks (sigma_1m, R_d, C4) of those micros would be expected close to their owned full-size
   cousins'; M6E (0.0001) and M6A (0.0001) have twice 6E's and 6A's tick (0.00005), QM (0.025) has 2.5 times
   CL's tick (0.01) and QG (0.005) has 5 times NG's (0.001). Volume statistics do not transfer.
2. ADV is v_0 front-contract volume only (see Method).
3. The FX and crypto repo calendars list only two EARLY_HALT dates in the window (2022-11-25, 2023-04-07), so US
   holiday sessions (for example 2023-01-16) stay in the FX and MBT samples as short days if they traded. The
   all-dates variant shows how little this moves the medians in the groups where it was applied.
4. Four roots have an empty first file (0 records, opened under the data rule): MBT 2021-04, MCL 2021-06,
   MHG 2022-04, RTY 2017-06 (`empty_files_opened` in the JSON). Their C4 spans start at the first non-empty file.
5. C4 first and last calendar years are partial (the first owned month to the year end; 2023 ends at 10-31); their
   per-year SD rests on fewer returns. Mean per full year uses only years with >= 240 trade dates (MHG has none).
   Daily-limit days cap returns (HE, LE and grains), which lowers the counts there.
6. The sigma_1m carry-forward choice gives zero changes for untraded minutes; the share of zero changes is in
   Table 1 (MBT 0.42, MHG 0.47, rates 0.35-0.42).
7. The C4 counts here are of the spec's fourth C4 item only. All owned roots show well under 10 big-move days per
   year (the highest rate is about 2 per full year: 6J, MBT).

<!-- GENERATED TABLES BELOW -->

## Table 1. Standard window 2022-11-01..2023-10-31 (regular trade dates; v_0 front contract)

| Root | Spec cand. | Tick (exch. units) | Tick USD | sigma_1m (ticks) | sigma_1m bars-only | zero-change share | R_d median (ticks) | ADV median (v_0) | Vol/min main median (mean) | Vol/min overnight median (mean) | Main vol share | Trade dates (excl. halts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | yes | 0.00005 | 5.00 | 3.09 | 3.12 | 0.21 | 138.0 | 82,950 | 46 (83.0) | 30 (52.1) | 0.38 | 257 (2) |
| 6B | no | 0.0001 | 6.25 | 2.33 | 2.37 | 0.28 | 101.0 | 85,833 | 53 (91.4) | 21 (51.6) | 0.41 | 257 (2) |
| 6C | no | 0.00005 | 5.00 | 2.35 | 2.38 | 0.26 | 89.0 | 68,345 | 59 (94.1) | 15 (33.2) | 0.53 | 257 (2) |
| 6E | yes | 0.00005 | 6.25 | 3.56 | 3.58 | 0.19 | 153.0 | 176,291 | 118 (195.2) | 50 (104.9) | 0.42 | 257 (2) |
| 6J | no | 5E-7 | 6.25 | 2.76 | 2.79 | 0.26 | 132.0 | 136,967 | 76 (133.3) | 51 (91.3) | 0.36 | 257 (2) |
| 6N | no | 0.00005 | 5.00 | 2.88 | 2.97 | 0.25 | 127.0 | 26,746 | 14 (29.2) | 7 (15.8) | 0.42 | 257 (2) |
| 6S | no | 0.00005 | 6.25 | 3.85 | 4.04 | 0.22 | 167.0 | 17,571 | 10 (21.1) | 4 (10.0) | 0.45 | 257 (2) |
| CL | yes | 0.01 | 10.00 | 6.30 | 6.31 | 0.10 | 244.0 | 227,772 | 241 (333.5) | 43 (93.7) | 0.58 | 250 (8) |
| GC | yes | 0.10 | 10.00 | 5.29 | 5.30 | 0.14 | 220.5 | 160,118 | 116 (199.8) | 44 (87.4) | 0.47 | 250 (8) |
| HE | no | 0.00025 | 10.00 | 3.44 | 3.46 | 0.19 | 84.0 | 14,854 | 30 (56.2) | - (-) | 1.00 | 250 (1) |
| HG | yes | 0.0005 | 12.50 | 3.14 | 3.18 | 0.22 | 159.0 | 59,578 | 36 (62.4) | 17 (36.0) | 0.41 | 250 (8) |
| LE | no | 0.00025 | 10.00 | 2.61 | 2.62 | 0.23 | 59.5 | 16,622 | 40 (65.4) | - (-) | 1.00 | 250 (1) |
| MBT | yes | 5.00 | 0.50 | 4.92 | 6.29 | 0.42 | 169.0 | 6,678 | 2 (12.0) | 0 (3.9) | 0.54 | 257 (2) |
| MCL | yes | 0.01 | 1.00 | 6.49 | 6.50 | 0.11 | 245.5 | 79,142 | 67 (106.1) | 19 (38.9) | 0.52 | 250 (8) |
| MES | no | 0.25 | 1.25 | 6.61 | 6.61 | 0.08 | 228.0 | 1,002,056 | 1,637 (2,131.5) | 111 (202.9) | 0.81 | 249 (10) |
| MGC | yes | 0.10 | 1.00 | 5.40 | 5.41 | 0.14 | 220.0 | 52,744 | 34 (66.5) | 15 (31.0) | 0.46 | 250 (8) |
| MHG | yes | 0.0005 | 1.25 | 3.38 | 4.23 | 0.46 | 159.0 | 4,373 | 1 (3.6) | 1 (3.0) | 0.32 | 250 (8) |
| NG | yes | 0.001 | 10.00 | 6.28 | 6.29 | 0.15 | 158.0 | 85,334 | 99 (150.0) | 7 (27.7) | 0.68 | 250 (8) |
| NQ | yes | 0.25 | 5.00 | 27.83 | 27.83 | 0.02 | 967.0 | 618,345 | 984 (1,252.5) | 77 (138.0) | 0.78 | 249 (10) |
| RTY | yes | 0.10 | 5.00 | 10.01 | 10.01 | 0.06 | 341.0 | 181,060 | 255 (380.5) | 14 (37.9) | 0.80 | 249 (10) |
| TN | no | 0.015625 | 15.625 | 1.55 | 1.57 | 0.36 | 64.0 | 325,356 | 341 (488.6) | 45 (148.2) | 0.57 | 250 (9) |
| UB | no | 0.03125 | 31.25 | 1.68 | 1.70 | 0.33 | 66.0 | 183,095 | 212 (300.7) | 22 (77.2) | 0.61 | 250 (9) |
| YM | yes | 1.00 | 5.00 | 12.14 | 12.14 | 0.05 | 393.0 | 163,416 | 226 (315.6) | 23 (43.2) | 0.74 | 249 (10) |
| ZB | yes | 0.03125 | 31.25 | 1.22 | 1.23 | 0.41 | 48.0 | 291,523 | 323 (462.0) | 39 (138.9) | 0.57 | 250 (9) |
| ZC | yes | 0.0025 | 12.50 | 1.71 | 1.71 | 0.31 | 43.5 | 91,946 | 183 (283.1) | 4 (22.6) | 0.83 | 250 (1) |
| ZF | yes | 0.0078125 | 7.8125 | 1.68 | 1.68 | 0.35 | 63.0 | 927,861 | 942 (1,359.6) | 141 (448.2) | 0.54 | 250 (9) |
| ZL | yes | 0.0001 | 6.00 | 5.52 | 5.52 | 0.11 | 166.0 | 42,686 | 78 (120.7) | 3 (10.4) | 0.82 | 250 (1) |
| ZM | yes | 0.10 | 10.00 | 3.15 | 3.15 | 0.18 | 96.0 | 36,690 | 71 (109.2) | 2 (8.5) | 0.83 | 250 (1) |
| ZN | yes | 0.015625 | 15.625 | 1.28 | 1.28 | 0.40 | 46.5 | 1,385,806 | 1,359 (1,984.9) | 207 (658.8) | 0.54 | 250 (9) |
| ZS | yes | 0.0025 | 12.50 | 3.11 | 3.11 | 0.18 | 90.5 | 77,862 | 143 (212.0) | 8 (22.8) | 0.78 | 250 (1) |
| ZT | yes | 0.00390625 | 7.8125 | 1.58 | 1.59 | 0.40 | 52.5 | 472,003 | 418 (692.3) | 53 (239.7) | 0.53 | 250 (9) |
| ZW | yes | 0.0025 | 12.50 | 2.72 | 2.73 | 0.21 | 77.5 | 39,362 | 70 (113.9) | 3 (11.2) | 0.80 | 250 (1) |

## Table 2. C4 big-move days (|daily log return| > 4 x that calendar year's daily SD), owned span to 2023-10-31

| Root | First trade date | Full years (>= 240 dates) | Mean per full year | Rate per 252 days, owned span | Rate per 252 days, 2019..2023-10-31 | Per year (big moves / returns) |
|---|---|---|---|---|---|---|
| 6A | 2019-05-01 | 3 | 0.67 | 0.44 | 0.44 | 2019: 0/170, 2020: 2/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| 6B | 2019-05-01 | 3 | 0.67 | 0.44 | 0.44 | 2019: 0/170, 2020: 1/255, 2021: 0/255, 2022: 1/254, 2023: 0/213 |
| 6C | 2019-05-01 | 3 | 0.33 | 0.22 | 0.22 | 2019: 0/170, 2020: 1/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| 6E | 2010-06-07 | 12 | 0.33 | 0.30 | 0.20 | 2010: 0/145, 2011: 0/254, 2012: 0/254, 2013: 0/248, 2014: 1/246, 2015: 0/255, 2016: 1/254, 2017: 0/253, 2018: 1/254, 2019: 0/254, 2020: 1/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| 6J | 2019-05-01 | 3 | 2.00 | 1.32 | 1.32 | 2019: 0/170, 2020: 3/255, 2021: 1/255, 2022: 2/254, 2023: 0/213 |
| 6N | 2019-05-01 | 3 | 0.67 | 0.44 | 0.44 | 2019: 0/170, 2020: 2/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| 6S | 2019-05-01 | 3 | 0.33 | 0.44 | 0.44 | 2019: 0/170, 2020: 0/255, 2021: 0/255, 2022: 1/254, 2023: 1/213 |
| CL | 2010-07-01 | 12 | 0.83 | 0.77 | 1.27 | 2010: 0/124, 2011: 1/246, 2012: 1/245, 2013: 0/240, 2014: 1/241, 2015: 0/246, 2016: 0/246, 2017: 0/245, 2018: 1/246, 2019: 1/246, 2020: 3/247, 2021: 1/246, 2022: 1/246, 2023: 0/205 |
| GC | 2010-06-07 | 12 | 0.67 | 0.67 | 0.62 | 2010: 0/146, 2011: 0/253, 2012: 1/251, 2013: 3/247, 2014: 0/247, 2015: 0/253, 2016: 2/253, 2017: 0/252, 2018: 0/253, 2019: 0/253, 2020: 2/254, 2021: 0/253, 2022: 0/253, 2023: 1/211 |
| HE | 2017-07-03 | 5 | 0.00 | 0.00 | 0.00 | 2017: 0/122, 2018: 0/241, 2019: 0/245, 2020: 0/244, 2021: 0/243, 2022: 0/244, 2023: 0/203 |
| HG | 2019-05-01 | 3 | 0.67 | 0.44 | 0.44 | 2019: 0/170, 2020: 1/254, 2021: 0/253, 2022: 1/253, 2023: 0/211 |
| LE | 2010-07-01 | 12 | 0.08 | 0.16 | 0.43 | 2010: 0/120, 2011: 0/236, 2012: 0/233, 2013: 0/242, 2014: 0/240, 2015: 0/242, 2016: 0/244, 2017: 0/243, 2018: 0/246, 2019: 1/242, 2020: 0/243, 2021: 0/246, 2022: 0/243, 2023: 1/202 |
| MBT | 2021-05-03 | 1 | 2.00 | 1.23 | 1.23 | 2021: 0/166, 2022: 2/246, 2023: 1/205 |
| MCL | 2021-07-12 | 1 | 1.00 | 0.89 | 0.89 | 2021: 1/117, 2022: 1/246, 2023: 0/205 |
| MES | 2019-05-06 | 3 | 1.33 | 1.10 | 1.10 | 2019: 1/167, 2020: 4/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| MGC | 2019-05-01 | 3 | 1.00 | 1.10 | 1.10 | 2019: 0/170, 2020: 2/254, 2021: 1/253, 2022: 0/253, 2023: 2/211 |
| MHG | 2022-05-04 | 0 | - | 0.66 | 0.66 | 2022: 1/168, 2023: 0/211 |
| NG | 2010-06-07 | 12 | 0.75 | 0.69 | 0.42 | 2010: 0/141, 2011: 0/246, 2012: 1/245, 2013: 0/240, 2014: 1/241, 2015: 1/246, 2016: 0/246, 2017: 1/245, 2018: 3/246, 2019: 1/246, 2020: 1/245, 2021: 0/246, 2022: 0/246, 2023: 0/205 |
| NQ | 2010-06-07 | 12 | 1.00 | 0.89 | 0.82 | 2010: 0/145, 2011: 2/254, 2012: 0/254, 2013: 0/248, 2014: 0/246, 2015: 2/255, 2016: 1/254, 2017: 2/253, 2018: 1/254, 2019: 1/254, 2020: 3/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| RTY | 2017-07-10 | 5 | 0.80 | 0.63 | 0.41 | 2017: 0/121, 2018: 2/254, 2019: 0/254, 2020: 2/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| TN | 2016-01-11 | 7 | 0.71 | 0.63 | 0.61 | 2016: 2/248, 2017: 0/253, 2018: 0/253, 2019: 0/254, 2020: 3/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| UB | 2010-07-01 | 12 | 0.50 | 0.45 | 0.82 | 2010: 0/128, 2011: 0/254, 2012: 0/254, 2013: 1/248, 2014: 0/251, 2015: 0/255, 2016: 1/254, 2017: 0/253, 2018: 0/253, 2019: 0/254, 2020: 4/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| YM | 2019-05-01 | 3 | 1.33 | 1.32 | 1.32 | 2019: 2/170, 2020: 3/255, 2021: 1/255, 2022: 0/254, 2023: 0/213 |
| ZB | 2010-07-01 | 12 | 0.58 | 0.52 | 0.82 | 2010: 0/128, 2011: 0/254, 2012: 0/254, 2013: 1/248, 2014: 0/251, 2015: 0/255, 2016: 2/254, 2017: 0/253, 2018: 0/253, 2019: 0/254, 2020: 4/255, 2021: 0/255, 2022: 0/254, 2023: 0/213 |
| ZC | 2010-06-07 | 12 | 0.42 | 0.46 | 0.43 | 2010: 1/142, 2011: 0/246, 2012: 0/246, 2013: 2/244, 2014: 0/245, 2015: 1/246, 2016: 0/248, 2017: 0/246, 2018: 0/246, 2019: 1/242, 2020: 0/244, 2021: 0/246, 2022: 1/245, 2023: 0/206 |
| ZF | 2010-07-01 | 12 | 0.92 | 0.82 | 1.23 | 2010: 0/128, 2011: 0/254, 2012: 0/254, 2013: 2/248, 2014: 1/251, 2015: 0/255, 2016: 1/254, 2017: 0/253, 2018: 1/251, 2019: 0/254, 2020: 4/255, 2021: 2/255, 2022: 0/254, 2023: 0/213 |
| ZL | 2010-07-01 | 12 | 0.33 | 0.31 | 0.21 | 2010: 0/123, 2011: 0/247, 2012: 0/247, 2013: 1/245, 2014: 0/243, 2015: 0/247, 2016: 1/247, 2017: 1/246, 2018: 0/245, 2019: 0/245, 2020: 0/248, 2021: 1/241, 2022: 0/244, 2023: 0/206 |
| ZM | 2019-05-01 | 3 | 0.33 | 0.46 | 0.46 | 2019: 0/161, 2020: 0/239, 2021: 1/245, 2022: 0/242, 2023: 1/206 |
| ZN | 2010-06-07 | 12 | 0.58 | 0.52 | 0.61 | 2010: 0/146, 2011: 0/254, 2012: 0/254, 2013: 2/248, 2014: 0/251, 2015: 0/255, 2016: 1/254, 2017: 0/253, 2018: 1/253, 2019: 0/254, 2020: 2/255, 2021: 1/255, 2022: 0/254, 2023: 0/213 |
| ZS | 2010-07-01 | 12 | 0.58 | 0.62 | 0.63 | 2010: 0/125, 2011: 0/247, 2012: 0/245, 2013: 0/241, 2014: 1/245, 2015: 2/245, 2016: 0/247, 2017: 1/244, 2018: 1/247, 2019: 0/247, 2020: 0/248, 2021: 2/245, 2022: 0/246, 2023: 1/205 |
| ZT | 2010-07-01 | 12 | 1.00 | 0.97 | 1.43 | 2010: 0/128, 2011: 0/254, 2012: 1/254, 2013: 1/248, 2014: 1/251, 2015: 0/255, 2016: 1/254, 2017: 0/253, 2018: 2/253, 2019: 0/254, 2020: 4/255, 2021: 2/255, 2022: 0/254, 2023: 1/213 |
| ZW | 2019-05-01 | 3 | 0.00 | 0.00 | 0.00 | 2019: 0/166, 2020: 0/248, 2021: 0/243, 2022: 0/244, 2023: 0/205 |

## Table 3. Owned files by name (every root), tick source, pilot-window coverage by file names only

| Root | Tick source | First file start | Last file end (excl.) | Files | Files opened (end <= 2023-11-01) | Gaps in file ranges | Pilot window 2023-11-01..2024-02-29 covered by names |
|---|---|---|---|---|---|---|---|
| 6A | rules/products.py:166 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| 6B | rules/products.py:168 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| 6C | rules/products.py:170 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| 6E | rules/products.py:163 | 2010-06-06 | 2026-06-21 | 180 | 161 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| 6J | rules/products.py:171 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| 6N | rules/products.py:173 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| 6S | rules/products.py:172 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| CL | rules/products.py:175 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| E7 | rules/products.py:165 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| GC | rules/products.py:184 | 2010-06-06 | 2026-06-21 | 180 | 161 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| HE | rules/products.py:197 | 2017-07-01 | 2026-06-21 | 95 | 76 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| HG | rules/products.py:188 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| HO | rules/products.py:182 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| LE | rules/products.py:198 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| M2K | rules/products.py:150 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| M6A | rules/products.py:167 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| M6B | rules/products.py:169 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| M6E | rules/products.py:164 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| MBT | rules/products.py:200 | 2021-04-01 | 2026-06-21 | 50 | 31 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| MCL | rules/products.py:176 | 2021-06-01 | 2026-06-21 | 48 | 29 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| MES | rules/products.py:154 | 2019-05-01 | 2026-06-01 | 72 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| MGC | rules/products.py:185 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| MHG | rules/products.py:189 | 2022-04-01 | 2026-06-21 | 38 | 19 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| MNG | rules/products.py:179 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| MNQ | rules/products.py:148 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| MYM | rules/products.py:152 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| NG | rules/products.py:178 | 2010-06-06 | 2026-06-21 | 180 | 161 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| NQ | rules/products.py:147 | 2010-06-06 | 2026-06-21 | 180 | 161 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| QG | rules/products.py:180 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| QM | rules/products.py:177 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| RB | rules/products.py:181 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| RTY | rules/products.py:149 | 2017-06-01 | 2026-06-21 | 96 | 77 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| SI | rules/products.py:186 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| SIL | rules/products.py:187 | 2025-04-01 | 2026-06-21 | 15 | 0 | none | no |
| TN | rules/products.py:159 | 2016-01-01 | 2026-06-21 | 113 | 94 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| UB | rules/products.py:161 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| YM | rules/products.py:151 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZB | rules/products.py:160 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZC | rules/products.py:191 | 2010-06-06 | 2026-06-21 | 180 | 161 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZF | rules/products.py:157 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZL | rules/products.py:195 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZM | rules/products.py:194 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZN | rules/products.py:158 | 2010-06-06 | 2026-06-21 | 180 | 161 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZS | rules/products.py:193 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZT | rules/products.py:156 | 2010-07-01 | 2026-06-21 | 179 | 160 | 2024-03-01..2025-04-01 | yes (4 monthly files) |
| ZW | rules/products.py:192 | 2019-05-01 | 2026-06-21 | 73 | 54 | 2024-03-01..2025-04-01 | yes (4 monthly files) |

## Candidate codes from the spec without owned window data

- No owned ohlcv-1m folder at all (15): MET, ETH, BTC, 2YY, 5YY, 10Y, 30Y, MZC, MZS, MZW, MZL, MZM, XC, XK, XW.
- Owned folder, but no file ends on or before 2023-11-01 (owned files cover only 2025-04-01..2026-06-21, so no statistic here and no pilot-window file by name) (10 spec candidates): M2K, M6A, M6E, MNG, MNQ, MYM, QG, QM, SI, SIL. Non-candidate roots in the same position: E7, HO, M6B, RB.
- Spec candidates with owned window statistics (22): 6A, 6E, CL, GC, HG, MBT, MCL, MGC, MHG, NG, NQ, RTY, YM, ZB, ZC, ZF, ZL, ZM, ZN, ZS, ZT, ZW.
- Owned roots with statistics that are not spec candidates: 6B, 6C, 6J, 6N, 6S, HE, LE, MES, TN, UB.
