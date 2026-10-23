# VERIFY_pilot: independent check of the E.31 ZM pilot kill-rule numbers

PilotVerifier-FableXHigh (worker-xhigh, model fable), written 2026-10-23 13:13 PDT. Spec: reports/stage_e31_pilot_spec.md (v2,
sha256 31d33e68736b..., section 7 governs the gate). Everything below is read-only on the data and the producer's
files; all code is in this folder. Producer's code was not used (a grep for the field name bad_flag_records listed
its line numbers in stats31.py and measure31_core.py; no logic was read). The producer's stats31.json / stats31.md
were opened only after my own K1/K2/K3 (my_numbers.json) and the engine comparisons (engine_compare*.json) were
written. Two things came after that opening and are marked: the 816-date bootstrap pool variant (added after I saw
"pool: all done trade dates" in stats31 meta) and the book-validity paragraph in section 5, which also uses the
producer's README_measure31.md (its description of how F_MAYBE_BAD_BOOK is treated). Holdout: `data.holdout status` run once at the end: unlocks_logged 0, all_ok true (not run at the
start; the brief did not ask for it). REGISTRATION.md is 0 bytes. No Databento call, no network, no commit.

## 1. Result

| Number | Mine | Producer (stats31.json) | Verdict |
|---|---|---|---|
| Population | ZM.v.0, DAY, model c, 764 included dates (of 816 done; 52 excluded: roll_day 23, after_roll_day 20, scheduled_late_open 5, cme_holiday_or_early_close 4), 85,568 placements (112 per date on every date) | 764 / 85,568 | CONFIRMED |
| K2 fills (before any markout drop) | 44,045 (fill rate 51.47%; buy 21,433, sell 22,612); threshold 400 | 44,045 | CONFIRMED (K2 does not hold) |
| K1 dropping: mean N_10(Topstep) = E_10 - 0.264 | -1.233894 over 44,045 fills with a valid markout (0 dropped) | -1.2338944 | CONFIRMED |
| K1 dropping: 95% day-block bootstrap | [-1.25241, -1.21419] (producer's pool and draw, seed 31); [-1.25296, -1.21500] (764 included dates only, seed 31) | [-1.2524068, -1.2141888] | CONFIRMED (exact to 5 decimals under the producer's pool) |
| K1 no-drop: mean and interval | identical to the dropping variant: mo_nd_10 equals mo_10 on all 44,045 fills (0 NaN in both) | identical, 0 dropped | CONFIRMED |
| K1 lower bound vs 0 | -1.2524 (both variants), far below 0: K1 holds, so ZM fails | lower_drop = lower_nodrop = -1.2524; holds true | CONFIRMED |
| Information only, fee 0.528 | mean -1.497894, [-1.51641, -1.47819] | -1.4978944, [-1.5164068, -1.4781888] | CONFIRMED |
| K3 mean round trips per DAY date (model c) | 111.568063 over 764 dates (min 29, median 110, max 221; 0 dates below 20); threshold 20 | 111.56806282722513 | CONFIRMED (K3 does not hold) |
| K3 interval | [109.55334, 113.46106] (ratio of sums over the 816-date pool, seed 31); [109.584, 113.560] (764 dates only) | [109.5533393, 113.4610600] | CONFIRMED (exact under the producer's convention) |
| Verdict | **FAIL**, on K1 alone (both variants); K2 and K3 do not hold; not a PASS, so the "fragile" label does not arise | FAIL, fragile false | CONFIRMED |

Fee independence: the failure does not depend on the fee reading. Gross E_10 (no fee at all) is -0.969894 with
interval [-0.98841, -0.95019] (pool 816, seed 31), so even a zero fee leaves K1 failing; both the 0.264 and the
0.528 readings fail by more than 1.2 ticks. By year the mean N_10 is -1.054 (2020), -1.216 (2021), -1.295 (2022),
-1.207 (2023), -1.180 (2024); by side -1.238 (sell) and -1.230 (buy); all 39 months are negative (the least
negative month is -1.054); median E_10 is -1.0 and 18.8% of fills have E_10 above 0. Terminology note: in
stats31 "holds" means the kill condition holds (so K1 "holds" means ZM fails).

## 2. Step 1: my own numbers (step1_numbers.py, boot_final.py, step1b_sanity.py)

Inputs only: placements.parquet and loop.parquet (and days.parquet for the date set) of the 816 DONE dates in
runs/expected31.txt (816 of 816 have DONE; no extra folder). Primary population = symbol ZM.v.0, session DAY,
model c, both sides, on the 764 days.parquet included dates. K2 = rows with filled. N_10 = mo_10 + c_half - 0.264
(and mo_nd_10 for the no-drop variant), pooled mean over fills (ratio of sums inside each replicate).

Day-block bootstrap, 2,000 replicates, numpy default_rng, rng.integers(0, n, size=(2000, n)). Two resampling pools:
(a) the 764 included dates, (b) all 816 done dates with the 52 excluded dates carrying zero weight (this is what
the producer does: stats31 meta "pool: all done trade dates"). Lower and upper bounds:

| pool | seed 31 | seed 7 | seed 101 | seed 20260 | seed 555 |
|---|---|---|---|---|---|
| 764 dates | [-1.25296, -1.21500] | [-1.25363, -1.21445] | [-1.25237, -1.21582] | [-1.25277, -1.21537] | [-1.25337, -1.21498] |
| 816 dates (producer's) | [-1.25241, -1.21419] | [-1.25256, -1.21572] | [-1.25343, -1.21577] | [-1.25322, -1.21494] | [-1.25336, -1.21509] |

Seed stability: the lower bound moves by at most 0.0007 tick across the four other seeds (764-date pool:
-1.25237 to -1.25363 against -1.25296 at seed 31); the limit in the brief is 0.01. The choice of pool moves the
seed-31 bounds by 0.0006 tick. Both variants give the same numbers because no fill has a dropped markout.

## 3. Step 2: independent engine check of model (c) from raw Z1 MBO

Sampling rule, fixed before any per-date result was looked at: the 10th included ZM.v.0 DAY date (days.parquet
included == True, ascending) of each of 2021, 2022, 2023: 2021-01-15, 2022-01-14, 2023-01-17. All three fell in
January (CST), so DST was not exercised. Second rule, fixed before any summer result was looked at: the 10th
included date on or after 1 July of 2021, 2022, 2023: 2021-07-16, 2022-07-19, 2023-07-18 (CDT). Three extra
adversarial dates were added by looking only at days.parquet counts: 2021-01-04 (a Monday with 40 bad-flag
records), 2022-12-27 (19 crossed moments) and 2023-01-03 (14 crossed moments).

Method (engine_check.py, own code; DBNStore only, no producer code). The instrument of ZM.v.0 on the date comes
from the raw file's own symbology mapping (matches days.parquet instrument_id on all 9 dates and on all 816
dates, see section 5). Records of that instrument are replayed in file order from the 00:00:00Z synthetic clear
of the UTC date: A adds, C removes (every C in the nine days removed the whole resting order: 0 partial cancels,
0 unknown orders, 0 over-size cancels, 0 duplicate adds), M re-prices or re-sizes, T/F/N change nothing. The book
is read only after a record carrying F_LAST. Time axis = running max of ts_event. Grid 08:35..13:10 CT every 5
min (56 times), both sides, j = g + 50 ms, price = best bid (buy) or best ask (sell) of the state at j, window
(j, j + 60.05 s]; fill = first trade record with aggressor A or B printed strictly through the price; mid0 = mid
of the last completed state when the trade record is read; E_10 = side * (mid(t_f + 10 s) - price) / 0.10 USD
(dropping variant: NaN if that state is crossed, locked or one-sided; no-drop: last valid state at or before).
Compared row by row with placements.parquet (model c, ZM.v.0, DAY), key (trade_date, g_ns, side):

| trade date | sample | raw instr. (= days.parquet) | placements | price match | filled match (mine/prod) | t_fill exact (ns) | c_half match | E_10 drop match | E_10 no-drop match | mismatches |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021-01-15 | rule: 10th incl. 2021 | ZMH1 (282089) | 112 | 112/112 | 112/112 (51/51) | 51/51 | 51/51 | 51/51 | 51/51 | 0 |
| 2022-01-14 | rule: 10th incl. 2022 | ZMH2 (689369) | 112 | 112/112 | 112/112 (56/56) | 56/56 | 56/56 | 56/56 | 56/56 | 0 |
| 2023-01-17 | rule: 10th incl. 2023 | ZMH3 (185432) | 112 | 112/112 | 112/112 (62/62) | 62/62 | 62/62 | 62/62 | 62/62 | 0 |
| 2021-07-16 | summer (CDT) 2021 | ZMZ1 (794459) | 112 | 112/112 | 112/112 (48/48) | 48/48 | 48/48 | 48/48 | 48/48 | 0 |
| 2022-07-19 | summer (CDT) 2022 | ZMZ2 (697256) | 112 | 112/112 | 112/112 (58/58) | 58/58 | 58/58 | 58/58 | 58/58 | 0 |
| 2023-07-18 | summer (CDT) 2023 | ZMZ3 (51239) | 112 | 112/112 | 112/112 (57/57) | 57/57 | 57/57 | 57/57 | 57/57 | 0 |
| 2021-01-04 | extra: Monday, bad-flag day | ZMH1 (282089) | 112 | 112/112 | 112/112 (67/67) | 67/67 | 67/67 | 67/67 | 67/67 | 0 |
| 2022-12-27 | extra: 19 crossed moments | ZMH3 (185432) | 112 | 112/112 | 112/112 (70/70) | 70/70 | 70/70 | 70/70 | 70/70 | 0 |
| 2023-01-03 | extra: 14 crossed moments | ZMH3 (185432) | 112 | 112/112 | 112/112 (65/65) | 65/65 | 65/65 | 65/65 | 65/65 | 0 |
| **total** | 9 dates | | **1008** | **1008/1008** | **1008/1008** (534/534) | **534/534** | **534/534** | **534/534** | **534/534** | **0** |

1,008 placements, 534 fills: 0 mismatches in price, fill flag, fill time (to the nanosecond), half-spread
captured, E_10 (dropping) and E_10 (no-drop); maximum absolute difference 0.0 in every comparison. No sampled
fill has an invalid (crossed, locked or one-sided) state inside its 10 s horizon, so no drop is expected, as the
producer found. No through trade falls exactly at j or exactly at the window end (tie sensitivity 0 on all 9
dates).

K3 loop (loop_check.py; section 6 of the spec: one 1-lot order at a time, entry side alternating from buy, join
50 ms after the decision, cancel after 60 s, replace at once, exit decided at t_f, no order decided at or after
13:15 CT). The spec does not say whether the replacement is decided at the cancel decision (j + 60 s) or when the
cancel takes effect (j + 60.05 s). The first reading reproduces the producer exactly on all 9 dates (round
trips, entries filled, orders placed, mean round-trip seconds); the second moves the count by -2 to +3 trips
(at most 3.2%), so the K3 conclusion (about 111 against 20) does not depend on it:

| trade date | producer RT / entries / orders / mean RT s | mine, replacement decided at the cancel decision (j+60 s) | mine, replacement at cancel effective (j+60.05 s) |
|---|---|---|---|
| 2021-01-15 | 105 / 106 / 415 / 158.94 | 105 / 106 / 415 / 158.94 (exact) | 103 / 104 / 413 / 162.03 |
| 2022-01-14 | 103 / 104 / 405 / 162.62 | 103 / 104 / 405 / 162.62 (exact) | 103 / 104 / 405 / 162.62 |
| 2023-01-17 | 140 / 140 / 469 / 118.96 | 140 / 140 / 469 / 118.96 (exact) | 140 / 140 / 469 / 118.96 |
| 2021-07-16 | 93 / 93 / 389 / 180.53 | 93 / 93 / 389 / 180.53 (exact) | 96 / 96 / 394 / 175.07 |
| 2022-07-19 | 95 / 95 / 400 / 176.84 | 95 / 95 / 400 / 176.84 (exact) | 95 / 95 / 400 / 176.84 |
| 2023-07-18 | 94 / 95 / 399 / 177.53 | 94 / 95 / 399 / 177.53 (exact) | 94 / 95 / 398 / 177.53 |
| 2021-01-04 | 171 / 172 / 522 / 98.24 | 171 / 172 / 522 / 98.24 (exact) | 169 / 170 / 517 / 99.41 |
| 2022-12-27 | 124 / 125 / 444 / 134.47 | 124 / 125 / 444 / 134.47 (exact) | 126 / 127 / 447 / 132.34 |
| 2023-01-03 | 160 / 160 / 492 / 105.05 | 160 / 160 / 492 / 105.05 (exact) | 158 / 158 / 490 / 106.38 |

## 4. Step 3: comparison with stats31.json / stats31.md

See section 1: every verdict number agrees. Under the producer's own resampling convention (816-date pool, seed
31, rng.integers) I reproduce its K1 bounds (-1.25241 / -1.21419; fee 0.528: -1.51641 / -1.47819) and its K3
interval (109.55334 / 113.46106) to the printed digits, which also confirms how the producer draws.
stats31.md line 11-14 and 18-19 carry the same values. stats31 checks block: 0 placement rows on non-included
dates, 0 model-c fills that are not "through", 0 fills with t_fill before j, 0 fills with NaN c_half (I
re-derived the same four counts from the tables: all agree).

## 5. Further checks on the whole population (step1b_sanity.py, pop_checks.py, chk_days.py, scan_flags*.py)

- Fill bookkeeping: all 44,045 fills have trigger "through"; wait_s equals (t_fill - j) exactly, minimum 0.0045 s,
  maximum 60.0436 s (inside the 60.05 s window); j - g is 50 ms on every placement; unfilled rows carry no fill time.
- DST and clock: for every one of the 764 included dates the g_ns values convert (zoneinfo America/Chicago) to
  exactly 56 grid times 08:35..13:10 CT with zero seconds, two orders each, on the right local date; 475 of the 764
  dates are in CDT. The 9-date engine check includes three CDT dates.
- Instrument per date: days.parquet instrument_id equals the raw files' ZM.v.0 symbology mapping on all 816 dates
  (0 mismatches).
- Exclusions: the 23 roll_day dates are exactly the 23 dates on which the ZM.v.0 instrument changes; the day after
  each of the 23 is excluded (20 labelled after_roll_day, 2 as roll_day, 1 as cme_holiday_or_early_close); no
  change date or next day is included. Every grains-calendar holiday or late-open date among the 816 (4 holidays,
  8 late opens) is excluded; none is included. The remaining difference between the 20 and 23 is only the label.
- Book-validity flags: a scan of all 39 Z1 files (scan_flags.py, scan_flags2.py) found 5,678 F_MAYBE_BAD_BOOK
  records and 169 non-snapshot F_BAD_TS_RECV records on the ZM.v.0 instrument of its UTC date; every one of them lies
  on a Sunday (UTC date and CT date), between 06:03 and 18:59 CT, before the Monday 00:00Z clear and the Monday
  19:00 CT open; none on any Monday-to-Friday date. So no included DAY session is behind a bad-book flag, whichever way the spec's "until the next
  valid snapshot" is read, and the producer's days.bad_flag_records (Monday dates only, 5,210 on the included
  ones) counts these Sunday records. I did not reproduce its exact per-date numbers (for example 40 on 2021-01-04,
  where I find 35 snapshot records with ts_event from 22:00Z and none after the clear); the count affects nothing
  in the verdict. F_TOB and F_MBP flags occur on no record.
- Manifest: manifest31.json exit_code 3 is RC_QUALITY: the only failed checks are in the Z4 definition files (35
  delivered-bytes-equal-quoted-billable, 8 metadata_partial_empty); no hard check failed and no Z1 check failed.
- Outliers: E_10 ranges from -87.5 to +78 ticks (1st to 99th percentile -6 to +3); the mean cannot be moved by
  them against a 1.23 tick margin over 44,045 fills.

## 6. Defects and caveats

No defect that changes any number or the verdict. Items for the lead to know:
1. The producer resamples all 816 done dates, with the 52 excluded dates at zero weight, not only the 764 measured
   ones. The effect on every bound is below 0.001 tick (K1) and 0.1 on K3 (109.55 against 109.58 lower bound).
   Both readings are defensible against "trade dates resampled with replacement"; the spec does not say.
2. The sampling rule in the brief ("10th included date of each year") landed on January dates only; I added three
   CDT dates and three adversarial dates (labelled above). The population-wide DST grid check covers the rest.
3. Spec ambiguity in section 6 (replacement time) moves K3 by -2 to +3 trips on a date; irrelevant at 111 against 20.
4. Model (c) fills only when the market trades through the order, which is adverse selection by construction
   (mean half-spread captured -0.425 tick, mean 10 s markout -0.545 tick). The pilot's verdict is a statement
   about that gate model, as registered; models (a) and (b) are not checked here and decide nothing.
5. Not done: no raw-file re-derivation of the 764-date population (only 9 dates, 1,008 placements) and no check of
   models (a) or (b), the overnight session, ZM.v.1, ZS/ZL conditions or the implied-liquidity check; the
   markout and loop numbers for the other 755 dates rest on the producer's tables, supported by the 9-date match and
   the population-wide consistency checks above.

## 7. Files in this folder

step1_numbers.py (my_numbers.json), boot_final.py (boot_final.json, gross_e10.json), step1b_sanity.py
(sanity.json), chk_days.py, pop_checks.py, pick_dates.py / pick_summer.py (picked_*.json), extract_raw.py /
extract_extra.py / extract_summer.py (raw_extract/*.parquet, own slices of the raw ZM.v.0 records), engine_check.py
(engine_rows_<date>.parquet, engine_info.json), compare_engine.py (engine_compare*.json), loop_check.py
(loop_check.json), scan_flags.py / scan_flags2.py (scan_flags.json, flagged_records.parquet), make_report.py.
