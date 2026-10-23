# VERIFY_pilot_opus: fresh-context Opus check of the E.31 ZM pilot kill-rule numbers

OpusVerifier-OpusXHigh (Opus 5.5, xhigh), 2026-10-23, 13:17 to 13:39 PDT. Brief:
reports/stage_e31_briefs/brief_opusverify.md (the V46 item 5 substitute for the Fable check). Spec:
reports/stage_e31_pilot_spec.md v2, sha256 31d33e68736b3c13ae46afcd0bf8d28411bbb3d96864802a6193cf5f33b9f61a
(checked at start); section 7 governs the gate.

Order kept. Step 1 came from placements.parquet and loop.parquet with my own code. days.parquet and
data.calendars.grains were used only for the population cross-check. Step 2 rebuilt the book from raw Z1 MBO. It
started at 13:35, after the lead's full pytest run had exited (PID 1387074 gone at 13:34:44, 8.1 GB free). The
sample-date rule was written at 13:19:50 PDT in sample_rule.txt, before any per-date result. stats31.json and
stats31.md were opened only after v1_numbers.json and every v2_cmp_*.json were on disk. Opened last:
work/verify_pilot/ (only its folder names had been listed before, to steer clear of its dates). No producer statistics
or engine module was imported. No Databento call, no network, no writes outside this folder. No ZM record dated on or
after 2024-03-01 was read: the largest ts_event and ts_recv over all 39 Z1 files is 2024-02-29 21:44:27Z.

## 1. Result

| Number | Mine | Producer (stats31.json kill_rule) | Verdict |
|---|---|---|---|
| Population | ZM.v.0, DAY, model c: 764 dates (of 816 done; 52 excluded: roll_day 23, after_roll_day 20, scheduled_late_open 5, cme_holiday_or_early_close 4), 85,568 placements, 112 on every date | 764 dates (K3 block), 85,568 placements (cell table) | CONFIRMED |
| K2 fills (before any drop) | 44,045 (buy 21,433, sell 22,612; fill rate 0.51474; all trigger "through"); threshold 400 | 44,045, holds false | CONFIRMED (K2 does not hold) |
| K1 dropping, mean N_10 = E_10 - 0.264 | -1.2338944 over 44,045 fills, 0 dropped (mean E_10 -0.9698944 = mo_10 -0.5448405 + c_half -0.4250539) | -1.2338944, n 44,045, dropped 0 | CONFIRMED |
| K1 dropping, 95% bound, rng(31) | 764-date pool: [-1.25296, -1.21500]. Producer's pool (all 816 done dates, excluded ones at zero weight): [-1.252407, -1.214189] | [-1.2524068, -1.2141888] | CONFIRMED (exact under the producer's pool; 0.00055 tick apart under mine) |
| K1 no-drop, mean and bound | identical to the dropping variant: mo_nd_10 equals mo_10 on all 44,045 fills (max abs diff 0.0; 0 NaN in either) | identical, dropped 0 | CONFIRMED |
| K1 bound stability (seed-free check) | lower bounds under seeds 31, 7, 2024, 987654: -1.25296, -1.25363, -1.25279, -1.25321; spread 0.00084 tick (< 0.01) | n/a | stable |
| K1 decision | lower bound -1.25 in both variants, far below 0: K1 holds | holds_drop = holds_nodrop = true | CONFIRMED |
| 0.528 bounds (information) | mean -1.4978944; 764 pool [-1.51696, -1.47900]; producer's pool [-1.516407, -1.478189] | -1.4978944, [-1.5164068, -1.4781888] | CONFIRMED |
| K3 mean round trips per DAY date (c) | 111.568063 over 764 loop rows (one per included date; median 110, min 29, max 221; 0 dates below 20); threshold 20 | 111.56806282722513, 764 dates, holds false | CONFIRMED (K3 does not hold) |
| K3 interval | 764 pool [109.584, 113.560]; producer's pool (ratio over the 816 draws) [109.553339, 113.461060] | [109.5533393, 113.4610600] | CONFIRMED (exact under the producer's pool) |
| Verdict | **FAIL**, on K1 alone (both variants). K2 and K3 do not hold. Not a PASS, so "fragile" does not arise | verdict FAIL, fragile false, verdict_line "FAIL" | CONFIRMED |
| Engine sample, model c (raw Z1) | 4 dates, 448 placements, 225 fills: 448/448 prices, 448/448 fill flags, 225/225 fill times, 225/225 E_10 (both variants), 225/225 mid0 | placements.parquet rows | CONFIRMED (0 mismatches) |
| Loop sample, model c (raw Z1, extra) | round trips, entries filled and orders placed equal on all 4 dates (128/129/452, 123/124/446, 155/155/496, 42/42/326) | loop.parquet rows | CONFIRMED (0 mismatches) |

The resampling call does not matter: rng.integers(0, n, (2000, n)) and rng.choice(n, (2000, n)) give identical draws
and identical bounds. Percentiles are numpy linear (2.5, 97.5).

## 2. Step 1 detail (v1_tables.py -> v1_numbers.json; v1b_drops.py; v1c_bootalt.py)

- Calendar: grains-calendar trade dates 2020-12-01..2024-02-29 (weekdays minus FULL_CLOSURE) = 816, exactly the
  dates in expected31.txt (0 either way). Every date has a DONE marker.
- Population. Placement dates equal the included ZM.v.0 dates of days.parquet (764 = 764, 0 either way), and none
  of them is a HOLIDAYS or LATE_OPENS date. The ZM.v.0 instrument_id changes on 23 dates. No change date and no
  following date is in the population.
- Grid. Every g_ns converts (zoneinfo) to a :00-second, 5-minute CT time in 08:35..13:10 on its own trade date
  (0 off-grid). j - g = 50 ms everywhere. 112 placements per date (min = max = 112), 0 duplicate (g, side).
- Fill bookkeeping. 0 fills outside (j, j + 60.05 s). wait_s equals (t_fill - j) on every fill. c_half equals
  s(mid0 - p)/0.1 on every fill. 0 unfilled rows carry a fill time.
- Drops, every cell. 0 NaN in mo_1, mo_10 and mo_60 and their no-drop twins, except one mo_60 drop in each model of
  ZM.v.1 DAY. So the drop path exists, but it never fires in the primary cell.
- Per side (information): mean N_10 is -1.2298 for buys and -1.2378 for sells. The share of fills with E_10 > 0 is 0.1877.

## 3. Step 2: model (c) from the raw Z1 MBO (v2_engine.py, v2b_flags.py, v2c_flagscan.py)

Rule, fixed at 13:19:50 PDT before any per-date result: for each of 2021, 2022 and 2023, the 15th included ZM.v.0
date, skipping the earlier verifier's dates. This gave 2021-01-25, 2022-01-24 and 2023-01-24. One targeted extra,
labelled as such: the first included date with days.bad_flag_records > 0, 2020-12-14.

Method. My own code, DBNStore only. The ZM.v.0 instrument comes from the DBN file's own symbology mapping, and it
equals days.parquet on all 4 dates. Records are the instrument's records with ts_recv in [D-1 16:00 CT, D 16:00 CT),
in file order. Before the first R (clear) record, records are skipped. The order book: A adds, C reduces or removes,
M re-prices or re-sizes (an unknown order is added), and T, F and N change nothing. The best bid and ask are
committed only at records with F_LAST. Time is the running maximum of ts_event (ts_recv for snapshot records).
Grid: 08:35..13:10 CT, both sides, j = g + 50 ms. Price p is the best bid or ask of the last committed state at or
before j. Model (c) fills at the first T record with side A or B and price strictly through p, with t in the open
interval (j, j + 60.05 s). E_10 = s(mid(t_f + 10 s) - p)/tick, where mid is the last valid committed mid at or
before t_f + 10 s. mid0 is the last committed state before the trade record, by record index.

| Date | Instrument | Placements matched | Price | Filled flag | Fills (mine/producer) | t_fill | E_10 drop | E_10 no-drop | mid0 | Invalid book in horizon | Loop RT / entries / orders (mine = producer) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021-01-25 | 282089 ZMH1 | 112/112 | 112 | 112 | 62/62 | 62 | 62 | 62 | 62 | 0 | 128 / 129 / 452 |
| 2022-01-24 | 689369 ZMH2 | 112/112 | 112 | 112 | 63/63 | 63 | 63 | 63 | 63 | 0 | 123 / 124 / 446 |
| 2023-01-24 | 185432 ZMH3 | 112/112 | 112 | 112 | 73/73 | 73 | 73 | 73 | 73 | 0 | 155 / 155 / 496 |
| 2020-12-14 (extra) | 504886 ZMF1 | 112/112 | 112 | 112 | 27/27 | 27 | 27 | 27 | 27 | 0 | 42 / 42 / 326 |
| Total | | 448/448 | 448 | 448 | 225/225 | 225 | 225 | 225 | 225 | 0 | 4/4 dates |

Tolerances: price 1e-9 USD, E_10 1e-6 tick, t_fill exact in ns. Every date had 0 unknown cancels, 0 duplicate adds,
0 unknown modifies and 1 R record (the 18:00 CT / 00:00Z clear). For the loop I read section 6 my own way: cancel
decided at j + 60 s and the replacement joining at j + 60.05 s, the exit decided at the entry fill, the next entry
decided at the exit fill with the side alternating, and no decision at or after 13:15 CT. That reading reproduces the
producer's loop rows exactly on all 4 dates.

Bad-book flags, on the whole window (v2c_flagscan.py, all 39 Z1 files, 58 s, 0.44 GB peak). On the included dates,
ZM.v.0 records flagged F_MAYBE_BAD_BOOK, F_TOB or F_MBP total 5,210 on 55 dates, all Mondays. That equals
days.bad_flag_records on all 764 included dates (40 on 2021-01-04, for example). On 0 dates does a flagged record
come after the first R. Every flagged record falls between Sunday 16:00 CT, where the Monday window starts, and that
date's first R record, so under the spec's validity rule no included DAY session sits behind a bad-book flag. On 2020-12-14, the 24 flagged records
are the 24 records before the first R (16:01 to 17:46 CT Sunday). Records after the R are 0 F_MAYBE_BAD_BOOK,
0 F_TOB, 0 F_MBP and 303 F_SNAPSHOT|F_BAD_TS_RECV.

## 4. Step 3: comparison with stats31.json / stats31.md

Every verdict number agrees; see section 1. stats31.md's verdict table (lines 5-19) and the primary cell table (line
585 on) carry the same values: 85,568 placements, 44,045 fills (46 of them inside the 50 ms cancel latency), fill rate
0.5147, mean c_half -0.4251. The only difference is the bootstrap pool. stats31.json meta.bootstrap says "all done trade
dates; one draw matrix for every statistic". That means 816 dates, with the 52 excluded ones at zero weight. My first
pass resampled the 764 measured dates. Reproducing the producer's pool with rng(31) gives its bounds to 6 decimals
(v3_pool816.py). Both readings fit spec 8's "trade dates resampled with replacement". They differ by at most 0.0008
tick on the K1 bounds and 0.1 on K3, so neither changes the verdict.

## 5. Comparison with the earlier verifier (work/verify_pilot/VERIFY_pilot.md, read last)

- Agreement. Every kill-rule number in its section 1 equals mine, as do the population, the 0-drop finding and the
  pool-convention note. Its 9 engine dates and my 4 do not overlap, and both found 0 mismatches. Together that is 13
  dates and 1,456 placements.
- Loop. It reports that the section 6 replacement-time ambiguity "moves K3 by -2 to +3 trips on a date". My reading
  (replacement decided at j + 60 s, joining at j + 60.05 s) reproduces the producer's loop counts exactly on 4 dates,
  so the producer's loop matches that reading. Either way the effect is irrelevant at 111 against 20.
- Bad-flag counter. It could not reproduce the per-date days.bad_flag_records (it found, for example, 35 snapshot
  records on 2021-01-04 against the producer's 40). The cause is how records are assigned to dates: it used the UTC
  date, while I assign by ts_recv in [D-1 16:00 CT, D 16:00 CT) and count F_MAYBE_BAD_BOOK, F_TOB or F_MBP. With my
  assignment the producer's counter is reproduced on all 764 dates (40 on 2021-01-04). Both verifiers agree that
  every flagged record precedes the date's first clear.

## 6. Defects and caveats

No defect changes a number or the verdict.
1. The no-drop check is degenerate on the primary cell. With 0 drops in the primary cell, the variant SpecReviewer
   item 2 added cannot differ, so K1's "both must clear" reduces to one test here. This is a fact about the data,
   not a code defect: the drop path does fire once, on ZM.v.1 at 60 s.
2. The bootstrap pool convention (816 against 764 dates) is not stated in the spec. It is immaterial here (section 4).
3. The name days.bad_flag_records can mislead. It counts flagged records before the date's first clear, which the
   validity rule ignores, not records under a bad book. Recommendation: say so in the README.
4. Model (c) fills only when the market trades through the order: fills are adversely selected by construction.
   The verdict is a statement about the registered gate model. Models (a) and (b), the overnight session, ZM.v.1,
   the ZS/ZL conditions and the implied check were not checked; they decide nothing.
5. Not done. There is no raw re-derivation of the other 760 dates' fills and markouts, and no raw check of a CDT
   date by me: all 4 of my dates are CST. The earlier verifier's 3 CDT dates and the population-wide grid check
   (every g converts to 08:35..13:10 CT on its own date) cover DST.

## 7. Files (this folder)

sample_rule.txt, sample_dates.json (the rule and dates, with Z1 paths and sha256 from the manifest). v1_tables.py ->
v1_numbers.json (step 1). v1b_drops.py and v1c_bootalt.py (drop census, alternative resampling call).
v2_engine.py -> v2_rows_<date>.parquet and v2_cmp_<date>.json (raw engine and loop check). v2b_flags.py (flag census
of one date). v2c_flagscan.py -> v2c_flagscan.json (all-file flag scan). v3_pool816.py (producer's pool, run after
opening stats31).
