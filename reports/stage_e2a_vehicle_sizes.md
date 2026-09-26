# Stage E.2a Task 9, phase 1: r_c, q_c and rho_c per admissible contract

Generated 2026-09-25 02:35 PDT by screening/vehicles_run.py (VehicleCoder-OpusXHigh). Rule: docs/STAGE_E_DESIGN.md D2 read as R1-R6 of reports/stage_e2a_vehicle_rule_readings.md (sha256 checked). Full data, date lists and input hashes: reports/stage_e2a_vehicle_sizes.json.

r_c = mean over the R2 dates of |close(C_X - 1 min) - open(O_X)| in ticks of the vendor's price units x tick_value_usd (R3, R4); q_c = min(cap_c, max(1, round-half-up(R*/r_c))), R* = $360.68; rho_c = q_c r_c / R* (R5, R6). Excluded-date columns count each cause separately (a date can have two causes); 'exact bar missing' counts used dates where the bar at O_X or at C_X - 1 min was missing and the nearest traded minute inside the window was used (R3).

Rulings applied: L-1 D6's O values stand (CME publishes no day-session open for most groups); L-2 early-settlement days are not early closes (rates' EARLY_SETTLEMENT_CT excludes nothing); L-4 revised the 2025-11-28 outage is not a calendar entry; R3's as-of reading handles a missing open bar; L-7 the 2026-02-25 metals halt is not a calendar entry; R3's as-of reading handles it; L-8 roll-blackout dates come from each product's group calendar, as BarsCoder recorded them in reports/stage_e2a_bars.json; L-9 MBT's research window ends at trade date 2026-06-18; L-10 O_X and C_X are clock times on the trade date's own calendar day; both R3 bars lie there, never in a booked-in holiday session; R1 no D6 value was corrected by the calendar confirmations; D6's table is used as written.

| Exposure | Contract | O-C (CT) | Trade dates | Used | roll | degraded | early close <= C | no bar | Exact bar missing | r_c (USD) | cap_c (source) | q_c | rho_c | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nasdaq-100 | MNQ | 08:30-15:00 | 316 | 285 | 15 | 5 | 13 | 0 | 0 | 363.46 | 10 (D9.5) | 1 | 1.0077 |  |
| Nasdaq-100 | NQ | 08:30-15:00 | 316 | 286 | 15 | 5 | 13 | 0 | 0 | 3613.08 | 1 (D9.5) | 1 | 10.0174 |  |
| Russell 2000 | RTY | 08:30-15:00 | 316 | 286 | 15 | 5 | 13 | 0 | 0 | 1060.72 | 1 (D9.5) | 1 | 2.9409 |  |
| Russell 2000 | M2K | 08:30-15:00 | 316 | 286 | 15 | 5 | 13 | 0 | 0 | 106.13 | 10 (D9.5) | 3 | 0.8828 |  |
| Dow | MYM | 08:30-15:00 | 316 | 286 | 15 | 5 | 13 | 0 | 0 | 131.15 | 10 (D9.5) | 3 | 1.0908 |  |
| Dow | YM | 08:30-15:00 | 316 | 286 | 15 | 5 | 13 | 0 | 0 | 1312.27 | 1 (D9.5) | 1 | 3.6383 |  |
| 2-year | ZT | 07:20-14:00 | 316 | 286 | 15 | 5 | 12 | 0 | 0 | 112.68 | 1 (D9.5) | 1 | 0.3124 |  |
| 5-year | ZF | 07:20-14:00 | 316 | 286 | 15 | 5 | 12 | 0 | 0 | 135.54 | 1 (D9.5) | 1 | 0.3758 |  |
| 10-year | ZN | 07:20-14:00 | 316 | 286 | 15 | 5 | 12 | 0 | 0 | 204.93 | 1 (D9.5) | 1 | 0.5682 |  |
| Ultra 10-year | TN | 07:20-14:00 | 316 | 286 | 15 | 5 | 12 | 0 | 0 | 259.94 | 1 (D9.5) | 1 | 0.7207 |  |
| Bond | ZB | 07:20-14:00 | 316 | 286 | 15 | 5 | 12 | 0 | 0 | 402.10 | 1 (D9.5) | 1 | 1.1148 |  |
| Ultra bond | UB | 07:20-14:00 | 316 | 286 | 15 | 5 | 12 | 0 | 0 | 501.42 | 1 (D9.5) | 1 | 1.3902 |  |
| EUR | 6E | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 1 | 319.45 | 1 (D9.5) | 1 | 0.8857 |  |
| EUR | M6E | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 8 | 32.03 | 10 (D9.5) | 10 | 0.8882 | R7: not a candidate |
| EUR | E7 | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 103 | 160.73 | 1 (D9.5) | 1 | 0.4456 |  |
| AUD | 6A | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 2 | 183.65 | 1 (D9.5) | 1 | 0.5092 |  |
| AUD | M6A | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 106 | 18.42 | 10 (D9.5) | 10 | 0.5106 | R7: not a candidate |
| GBP | 6B | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 1 | 186.22 | 1 (D9.5) | 1 | 0.5163 |  |
| GBP | M6B | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 99 | 18.71 | 10 (D9.5) | 10 | 0.5188 |  |
| CAD | 6C | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 4 | 120.29 | 1 (D9.5) | 1 | 0.3335 |  |
| JPY | 6J | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 0 | 204.82 | 1 (D9.5) | 1 | 0.5679 |  |
| CHF | 6S | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 3 | 410.75 | 1 (D9.5) | 1 | 1.1388 |  |
| NZD | 6N | 07:20-14:00 | 316 | 293 | 15 | 5 | 5 | 0 | 4 | 156.48 | 1 (D9.5) | 1 | 0.4339 |  |
| WTI crude | CL | 08:00-13:30 | 315 | 256 | 45 | 5 | 10 | 0 | 0 | 918.79 | 1 (D9.5) | 1 | 2.5474 |  |
| WTI crude | MCL | 08:00-13:30 | 315 | 258 | 45 | 5 | 10 | 0 | 0 | 91.57 | 10 (D9.5) | 4 | 1.0155 |  |
| WTI crude | QM | 08:00-13:30 | 315 | 258 | 45 | 5 | 10 | 0 | 2 | 457.22 | 1 (D9.5) | 1 | 1.2677 |  |
| Henry Hub gas | NG | 08:00-13:30 | 315 | 259 | 44 | 5 | 10 | 0 | 0 | 639.31 | 1 (D9.5) | 1 | 1.7725 |  |
| Henry Hub gas | MNG | 08:00-13:30 | 315 | 262 | 42 | 5 | 10 | 0 | 2 | 65.31 | 10 (D9.5) | 6 | 1.0864 |  |
| Henry Hub gas | QG | 08:00-13:30 | 315 | 262 | 42 | 5 | 10 | 0 | 25 | 159.16 | 1 (D9.5) | 1 | 0.4413 |  |
| RBOB | RB | 08:00-13:30 | 315 | 241 | 61 | 5 | 10 | 0 | 0 | 1012.79 | 1 (D9.5) | 1 | 2.8080 |  |
| ULSD | HO | 08:00-13:30 | 315 | 253 | 48 | 5 | 10 | 0 | 0 | 1441.40 | 1 (D9.5) | 1 | 3.9963 |  |
| gold | MGC | 07:20-12:30 | 315 | 290 | 18 | 5 | 2 | 0 | 1 | 258.59 | 10 (D9.5) | 1 | 0.7170 |  |
| gold | GC | 07:20-12:30 | 315 | 290 | 18 | 5 | 2 | 0 | 1 | 2586.97 | 1 (D9.5) | 1 | 7.1725 |  |
| silver | SIL | 07:20-12:25 | 315 | 290 | 18 | 5 | 2 | 0 | 0 | 931.05 | 2 (D9.11) | 1 | 2.5814 |  |
| silver | SI | 07:20-12:25 | 315 | 290 | 18 | 5 | 2 | 0 | 0 | 4653.97 | 1 (D9.5) | 1 | 12.9033 |  |
| copper | HG | 07:10-12:00 | 315 | 290 | 18 | 5 | 2 | 0 | 0 | 1101.29 | 1 (D9.5) | 1 | 3.0534 |  |
| copper | MHG | 07:10-12:00 | 315 | 290 | 18 | 5 | 2 | 0 | 3 | 110.22 | 2 (D9.11) | 2 | 0.6112 |  |
| corn | ZC | 08:30-13:15 | 306 | 271 | 29 | 5 | 2 | 0 | 0 | 158.16 | 1 (D9.5) | 1 | 0.4385 |  |
| wheat | ZW | 08:30-13:15 | 306 | 277 | 23 | 5 | 2 | 0 | 0 | 234.75 | 1 (D9.5) | 1 | 0.6508 |  |
| soybeans | ZS | 08:30-13:15 | 306 | 279 | 21 | 5 | 2 | 0 | 0 | 304.39 | 1 (D9.5) | 1 | 0.8439 |  |
| soybean meal | ZM | 08:30-13:15 | 306 | 273 | 27 | 5 | 2 | 0 | 0 | 212.64 | 1 (D9.5) | 1 | 0.5895 |  |
| soybean oil | ZL | 08:30-13:15 | 306 | 282 | 18 | 5 | 2 | 0 | 0 | 304.83 | 1 (D9.5) | 1 | 0.8452 |  |
| lean hogs | HE | 08:30-13:00 | 306 | 270 | 32 | 5 | 2 | 0 | 0 | 322.96 | 1 (D9.5) | 1 | 0.8954 |  |
| live cattle | LE | 08:30-13:00 | 306 | 264 | 39 | 5 | 2 | 0 | 0 | 707.16 | 1 (D9.5) | 1 | 1.9606 |  |
| bitcoin | MBT | 08:30-15:00 | 308 | 260 | 42 | 5 | 4 | 0 | 0 | 120.61 | 1 (D9.5) | 1 | 0.3344 |  |

## Input checks

- Vendor tick: every price of all 45 parquets lies on the vendor-unit grid, and at least 10% lie off the 2x and the 10x grid (so the tick is not too fine); the scale agrees with BarsCoder's grid probe and CostCoder's vendor_price_factor for every contract. 100 x the E.0 tick: HE, LE, ZC, ZL, ZS, ZW.
- Roll blackout: BarsCoder's recorded list (L-8) equals the parquet metadata and a recomputation from the group calendar (splice trade date and the 2 group trade dates before it); the is_roll_session flag marks exactly the splice trade dates.
- Vendor-degraded: the list (research trade dates on Databento's degraded UTC-date list, as BarsCoder records it) equals the parquet metadata, and inside every [O_X, C_X) window the per-bar flag agrees with it (0 mismatches).
- Trade dates off the list with a flagged bar outside the window: ['2025-09-18', '2025-09-25', '2026-03-17', '2026-05-25', '2026-05-26'] (question Q-2 below).
- Calendar trade dates with no bar in the parquet: none.
- Bars of another trade date inside a window (L-10): none.
- BarsCoder's step-4b calendar check (reports/stage_e2a_bars.json) lists days on 21 contracts (days listed / of which used for r_c): 6E 1/1; M6E 9/6; E7 82/70; 6A 2/2; M6A 63/55; 6B 3/1; M6B 55/47; 6C 6/4; 6J 3/0; 6S 7/2; 6N 4/2; QM 27/2; MNG 11/1; QG 36/22; MGC 6/1; GC 2/1; SIL 6/0; SI 4/0; HG 3/2; MHG 3/1; MBT 14/0. Nearly all are 'early stop' findings: no trade in the last minutes before C_X on a thin contract (BarsCoder's thin-trading class; lead rulings L-5 and L-7 for the named days; MBT's 14 are the monthly-expiry Fridays, all inside its roll blackout). Every such day that r_c uses is in that contract's R3 close-bar-missing list (the last traded minute before C_X was used); the rest ('listed entry not observed') concern halts after C_X or dates R2 excludes. Kinds and full lists per contract: bars_json_calendar_check in the JSON.

## Notes and questions for the lead

- Q-1 (R5, SI and HG): D9.11 quotes Topstep's 50K figure for SI and HG as 0. R5's list of what D9.11 lowers (SIL, MHG) and D9.11's own 'Encoded:' sentence leave SI and HG out (D9.11 handles them by D2's SIL/MHG preference), so cap_c is D9.5's 1 here. A literal min(D9.5, 0) would give cap 0 and q_c = 0, which R6 and D8's depth term cannot use. It cannot change a vehicle: SI and HG move 5 and 10 times SIL and MHG, so if SIL (MHG) has rho > 2 at q = 1, SI (HG) does too, and if SIL (MHG) is a candidate it is the vehicle (R9).
- Q-2 (R2, vendor-degraded dates): R2 excludes the research trade dates on Databento's degraded UTC-date list (reports/stage_e2a_bars.json degraded.on_research_trade_dates, as the brief directs; D.1e also treated the list as dates). A degraded UTC date also covers the evening session (17:00-19:00 CT) that opens the NEXT trade date, so 2025-09-18, 2025-09-25, 2026-03-17, 2026-05-25, 2026-05-26 carry flagged evening bars on most contracts (not grains or livestock, whose evening opens at 00:00 UTC). Their [O_X, C_X) bars lie on a clean UTC date; where no other cause excludes them they are used (on 38 contracts, 1 to 4 dates each; lists per contract: degraded_off_list_dates_used_for_r_c in the JSON). Reading 'any flagged bar of the trade date' would drop them too; no r_c was computed under that reading.
- BarsCoder's limitation carries over: symbology covers UTC dates to 2026-06-20, so a roll splice on 2026-06-21/22 would put 2026-06-18/19 into a blackout no report can show from research-window metadata.
- No contract is pending: all 45 have q_c (MBT's parquet and bars.json entry exist; L-9 and L-10 applied).
