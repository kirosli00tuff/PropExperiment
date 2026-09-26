# Stage E.2a Task 7: research-window bar builds

Generated 2026-09-25T09:46:33.799615+00:00. Trade dates 2025-04-01..2026-06-19; files 2025-04-01..2026-06-21 UTC (end exclusive). Counts, dates and flags only: no return, volatility, volume or coverage statistic and no price summary. Full records: stage_e2a_bars.json.

- First trade date 2025-04-01: its evening segment before 2025-04-01 00:00 UTC is not in the files. As in MES's research build, the trade date is kept (partial) and the expected-minute grid starts at 2025-04-01 00:00 UTC, so the missing evening minutes are neither expected nor gaps (a grain session opens 19:00 CT = 00:00 UTC in CDT and is complete).
- Roll blackout = the splice trade date and the 2 group trade dates before it (data.group_session.roll_blackout, sim.engine.roll_blackout_dates's rule with the group's full closures); any difference from sim.engine's equity-calendar version is listed per product.
- Symbology covers UTC dates 2025-04-01..2026-06-20 (resolve end 2026-06-21, exclusive). A splice dated after 2026-06-20 is not visible from research-window metadata, so a roll on 2026-06-21/22 would put 2026-06-18/19 into a blackout this report cannot show.
- Lead ruling L-3 (01:10 PDT): bars inside a scheduled closure are not a hard failure (MES's convention): kept, flagged in_scheduled_closure, listed per product (closure_bars). A bar in the close minute takes the trade date of the session it closes; any closure bar beyond the close minute holds the product for the lead. Diagnosis recorded for ZN, ZF, ZT: a single print stamped in the 16:00 CT close minute on Fri 2026-03-13 (TN, UB, ZB end at 15:59); not a calendar question.
- Lead ruling L-4 revised (01:21 PDT): no closed window for the 2025-11-28 CME outage in any group; it stays a reported gap run (about 20:44-20:49 CT on 11-27 to 07:30 CT on 11-28) and LATE_OPENS is checked only (the first bar of 2025-11-28 at or after 07:30 CT).
- NG: the first build (01:21 PDT, 45,872 bars) dropped 345,929 bars because the outright pattern accepted a one-digit year only, and NG's raw symbols carry two digits from mid-2025 (NGN25, NGF26). Builder bug, fixed in data.bars.outright_pattern (one or two digits); the wrong parquet was moved to data/processed/NG/superseded/ (not deleted) and NG rebuilt (391,801 bars). No other product had a no-outright drop.
- Volume-ranked flip-flops: NG (2026-01-22/23/25), HO and RB switch back and forth between two contracts on some dates; the per-roll splice test cannot pass for a flip-flop, so each product also carries a day-level check (bars_off_symbology_mapping: 0 bars off the symbology mapping for every product).
- Lead ruling L-6 (01:45 PDT): the grains module's 20 LATE_OPENS are SCHEDULED (no overnight segment; first minute 08:30 CT) and are closed windows (trade dates, flags, expected minutes). Told apart by the module's own type: the grains LateOpen has no stop-time field and its entries are named for the holiday; the rates/FX/energy/metals LateOpen carries halt_from_ct and its one entry is named an outage/unscheduled halt (data.group_session.is_scheduled_late_open refuses a module where the two disagree).
- Vendor price scale: the grid-scale probe shows 0 off-grid prices at 10x and 100x the E.0 tick for ZC, ZW, ZS, ZL, HE and LE: Databento quotes them in cents, so their tick in vendor price units is 100 x the E.0 tick_size (USD). The check ran at the E.0 tick as the brief says (it passes, and is weaker there); the tick was not changed. ZM (USD per short ton) is on the E.0 scale.
- Crypto (MBT), lead rulings L-9 and L-10 (02:17 PDT): BOOKED_FORWARD holidays are not trade dates; their regular session belongs to CME's trade date for them (booked_forward_sessions per product, 7 in the window). 2026-06-19 and the 24/7 weekend are booked to 2026-06-22 (holdout-1): 1,617 bars, Thu 06-18 16:02 to Sat 06-20 18:59 CT, dropped and written nowhere; MBT's last research trade date is 2026-06-18. Day-session quantities are read on the trade date's own CT calendar date (parquet metadata day_session_rule); the flatten flags follow each CT calendar day (MES's rule) plus TopstepX's weekend closure.
- The manifest's per-file instrument_ids come from the files' embedded mappings and can list an id with no bar (a mapping interval that starts on the weekend before the file: MBT 2025-06, 2025-11, 2026-02, 2026-03). The check is that every bar's id is listed; ids without bars are reported per file.
- Products built before a later code change were re-derived with the final code (--refresh): each such parquet equals the final code's table row for row (parquet.rows_equal_to_rebuild_with_current_code); the parquet keeps the builder sha256s stamped at its write, and the summary carries the current ones.

## Per product

| Product | Group | Status | Bars | Trade dates | First | Last | Rolls | Blackout dates in window | Degraded on trade dates | Drops (window / coverage / no outright) | Calendar discrepancies | Build s | Peak MB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MBT | crypto | built | 407393 | 308 | 2025-04-01 | 2026-06-18 | 14 | 42 | 5 | 1617 / 0 / 0 | 15 | 3.6 | 364.0 |
| CL | energy | built | 424910 | 315 | 2025-04-01 | 2026-06-19 | 15 | 45 | 5 | 0 / 0 / 0 | 0 | 3.7 | 360.9 |
| HO | energy | built | 327126 | 315 | 2025-04-01 | 2026-06-19 | 18 | 48 | 5 | 0 / 0 / 0 | 0 | 4.5 | 336.1 |
| MCL | energy | built | 416170 | 315 | 2025-04-01 | 2026-06-19 | 15 | 45 | 5 | 0 / 0 / 0 | 0 | 4.1 | 351.3 |
| MNG | energy | built | 305790 | 315 | 2025-04-01 | 2026-06-19 | 14 | 42 | 5 | 0 / 0 / 0 | 12 | 3.2 | 328.8 |
| NG | energy | built | 391801 | 315 | 2025-04-01 | 2026-06-19 | 16 | 44 | 5 | 0 / 0 / 0 | 0 | 3.7 | 345.1 |
| QG | energy | built | 178979 | 315 | 2025-04-01 | 2026-06-19 | 14 | 42 | 5 | 0 / 0 / 0 | 40 | 2.1 | 296.2 |
| QM | energy | built | 258210 | 315 | 2025-04-01 | 2026-06-19 | 15 | 45 | 5 | 0 / 0 / 0 | 33 | 2.9 | 302.3 |
| RB | energy | built | 330620 | 315 | 2025-04-01 | 2026-06-19 | 25 | 61 | 5 | 0 / 0 / 0 | 0 | 3.2 | 335.1 |
| M2K | equity | built | 419079 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.0 | 360.4 |
| MNQ | equity | built | 432011 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 4.4 | 369.3 |
| MYM | equity | built | 423839 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.4 | 369.3 |
| NQ | equity | built | 431881 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.5 | 366.1 |
| RTY | equity | built | 420497 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.5 | 362.7 |
| YM | equity | built | 423656 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.6 | 362.6 |
| 6A | fx | built | 418305 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 2 | 3.7 | 348.0 |
| 6B | fx | built | 394563 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 4 | 3.5 | 353.1 |
| 6C | fx | built | 373511 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 7 | 3.7 | 347.6 |
| 6E | fx | built | 424708 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 1 | 3.7 | 357.3 |
| 6J | fx | built | 421075 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 3 | 3.9 | 357.3 |
| 6N | fx | built | 386595 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 4 | 4.0 | 348.6 |
| 6S | fx | built | 366753 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 9 | 3.6 | 342.0 |
| E7 | fx | built | 239304 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 86 | 2.8 | 293.1 |
| M6A | fx | built | 278695 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 64 | 3.1 | 325.8 |
| M6B | fx | built | 211257 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 57 | 3.1 | 293.9 |
| M6E | fx | built | 386230 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 9 | 3.9 | 348.0 |
| ZC | grains | built | 243019 | 306 | 2025-04-01 | 2026-06-18 | 12 | 29 | 5 | 0 / 0 / 0 | 0 | 2.5 | 293.4 |
| ZL | grains | built | 283222 | 306 | 2025-04-01 | 2026-06-18 | 6 | 18 | 5 | 0 / 0 / 0 | 0 | 2.6 | 302.2 |
| ZM | grains | built | 240098 | 306 | 2025-04-01 | 2026-06-18 | 11 | 27 | 5 | 0 / 0 / 0 | 0 | 2.5 | 293.1 |
| ZS | grains | built | 277118 | 306 | 2025-04-01 | 2026-06-18 | 7 | 21 | 5 | 0 / 0 / 0 | 0 | 2.4 | 301.0 |
| ZW | grains | built | 247726 | 306 | 2025-04-01 | 2026-06-18 | 9 | 23 | 5 | 0 / 0 / 0 | 0 | 2.5 | 299.5 |
| HE | livestock | built | 83469 | 306 | 2025-04-01 | 2026-06-18 | 13 | 32 | 5 | 0 / 0 / 0 | 0 | 0.9 | 222.1 |
| LE | livestock | built | 83785 | 306 | 2025-04-01 | 2026-06-18 | 19 | 39 | 5 | 0 / 0 / 0 | 0 | 0.9 | 224.6 |
| GC | metals | built | 428393 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 2 | 3.5 | 376.2 |
| HG | metals | built | 399401 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 3 | 3.4 | 359.8 |
| MGC | metals | built | 429238 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 6 | 3.4 | 366.5 |
| MHG | metals | built | 367105 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 4 | 3.5 | 337.4 |
| SI | metals | built | 415684 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 4 | 3.3 | 364.3 |
| SIL | metals | built | 412811 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 6 | 3.7 | 356.8 |
| TN | rates | built | 355564 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.7 | 335.5 |
| UB | rates | built | 372992 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.3 | 343.7 |
| ZB | rates | built | 358068 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.2 | 340.9 |
| ZF | rates | built | 377319 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.3 | 351.2 |
| ZN | rates | built | 396178 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.5 | 351.9 |
| ZT | rates | built | 348230 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.3 | 333.5 |

## Refusals

- none

### 6A (fx, built)

- Parquet: `data/processed/6A/ohlcv-1m_6A_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `41d579724f2e04bb5a6183fde996fe76bb05b78e44cb6cdb49f631a1caa8133b`, 418305 rows, read-only
- Tick 0.00005 (reports/stage_e0_liquidity.json tick_size '0.00005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1505276, 'x100': 1656004}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 6AM5->6AU5 (splice trade date 2025-06-16); 2025-09-15 6AU5->6AZ5 (splice trade date 2025-09-15); 2025-12-15 6AZ5->6AH6 (splice trade date 2025-12-15); 2026-03-16 6AH6->6AM6 (splice trade date 2026-03-16); 2026-06-15 6AM6->6AU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5929
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 10918 {'1': 8617, '2-5': 2091, '6-30': 205, '>30': 5}
- Flag counts: {'in_flatten_window': 13417, 'in_no_new_positions_window': 13417, 'in_scheduled_closure': 0, 'is_roll_session': 6305, 'vendor_degraded_day': 5929, 'bars_with_gap_before': 10918}

### 6B (fx, built)

- Parquet: `data/processed/6B/ohlcv-1m_6B_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `ec0af6afb9541f6ab8ebefe116add156416290ee4faf76a7c962dc261b428fa8`, 394563 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1421981, 'x100': 1562689}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 6BM5->6BU5 (splice trade date 2025-06-16); 2025-09-15 6BU5->6BZ5 (splice trade date 2025-09-15); 2025-12-15 6BZ5->6BH6 (splice trade date 2025-12-15); 2026-03-16 6BH6->6BM6 (splice trade date 2026-03-16); 2026-06-15 6BM6->6BU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5447
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 26009 {'1': 18874, '2-5': 6714, '6-30': 412, '>30': 9}
- Flag counts: {'in_flatten_window': 12326, 'in_no_new_positions_window': 12326, 'in_scheduled_closure': 0, 'is_roll_session': 5935, 'vendor_degraded_day': 5447, 'bars_with_gap_before': 26009}

### 6C (fx, built)

- Parquet: `data/processed/6C/ohlcv-1m_6C_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `5c39143960d544c11b4fb9790e64450e98faee60cb07fe8d7e2ee4eccca52eb8`, 373511 rows, read-only
- Tick 0.00005 (reports/stage_e0_liquidity.json tick_size '0.00005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1343676, 'x100': 1479113}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 6CM5->6CU5 (splice trade date 2025-06-16); 2025-09-15 6CU5->6CZ5 (splice trade date 2025-09-15); 2025-12-15 6CZ5->6CH6 (splice trade date 2025-12-15); 2026-03-16 6CH6->6CM6 (splice trade date 2026-03-16); 2026-06-15 6CM6->6CU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5150
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 38327 {'1': 26703, '2-5': 10869, '6-30': 748, '>30': 7}
- Flag counts: {'in_flatten_window': 13146, 'in_no_new_positions_window': 13146, 'in_scheduled_closure': 0, 'is_roll_session': 5681, 'vendor_degraded_day': 5150, 'bars_with_gap_before': 38327}

### 6E (fx, built)

- Parquet: `data/processed/6E/ohlcv-1m_6E_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `32738b639684cc382cc06597bb39ea9c4c7d5df0925bc40977c1e6ebc53bc8d5`, 424708 rows, read-only
- Tick 0.00005 (reports/stage_e0_liquidity.json tick_size '0.00005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1527808, 'x100': 1681646}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 6EM5->6EU5 (splice trade date 2025-06-16); 2025-09-15 6EU5->6EZ5 (splice trade date 2025-09-15); 2025-12-15 6EZ5->6EH6 (splice trade date 2025-12-15); 2026-03-16 6EH6->6EM6 (splice trade date 2026-03-16); 2026-06-15 6EM6->6EU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6035
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 7245 {'1': 6008, '2-5': 1174, '6-30': 61, '>30': 2}
- Flag counts: {'in_flatten_window': 15216, 'in_no_new_positions_window': 15216, 'in_scheduled_closure': 0, 'is_roll_session': 6412, 'vendor_degraded_day': 6035, 'bars_with_gap_before': 7245}

### 6J (fx, built)

- Parquet: `data/processed/6J/ohlcv-1m_6J_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `bf8f6a218c01e05cbad48488d0d3c3e71e7076afacd2c9f12914a2f87142bbb2`, 421075 rows, read-only
- Tick 0.0000005 (reports/stage_e0_liquidity.json tick_size '0.0000005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1514278, 'x100': 1667391}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 6JM5->6JU5 (splice trade date 2025-06-16); 2025-09-15 6JU5->6JZ5 (splice trade date 2025-09-15); 2025-12-15 6JZ5->6JH6 (splice trade date 2025-12-15); 2026-03-16 6JH6->6JM6 (splice trade date 2026-03-16); 2026-06-15 6JM6->6JU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5962
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 9597 {'1': 7687, '2-5': 1793, '6-30': 115, '>30': 2}
- Flag counts: {'in_flatten_window': 14513, 'in_no_new_positions_window': 14513, 'in_scheduled_closure': 0, 'is_roll_session': 6341, 'vendor_degraded_day': 5962, 'bars_with_gap_before': 9597}

### 6N (fx, built)

- Parquet: `data/processed/6N/ohlcv-1m_6N_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `d6497c80be6ef65c5d58b29152fffd6fe6dcdc4fe1ad927a0449e226810dc6e8`, 386595 rows, read-only
- Tick 0.00005 (reports/stage_e0_liquidity.json tick_size '0.00005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1391773, 'x100': 1531895}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-15 6NM5->6NU5 (splice trade date 2025-06-16); 2025-09-12 6NU5->6NZ5 (splice trade date 2025-09-12); 2025-12-15 6NZ5->6NH6 (splice trade date 2025-12-15); 2026-03-16 6NH6->6NM6 (splice trade date 2026-03-16); 2026-06-15 6NM6->6NU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-10, 2025-09-11, 2025-09-12, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5258
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 32192 {'1': 24146, '2-5': 7597, '6-30': 440, '>30': 9}
- Flag counts: {'in_flatten_window': 11176, 'in_no_new_positions_window': 11176, 'in_scheduled_closure': 0, 'is_roll_session': 5898, 'vendor_degraded_day': 5258, 'bars_with_gap_before': 32192}

### 6S (fx, built)

- Parquet: `data/processed/6S/ohlcv-1m_6S_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `579bce49a102928240088400b4ba4d6398fe5974ef7b5dab43326a2ba1fbf27c`, 366753 rows, read-only
- Tick 0.00005 (reports/stage_e0_liquidity.json tick_size '0.00005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1317718, 'x100': 1451917}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 6SM5->6SU5 (splice trade date 2025-06-16); 2025-09-15 6SU5->6SZ5 (splice trade date 2025-09-15); 2025-12-15 6SZ5->6SH6 (splice trade date 2025-12-15); 2026-03-15 6SH6->6SM6 (splice trade date 2026-03-16); 2026-06-15 6SM6->6SU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5236
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 37658 {'1': 24718, '2-5': 11653, '6-30': 1261, '>30': 26}
- Flag counts: {'in_flatten_window': 11171, 'in_no_new_positions_window': 11171, 'in_scheduled_closure': 0, 'is_roll_session': 5730, 'vendor_degraded_day': 5236, 'bars_with_gap_before': 37658}

### CL (energy, built)

- Parquet: `data/processed/CL/ohlcv-1m_CL_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `589b824c8a622b1fb583c36a0226d845bd427dd2a00f2b0c659f66cbb9a08c4b`, 424910 rows, read-only
- Tick 0.01 (reports/stage_e0_liquidity.json tick_size '0.01'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1525601, 'x100': 1682362}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-17 CLK5->CLM5 (splice trade date 2025-04-17); 2025-05-18 CLM5->CLN5 (splice trade date 2025-05-19); 2025-06-16 CLN5->CLQ5 (splice trade date 2025-06-16); 2025-07-18 CLQ5->CLU5 (splice trade date 2025-07-18); 2025-08-18 CLU5->CLV5 (splice trade date 2025-08-18); 2025-09-19 CLV5->CLX5 (splice trade date 2025-09-19); 2025-10-17 CLX5->CLZ5 (splice trade date 2025-10-17); 2025-11-19 CLZ5->CLF6 (splice trade date 2025-11-19); 2025-12-18 CLF6->CLG6 (splice trade date 2025-12-18); 2026-01-16 CLG6->CLH6 (splice trade date 2026-01-16); 2026-02-19 CLH6->CLJ6 (splice trade date 2026-02-19); 2026-03-19 CLJ6->CLK6 (splice trade date 2026-03-19); 2026-04-19 CLK6->CLM6 (splice trade date 2026-04-20); 2026-05-18 CLM6->CLN6 (splice trade date 2026-05-18); 2026-06-18 CLN6->CLQ6 (splice trade date 2026-06-18)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-15, 2025-04-16, 2025-04-17, 2025-05-15, 2025-05-16, 2025-05-19, 2025-06-12, 2025-06-13, 2025-06-16, 2025-07-16, 2025-07-17, 2025-07-18, 2025-08-14, 2025-08-15, 2025-08-18, 2025-09-17, 2025-09-18, 2025-09-19, 2025-10-15, 2025-10-16, 2025-10-17, 2025-11-17, 2025-11-18, 2025-11-19, 2025-12-16, 2025-12-17, 2025-12-18, 2026-01-14, 2026-01-15, 2026-01-16, 2026-02-17, 2026-02-18, 2026-02-19, 2026-03-17, 2026-03-18, 2026-03-19, 2026-04-16, 2026-04-17, 2026-04-20, 2026-05-14, 2026-05-15, 2026-05-18, 2026-06-16, 2026-06-17, 2026-06-18
- Splice check: 15/15 consistent; instrument changes in bars 15, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6044
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 5349 {'1': 4278, '2-5': 1030, '6-30': 39, '>30': 2}
- Flag counts: {'in_flatten_window': 15743, 'in_no_new_positions_window': 15743, 'in_scheduled_closure': 0, 'is_roll_session': 20178, 'vendor_degraded_day': 6044, 'bars_with_gap_before': 5349}

### E7 (fx, built)

- Parquet: `data/processed/E7/ohlcv-1m_E7_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `3c44af807c4be19346c9a6cea8f00eb75f9f234e28e327d914e4b0c33327f138`, 239304 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 856739, 'x100': 946994}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 E7M5->E7U5 (splice trade date 2025-06-16); 2025-09-15 E7U5->E7Z5 (splice trade date 2025-09-15); 2025-12-15 E7Z5->E7H6 (splice trade date 2025-12-15); 2026-03-16 E7H6->E7M6 (splice trade date 2026-03-16); 2026-06-15 E7M6->E7U6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3598
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 79885 {'2-5': 32740, '1': 40544, '6-30': 6536, '>30': 65}
- Flag counts: {'in_flatten_window': 7204, 'in_no_new_positions_window': 7204, 'in_scheduled_closure': 0, 'is_roll_session': 3506, 'vendor_degraded_day': 3598, 'bars_with_gap_before': 79884}

### GC (metals, built)

- Parquet: `data/processed/GC/ohlcv-1m_GC_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `fa8c47a0eb2bed8860caaac7831ce9d374dddd06b0269c494c5c7602d08f9c65`, 428393 rows, read-only
- Tick 0.10 (reports/stage_e0_liquidity.json tick_size '0.10'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1514178, 'x100': 1693195}
- Calendar modules: {'data/calendars/metals.py': '8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 GCM5->GCQ5 (splice trade date 2025-05-30); 2025-07-31 GCQ5->GCZ5 (splice trade date 2025-07-31); 2025-11-27 GCZ5->GCG6 (splice trade date 2025-11-27); 2026-01-30 GCG6->GCJ6 (splice trade date 2026-01-30); 2026-03-30 GCJ6->GCM6 (splice trade date 2026-03-30); 2026-05-29 GCM6->GCQ6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-07-29, 2025-07-30, 2025-07-31, 2025-11-25, 2025-11-26, 2025-11-27, 2026-01-28, 2026-01-29, 2026-01-30, 2026-03-26, 2026-03-27, 2026-03-30, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6178
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 1641 {'1': 1017, '2-5': 510, '6-30': 107, '>30': 7}
- Flag counts: {'in_flatten_window': 15681, 'in_no_new_positions_window': 15681, 'in_scheduled_closure': 0, 'is_roll_session': 7624, 'vendor_degraded_day': 6178, 'bars_with_gap_before': 1641}

### HE (livestock, built)

- Parquet: `data/processed/HE/ohlcv-1m_HE_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `7188ac519e199e6cdbe0a7bb50b5a462e16d9922a3c548c2b58d7c604f17cce6`, 83469 rows, read-only
- Tick 0.00025 (reports/stage_e0_liquidity.json tick_size '0.00025 (USD per pound)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 0, 'x100': 0}
- Calendar modules: {'data/calendars/livestock.py': '57727e68c448153ed018d0c0d0f03107db56d93e26da190e6d356f34e743c501', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-19 HEM5->HEN5 (splice trade date 2025-05-19); 2025-06-15 HEN5->HEQ5 (splice trade date 2025-06-16); 2025-07-17 HEQ5->HEV5 (splice trade date 2025-07-17); 2025-07-18 HEV5->HEQ5 (splice trade date 2025-07-18); 2025-07-20 HEQ5->HEV5 (splice trade date 2025-07-21); 2025-09-17 HEV5->HEZ5 (splice trade date 2025-09-17); 2025-11-17 HEZ5->HEG6 (splice trade date 2025-11-17); 2026-01-19 HEG6->HEJ6 (splice trade date 2026-01-20); 2026-03-15 HEJ6->HEM6 (splice trade date 2026-03-16); 2026-03-16 HEM6->HEJ6 (splice trade date 2026-03-16); 2026-03-20 HEJ6->HEM6 (splice trade date 2026-03-20); 2026-05-18 HEM6->HEN6 (splice trade date 2026-05-18); 2026-06-14 HEN6->HEQ6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-15, 2025-05-16, 2025-05-19, 2025-06-12, 2025-06-13, 2025-06-16, 2025-07-15, 2025-07-16, 2025-07-17, 2025-07-18, 2025-07-21, 2025-09-15, 2025-09-16, 2025-09-17, 2025-11-13, 2025-11-14, 2025-11-17, 2026-01-15, 2026-01-16, 2026-01-20, 2026-03-12, 2026-03-13, 2026-03-16, 2026-03-18, 2026-03-19, 2026-03-20, 2026-05-14, 2026-05-15, 2026-05-18, 2026-06-11, 2026-06-12, 2026-06-15
- sim.engine.roll_blackout_dates (equity calendar) differs on: ['2026-01-15', '2026-01-19']
- Splice check: 8/13 consistent; instrument changes in bars 11, unexplained 3
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 1312
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 550 {'1': 532, '2-5': 18}
- Flag counts: {'in_flatten_window': 637, 'in_no_new_positions_window': 637, 'in_scheduled_closure': 0, 'is_roll_session': 3266, 'vendor_degraded_day': 1312, 'bars_with_gap_before': 550}

### HG (metals, built)

- Parquet: `data/processed/HG/ohlcv-1m_HG_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `ebce30184089590ef65c800e0a45c354def557b867447c23fa995d995a6179e9`, 399401 rows, read-only
- Tick 0.0005 (reports/stage_e0_liquidity.json tick_size '0.0005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1424698, 'x100': 1580904}
- Calendar modules: {'data/calendars/metals.py': '8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-28 HGK5->HGN5 (splice trade date 2025-04-28); 2025-06-26 HGN5->HGU5 (splice trade date 2025-06-26); 2025-08-27 HGU5->HGZ5 (splice trade date 2025-08-27); 2025-11-26 HGZ5->HGH6 (splice trade date 2025-11-26); 2026-02-26 HGH6->HGK6 (splice trade date 2026-02-26); 2026-04-29 HGK6->HGN6 (splice trade date 2026-04-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-24, 2025-04-25, 2025-04-28, 2025-06-24, 2025-06-25, 2025-06-26, 2025-08-25, 2025-08-26, 2025-08-27, 2025-11-24, 2025-11-25, 2025-11-26, 2026-02-24, 2026-02-25, 2026-02-26, 2026-04-27, 2026-04-28, 2026-04-29
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5631
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 21752 {'1': 15881, '2-5': 5560, '6-30': 305, '>30': 6}
- Flag counts: {'in_flatten_window': 13097, 'in_no_new_positions_window': 13097, 'in_scheduled_closure': 0, 'is_roll_session': 7430, 'vendor_degraded_day': 5631, 'bars_with_gap_before': 21752}

### HO (energy, built)

- Parquet: `data/processed/HO/ohlcv-1m_HO_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `a5cde179158087720c1d1f3cb210fe66934b3adadddc3d33d923023a095b6781`, 327126 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1159744, 'x100': 1289580}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-10 HOK5->HOM5 (splice trade date 2025-04-10); 2025-05-16 HOM5->HON5 (splice trade date 2025-05-16); 2025-06-16 HON5->HOQ5 (splice trade date 2025-06-16); 2025-07-17 HOQ5->HOU5 (splice trade date 2025-07-17); 2025-08-20 HOU5->HOV5 (splice trade date 2025-08-20); 2025-09-18 HOV5->HOX5 (splice trade date 2025-09-18); 2025-10-17 HOX5->HOZ5 (splice trade date 2025-10-17); 2025-11-16 HOZ5->HOF6 (splice trade date 2025-11-17); 2025-12-18 HOF6->HOG6 (splice trade date 2025-12-18); 2026-01-16 HOG6->HOH6 (splice trade date 2026-01-16); 2026-02-19 HOH6->HOJ6 (splice trade date 2026-02-19); 2026-03-08 HOJ6->HOM6 (splice trade date 2026-03-09); 2026-03-09 HOM6->HOK6 (splice trade date 2026-03-09); 2026-03-11 HOK6->HOJ6 (splice trade date 2026-03-11); 2026-03-12 HOJ6->HOK6 (splice trade date 2026-03-12); 2026-04-19 HOK6->HOM6 (splice trade date 2026-04-20); 2026-05-20 HOM6->HON6 (splice trade date 2026-05-20); 2026-06-18 HON6->HOQ6 (splice trade date 2026-06-18)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-08, 2025-04-09, 2025-04-10, 2025-05-14, 2025-05-15, 2025-05-16, 2025-06-12, 2025-06-13, 2025-06-16, 2025-07-15, 2025-07-16, 2025-07-17, 2025-08-18, 2025-08-19, 2025-08-20, 2025-09-16, 2025-09-17, 2025-09-18, 2025-10-15, 2025-10-16, 2025-10-17, 2025-11-13, 2025-11-14, 2025-11-17, 2025-12-16, 2025-12-17, 2025-12-18, 2026-01-14, 2026-01-15, 2026-01-16, 2026-02-17, 2026-02-18, 2026-02-19, 2026-03-05, 2026-03-06, 2026-03-09, 2026-03-10, 2026-03-11, 2026-03-12, 2026-04-16, 2026-04-17, 2026-04-20, 2026-05-18, 2026-05-19, 2026-05-20, 2026-06-16, 2026-06-17, 2026-06-18
- Splice check: 13/18 consistent; instrument changes in bars 18, unexplained 5
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 4406
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 41503 {'1': 22263, '2-5': 15280, '6-30': 3926, '>30': 34}
- Flag counts: {'in_flatten_window': 12260, 'in_no_new_positions_window': 12260, 'in_scheduled_closure': 0, 'is_roll_session': 18345, 'vendor_degraded_day': 4406, 'bars_with_gap_before': 41503}

### LE (livestock, built)

- Bars inside a scheduled closure (kept, flagged in_scheduled_closure; ruling L-3): 2025-04-17 Thu 13:05 CT -> trade date 2025-04-17 (close minute)
- Parquet: `data/processed/LE/ohlcv-1m_LE_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `883b34eb75e2d79b3d6e56daf1e3dba18d89b3fd97b301a68e9e09a86255cd91`, 83785 rows, read-only
- Tick 0.00025 (reports/stage_e0_liquidity.json tick_size '0.00025 (USD per pound)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 0, 'x100': 0}
- Calendar modules: {'data/calendars/livestock.py': '57727e68c448153ed018d0c0d0f03107db56d93e26da190e6d356f34e743c501', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-15 LEM5->LEQ5 (splice trade date 2025-05-15); 2025-05-16 LEQ5->LEM5 (splice trade date 2025-05-16); 2025-05-18 LEM5->LEQ5 (splice trade date 2025-05-19); 2025-07-17 LEQ5->LEV5 (splice trade date 2025-07-17); 2025-07-18 LEV5->LEQ5 (splice trade date 2025-07-18); 2025-07-23 LEQ5->LEV5 (splice trade date 2025-07-23); 2025-09-15 LEV5->LEZ5 (splice trade date 2025-09-15); 2025-09-17 LEZ5->LEV5 (splice trade date 2025-09-17); 2025-09-18 LEV5->LEZ5 (splice trade date 2025-09-18); 2025-11-17 LEZ5->LEG6 (splice trade date 2025-11-17); 2025-11-26 LEG6->LEM6 (splice trade date 2025-11-26); 2025-11-27 LEM6->LEG6 (splice trade date 2025-11-28); 2026-01-15 LEG6->LEJ6 (splice trade date 2026-01-15); 2026-01-16 LEJ6->LEG6 (splice trade date 2026-01-16); 2026-01-18 LEG6->LEJ6 (splice trade date 2026-01-20); 2026-03-16 LEJ6->LEM6 (splice trade date 2026-03-16); 2026-03-18 LEM6->LEJ6 (splice trade date 2026-03-18); 2026-03-19 LEJ6->LEM6 (splice trade date 2026-03-19); 2026-05-15 LEM6->LEQ6 (splice trade date 2026-05-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-13, 2025-05-14, 2025-05-15, 2025-05-16, 2025-05-19, 2025-07-15, 2025-07-16, 2025-07-17, 2025-07-18, 2025-07-21, 2025-07-22, 2025-07-23, 2025-09-11, 2025-09-12, 2025-09-15, 2025-09-16, 2025-09-17, 2025-09-18, 2025-11-13, 2025-11-14, 2025-11-17, 2025-11-24, 2025-11-25, 2025-11-26, 2025-11-28, 2026-01-13, 2026-01-14, 2026-01-15, 2026-01-16, 2026-01-20, 2026-03-12, 2026-03-13, 2026-03-16, 2026-03-17, 2026-03-18, 2026-03-19, 2026-05-13, 2026-05-14, 2026-05-15
- sim.engine.roll_blackout_dates (equity calendar) differs on: ['2025-11-27', '2026-01-19']
- Splice check: 2/19 consistent; instrument changes in bars 19, unexplained 17
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 1315
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 141 {'1': 104, '2-5': 27, '6-30': 10}
- Flag counts: {'in_flatten_window': 639, 'in_no_new_positions_window': 639, 'in_scheduled_closure': 1, 'is_roll_session': 5144, 'vendor_degraded_day': 1315, 'bars_with_gap_before': 141}

### M2K (equity, built)

- Parquet: `data/processed/M2K/ohlcv-1m_M2K_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `fb08ff51bb7c5e85208bdf567e6d09a7dec654c9c6ab47f427b5118c3852f7dc`, 419079 rows, read-only
- Tick 0.10 (reports/stage_e0_liquidity.json tick_size '0.10'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1496914, 'x100': 1657862}
- Calendar modules: {'data/cme_calendar.py': '61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89', 'data/calendars/equity.py': '3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-18 M2KM5->M2KU5 (splice trade date 2025-06-18); 2025-09-17 M2KU5->M2KZ5 (splice trade date 2025-09-17); 2025-12-17 M2KZ5->M2KH6 (splice trade date 2025-12-17); 2026-03-18 M2KH6->M2KM6 (splice trade date 2026-03-18); 2026-06-17 M2KM6->M2KU6 (splice trade date 2026-06-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-15, 2025-09-16, 2025-09-17, 2025-12-15, 2025-12-16, 2025-12-17, 2026-03-16, 2026-03-17, 2026-03-18, 2026-06-15, 2026-06-16, 2026-06-17
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5739
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 10313 {'1': 8522, '2-5': 1755, '6-30': 35, '>30': 1}
- Flag counts: {'in_flatten_window': 15746, 'in_no_new_positions_window': 15746, 'in_scheduled_closure': 0, 'is_roll_session': 6394, 'vendor_degraded_day': 5739, 'bars_with_gap_before': 10313}

### M6A (fx, built)

- Parquet: `data/processed/M6A/ohlcv-1m_M6A_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `1edea024a19420cc10a73e03a2ccc0f962b122797d2a4120c21f683512dd86a1`, 278695 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1000281, 'x100': 1102070}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 M6AM5->M6AU5 (splice trade date 2025-06-16); 2025-09-15 M6AU5->M6AZ5 (splice trade date 2025-09-15); 2025-12-15 M6AZ5->M6AH6 (splice trade date 2025-12-15); 2026-03-16 M6AH6->M6AM6 (splice trade date 2026-03-16); 2026-06-15 M6AM6->M6AU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3719
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 78569 {'1': 44793, '2-5': 30473, '6-30': 3281, '>30': 22}
- Flag counts: {'in_flatten_window': 8735, 'in_no_new_positions_window': 8735, 'in_scheduled_closure': 0, 'is_roll_session': 3853, 'vendor_degraded_day': 3719, 'bars_with_gap_before': 78569}

### M6B (fx, built)

- Parquet: `data/processed/M6B/ohlcv-1m_M6B_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `3b1cacc19d3727e111f16709ce30eefada71ed4a701c36ca1d254679c6503633`, 211257 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 756175, 'x100': 836051}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 M6BM5->M6BU5 (splice trade date 2025-06-16); 2025-09-15 M6BU5->M6BZ5 (splice trade date 2025-09-15); 2025-12-15 M6BZ5->M6BH6 (splice trade date 2025-12-15); 2026-03-16 M6BH6->M6BM6 (splice trade date 2026-03-16); 2026-06-15 M6BM6->M6BU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 2789
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 84151 {'2-5': 36341, '1': 39396, '6-30': 8343, '>30': 71}
- Flag counts: {'in_flatten_window': 7388, 'in_no_new_positions_window': 7388, 'in_scheduled_closure': 0, 'is_roll_session': 2750, 'vendor_degraded_day': 2789, 'bars_with_gap_before': 84151}

### M6E (fx, built)

- Parquet: `data/processed/M6E/ohlcv-1m_M6E_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `c1cd01a3741a5097bfdf9cbf2d250f3c0a1201bf1c7b2e86a8ddee3dac71efbb`, 386230 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1387788, 'x100': 1529522}
- Calendar modules: {'data/calendars/fx.py': '07bdf8c6e4363d5626e655841dbb4ffa65458cd66d5b273a069ed4e47eb746b6', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-16 M6EM5->M6EU5 (splice trade date 2025-06-16); 2025-09-15 M6EU5->M6EZ5 (splice trade date 2025-09-15); 2025-12-15 M6EZ5->M6EH6 (splice trade date 2025-12-15); 2026-03-16 M6EH6->M6EM6 (splice trade date 2026-03-16); 2026-06-15 M6EM6->M6EU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5472
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 33203 {'1': 24823, '2-5': 7993, '6-30': 383, '>30': 4}
- Flag counts: {'in_flatten_window': 13612, 'in_no_new_positions_window': 13612, 'in_scheduled_closure': 0, 'is_roll_session': 5902, 'vendor_degraded_day': 5472, 'bars_with_gap_before': 33203}

### MBT (crypto, built)

- Parquet: `data/processed/MBT/ohlcv-1m_MBT_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `78ef1710165fd3a184d84d5e544526c85b6608355178b2b62ec60550d479cf14`, 407393 rows, read-only
- Tick 5.00 (reports/stage_e0_liquidity.json tick_size '5.00 (USD per bitcoin)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1453143, 'x100': 1617004}
- Calendar modules: {'data/calendars/crypto.py': '683807b74d5fb888dcdbcb61ec816adc436a7edec4da28576ebc267a07d97227', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-27 MBTJ5->MBTK5 (splice trade date 2025-04-28); 2025-06-01 MBTK5->MBTM5 (splice trade date 2025-06-02); 2025-06-29 MBTM5->MBTN5 (splice trade date 2025-06-30); 2025-07-27 MBTN5->MBTQ5 (splice trade date 2025-07-28); 2025-08-31 MBTQ5->MBTU5 (splice trade date 2025-09-02); 2025-09-28 MBTU5->MBTV5 (splice trade date 2025-09-29); 2025-11-02 MBTV5->MBTX5 (splice trade date 2025-11-03); 2025-11-30 MBTX5->MBTZ5 (splice trade date 2025-12-01); 2025-12-28 MBTZ5->MBTF6 (splice trade date 2025-12-29); 2026-02-01 MBTF6->MBTG6 (splice trade date 2026-02-02); 2026-03-01 MBTG6->MBTH6 (splice trade date 2026-03-02); 2026-03-29 MBTH6->MBTJ6 (splice trade date 2026-03-30); 2026-04-26 MBTJ6->MBTK6 (splice trade date 2026-04-27); 2026-05-30 MBTK6->MBTM6 (splice trade date 2026-06-01)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-24, 2025-04-25, 2025-04-28, 2025-05-29, 2025-05-30, 2025-06-02, 2025-06-26, 2025-06-27, 2025-06-30, 2025-07-24, 2025-07-25, 2025-07-28, 2025-08-28, 2025-08-29, 2025-09-02, 2025-09-25, 2025-09-26, 2025-09-29, 2025-10-30, 2025-10-31, 2025-11-03, 2025-11-26, 2025-11-28, 2025-12-01, 2025-12-24, 2025-12-26, 2025-12-29, 2026-01-29, 2026-01-30, 2026-02-02, 2026-02-26, 2026-02-27, 2026-03-02, 2026-03-26, 2026-03-27, 2026-03-30, 2026-04-23, 2026-04-24, 2026-04-27, 2026-05-28, 2026-05-29, 2026-06-01
- sim.engine.roll_blackout_dates (equity calendar) differs on: ['2025-08-28', '2025-09-01', '2025-11-26', '2025-11-27']
- Splice check: 14/14 consistent; instrument changes in bars 14, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5344
- Drops: before window {}; after window {'2026-06-22': 1617}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 17280 {'1': 12940, '2-5': 3831, '6-30': 474, '>30': 35}
- Flag counts: {'in_flatten_window': 17853, 'in_no_new_positions_window': 17853, 'in_scheduled_closure': 0, 'is_roll_session': 20440, 'vendor_degraded_day': 5344, 'bars_with_gap_before': 17280}

### MCL (energy, built)

- Parquet: `data/processed/MCL/ohlcv-1m_MCL_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `6be9bb5ba95ab66515c8a4739bfcbc82894f8602619ff97ab8ee9799d2e2cd69`, 416170 rows, read-only
- Tick 0.01 (reports/stage_e0_liquidity.json tick_size '0.01'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1488604, 'x100': 1647578}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-20 MCLK5->MCLM5 (splice trade date 2025-04-21); 2025-05-19 MCLM5->MCLN5 (splice trade date 2025-05-19); 2025-06-19 MCLN5->MCLQ5 (splice trade date 2025-06-19); 2025-07-21 MCLQ5->MCLU5 (splice trade date 2025-07-21); 2025-08-20 MCLU5->MCLV5 (splice trade date 2025-08-20); 2025-09-21 MCLV5->MCLX5 (splice trade date 2025-09-22); 2025-10-20 MCLX5->MCLZ5 (splice trade date 2025-10-20); 2025-11-20 MCLZ5->MCLF6 (splice trade date 2025-11-20); 2025-12-19 MCLF6->MCLG6 (splice trade date 2025-12-19); 2026-01-18 MCLG6->MCLH6 (splice trade date 2026-01-19); 2026-02-20 MCLH6->MCLJ6 (splice trade date 2026-02-20); 2026-03-20 MCLJ6->MCLK6 (splice trade date 2026-03-20); 2026-04-20 MCLK6->MCLM6 (splice trade date 2026-04-20); 2026-05-18 MCLM6->MCLN6 (splice trade date 2026-05-18); 2026-06-19 MCLN6->MCLQ6 (splice trade date 2026-06-19)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-16, 2025-04-17, 2025-04-21, 2025-05-15, 2025-05-16, 2025-05-19, 2025-06-17, 2025-06-18, 2025-06-19, 2025-07-17, 2025-07-18, 2025-07-21, 2025-08-18, 2025-08-19, 2025-08-20, 2025-09-18, 2025-09-19, 2025-09-22, 2025-10-16, 2025-10-17, 2025-10-20, 2025-11-18, 2025-11-19, 2025-11-20, 2025-12-17, 2025-12-18, 2025-12-19, 2026-01-15, 2026-01-16, 2026-01-19, 2026-02-18, 2026-02-19, 2026-02-20, 2026-03-18, 2026-03-19, 2026-03-20, 2026-04-16, 2026-04-17, 2026-04-20, 2026-05-14, 2026-05-15, 2026-05-18, 2026-06-17, 2026-06-18, 2026-06-19
- Splice check: 15/15 consistent; instrument changes in bars 15, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5980
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 9953 {'1': 7785, '2-5': 2006, '6-30': 152, '>30': 10}
- Flag counts: {'in_flatten_window': 15071, 'in_no_new_positions_window': 15071, 'in_scheduled_closure': 0, 'is_roll_session': 19119, 'vendor_degraded_day': 5980, 'bars_with_gap_before': 9953}

### MGC (metals, built)

- Parquet: `data/processed/MGC/ohlcv-1m_MGC_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `f6bcdd63c9bfc99b1b5a358fc549fe795796209dc5f8374e752906ca75852dd2`, 429238 rows, read-only
- Tick 0.10 (reports/stage_e0_liquidity.json tick_size '0.10'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1525665, 'x100': 1697714}
- Calendar modules: {'data/calendars/metals.py': '8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 MGCM5->MGCQ5 (splice trade date 2025-05-30); 2025-07-31 MGCQ5->MGCZ5 (splice trade date 2025-07-31); 2025-11-27 MGCZ5->MGCG6 (splice trade date 2025-11-27); 2026-01-30 MGCG6->MGCJ6 (splice trade date 2026-01-30); 2026-03-30 MGCJ6->MGCM6 (splice trade date 2026-03-30); 2026-05-29 MGCM6->MGCQ6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-07-29, 2025-07-30, 2025-07-31, 2025-11-25, 2025-11-26, 2025-11-27, 2026-01-28, 2026-01-29, 2026-01-30, 2026-03-26, 2026-03-27, 2026-03-30, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6184
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 1073 {'2-5': 384, '1': 603, '6-30': 79, '>30': 7}
- Flag counts: {'in_flatten_window': 15762, 'in_no_new_positions_window': 15762, 'in_scheduled_closure': 0, 'is_roll_session': 7683, 'vendor_degraded_day': 6184, 'bars_with_gap_before': 1073}

### MHG (metals, built)

- Parquet: `data/processed/MHG/ohlcv-1m_MHG_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `4c3deb8ecd7c2b322f42b7eefc836d99e71ec8014be4fa1d254952e10543b2f8`, 367105 rows, read-only
- Tick 0.0005 (reports/stage_e0_liquidity.json tick_size '0.0005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1296201, 'x100': 1451097}
- Calendar modules: {'data/calendars/metals.py': '8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-28 MHGK5->MHGN5 (splice trade date 2025-04-28); 2025-06-27 MHGN5->MHGU5 (splice trade date 2025-06-27); 2025-08-28 MHGU5->MHGZ5 (splice trade date 2025-08-28); 2025-11-26 MHGZ5->MHGH6 (splice trade date 2025-11-26); 2026-02-26 MHGH6->MHGK6 (splice trade date 2026-02-26); 2026-04-29 MHGK6->MHGN6 (splice trade date 2026-04-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-24, 2025-04-25, 2025-04-28, 2025-06-25, 2025-06-26, 2025-06-27, 2025-08-26, 2025-08-27, 2025-08-28, 2025-11-24, 2025-11-25, 2025-11-26, 2026-02-24, 2026-02-25, 2026-02-26, 2026-04-27, 2026-04-28, 2026-04-29
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5163
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 40490 {'1': 28138, '2-5': 11688, '6-30': 657, '>30': 7}
- Flag counts: {'in_flatten_window': 11272, 'in_no_new_positions_window': 11272, 'in_scheduled_closure': 0, 'is_roll_session': 6417, 'vendor_degraded_day': 5163, 'bars_with_gap_before': 40490}

### MNG (energy, built)

- Parquet: `data/processed/MNG/ohlcv-1m_MNG_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `ef4b32d857d2c721ff65aaa31d03d377439b5fde0ffc1e5224f2ff8e74760767`, 305790 rows, read-only
- Tick 0.001 (reports/stage_e0_liquidity.json tick_size '0.001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1078683, 'x100': 1208428}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-25 MNGK5->MNGM5 (splice trade date 2025-04-25); 2025-05-26 MNGM5->MNGN5 (splice trade date 2025-05-26); 2025-06-25 MNGN5->MNGQ5 (splice trade date 2025-06-25); 2025-07-27 MNGQ5->MNGU5 (splice trade date 2025-07-28); 2025-08-27 MNGU5->MNGV5 (splice trade date 2025-08-27); 2025-09-25 MNGV5->MNGX5 (splice trade date 2025-09-25); 2025-10-29 MNGX5->MNGZ5 (splice trade date 2025-10-29); 2025-11-24 MNGZ5->MNGF6 (splice trade date 2025-11-24); 2025-12-26 MNGF6->MNGG6 (splice trade date 2025-12-26); 2026-01-28 MNGG6->MNGH6 (splice trade date 2026-01-28); 2026-02-25 MNGH6->MNGJ6 (splice trade date 2026-02-25); 2026-03-26 MNGJ6->MNGK6 (splice trade date 2026-03-26); 2026-04-27 MNGK6->MNGM6 (splice trade date 2026-04-27); 2026-05-25 MNGM6->MNGN6 (splice trade date 2026-05-25)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-23, 2025-04-24, 2025-04-25, 2025-05-22, 2025-05-23, 2025-05-26, 2025-06-23, 2025-06-24, 2025-06-25, 2025-07-24, 2025-07-25, 2025-07-28, 2025-08-25, 2025-08-26, 2025-08-27, 2025-09-23, 2025-09-24, 2025-09-25, 2025-10-27, 2025-10-28, 2025-10-29, 2025-11-20, 2025-11-21, 2025-11-24, 2025-12-23, 2025-12-24, 2025-12-26, 2026-01-26, 2026-01-27, 2026-01-28, 2026-02-23, 2026-02-24, 2026-02-25, 2026-03-24, 2026-03-25, 2026-03-26, 2026-04-23, 2026-04-24, 2026-04-27, 2026-05-21, 2026-05-22, 2026-05-25
- Splice check: 14/14 consistent; instrument changes in bars 14, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3870
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 61481 {'2-5': 23314, '1': 35128, '6-30': 3023, '>30': 16}
- Flag counts: {'in_flatten_window': 10532, 'in_no_new_positions_window': 10532, 'in_scheduled_closure': 0, 'is_roll_session': 13142, 'vendor_degraded_day': 3870, 'bars_with_gap_before': 61481}

### MNQ (equity, built)

- Parquet: `data/processed/MNQ/ohlcv-1m_MNQ_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `9506eace6dae2e8193947db083451766d0ed168bcfe86f1ece2d25ee845fe315`, 432011 rows, read-only
- Tick 0.25 (reports/stage_e0_liquidity.json tick_size '0.25'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1545466, 'x100': 1708790}
- Calendar modules: {'data/cme_calendar.py': '61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89', 'data/calendars/equity.py': '3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-18 MNQM5->MNQU5 (splice trade date 2025-06-18); 2025-09-18 MNQU5->MNQZ5 (splice trade date 2025-09-18); 2025-12-18 MNQZ5->MNQH6 (splice trade date 2025-12-18); 2026-03-19 MNQH6->MNQM6 (splice trade date 2026-03-19); 2026-06-17 MNQM6->MNQU6 (splice trade date 2026-06-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-16, 2025-09-17, 2025-09-18, 2025-12-16, 2025-12-17, 2025-12-18, 2026-03-17, 2026-03-18, 2026-03-19, 2026-06-15, 2026-06-16, 2026-06-17
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6089
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 4 {'1': 2, '2-5': 1, '>30': 1}
- Flag counts: {'in_flatten_window': 15950, 'in_no_new_positions_window': 15950, 'in_scheduled_closure': 0, 'is_roll_session': 6900, 'vendor_degraded_day': 6089, 'bars_with_gap_before': 4}

### MYM (equity, built)

- Parquet: `data/processed/MYM/ohlcv-1m_MYM_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `061e816d27b3a5e824abda357f21be6a6aded672558ea4ce3aeb3660d9fd09d8`, 423839 rows, read-only
- Tick 1.0 (reports/stage_e0_liquidity.json tick_size '1.0'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1511188, 'x100': 1676037}
- Calendar modules: {'data/cme_calendar.py': '61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89', 'data/calendars/equity.py': '3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-18 MYMM5->MYMU5 (splice trade date 2025-06-18); 2025-09-17 MYMU5->MYMZ5 (splice trade date 2025-09-17); 2025-12-17 MYMZ5->MYMH6 (splice trade date 2025-12-17); 2026-03-18 MYMH6->MYMM6 (splice trade date 2026-03-18); 2026-06-17 MYMM6->MYMU6 (splice trade date 2026-06-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-15, 2025-09-16, 2025-09-17, 2025-12-15, 2025-12-16, 2025-12-17, 2026-03-16, 2026-03-17, 2026-03-18, 2026-06-15, 2026-06-16, 2026-06-17
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5864
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 6789 {'1': 5817, '2-5': 955, '6-30': 16, '>30': 1}
- Flag counts: {'in_flatten_window': 15862, 'in_no_new_positions_window': 15862, 'in_scheduled_closure': 0, 'is_roll_session': 6564, 'vendor_degraded_day': 5864, 'bars_with_gap_before': 6789}

### NG (energy, built)

- Parquet: `data/processed/NG/ohlcv-1m_NG_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `41f1f1c8e00dbef5b5065544371cd2af25878dc1316e099781145b00c60e9648`, 391801 rows, read-only
- Tick 0.001 (reports/stage_e0_liquidity.json tick_size '0.001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1408309, 'x100': 1552241}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-25 NGK5->NGM5 (splice trade date 2025-04-25); 2025-05-25 NGM5->NGN25 (splice trade date 2025-05-26); 2025-06-25 NGN25->NGQ25 (splice trade date 2025-06-25); 2025-07-25 NGQ25->NGU25 (splice trade date 2025-07-25); 2025-08-24 NGU25->NGV25 (splice trade date 2025-08-25); 2025-09-25 NGV25->NGX25 (splice trade date 2025-09-25); 2025-10-27 NGX25->NGZ25 (splice trade date 2025-10-27); 2025-11-23 NGZ25->NGF26 (splice trade date 2025-11-24); 2025-12-25 NGF26->NGG26 (splice trade date 2025-12-26); 2026-01-22 NGG26->NGH26 (splice trade date 2026-01-22); 2026-01-23 NGH26->NGG26 (splice trade date 2026-01-23); 2026-01-25 NGG26->NGH26 (splice trade date 2026-01-26); 2026-02-23 NGH26->NGJ26 (splice trade date 2026-02-23); 2026-03-23 NGJ26->NGK26 (splice trade date 2026-03-23); 2026-04-26 NGK26->NGM26 (splice trade date 2026-04-27); 2026-05-22 NGM26->NGN26 (splice trade date 2026-05-22)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-23, 2025-04-24, 2025-04-25, 2025-05-22, 2025-05-23, 2025-05-26, 2025-06-23, 2025-06-24, 2025-06-25, 2025-07-23, 2025-07-24, 2025-07-25, 2025-08-21, 2025-08-22, 2025-08-25, 2025-09-23, 2025-09-24, 2025-09-25, 2025-10-23, 2025-10-24, 2025-10-27, 2025-11-20, 2025-11-21, 2025-11-24, 2025-12-23, 2025-12-24, 2025-12-26, 2026-01-20, 2026-01-21, 2026-01-22, 2026-01-23, 2026-01-26, 2026-02-19, 2026-02-20, 2026-02-23, 2026-03-19, 2026-03-20, 2026-03-23, 2026-04-23, 2026-04-24, 2026-04-27, 2026-05-20, 2026-05-21, 2026-05-22
- Splice check: 13/16 consistent; instrument changes in bars 16, unexplained 3
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5332
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 24955 {'1': 16883, '2-5': 7556, '6-30': 514, '>30': 2}
- Flag counts: {'in_flatten_window': 15427, 'in_no_new_positions_window': 15427, 'in_scheduled_closure': 0, 'is_roll_session': 20301, 'vendor_degraded_day': 5332, 'bars_with_gap_before': 24955}

### NQ (equity, built)

- Parquet: `data/processed/NQ/ohlcv-1m_NQ_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `5284f91e7ada8da99438975f53f8a190626c508e6ab8042a7f8c6cd140df4d6e`, 431881 rows, read-only
- Tick 0.25 (reports/stage_e0_liquidity.json tick_size '0.25'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1540631, 'x100': 1707134}
- Calendar modules: {'data/cme_calendar.py': '61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89', 'data/calendars/equity.py': '3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-18 NQM5->NQU5 (splice trade date 2025-06-18); 2025-09-18 NQU5->NQZ5 (splice trade date 2025-09-18); 2025-12-17 NQZ5->NQH6 (splice trade date 2025-12-17); 2026-03-18 NQH6->NQM6 (splice trade date 2026-03-18); 2026-06-17 NQM6->NQU6 (splice trade date 2026-06-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-16, 2025-09-17, 2025-09-18, 2025-12-15, 2025-12-16, 2025-12-17, 2026-03-16, 2026-03-17, 2026-03-18, 2026-06-15, 2026-06-16, 2026-06-17
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6059
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 127 {'1': 118, '2-5': 8, '>30': 1}
- Flag counts: {'in_flatten_window': 15949, 'in_no_new_positions_window': 15949, 'in_scheduled_closure': 0, 'is_roll_session': 6865, 'vendor_degraded_day': 6059, 'bars_with_gap_before': 127}

### QG (energy, built)

- Parquet: `data/processed/QG/ohlcv-1m_QG_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `5d67ced9f2e7705c9d7856df4872469d46b4dd322ff8b14859db18f585657ce0`, 178979 rows, read-only
- Tick 0.005 (reports/stage_e0_liquidity.json tick_size '0.005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 644218, 'x100': 708462}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-25 QGK5->QGM5 (splice trade date 2025-04-25); 2025-05-25 QGM5->QGN5 (splice trade date 2025-05-26); 2025-06-25 QGN5->QGQ5 (splice trade date 2025-06-25); 2025-07-27 QGQ5->QGU5 (splice trade date 2025-07-28); 2025-08-25 QGU5->QGV5 (splice trade date 2025-08-25); 2025-09-25 QGV5->QGX5 (splice trade date 2025-09-25); 2025-10-27 QGX5->QGZ5 (splice trade date 2025-10-27); 2025-11-23 QGZ5->QGF6 (splice trade date 2025-11-24); 2025-12-25 QGF6->QGG6 (splice trade date 2025-12-26); 2026-01-26 QGG6->QGH6 (splice trade date 2026-01-26); 2026-02-23 QGH6->QGJ6 (splice trade date 2026-02-23); 2026-03-26 QGJ6->QGK6 (splice trade date 2026-03-26); 2026-04-26 QGK6->QGM6 (splice trade date 2026-04-27); 2026-05-24 QGM6->QGN6 (splice trade date 2026-05-25)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-23, 2025-04-24, 2025-04-25, 2025-05-22, 2025-05-23, 2025-05-26, 2025-06-23, 2025-06-24, 2025-06-25, 2025-07-24, 2025-07-25, 2025-07-28, 2025-08-21, 2025-08-22, 2025-08-25, 2025-09-23, 2025-09-24, 2025-09-25, 2025-10-23, 2025-10-24, 2025-10-27, 2025-11-20, 2025-11-21, 2025-11-24, 2025-12-23, 2025-12-24, 2025-12-26, 2026-01-22, 2026-01-23, 2026-01-26, 2026-02-19, 2026-02-20, 2026-02-23, 2026-03-24, 2026-03-25, 2026-03-26, 2026-04-23, 2026-04-24, 2026-04-27, 2026-05-21, 2026-05-22, 2026-05-25
- Splice check: 14/14 consistent; instrument changes in bars 14, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 2070
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 71136 {'6-30': 11627, '2-5': 30113, '1': 29054, '>30': 342}
- Flag counts: {'in_flatten_window': 6319, 'in_no_new_positions_window': 6319, 'in_scheduled_closure': 0, 'is_roll_session': 8409, 'vendor_degraded_day': 2070, 'bars_with_gap_before': 71136}

### QM (energy, built)

- Parquet: `data/processed/QM/ohlcv-1m_QM_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `c1ded239a5a836ddf545b429b2a8b1bd20e3ac00afeddae8b756f3b52a77508c`, 258210 rows, read-only
- Tick 0.025 (reports/stage_e0_liquidity.json tick_size '0.025'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 922623, 'x100': 1021875}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-20 QMK5->QMM5 (splice trade date 2025-04-21); 2025-05-19 QMM5->QMN5 (splice trade date 2025-05-19); 2025-06-19 QMN5->QMQ5 (splice trade date 2025-06-19); 2025-07-21 QMQ5->QMU5 (splice trade date 2025-07-21); 2025-08-20 QMU5->QMV5 (splice trade date 2025-08-20); 2025-09-21 QMV5->QMX5 (splice trade date 2025-09-22); 2025-10-20 QMX5->QMZ5 (splice trade date 2025-10-20); 2025-11-20 QMZ5->QMF6 (splice trade date 2025-11-20); 2025-12-19 QMF6->QMG6 (splice trade date 2025-12-19); 2026-01-18 QMG6->QMH6 (splice trade date 2026-01-19); 2026-02-20 QMH6->QMJ6 (splice trade date 2026-02-20); 2026-03-20 QMJ6->QMK6 (splice trade date 2026-03-20); 2026-04-20 QMK6->QMM6 (splice trade date 2026-04-20); 2026-05-18 QMM6->QMN6 (splice trade date 2026-05-18); 2026-06-19 QMN6->QMQ6 (splice trade date 2026-06-19)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-16, 2025-04-17, 2025-04-21, 2025-05-15, 2025-05-16, 2025-05-19, 2025-06-17, 2025-06-18, 2025-06-19, 2025-07-17, 2025-07-18, 2025-07-21, 2025-08-18, 2025-08-19, 2025-08-20, 2025-09-18, 2025-09-19, 2025-09-22, 2025-10-16, 2025-10-17, 2025-10-20, 2025-11-18, 2025-11-19, 2025-11-20, 2025-12-17, 2025-12-18, 2025-12-19, 2026-01-15, 2026-01-16, 2026-01-19, 2026-02-18, 2026-02-19, 2026-02-20, 2026-03-18, 2026-03-19, 2026-03-20, 2026-04-16, 2026-04-17, 2026-04-20, 2026-05-14, 2026-05-15, 2026-05-18, 2026-06-17, 2026-06-18, 2026-06-19
- Splice check: 15/15 consistent; instrument changes in bars 15, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 4227
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 64918 {'1': 33038, '2-5': 25654, '6-30': 6059, '>30': 167}
- Flag counts: {'in_flatten_window': 7660, 'in_no_new_positions_window': 7660, 'in_scheduled_closure': 0, 'is_roll_session': 12315, 'vendor_degraded_day': 4227, 'bars_with_gap_before': 64918}

### RB (energy, built)

- Parquet: `data/processed/RB/ohlcv-1m_RB_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `e086852ec627240b7b44d177a7e5b1637681e886aab214f1f333031446c90be7`, 330620 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1176901, 'x100': 1305077}
- Calendar modules: {'data/calendars/energy.py': 'ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-04 RBK5->RBM5 (splice trade date 2025-04-04); 2025-04-09 RBM5->RBK5 (splice trade date 2025-04-09); 2025-04-10 RBK5->RBM5 (splice trade date 2025-04-10); 2025-05-14 RBM5->RBN5 (splice trade date 2025-05-14); 2025-06-12 RBN5->RBQ5 (splice trade date 2025-06-12); 2025-07-11 RBQ5->RBU5 (splice trade date 2025-07-11); 2025-07-14 RBU5->RBQ5 (splice trade date 2025-07-14); 2025-07-16 RBQ5->RBU5 (splice trade date 2025-07-16); 2025-08-13 RBU5->RBV5 (splice trade date 2025-08-13); 2025-08-14 RBV5->RBU5 (splice trade date 2025-08-14); 2025-08-15 RBU5->RBV5 (splice trade date 2025-08-15); 2025-09-14 RBV5->RBX5 (splice trade date 2025-09-15); 2025-09-17 RBX5->RBV5 (splice trade date 2025-09-17); 2025-09-18 RBV5->RBX5 (splice trade date 2025-09-18); 2025-10-17 RBX5->RBZ5 (splice trade date 2025-10-17); 2025-11-12 RBZ5->RBF6 (splice trade date 2025-11-12); 2025-12-18 RBF6->RBG6 (splice trade date 2025-12-18); 2026-01-15 RBG6->RBH6 (splice trade date 2026-01-15); 2026-02-15 RBH6->RBJ6 (splice trade date 2026-02-16); 2026-03-08 RBJ6->RBK6 (splice trade date 2026-03-09); 2026-04-09 RBK6->RBM6 (splice trade date 2026-04-09); 2026-05-14 RBM6->RBN6 (splice trade date 2026-05-14); 2026-06-11 RBN6->RBQ6 (splice trade date 2026-06-11); 2026-06-15 RBQ6->RBN6 (splice trade date 2026-06-15); 2026-06-17 RBN6->RBQ6 (splice trade date 2026-06-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-02, 2025-04-03, 2025-04-04, 2025-04-07, 2025-04-08, 2025-04-09, 2025-04-10, 2025-05-12, 2025-05-13, 2025-05-14, 2025-06-10, 2025-06-11, 2025-06-12, 2025-07-09, 2025-07-10, 2025-07-11, 2025-07-14, 2025-07-15, 2025-07-16, 2025-08-11, 2025-08-12, 2025-08-13, 2025-08-14, 2025-08-15, 2025-09-11, 2025-09-12, 2025-09-15, 2025-09-16, 2025-09-17, 2025-09-18, 2025-10-15, 2025-10-16, 2025-10-17, 2025-11-10, 2025-11-11, 2025-11-12, 2025-12-16, 2025-12-17, 2025-12-18, 2026-01-13, 2026-01-14, 2026-01-15, 2026-02-12, 2026-02-13, 2026-02-16, 2026-03-05, 2026-03-06, 2026-03-09, 2026-04-07, 2026-04-08, 2026-04-09, 2026-05-12, 2026-05-13, 2026-05-14, 2026-06-09, 2026-06-10, 2026-06-11, 2026-06-12, 2026-06-15, 2026-06-16, 2026-06-17
- Splice check: 10/25 consistent; instrument changes in bars 25, unexplained 15
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 4570
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 40624 {'1': 21787, '2-5': 15225, '6-30': 3568, '>30': 44}
- Flag counts: {'in_flatten_window': 11957, 'in_no_new_positions_window': 11957, 'in_scheduled_closure': 0, 'is_roll_session': 25076, 'vendor_degraded_day': 4570, 'bars_with_gap_before': 40624}

### RTY (equity, built)

- Parquet: `data/processed/RTY/ohlcv-1m_RTY_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `45d340b8853595cb4c97dc11abffa4191bc2b44a0260c94adb28904fd7a9a693`, 420497 rows, read-only
- Tick 0.10 (reports/stage_e0_liquidity.json tick_size '0.10'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1509958, 'x100': 1664256}
- Calendar modules: {'data/cme_calendar.py': '61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89', 'data/calendars/equity.py': '3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-18 RTYM5->RTYU5 (splice trade date 2025-06-18); 2025-09-17 RTYU5->RTYZ5 (splice trade date 2025-09-17); 2025-12-17 RTYZ5->RTYH6 (splice trade date 2025-12-17); 2026-03-18 RTYH6->RTYM6 (splice trade date 2026-03-18); 2026-06-17 RTYM6->RTYU6 (splice trade date 2026-06-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-15, 2025-09-16, 2025-09-17, 2025-12-15, 2025-12-16, 2025-12-17, 2026-03-16, 2026-03-17, 2026-03-18, 2026-06-15, 2026-06-16, 2026-06-17
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5800
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 8366 {'1': 6568, '2-5': 1701, '6-30': 96, '>30': 1}
- Flag counts: {'in_flatten_window': 15900, 'in_no_new_positions_window': 15900, 'in_scheduled_closure': 0, 'is_roll_session': 6413, 'vendor_degraded_day': 5800, 'bars_with_gap_before': 8366}

### SI (metals, built)

- Parquet: `data/processed/SI/ohlcv-1m_SI_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `340679454cf50829ca631ca9e51ae8eb744cbe01f285f4bff1b8153c42b42d8b`, 415684 rows, read-only
- Tick 0.005 (reports/stage_e0_liquidity.json tick_size '0.005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1476677, 'x100': 1643251}
- Calendar modules: {'data/calendars/metals.py': '8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-30 SIK5->SIN5 (splice trade date 2025-04-30); 2025-06-29 SIN5->SIU5 (splice trade date 2025-06-30); 2025-08-29 SIU5->SIZ5 (splice trade date 2025-08-29); 2025-11-27 SIZ5->SIH6 (splice trade date 2025-11-27); 2026-02-27 SIH6->SIK6 (splice trade date 2026-02-27); 2026-04-30 SIK6->SIN6 (splice trade date 2026-04-30)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-28, 2025-04-29, 2025-04-30, 2025-06-26, 2025-06-27, 2025-06-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-04-28, 2026-04-29, 2026-04-30
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6000
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 9724 {'1': 7360, '2-5': 2073, '6-30': 272, '>30': 19}
- Flag counts: {'in_flatten_window': 14688, 'in_no_new_positions_window': 14688, 'in_scheduled_closure': 0, 'is_roll_session': 7490, 'vendor_degraded_day': 6000, 'bars_with_gap_before': 9724}

### SIL (metals, built)

- Parquet: `data/processed/SIL/ohlcv-1m_SIL_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `b1e4b093f972c9ad698f757c5f36f29a9f4e05708338869878f1de539ade6d61`, 412811 rows, read-only
- Tick 0.005 (reports/stage_e0_liquidity.json tick_size '0.005'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1471459, 'x100': 1633336}
- Calendar modules: {'data/calendars/metals.py': '8224189e04e349ab13047b10181ed41ceb5d61567fb681726545b0a03cad58d1', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-30 SILK5->SILN5 (splice trade date 2025-04-30); 2025-06-30 SILN5->SILU5 (splice trade date 2025-06-30); 2025-08-31 SILU5->SILZ5 (splice trade date 2025-09-01); 2025-11-27 SILZ5->SILH6 (splice trade date 2025-11-27); 2026-02-27 SILH6->SILK6 (splice trade date 2026-02-27); 2026-04-30 SILK6->SILN6 (splice trade date 2026-04-30)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-28, 2025-04-29, 2025-04-30, 2025-06-26, 2025-06-27, 2025-06-30, 2025-08-28, 2025-08-29, 2025-09-01, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-04-28, 2026-04-29, 2026-04-30
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 6146
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 10403 {'1': 7652, '2-5': 2363, '6-30': 364, '>30': 24}
- Flag counts: {'in_flatten_window': 14823, 'in_no_new_positions_window': 14823, 'in_scheduled_closure': 0, 'is_roll_session': 7339, 'vendor_degraded_day': 6146, 'bars_with_gap_before': 10403}

### TN (rates, built)

- Parquet: `data/processed/TN/ohlcv-1m_TN_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `3d7e1affa41ab8fb3e4a2704fcf583ff75c8d1745e40fc503a9e723191a0a2df`, 355564 rows, read-only
- Tick 0.015625 (reports/stage_e0_liquidity.json tick_size '1/2 of 1/32 (0.015625)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1281833, 'x100': 1407256}
- Calendar modules: {'data/calendars/rates.py': '449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 TNM5->TNU5 (splice trade date 2025-05-30); 2025-08-29 TNU5->TNZ5 (splice trade date 2025-08-29); 2025-11-27 TNZ5->TNH6 (splice trade date 2025-11-27); 2026-02-27 TNH6->TNM6 (splice trade date 2026-02-27); 2026-05-29 TNM6->TNU6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 4913
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 40177 {'1': 24588, '2-5': 13796, '6-30': 1785, '>30': 8}
- Flag counts: {'in_flatten_window': 14109, 'in_no_new_positions_window': 14109, 'in_scheduled_closure': 0, 'is_roll_session': 4969, 'vendor_degraded_day': 4913, 'bars_with_gap_before': 40177}

### UB (rates, built)

- Parquet: `data/processed/UB/ohlcv-1m_UB_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `98c384f0d0f165be4b74917b8a16f6e6ba0e1bc642516fbf7383444da9a12369`, 372992 rows, read-only
- Tick 0.03125 (reports/stage_e0_liquidity.json tick_size '1/32 (0.03125)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1342611, 'x100': 1477179}
- Calendar modules: {'data/calendars/rates.py': '449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 UBM5->UBU5 (splice trade date 2025-05-30); 2025-08-29 UBU5->UBZ5 (splice trade date 2025-08-29); 2025-11-27 UBZ5->UBH6 (splice trade date 2025-11-27); 2026-02-27 UBH6->UBM6 (splice trade date 2026-02-27); 2026-05-29 UBM6->UBU6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5278
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 36007 {'1': 24629, '2-5': 10482, '6-30': 888, '>30': 8}
- Flag counts: {'in_flatten_window': 14550, 'in_no_new_positions_window': 14550, 'in_scheduled_closure': 0, 'is_roll_session': 5180, 'vendor_degraded_day': 5278, 'bars_with_gap_before': 36007}

### YM (equity, built)

- Parquet: `data/processed/YM/ohlcv-1m_YM_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `71d4f33718d5ab5ff609d4fcddfdff087413f757dbae887473111466d52f0c0f`, 423656 rows, read-only
- Tick 1.00 (reports/stage_e0_liquidity.json tick_size '1.00'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1516957, 'x100': 1676170}
- Calendar modules: {'data/cme_calendar.py': '61218c13635ca73558fcf6ff73884e7cd6f09d5f5f5ceb0d7d7abd28ad968c89', 'data/calendars/equity.py': '3315e81225400add3ba2cc949117c090db0806d495879382d5f3ad02b59e041c', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-06-18 YMM5->YMU5 (splice trade date 2025-06-18); 2025-09-17 YMU5->YMZ5 (splice trade date 2025-09-17); 2025-12-17 YMZ5->YMH6 (splice trade date 2025-12-17); 2026-03-18 YMH6->YMM6 (splice trade date 2026-03-18); 2026-06-15 YMM6->YMU6 (splice trade date 2026-06-15)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-15, 2025-09-16, 2025-09-17, 2025-12-15, 2025-12-16, 2025-12-17, 2026-03-16, 2026-03-17, 2026-03-18, 2026-06-11, 2026-06-12, 2026-06-15
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5831
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 6536 {'1': 5396, '2-5': 1106, '6-30': 33, '>30': 1}
- Flag counts: {'in_flatten_window': 15820, 'in_no_new_positions_window': 15820, 'in_scheduled_closure': 0, 'is_roll_session': 6555, 'vendor_degraded_day': 5831, 'bars_with_gap_before': 6536}

### ZB (rates, built)

- Parquet: `data/processed/ZB/ohlcv-1m_ZB_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `bc437fe4d7fefbd60f2f84a2d2e9b04ef0eae2672f049f62a0adb55f0dc920c0`, 358068 rows, read-only
- Tick 0.03125 (reports/stage_e0_liquidity.json tick_size '1/32 (0.03125)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1291390, 'x100': 1418643}
- Calendar modules: {'data/calendars/rates.py': '449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 ZBM5->ZBU5 (splice trade date 2025-05-30); 2025-08-29 ZBU5->ZBZ5 (splice trade date 2025-08-29); 2025-11-27 ZBZ5->ZBH6 (splice trade date 2025-11-27); 2026-02-27 ZBH6->ZBM6 (splice trade date 2026-02-27); 2026-05-29 ZBM6->ZBU6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 4994
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 39930 {'1': 24718, '2-5': 13670, '6-30': 1537, '>30': 5}
- Flag counts: {'in_flatten_window': 14423, 'in_no_new_positions_window': 14423, 'in_scheduled_closure': 0, 'is_roll_session': 5104, 'vendor_degraded_day': 4994, 'bars_with_gap_before': 39930}

### ZC (grains, built)

- Parquet: `data/processed/ZC/ohlcv-1m_ZC_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `37106ebc79d7d331d1f7d8847ca329eacb95b828ca5386af3d2b39a556e0e410`, 243019 rows, read-only
- Tick 0.0025 (reports/stage_e0_liquidity.json tick_size '0.0025 (USD per bushel; quoted in cents: 1/4 cent)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 0, 'x100': 0}
- Calendar modules: {'data/calendars/grains.py': 'a685731be437412fa8dcb9120f0f37392112d6b4d41a781db393351a38f7806f', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-13 ZCK5->ZCN5 (splice trade date 2025-04-14); 2025-04-14 ZCN5->ZCK5 (splice trade date 2025-04-14); 2025-04-17 ZCK5->ZCN5 (splice trade date 2025-04-17); 2025-04-20 ZCN5->ZCK5 (splice trade date 2025-04-21); 2025-04-23 ZCK5->ZCN5 (splice trade date 2025-04-23); 2025-06-27 ZCN5->ZCU5 (splice trade date 2025-06-27); 2025-07-02 ZCU5->ZCZ5 (splice trade date 2025-07-02); 2025-07-28 ZCZ5->ZCU5 (splice trade date 2025-07-28); 2025-07-30 ZCU5->ZCZ5 (splice trade date 2025-07-30); 2025-11-23 ZCZ5->ZCH6 (splice trade date 2025-11-24); 2026-02-23 ZCH6->ZCK6 (splice trade date 2026-02-23); 2026-04-23 ZCK6->ZCN6 (splice trade date 2026-04-23)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-10, 2025-04-11, 2025-04-14, 2025-04-15, 2025-04-16, 2025-04-17, 2025-04-21, 2025-04-22, 2025-04-23, 2025-06-25, 2025-06-26, 2025-06-27, 2025-06-30, 2025-07-01, 2025-07-02, 2025-07-24, 2025-07-25, 2025-07-28, 2025-07-29, 2025-07-30, 2025-11-20, 2025-11-21, 2025-11-24, 2026-02-19, 2026-02-20, 2026-02-23, 2026-04-21, 2026-04-22, 2026-04-23
- Splice check: 4/12 consistent; instrument changes in bars 10, unexplained 6
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3514
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 36684 {'2-5': 14316, '1': 20284, '6-30': 2079, '>30': 5}
- Flag counts: {'in_flatten_window': 1238, 'in_no_new_positions_window': 1238, 'in_scheduled_closure': 0, 'is_roll_session': 8150, 'vendor_degraded_day': 3514, 'bars_with_gap_before': 36684}

### ZF (rates, built)

- Bars inside a scheduled closure (kept, flagged in_scheduled_closure; ruling L-3): 2026-03-13 Fri 16:00 CT -> trade date 2026-03-13 (close minute)
- Parquet: `data/processed/ZF/ohlcv-1m_ZF_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `12f7aba9b57d49c93370e27529677224d715559e94d5001e8a4c9b5471111d10`, 377319 rows, read-only
- Tick 0.0078125 (reports/stage_e0_liquidity.json tick_size '1/4 of 1/32 (0.0078125)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1354476, 'x100': 1498099}
- Calendar modules: {'data/calendars/rates.py': '449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 ZFM5->ZFU5 (splice trade date 2025-05-30); 2025-08-29 ZFU5->ZFZ5 (splice trade date 2025-08-29); 2025-11-27 ZFZ5->ZFH6 (splice trade date 2025-11-27); 2026-02-27 ZFH6->ZFM6 (splice trade date 2026-02-27); 2026-05-29 ZFM6->ZFU6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5256
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 30360 {'1': 18934, '2-5': 10386, '6-30': 1035, '>30': 5}
- Flag counts: {'in_flatten_window': 15298, 'in_no_new_positions_window': 15298, 'in_scheduled_closure': 1, 'is_roll_session': 5266, 'vendor_degraded_day': 5256, 'bars_with_gap_before': 30360}

### ZL (grains, built)

- Parquet: `data/processed/ZL/ohlcv-1m_ZL_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `4a33fdc073176e521a564d00c474be1755b761863eb3344cba154baa99340641`, 283222 rows, read-only
- Tick 0.0001 (reports/stage_e0_liquidity.json tick_size '0.0001 (USD per pound; quoted in cents: 0.01 cent)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 0, 'x100': 0}
- Calendar modules: {'data/calendars/grains.py': 'a685731be437412fa8dcb9120f0f37392112d6b4d41a781db393351a38f7806f', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-16 ZLK5->ZLN5 (splice trade date 2025-04-16); 2025-06-23 ZLN5->ZLZ5 (splice trade date 2025-06-23); 2025-11-20 ZLZ5->ZLF6 (splice trade date 2025-11-20); 2025-12-18 ZLF6->ZLH6 (splice trade date 2025-12-18); 2026-02-19 ZLH6->ZLK6 (splice trade date 2026-02-19); 2026-04-17 ZLK6->ZLN6 (splice trade date 2026-04-17)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-14, 2025-04-15, 2025-04-16, 2025-06-18, 2025-06-20, 2025-06-23, 2025-11-18, 2025-11-19, 2025-11-20, 2025-12-16, 2025-12-17, 2025-12-18, 2026-02-17, 2026-02-18, 2026-02-19, 2026-04-15, 2026-04-16, 2026-04-17
- sim.engine.roll_blackout_dates (equity calendar) differs on: ['2025-06-18', '2025-06-19']
- Splice check: 6/6 consistent; instrument changes in bars 6, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3973
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 23390 {'1': 16201, '2-5': 6728, '6-30': 461}
- Flag counts: {'in_flatten_window': 1242, 'in_no_new_positions_window': 1242, 'in_scheduled_closure': 0, 'is_roll_session': 5590, 'vendor_degraded_day': 3973, 'bars_with_gap_before': 23390}

### ZM (grains, built)

- Parquet: `data/processed/ZM/ohlcv-1m_ZM_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `74d0b79665c9dd34b1e691fcc81adbb0669be89380dca911229e78640a9cb486`, 240098 rows, read-only
- Tick 0.10 (reports/stage_e0_liquidity.json tick_size '0.10'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 863964, 'x100': 953111}
- Calendar modules: {'data/calendars/grains.py': 'a685731be437412fa8dcb9120f0f37392112d6b4d41a781db393351a38f7806f', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-16 ZMK5->ZMN5 (splice trade date 2025-04-16); 2025-04-17 ZMN5->ZMK5 (splice trade date 2025-04-17); 2025-04-18 ZMK5->ZMN5 (splice trade date 2025-04-21); 2025-06-27 ZMN5->ZMQ5 (splice trade date 2025-06-27); 2025-06-30 ZMQ5->ZMZ5 (splice trade date 2025-06-30); 2025-07-28 ZMZ5->ZMU5 (splice trade date 2025-07-28); 2025-07-31 ZMU5->ZMZ5 (splice trade date 2025-07-31); 2025-11-20 ZMZ5->ZMF6 (splice trade date 2025-11-20); 2025-12-19 ZMF6->ZMH6 (splice trade date 2025-12-19); 2026-02-19 ZMH6->ZMK6 (splice trade date 2026-02-19); 2026-04-16 ZMK6->ZMN6 (splice trade date 2026-04-16)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-14, 2025-04-15, 2025-04-16, 2025-04-17, 2025-04-21, 2025-06-25, 2025-06-26, 2025-06-27, 2025-06-30, 2025-07-24, 2025-07-25, 2025-07-28, 2025-07-29, 2025-07-30, 2025-07-31, 2025-11-18, 2025-11-19, 2025-11-20, 2025-12-17, 2025-12-18, 2025-12-19, 2026-02-17, 2026-02-18, 2026-02-19, 2026-04-14, 2026-04-15, 2026-04-16
- Splice check: 6/11 consistent; instrument changes in bars 11, unexplained 5
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3480
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 37510 {'1': 20990, '2-5': 14294, '6-30': 2218, '>30': 8}
- Flag counts: {'in_flatten_window': 1238, 'in_no_new_positions_window': 1238, 'in_scheduled_closure': 0, 'is_roll_session': 7583, 'vendor_degraded_day': 3480, 'bars_with_gap_before': 37510}

### ZN (rates, built)

- Bars inside a scheduled closure (kept, flagged in_scheduled_closure; ruling L-3): 2026-03-13 Fri 16:00 CT -> trade date 2026-03-13 (close minute)
- Parquet: `data/processed/ZN/ohlcv-1m_ZN_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `f4a403f8641c593daac8b8ea42674233c90574181fac3a001d26c4c31e487ee0`, 396178 rows, read-only
- Tick 0.015625 (reports/stage_e0_liquidity.json tick_size '1/2 of 1/32 (0.015625)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1421254, 'x100': 1567939}
- Calendar modules: {'data/calendars/rates.py': '449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 ZNM5->ZNU5 (splice trade date 2025-05-30); 2025-08-29 ZNU5->ZNZ5 (splice trade date 2025-08-29); 2025-11-27 ZNZ5->ZNH6 (splice trade date 2025-11-27); 2026-02-27 ZNH6->ZNM6 (splice trade date 2026-02-27); 2026-05-29 ZNM6->ZNU6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 5611
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 23160 {'1': 15978, '2-5': 6846, '6-30': 335, '>30': 1}
- Flag counts: {'in_flatten_window': 15504, 'in_no_new_positions_window': 15504, 'in_scheduled_closure': 1, 'is_roll_session': 5759, 'vendor_degraded_day': 5611, 'bars_with_gap_before': 23160}

### ZS (grains, built)

- Parquet: `data/processed/ZS/ohlcv-1m_ZS_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `4d159a37b36f6d354a55b685fdb1cc4310cefda246e4df8dab798c7e8e0464c8`, 277118 rows, read-only
- Tick 0.0025 (reports/stage_e0_liquidity.json tick_size '0.0025 (USD per bushel; quoted in cents: 1/4 cent)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 0, 'x100': 0}
- Calendar modules: {'data/calendars/grains.py': 'a685731be437412fa8dcb9120f0f37392112d6b4d41a781db393351a38f7806f', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-20 ZSK5->ZSN5 (splice trade date 2025-04-21); 2025-06-23 ZSN5->ZSX5 (splice trade date 2025-06-23); 2025-10-29 ZSX5->ZSF6 (splice trade date 2025-10-29); 2025-12-22 ZSF6->ZSH6 (splice trade date 2025-12-22); 2026-02-19 ZSH6->ZSK6 (splice trade date 2026-02-19); 2026-04-24 ZSK6->ZSN6 (splice trade date 2026-04-24); 2026-06-18 ZSN6->ZSX6 (splice trade date 2026-06-18)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-16, 2025-04-17, 2025-04-21, 2025-06-18, 2025-06-20, 2025-06-23, 2025-10-27, 2025-10-28, 2025-10-29, 2025-12-18, 2025-12-19, 2025-12-22, 2026-02-17, 2026-02-18, 2026-02-19, 2026-04-22, 2026-04-23, 2026-04-24, 2026-06-16, 2026-06-17, 2026-06-18
- sim.engine.roll_blackout_dates (equity calendar) differs on: ['2025-06-18', '2025-06-19']
- Splice check: 7/7 consistent; instrument changes in bars 7, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3938
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 26264 {'2-5': 8002, '1': 17660, '6-30': 602}
- Flag counts: {'in_flatten_window': 1244, 'in_no_new_positions_window': 1244, 'in_scheduled_closure': 0, 'is_roll_session': 6146, 'vendor_degraded_day': 3938, 'bars_with_gap_before': 26264}

### ZT (rates, built)

- Bars inside a scheduled closure (kept, flagged in_scheduled_closure; ruling L-3): 2026-03-13 Fri 16:00 CT -> trade date 2026-03-13 (close minute)
- Parquet: `data/processed/ZT/ohlcv-1m_ZT_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `729a661b70e50e0254eb6366b90da48e526b079b4ded34c3c8752080f9d04b08`, 348230 rows, read-only
- Tick 0.00390625 (reports/stage_e0_liquidity.json tick_size '1/8 of 1/32 (0.00390625)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 1249684, 'x100': 1378508}
- Calendar modules: {'data/calendars/rates.py': '449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-05-30 ZTM5->ZTU5 (splice trade date 2025-05-30); 2025-08-29 ZTU5->ZTZ5 (splice trade date 2025-08-29); 2025-11-27 ZTZ5->ZTH6 (splice trade date 2025-11-27); 2026-02-27 ZTH6->ZTM6 (splice trade date 2026-02-27); 2026-05-29 ZTM6->ZTU6 (splice trade date 2026-05-29)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-05-28, 2025-05-29, 2025-05-30, 2025-08-27, 2025-08-28, 2025-08-29, 2025-11-25, 2025-11-26, 2025-11-27, 2026-02-25, 2026-02-26, 2026-02-27, 2026-05-27, 2026-05-28, 2026-05-29
- Splice check: 5/5 consistent; instrument changes in bars 5, unexplained 0
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 4920
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 42813 {'1': 25077, '2-5': 15842, '6-30': 1887, '>30': 7}
- Flag counts: {'in_flatten_window': 14624, 'in_no_new_positions_window': 14624, 'in_scheduled_closure': 1, 'is_roll_session': 4762, 'vendor_degraded_day': 4920, 'bars_with_gap_before': 42813}

### ZW (grains, built)

- Parquet: `data/processed/ZW/ohlcv-1m_ZW_v_0_2025-04-01_2026-06-19_research.parquet` sha256 `a9c459d94f4dacdadbb5d5ec75be31cc0c76edecfd7f1d53f45476cf84b9c55a`, 247726 rows, read-only
- Tick 0.0025 (reports/stage_e0_liquidity.json tick_size '0.0025 (USD per bushel; quoted in cents: 1/4 cent)'); raw off-tick prices 0; grid-scale probe {'x1': 0, 'x10': 0, 'x100': 0}
- Calendar modules: {'data/calendars/grains.py': 'a685731be437412fa8dcb9120f0f37392112d6b4d41a781db393351a38f7806f', 'data/calendars/__init__.py': 'a13255d8f91a806aa8c056ce2a4014d9eedfbbd969ec4e467ad8d6a295a7b86a'}
- Rolls (symbology.resolve (cached)): 2025-04-17 ZWK5->ZWN5 (splice trade date 2025-04-17); 2025-06-20 ZWN5->ZWU5 (splice trade date 2025-06-20); 2025-08-17 ZWU5->ZWZ5 (splice trade date 2025-08-18); 2025-11-13 ZWZ5->ZWH6 (splice trade date 2025-11-13); 2025-11-14 ZWH6->ZWZ5 (splice trade date 2025-11-14); 2025-11-16 ZWZ5->ZWH6 (splice trade date 2025-11-17); 2026-02-19 ZWH6->ZWK6 (splice trade date 2026-02-19); 2026-04-16 ZWK6->ZWN6 (splice trade date 2026-04-16); 2026-06-18 ZWN6->ZWU6 (splice trade date 2026-06-18)
- Roll blackout dates (group calendar, splice + 2 sessions before): 2025-04-15, 2025-04-16, 2025-04-17, 2025-06-17, 2025-06-18, 2025-06-20, 2025-08-14, 2025-08-15, 2025-08-18, 2025-11-11, 2025-11-12, 2025-11-13, 2025-11-14, 2025-11-17, 2026-02-17, 2026-02-18, 2026-02-19, 2026-04-14, 2026-04-15, 2026-04-16, 2026-06-16, 2026-06-17, 2026-06-18
- sim.engine.roll_blackout_dates (equity calendar) differs on: ['2025-06-17', '2025-06-19']
- Splice check: 6/9 consistent; instrument changes in bars 9, unexplained 3
- Bars whose instrument is not symbology's mapping on their UTC date: 0 []
- Embedded-mapping cross-check: 446 UTC dates, 0 disagreements []
- Vendor-degraded dates on research trade dates: ['2025-09-17', '2025-09-24', '2025-11-28', '2026-03-16', '2026-04-10']; bars flagged 3533
- Drops: before window {}; after window {}; past calendar coverage 0; no outright 0
- Validation: hard failures []; zero-volume bars 0; gap runs 35847 {'1': 20510, '2-5': 13518, '6-30': 1818, '>30': 1}
- Flag counts: {'in_flatten_window': 1236, 'in_no_new_positions_window': 1236, 'in_scheduled_closure': 0, 'is_roll_session': 7267, 'vendor_degraded_day': 3533, 'bars_with_gap_before': 35847}

## MES regression

```json
{
 "status": "built",
 "refusal_causes": [],
 "raw_files": [
  "range=2025-04-01_2025-05-01.dbn.zst",
  "range=2025-05-01_2025-06-01.dbn.zst",
  "range=2025-06-01_2025-07-01.dbn.zst",
  "range=2025-07-01_2025-08-01.dbn.zst",
  "range=2025-08-01_2025-09-01.dbn.zst",
  "range=2025-09-01_2025-10-01.dbn.zst",
  "range=2025-10-01_2025-11-01.dbn.zst",
  "range=2025-11-01_2025-12-01.dbn.zst",
  "range=2025-12-01_2026-01-01.dbn.zst",
  "range=2026-01-01_2026-02-01.dbn.zst",
  "range=2026-02-01_2026-03-01.dbn.zst",
  "range=2026-03-01_2026-04-01.dbn.zst",
  "range=2026-04-01_2026-05-01.dbn.zst",
  "range=2026-05-01_2026-06-01.dbn.zst"
 ],
 "rows_rebuilt": 411659,
 "rows_in_research_parquet": 431999,
 "same_columns_and_types": true,
 "rows_equal": true,
 "mismatched_values_by_column": {},
 "next_research_row_at_or_after_rebuild_end": true,
 "last_rebuilt_trade_date": "2026-06-01",
 "research_parquet_sha256": "aea959a518c32984832126f8314000796318efa219379a1ac4aea556a1736ae0",
 "rebuild_sha256": "ffcb154b9dc2b060af969f252292dc0c210c96328aa2e8b2785bfc17ba06d09d",
 "file_bytes_equal": false,
 "why_bytes_differ": "the rebuild covers trade dates 2025-04-01..2026-06-01 (partial) because the 2026-06 raw chunk is sealed (holdout-1); the research parquet also holds 2026-06-01..2026-06-19, and its schema metadata differs (Stage A.1 stamps vs Stage E stamps)"
}
```
