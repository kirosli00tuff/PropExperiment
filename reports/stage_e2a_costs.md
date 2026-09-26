# Stage E.2a Task 8: per-product cost model (design D8)

Generated 2026-09-25 02:39 PDT by CostCoder-OpusXHigh. Rule: docs/STAGE_E_DESIGN.md D8 (frozen, commit ba67073). Machine-readable table: reports/stage_e2a_costs.json (loaded by `sim.product_costs`). Code: sim/cost_inputs.py, sim/calibrate_costs.py, sim/cost_rule.py, sim/cost_report.py, sim/cost_report_md.py, sim/product_costs.py; tests: tests/test_e2a_costs.py.

STATUS: FROZEN. Depth term applied at q_c from `reports/stage_e2a_vehicle_sizes.json` (sha256 280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325).

Sample: mbp-1, the five trade dates 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15; 45 of 45 contracts calibrated; not calibrated: none; missing from this build: none.

## Headline per contract (day session, O to C of D6)

Round turn (RT) = commission/tick value + buy-side + sell-side slippage in the same bucket; mean and range over the buckets overlapping [O, C) (reading R9).

| Contract | Group | Tick | Tick $ | Comm. RT $ | Comm. ticks | q_c | Day buckets | RT ticks mean [min, max] | RT $ mean [min, max] | Event side ticks buy / sell | Fallback buckets (all / day) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | fx | 0.00005 | 5.0 | 4.22 | 0.844 | 1 | 14 (07:00-13:30) | 2.191 [2.148, 2.243] | 10.96 [10.74, 11.22] | 0.817 / 0.817 | 0 / 0 |
| 6B | fx | 0.0001 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 1.916 [1.826, 1.972] | 11.97 [11.42, 12.33] | 0.677 / 0.677 | 0 / 0 |
| 6C | fx | 0.00005 | 5.0 | 4.22 | 0.844 | 1 | 14 (07:00-13:30) | 2.026 [1.992, 2.069] | 10.13 [9.96, 10.34] | 0.685 / 0.685 | 0 / 0 |
| 6E | fx | 0.00005 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 1.935 [1.894, 1.975] | 12.09 [11.84, 12.35] | 0.815 / 0.815 | 0 / 0 |
| 6J | fx | 5E-7 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 1.890 [1.857, 1.927] | 11.81 [11.61, 12.04] | 0.713 / 0.713 | 0 / 0 |
| 6N | fx | 0.00005 | 5.0 | 4.22 | 0.844 | 1 | 14 (07:00-13:30) | 2.252 [2.154, 2.301] | 11.26 [10.77, 11.50] | 0.887 / 0.887 | 0 / 0 |
| 6S | fx | 0.00005 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 2.650 [2.508, 2.806] | 16.56 [15.67, 17.54] | 1.654 / 1.654 | 0 / 0 |
| CL | energy | 0.01 | 10.0 | 4.02 | 0.402 | 1 | 11 (08:00-13:00) | 1.728 [1.699, 1.768] | 17.28 [16.99, 17.68] | 1.319 / 1.319 | 0 / 0 |
| E7 | fx | 0.0001 | 6.25 | 2.72 | 0.435 | 1 | 14 (07:00-13:30) | 1.712 [1.677, 1.781] | 10.70 [10.48, 11.13] | 0.781 / 0.781 | 0 / 0 |
| GC | metals | 0.10 | 10.0 | 4.32 | 0.432 | 1 | 11 (07:00-12:00) | 4.351 [3.855, 4.968] | 43.51 [38.55, 49.68] | 3.074 / 3.074 | 0 / 0 |
| HE | livestock | 0.00025 | 10.0 | 5.22 | 0.522 | 1 | 9 (08:30-12:30) | 1.860 [1.752, 1.965] | 18.60 [17.52, 19.65] | 0.721 / 0.721 | 0 / 0 |
| HG | metals | 0.0005 | 12.5 | 4.32 | 0.346 | 1 | 10 (07:00-11:30) | 2.588 [2.428, 2.813] | 32.35 [30.35, 35.16] | 1.575 / 1.575 | 0 / 0 |
| HO | energy | 0.0001 | 4.2 | 4.02 | 0.957 | 1 | 11 (08:00-13:00) | 9.827 [8.241, 11.624] | 41.27 [34.61, 48.82] | 24.133 / 24.133 | 0 / 0 |
| LE | livestock | 0.00025 | 10.0 | 5.22 | 0.522 | 1 | 9 (08:30-12:30) | 2.393 [2.230, 2.498] | 23.93 [22.30, 24.98] | 0.988 / 0.988 | 0 / 0 |
| M2K | equity | 0.10 | 0.5 | 1.22 | 2.440 | 3 | 13 (08:30-14:30) | 3.954 [3.906, 4.087] | 1.98 [1.95, 2.04] | 1.953 / 1.953 | 0 / 0 |
| M6A | fx | 0.0001 | 1.0 | 1.00 | 1.000 | 10 | 14 (07:00-13:30) | 2.172 [2.155, 2.195] | 2.17 [2.16, 2.19] | 0.613 / 0.613 | 0 / 0 |
| M6B | fx | 0.0001 | 0.625 | 1.00 | 1.600 | 10 | 14 (07:00-13:30) | 3.354 [3.079, 3.720] | 2.10 [1.92, 2.33] | 1.487 / 1.587 | 0 / 0 |
| M6E | fx | 0.0001 | 1.25 | 1.00 | 0.800 | 10 | 14 (07:00-13:30) | 1.922 [1.895, 1.961] | 2.40 [2.37, 2.45] | 0.609 / 0.609 | 0 / 0 |
| MBT | crypto | 5.00 | 0.5 | 2.82 | 5.640 | 1 | 13 (08:30-14:30) | 8.846 [8.554, 9.010] | 4.42 [4.28, 4.50] | 2.613 / 2.613 | 0 / 0 |
| MCL | energy | 0.01 | 1.0 | 1.72 | 1.720 | 4 | 11 (08:00-13:00) | 3.167 [3.122, 3.222] | 3.17 [3.12, 3.22] | 1.313 / 1.313 | 0 / 0 |
| MGC | metals | 0.10 | 1.0 | 1.92 | 1.920 | 1 | 11 (07:00-12:00) | 4.086 [3.946, 4.414] | 4.09 [3.95, 4.41] | 1.838 / 1.838 | 0 / 0 |
| MHG | metals | 0.0005 | 1.25 | 1.92 | 1.536 | 2 | 10 (07:00-11:30) | 3.701 [3.489, 4.096] | 4.63 [4.36, 5.12] | 1.739 / 1.739 | 0 / 0 |
| MNG | energy | 0.001 | 1.0 | 1.92 | 1.920 | 6 | 11 (08:00-13:00) | 5.350 [5.243, 5.602] | 5.35 [5.24, 5.60] | 3.219 / 3.219 | 0 / 0 |
| MNQ | equity | 0.25 | 0.5 | 1.22 | 2.440 | 1 | 13 (08:30-14:30) | 4.119 [4.061, 4.379] | 2.06 [2.03, 2.19] | 1.486 / 1.486 | 0 / 0 |
| MYM | equity | 1.0 | 0.5 | 1.22 | 2.440 | 3 | 13 (08:30-14:30) | 3.983 [3.915, 4.095] | 1.99 [1.96, 2.05] | 2.208 / 2.541 | 0 / 0 |
| NG | energy | 0.001 | 10.0 | 4.22 | 0.422 | 1 | 11 (08:00-13:00) | 1.672 [1.631, 1.686] | 16.72 [16.31, 16.86] | 0.993 / 0.993 | 0 / 0 |
| NQ | equity | 0.25 | 5.0 | 3.78 | 0.756 | 1 | 13 (08:30-14:30) | 3.110 [2.938, 3.532] | 15.55 [14.69, 17.66] | 2.300 / 2.300 | 0 / 0 |
| QG | energy | 0.005 | 12.5 | 2.02 | 0.162 | 1 | 11 (08:00-13:00) | 1.381 [1.335, 1.423] | 17.27 [16.68, 17.79] | 0.774 / 0.774 | 0 / 0 |
| QM | energy | 0.025 | 12.5 | 3.42 | 0.274 | 1 | 11 (08:00-13:00) | 1.599 [1.535, 1.682] | 19.99 [19.19, 21.03] | 1.323 / 1.323 | 0 / 0 |
| RB | energy | 0.0001 | 4.2 | 4.02 | 0.957 | 1 | 11 (08:00-13:00) | 5.515 [4.940, 6.143] | 23.16 [20.75, 25.80] | 10.566 / 10.566 | 0 / 0 |
| RTY | equity | 0.10 | 5.0 | 3.78 | 0.756 | 1 | 13 (08:30-14:30) | 2.359 [2.241, 2.525] | 11.80 [11.20, 12.63] | 1.590 / 1.590 | 0 / 0 |
| SI | metals | 0.005 | 25.0 | 4.32 | 0.173 | 1 | 11 (07:00-12:00) | 3.551 [3.183, 4.019] | 88.78 [79.56, 100.48] | 2.512 / 2.512 | 0 / 0 |
| SIL | metals | 0.005 | 5.0 | 2.72 | 0.544 | 1 | 11 (07:00-12:00) | 2.791 [2.618, 3.257] | 13.95 [13.09, 16.29] | 1.874 / 1.874 | 0 / 0 |
| TN | rates | 0.015625 | 15.625 | 2.62 | 0.168 | 1 | 14 (07:00-13:30) | 1.174 [1.169, 1.180] | 18.35 [18.27, 18.43] | 0.534 / 0.534 | 0 / 0 |
| UB | rates | 0.03125 | 31.25 | 2.92 | 0.093 | 1 | 14 (07:00-13:30) | 1.098 [1.094, 1.107] | 34.33 [34.18, 34.59] | 0.514 / 0.514 | 0 / 0 |
| YM | equity | 1.00 | 5.0 | 3.78 | 0.756 | 1 | 13 (08:30-14:30) | 2.823 [2.759, 2.879] | 14.12 [13.79, 14.39] | 1.779 / 1.779 | 0 / 0 |
| ZB | rates | 0.03125 | 31.25 | 2.76 | 0.088 | 1 | 14 (07:00-13:30) | 1.089 [1.088, 1.092] | 34.04 [34.01, 34.11] | 0.517 / 0.517 | 0 / 0 |
| ZC | grains | 0.0025 | 12.5 | 5.28 | 0.422 | 1 | 10 (08:30-13:00) | 1.425 [1.423, 1.430] | 17.82 [17.79, 17.87] | 0.537 / 0.537 | 0 / 0 |
| ZF | rates | 0.0078125 | 7.8125 | 2.32 | 0.297 | 1 | 14 (07:00-13:30) | 1.298 [1.297, 1.301] | 10.14 [10.13, 10.17] | 0.508 / 0.508 | 0 / 0 |
| ZL | grains | 0.0001 | 6.0 | 5.28 | 0.880 | 1 | 10 (08:30-13:00) | 2.174 [2.113, 2.210] | 13.04 [12.68, 13.26] | 0.897 / 0.897 | 0 / 0 |
| ZM | grains | 0.10 | 10.0 | 5.28 | 0.528 | 1 | 10 (08:30-13:00) | 1.608 [1.585, 1.632] | 16.08 [15.85, 16.32] | 0.632 / 0.632 | 0 / 0 |
| ZN | rates | 0.015625 | 15.625 | 2.62 | 0.168 | 1 | 14 (07:00-13:30) | 1.168 [1.168, 1.168] | 18.25 [18.25, 18.26] | 0.501 / 0.501 | 0 / 0 |
| ZS | grains | 0.0025 | 12.5 | 5.28 | 0.422 | 1 | 10 (08:30-13:00) | 1.469 [1.460, 1.478] | 18.36 [18.25, 18.47] | 0.611 / 0.611 | 0 / 0 |
| ZT | rates | 0.00390625 | 7.8125 | 2.32 | 0.297 | 1 | 14 (07:00-13:30) | 1.301 [1.297, 1.308] | 10.17 [10.13, 10.22] | 0.513 / 0.513 | 0 / 0 |
| ZW | grains | 0.0025 | 12.5 | 5.28 | 0.422 | 1 | 10 (08:30-13:00) | 1.479 [1.463, 1.499] | 18.49 [18.28, 18.73] | 0.636 / 0.636 | 0 / 0 |

## Flags

- none: every bucket of every contract is quoted on at least 3 of 5 dates.

## Depth term at q_c

A contract with q_c = 1 never pays a depth term (a valid book has at least one contract at the top). Contracts with a non-zero depth term in any bucket:

- M2K (q_c 3): 1 of 46 buckets (0 in the day session), largest one-side depth term 0.333 ticks
- M6B (q_c 10): 38 of 46 buckets (11 in the day session), largest one-side depth term 0.600 ticks
- MCL (q_c 4): 4 of 46 buckets (0 in the day session), largest one-side depth term 0.250 ticks
- MNG (q_c 6): 46 of 46 buckets (11 in the day session), largest one-side depth term 0.667 ticks
- MYM (q_c 3): 9 of 46 buckets (0 in the day session), largest one-side depth term 0.333 ticks

## Readings of the rule

- R1 time axis: Databento ts_recv; each mbp-1 record's top of book lasts until the next record's ts_recv (exact event-time weighting, not D.1's 1-second sampling).
- R2 'time-weighted mean over the five dates': pooled over the valid-book time of all five dates in the bucket (a date with less valid time weighs less); the equal-weight-per-date alternative is computed beside it as a sensitivity figure and is not used.
- R3 'quotes on a date': the bucket has any positive valid-book time (two-sided, ask > bid) on that date after the closure and grace exclusions; a standing book carried in from before the bucket counts.
- R4 median: the lower time-weighted median, the smallest size m whose cumulative time share is at least one half, pooled over the five dates' valid-book time in the bucket.
- R5 depth term per side: buy orders hit the ask, sell orders the bid; one-side slippage is s_b plus that side's depth term; the table's round turn at bucket b is commission/tick value + (s_b + depth_ask) + (s_b + depth_bid).
- R6 fallback: 'the product's other buckets' are those quoted on >= 3 dates; the fallback replaces the whole one-side slippage per side (half-spread and depth), taking the largest such value per side. A fallback bucket's own thin data are reported, not used.
- R7 event window: per side, the largest final one-side slippage over all the product's buckets (fallback buckets equal a qualified maximum, so they never raise it).
- R8 buckets: 30-minute CT clock buckets of the group's trading segments on each sample date; a partial half-hour at a segment edge is its own bucket keyed by its CT start (grains 07:30-07:45 and 13:00-13:20, livestock 13:00-13:05); the 1-second reopen grace after every closure (as sim/calibrate_slippage.py) is excluded from the first bucket of a segment.
- R9 headline: the unweighted mean, min and max of the round turn over the buckets that overlap design D6's day session [O, C) for the product (a bucket straddling O, such as 07:00-07:30 for a 07:20 open, is included).
- R10 the depth term is evaluated at the contract's q_c from Task 9 (reports/stage_e2a_vehicle_sizes.json); a member trading fewer than q_c contracts still pays the q_c depth term per contract (the rule states one table at q_c).

Reading R2's alternative (each date weighted equally instead of by its valid time) changes s_b by at most the following (largest five over all buckets):

- GC 04:30: pooled 2.0467 vs equal-date 2.0541 (|diff| 0.0075)
- CL 18:30: pooled 1.3192 vs equal-date 1.3222 (|diff| 0.0030)
- GC 06:30: pooled 1.9840 vs equal-date 1.9866 (|diff| 0.0026)
- MCL 18:30: pooled 1.0524 vs equal-date 1.0544 (|diff| 0.0020)
- MGC 04:30: pooled 1.1715 vs equal-date 1.1729 (|diff| 0.0014)

## Known limitations (recorded, not corrected)

- tbbo was not bought (user decisions U4 and U8), so D8's tbbo cross-check (trade-weighted effective half-spread beside s_b) does not exist; nothing replaces it.
- All five sample dates are Wednesdays, EIA crude-inventory release days, so energy's 09:30 CT bucket includes the release on every date (recorded, not corrected; D8 known limitation).
- Five dates is thin for a time-of-day table; no latency or adverse-selection model (as for MES). Calibrated on 2025-26 books, the table understates costs in thinner earlier years (D8 early-era bias: any member passing confirmation gets a period-appropriate re-check).
- The event-window cost needs E.2b's release calendar; the table gives the per-side value.

## Data handling

Every file's sha256 was checked against the E.1 manifest before decoding, and its record count against the manifest after. Databento writes one snapshot record per file at 00:00:00 UTC (flags SNAPSHOT and BAD_TS_RECV, ts_event = the book's last change, which is why 11 files show a first ts_event before their request window); it restates the standing book and is used as a state. RB's v.0 changed instrument at 00:00 UTC on 2025-05-14, 2025-08-13 and 2025-11-12 (the new instrument's first record is that snapshot, so the old book ends exactly there). MNQ 2025-11-12 and 2026-02-11 are three contiguous request pieces each, streamed as one.

Price scale (declared in sim/cost_inputs.py VENDOR_PRICE_FACTOR, verified here per product on every valid book state of the five dates): Databento quotes ZC, ZW, ZS, ZL, HE and LE in US cents, so their vendor-unit tick is 100 x the E.0 tick_size (USD); all others are factor 1. The check passes when every valid bid and ask lies on the vendor-unit tick grid (any off-grid price refuses the calibration), some lie off the grid of 10 x that tick, and a one-tick quoted spread occurs. Half-spreads are in vendor-unit ticks; USD = ticks x tick_value_usd.

Crossed books inside open time are short (seconds) and cluster in a few buckets (for example CL and MCL 18:30 CT on 2026-04-15, GC and MGC 04:30 CT on 2026-02-11), which looks like CME's brief reserve states after fast moves; they are dropped as D8 says and counted below.

Calendar modules changed after calibration for M2K, MNQ, MYM, NQ, RTY, YM (for the equity group, data/calendars/equity.py appeared at 02:26 PDT). The build recomputed every sample date's buckets from the current modules and found them identical to the nanosecond, so the calibration stands; both hashes are in the json (calendar_sha256 at calibration, calendar_sha256_at_build).

| Contract | Records | Midnight snapshots | Instrument switches | Empty rec / s | Locked rec / s | Crossed rec / s | Unknown s | Vendor factor | Prices off tick grid | Prices off 10x grid / checked | Min spread ticks | Scale check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 4,897,698 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 8,747,129 / 9,795,390 | 1 | pass |
| 6B | 3,286,321 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 5,881,825 / 6,572,636 | 1 | pass |
| 6C | 2,008,386 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 3,611,682 / 4,016,772 | 1 | pass |
| 6E | 6,421,321 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 11,541,552 / 12,842,638 | 1 | pass |
| 6J | 5,932,420 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 10,683,916 / 11,864,838 | 1 | pass |
| 6N | 2,380,451 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 4,256,880 / 4,760,900 | 1 | pass |
| 6S | 1,524,850 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 2,742,303 / 3,049,700 | 1 | pass |
| CL | 6,631,355 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 339 / 10.2 | 0.000 | 1 | 0 | 11,913,758 / 13,262,024 | 1 | pass |
| E7 | 1,255,761 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 2,276,217 / 2,511,522 | 1 | pass |
| GC | 7,645,686 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 238 / 45.1 | 0.000 | 1 | 0 | 13,695,830 / 15,290,886 | 1 | pass |
| HE | 246,577 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 100 | 0 | 443,919 / 493,040 | 1 | pass |
| HG | 1,906,104 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 16 / 5.0 | 0.000 | 1 | 0 | 3,425,558 / 3,812,172 | 1 | pass |
| HO | 2,524,492 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 4,504,486 / 5,048,982 | 1 | pass |
| LE | 427,453 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 100 | 0 | 766,891 / 854,822 | 1 | pass |
| M2K | 9,966,705 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 17,943,618 / 19,933,400 | 1 | pass |
| M6A | 792,718 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 1,442,322 / 1,585,434 | 1 | pass |
| M6B | 764,375 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 1,369,945 / 1,528,750 | 1 | pass |
| M6E | 1,911,097 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 3,466,702 / 3,822,192 | 1 | pass |
| MBT | 8,971,283 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 16,139,818 / 17,942,558 | 1 | pass |
| MCL | 4,807,541 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 644 / 15.1 | 0.000 | 1 | 0 | 8,637,170 / 9,613,784 | 1 | pass |
| MGC | 17,103,267 | 5 | 0 | 0 / 0.0 | 6 / 0.0 | 787 / 55.1 | 0.000 | 1 | 0 | 30,756,617 / 34,204,938 | 1 | pass |
| MHG | 2,086,991 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 3 / 5.0 | 0.000 | 1 | 0 | 3,753,866 / 4,173,968 | 1 | pass |
| MNG | 946,721 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 1,702,076 / 1,893,438 | 1 | pass |
| MNQ | 100,341,248 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 180,699,274 / 200,682,486 | 1 | pass |
| MYM | 18,628,234 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 33,512,865 / 37,256,460 | 1 | pass |
| NG | 1,895,733 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 3,418,428 / 3,791,458 | 1 | pass |
| NQ | 44,176,511 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 79,519,578 / 88,353,012 | 1 | pass |
| QG | 385,440 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 685,711 / 770,880 | 1 | pass |
| QM | 947,496 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 8 / 5.2 | 0.000 | 1 | 0 | 1,713,426 / 1,894,976 | 1 | pass |
| RB | 3,173,838 | 5 | 3 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 5,693,030 / 6,347,676 | 1 | pass |
| RTY | 13,888,284 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 24,985,364 / 27,776,562 | 1 | pass |
| SI | 4,307,011 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 16 / 5.0 | 0.000 | 1 | 0 | 7,714,647 / 8,613,984 | 1 | pass |
| SIL | 4,915,740 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 44 / 10.0 | 0.000 | 1 | 0 | 8,832,273 / 9,831,388 | 1 | pass |
| TN | 5,549,905 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 9,833,979 / 11,099,808 | 1 | pass |
| UB | 3,857,804 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 6,932,000 / 7,715,600 | 1 | pass |
| YM | 11,266,038 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 20,253,768 / 22,532,068 | 1 | pass |
| ZB | 4,480,209 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 8,303,829 / 8,960,410 | 1 | pass |
| ZC | 699,151 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 100 | 0 | 1,245,371 / 1,397,988 | 1 | pass |
| ZF | 7,999,644 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 14,348,396 / 15,999,278 | 1 | pass |
| ZL | 1,151,186 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 100 | 0 | 2,083,427 / 2,301,936 | 1 | pass |
| ZM | 968,252 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 1,715,755 / 1,936,266 | 1 | pass |
| ZN | 9,795,624 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 17,856,085 / 19,591,240 | 1 | pass |
| ZS | 1,551,302 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 100 | 0 | 2,797,225 / 3,102,224 | 1 | pass |
| ZT | 7,528,111 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 1 | 0 | 13,487,216 / 15,056,214 | 1 | pass |
| ZW | 713,234 | 5 | 0 | 0 / 0.0 | 0 / 0.0 | 0 / 0.0 | 0.000 | 100 | 0 | 1,300,621 / 1,426,024 | 1 | pass |

Compute (overnight profile): `free -m` before each run showed 10.3 GB available; peak estimate 1 GB per process (1M-record decode chunks, derived arrays and the per-contract histogram line), kept under a third of available memory with at most two processes at once. Measured peaks 0.54 and 0.84 GB RSS (the 44-contract run, 02:02-02:03 PDT, two single-threaded processes) and 0.89 GB (MBT, 02:13 PDT, after the crypto calendar loaded); nice 10; resumable per contract (one JSONL line per finished contract under the session scratchpad, `costs/calibration_raw_*.jsonl`). A first run at 01:44 PDT, made before the 10x-grid scale counter was added, was discarded whole and re-run with the final code; its figures were identical where comparable.

## MES check

30-minute s_b = mean of the two 15-minute 'half_spread_ticks_mean' values (each half equally weighted, as both are 1800 s of open time in D.1's uniform-second sampling); MES round turn = 1.22/1.25 + 2 s_b. No depth term: D.1's table records no top-of-book size (its size-5 walk is within 0.03 ticks of size 1 in the day session, so a 2-micro order would add at most about that).

Source: sim/slippage_calibration.json (D.1; read as recorded; no MES book file opened).

| Bucket CT | D.1 MES 15-min half-spreads | MES s_b (D8) | MES RT ticks | MES RT $ | MNQ s_b | MNQ RT ticks | MNQ RT $ |
|---|---|---|---|---|---|---|---|
| 00:00 | 0.5542, 0.5611 | 0.5576 | 2.0913 | 2.614 | 1.0495 | 4.5390 | 2.270 |
| 00:30 | 0.5514, 0.5514 | 0.5514 | 2.0788 | 2.599 | 1.0357 | 4.5114 | 2.256 |
| 01:00 | 0.5711, 0.5444 | 0.5577 | 2.0915 | 2.614 | 1.0461 | 4.5323 | 2.266 |
| 01:30 | 0.5497, 0.5786 | 0.5642 | 2.1043 | 2.630 | 1.0768 | 4.5937 | 2.297 |
| 02:00 | 0.5636, 0.5556 | 0.5596 | 2.0952 | 2.619 | 1.1077 | 4.6554 | 2.328 |
| 02:30 | 0.5603, 0.5589 | 0.5596 | 2.0952 | 2.619 | 1.1048 | 4.6496 | 2.325 |
| 03:00 | 0.5631, 0.5667 | 0.5649 | 2.1058 | 2.632 | 1.1286 | 4.6972 | 2.349 |
| 03:30 | 0.5614, 0.5642 | 0.5628 | 2.1016 | 2.627 | 1.0968 | 4.6335 | 2.317 |
| 04:00 | 0.5508, 0.5506 | 0.5507 | 2.0774 | 2.597 | 1.1666 | 4.7732 | 2.387 |
| 04:30 | 0.5522, 0.5492 | 0.5507 | 2.0774 | 2.597 | 1.1246 | 4.6892 | 2.345 |
| 05:00 | 0.5561, 0.5622 | 0.5592 | 2.0943 | 2.618 | 1.1062 | 4.6525 | 2.326 |
| 05:30 | 0.5636, 0.5553 | 0.5595 | 2.0949 | 2.619 | 1.1255 | 4.6910 | 2.346 |
| 06:00 | 0.5703, 0.5747 | 0.5725 | 2.1210 | 2.651 | 1.1255 | 4.6911 | 2.346 |
| 06:30 | 0.5611, 0.5656 | 0.5634 | 2.1027 | 2.628 | 1.1463 | 4.7327 | 2.366 |
| 07:00 | 0.5475, 0.5508 | 0.5492 | 2.0743 | 2.593 | 1.1424 | 4.7248 | 2.362 |
| 07:30 | 0.6222, 0.5333 | 0.5777 | 2.1315 | 2.664 | 1.1123 | 4.6646 | 2.332 |
| 08:00 | 0.5106, 0.5178 | 0.5142 | 2.0044 | 2.506 | 0.9373 | 4.3147 | 2.157 |
| 08:30 | 0.5408, 0.5536 | 0.5472 | 2.0704 | 2.588 | 0.9693 | 4.3786 | 2.189 |
| 09:00 | 0.5414, 0.5392 | 0.5403 | 2.0566 | 2.571 | 0.9031 | 4.2463 | 2.123 |
| 09:30 | 0.5481, 0.5461 | 0.5471 | 2.0702 | 2.588 | 0.8567 | 4.1535 | 2.077 |
| 10:00 | 0.5517, 0.5408 | 0.5463 | 2.0685 | 2.586 | 0.8279 | 4.0958 | 2.048 |
| 10:30 | 0.5397, 0.5344 | 0.5371 | 2.0501 | 2.563 | 0.8194 | 4.0788 | 2.039 |
| 11:00 | 0.5325, 0.5308 | 0.5316 | 2.0393 | 2.549 | 0.8160 | 4.0720 | 2.036 |
| 11:30 | 0.5261, 0.5317 | 0.5289 | 2.0338 | 2.542 | 0.8192 | 4.0784 | 2.039 |
| 12:00 | 0.5175, 0.5125 | 0.5150 | 2.0060 | 2.507 | 0.8231 | 4.0861 | 2.043 |
| 12:30 | 0.5189, 0.5136 | 0.5162 | 2.0085 | 2.511 | 0.8138 | 4.0675 | 2.034 |
| 13:00 | 0.5175, 0.5106 | 0.5141 | 2.0041 | 2.505 | 0.8104 | 4.0608 | 2.030 |
| 13:30 | 0.5142, 0.5158 | 0.5150 | 2.0060 | 2.507 | 0.8198 | 4.0795 | 2.040 |
| 14:00 | 0.5206, 0.5153 | 0.5180 | 2.0119 | 2.515 | 0.8166 | 4.0733 | 2.037 |
| 14:30 | 0.5178, 0.5203 | 0.5191 | 2.0141 | 2.518 | 0.8174 | 4.0748 | 2.037 |
| 15:00 | 0.5425, 0.5431 | 0.5428 | 2.0616 | 2.577 | 0.8717 | 4.1834 | 2.092 |
| 15:30 | 0.5281, 0.5844 | 0.5563 | 2.0885 | 2.611 | 0.9173 | 4.2746 | 2.137 |
| 17:00 | 0.5762, 0.5750 | 0.5756 | 2.1272 | 2.659 | 1.4859 | 5.4118 | 2.706 |
| 17:30 | 0.5533, 0.5761 | 0.5647 | 2.1054 | 2.632 | 1.2037 | 4.8474 | 2.424 |
| 18:00 | 0.5650, 0.5822 | 0.5736 | 2.1232 | 2.654 | 1.1297 | 4.6995 | 2.350 |
| 18:30 | 0.5411, 0.5572 | 0.5492 | 2.0743 | 2.593 | 1.1002 | 4.6403 | 2.320 |
| 19:00 | 0.5922, 0.5725 | 0.5824 | 2.1407 | 2.676 | 1.0663 | 4.5726 | 2.286 |
| 19:30 | 0.5517, 0.5608 | 0.5563 | 2.0885 | 2.611 | 1.0342 | 4.5083 | 2.254 |
| 20:00 | 0.5442, 0.5475 | 0.5458 | 2.0677 | 2.585 | 1.0202 | 4.4804 | 2.240 |
| 20:30 | 0.5583, 0.5511 | 0.5547 | 2.0854 | 2.607 | 1.0095 | 4.4590 | 2.230 |
| 21:00 | 0.5497, 0.5472 | 0.5484 | 2.0729 | 2.591 | 0.9997 | 4.4394 | 2.220 |
| 21:30 | 0.5411, 0.5314 | 0.5363 | 2.0485 | 2.561 | 1.0103 | 4.4606 | 2.230 |
| 22:00 | 0.5508, 0.5522 | 0.5515 | 2.0790 | 2.599 | 1.0146 | 4.4692 | 2.235 |
| 22:30 | 0.5575, 0.5494 | 0.5534 | 2.0829 | 2.604 | 1.0046 | 4.4492 | 2.225 |
| 23:00 | 0.5522, 0.5372 | 0.5447 | 2.0654 | 2.582 | 1.0106 | 4.4612 | 2.231 |
| 23:30 | 0.5400, 0.5336 | 0.5368 | 2.0496 | 2.562 | 1.0088 | 4.4577 | 2.229 |

Day session 08:30-15:00 CT (13 buckets), mean [min, max]:

- MES s_b ticks: 0.5289 [0.5141, 0.5472] (n=13)
- MES round turn ticks: 2.0338 [2.0041, 2.0704] (n=13)
- MES round turn USD: 2.5423 [2.5051, 2.5880] (n=13)
- MNQ s_b ticks: 0.8394 [0.8104, 0.9693] (n=13)
- MNQ round turn ticks: 4.1189 [4.0608, 4.3786] (n=13)
- MNQ round turn USD: 2.0594 [2.0304, 2.1893] (n=13)

All buckets (every 30-minute bucket both tables have), mean [min, max]:

- mes_round_turn_ticks: 2.0726 [2.0041, 2.1407] (n=46)
- mes_round_turn_usd: 2.5908 [2.5051, 2.6759] (n=46)
- mnq_round_turn_ticks: 4.4588 [4.0608, 5.4118] (n=46)
- mnq_round_turn_usd: 2.2294 [2.0304, 2.7059] (n=46)

D8's reasoning cites MES's model at 'about 2.11 ticks a round turn' (commission plus a time-of-day half-spread table).


Documented differences:
- D.1: two days of MES mbp-10 (2026-07-15, 2026-07-31, UTC-date files in MLCryptoEngine, inside holdout-1); D8: five full trade dates of mbp-1 (2025-05-14 to 2026-04-15) for MNQ.
- Different contracts: MES (tick $1.25, commission $1.22) against MNQ (tick $0.50, commission $1.22); the same exchange's micro equity index futures, not the same book.
- 15-minute buckets from uniform 1-second sampling (D.1) against 30-minute buckets time-weighted exactly by event time (D8); D.1's 15-minute means are recorded to 4 decimals.
- D.1 excluded seconds in closures and a 1 s grace like this calibration; its overnight buckets mix two trade dates (UTC-date files).

## Per-contract tables

Columns: dates quoted (of 5); s_b = pooled time-weighted mean half-spread (ticks); s_b equal-date = R2's alternative (not used); median top sizes (lower, time-weighted); depth term per side at q_c; final one-side slippage per side (fallback applied); round turn in ticks and USD. 'D' marks a day-session bucket.

### 6A (fx)

Tick 0.00005 (vendor units 0.00005, factor 1), tick value $5.0; commission $4.22 round turn = 0.8440 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.8167, sell 0.8167 ticks (round turn inside a window 2.4774 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.8167 | 0.8167 | 22 | 21 | 0.000 / 0.000 | 0.8167 / 0.8167 | 2.4774 | 12.387 |
| 17:30-18:00 |  | 5/5 |  | 0.7125 | 0.7125 | 38 | 31 | 0.000 / 0.000 | 0.7125 / 0.7125 | 2.2690 | 11.345 |
| 18:00-18:30 |  | 5/5 |  | 0.7298 | 0.7298 | 38 | 35 | 0.000 / 0.000 | 0.7298 / 0.7298 | 2.3037 | 11.518 |
| 18:30-19:00 |  | 5/5 |  | 0.7049 | 0.7049 | 37 | 37 | 0.000 / 0.000 | 0.7049 / 0.7049 | 2.2539 | 11.269 |
| 19:00-19:30 |  | 5/5 |  | 0.6663 | 0.6663 | 24 | 33 | 0.000 / 0.000 | 0.6663 / 0.6663 | 2.1765 | 10.883 |
| 19:30-20:00 |  | 5/5 |  | 0.6836 | 0.6836 | 31 | 31 | 0.000 / 0.000 | 0.6836 / 0.6836 | 2.2112 | 11.056 |
| 20:00-20:30 |  | 5/5 |  | 0.6963 | 0.6963 | 31 | 24 | 0.000 / 0.000 | 0.6963 / 0.6963 | 2.2366 | 11.183 |
| 20:30-21:00 |  | 5/5 |  | 0.6844 | 0.6844 | 22 | 23 | 0.000 / 0.000 | 0.6844 / 0.6844 | 2.2128 | 11.064 |
| 21:00-21:30 |  | 5/5 |  | 0.6759 | 0.6759 | 28 | 24 | 0.000 / 0.000 | 0.6759 / 0.6759 | 2.1958 | 10.979 |
| 21:30-22:00 |  | 5/5 |  | 0.6806 | 0.6806 | 24 | 25 | 0.000 / 0.000 | 0.6806 / 0.6806 | 2.2051 | 11.026 |
| 22:00-22:30 |  | 5/5 |  | 0.6597 | 0.6597 | 26 | 25 | 0.000 / 0.000 | 0.6597 / 0.6597 | 2.1634 | 10.817 |
| 22:30-23:00 |  | 5/5 |  | 0.7055 | 0.7055 | 34 | 31 | 0.000 / 0.000 | 0.7055 / 0.7055 | 2.2550 | 11.275 |
| 23:00-23:30 |  | 5/5 |  | 0.7010 | 0.7010 | 35 | 25 | 0.000 / 0.000 | 0.7010 / 0.7010 | 2.2460 | 11.230 |
| 23:30-00:00 |  | 5/5 |  | 0.6902 | 0.6902 | 37 | 31 | 0.000 / 0.000 | 0.6902 / 0.6902 | 2.2244 | 11.122 |
| 00:00-00:30 |  | 5/5 |  | 0.7079 | 0.7079 | 35 | 37 | 0.000 / 0.000 | 0.7079 / 0.7079 | 2.2597 | 11.299 |
| 00:30-01:00 |  | 5/5 |  | 0.6990 | 0.6990 | 30 | 36 | 0.000 / 0.000 | 0.6990 / 0.6990 | 2.2420 | 11.210 |
| 01:00-01:30 |  | 5/5 |  | 0.6967 | 0.6967 | 33 | 36 | 0.000 / 0.000 | 0.6967 / 0.6967 | 2.2375 | 11.187 |
| 01:30-02:00 |  | 5/5 |  | 0.6658 | 0.6658 | 30 | 35 | 0.000 / 0.000 | 0.6658 / 0.6658 | 2.1756 | 10.878 |
| 02:00-02:30 |  | 5/5 |  | 0.6525 | 0.6525 | 29 | 27 | 0.000 / 0.000 | 0.6525 / 0.6525 | 2.1490 | 10.745 |
| 02:30-03:00 |  | 5/5 |  | 0.6744 | 0.6744 | 37 | 31 | 0.000 / 0.000 | 0.6744 / 0.6744 | 2.1929 | 10.964 |
| 03:00-03:30 |  | 5/5 |  | 0.6781 | 0.6781 | 35 | 36 | 0.000 / 0.000 | 0.6781 / 0.6781 | 2.2002 | 11.001 |
| 03:30-04:00 |  | 5/5 |  | 0.6614 | 0.6614 | 34 | 28 | 0.000 / 0.000 | 0.6614 / 0.6614 | 2.1668 | 10.834 |
| 04:00-04:30 |  | 5/5 |  | 0.6963 | 0.6963 | 34 | 35 | 0.000 / 0.000 | 0.6963 / 0.6963 | 2.2366 | 11.183 |
| 04:30-05:00 |  | 5/5 |  | 0.6982 | 0.6982 | 51 | 35 | 0.000 / 0.000 | 0.6982 / 0.6982 | 2.2405 | 11.202 |
| 05:00-05:30 |  | 5/5 |  | 0.6912 | 0.6912 | 41 | 43 | 0.000 / 0.000 | 0.6912 / 0.6912 | 2.2264 | 11.132 |
| 05:30-06:00 |  | 5/5 |  | 0.6775 | 0.6775 | 36 | 38 | 0.000 / 0.000 | 0.6775 / 0.6775 | 2.1990 | 10.995 |
| 06:00-06:30 |  | 5/5 |  | 0.6890 | 0.6890 | 45 | 40 | 0.000 / 0.000 | 0.6890 / 0.6890 | 2.2220 | 11.110 |
| 06:30-07:00 |  | 5/5 |  | 0.6996 | 0.6996 | 46 | 48 | 0.000 / 0.000 | 0.6996 / 0.6996 | 2.2432 | 11.216 |
| 07:00-07:30 | D | 5/5 |  | 0.6684 | 0.6684 | 35 | 37 | 0.000 / 0.000 | 0.6684 / 0.6684 | 2.1807 | 10.904 |
| 07:30-08:00 | D | 5/5 |  | 0.6815 | 0.6815 | 39 | 36 | 0.000 / 0.000 | 0.6815 / 0.6815 | 2.2069 | 11.035 |
| 08:00-08:30 | D | 5/5 |  | 0.6677 | 0.6677 | 41 | 43 | 0.000 / 0.000 | 0.6677 / 0.6677 | 2.1793 | 10.897 |
| 08:30-09:00 | D | 5/5 |  | 0.6778 | 0.6778 | 41 | 42 | 0.000 / 0.000 | 0.6778 / 0.6778 | 2.1995 | 10.998 |
| 09:00-09:30 | D | 5/5 |  | 0.6788 | 0.6788 | 46 | 40 | 0.000 / 0.000 | 0.6788 / 0.6788 | 2.2015 | 11.008 |
| 09:30-10:00 | D | 5/5 |  | 0.6521 | 0.6521 | 45 | 43 | 0.000 / 0.000 | 0.6521 / 0.6521 | 2.1482 | 10.741 |
| 10:00-10:30 | D | 5/5 |  | 0.6566 | 0.6566 | 53 | 50 | 0.000 / 0.000 | 0.6566 / 0.6566 | 2.1572 | 10.786 |
| 10:30-11:00 | D | 5/5 |  | 0.6843 | 0.6843 | 59 | 56 | 0.000 / 0.000 | 0.6843 / 0.6843 | 2.2127 | 11.063 |
| 11:00-11:30 | D | 5/5 |  | 0.6726 | 0.6726 | 55 | 53 | 0.000 / 0.000 | 0.6726 / 0.6726 | 2.1892 | 10.946 |
| 11:30-12:00 | D | 5/5 |  | 0.6996 | 0.6996 | 64 | 64 | 0.000 / 0.000 | 0.6996 / 0.6996 | 2.2433 | 11.216 |
| 12:00-12:30 | D | 5/5 |  | 0.6755 | 0.6755 | 65 | 59 | 0.000 / 0.000 | 0.6755 / 0.6755 | 2.1949 | 10.975 |
| 12:30-13:00 | D | 5/5 |  | 0.6782 | 0.6782 | 68 | 55 | 0.000 / 0.000 | 0.6782 / 0.6782 | 2.2004 | 11.002 |
| 13:00-13:30 | D | 5/5 |  | 0.6747 | 0.6747 | 69 | 56 | 0.000 / 0.000 | 0.6747 / 0.6747 | 2.1935 | 10.967 |
| 13:30-14:00 | D | 5/5 |  | 0.6637 | 0.6637 | 71 | 61 | 0.000 / 0.000 | 0.6637 / 0.6637 | 2.1714 | 10.857 |
| 14:00-14:30 |  | 5/5 |  | 0.6823 | 0.6823 | 86 | 73 | 0.000 / 0.000 | 0.6823 / 0.6823 | 2.2087 | 11.043 |
| 14:30-15:00 |  | 5/5 |  | 0.6504 | 0.6504 | 67 | 67 | 0.000 / 0.000 | 0.6504 / 0.6504 | 2.1448 | 10.724 |
| 15:00-15:30 |  | 5/5 |  | 0.6646 | 0.6646 | 61 | 59 | 0.000 / 0.000 | 0.6646 / 0.6646 | 2.1731 | 10.866 |
| 15:30-16:00 |  | 5/5 |  | 0.7048 | 0.7048 | 52 | 49 | 0.000 / 0.000 | 0.7048 / 0.7048 | 2.2536 | 11.268 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6A_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 566305ac95c5df0e37176ba008a063eddb7cf1fbcd3c738f6233089ae7a509bb (1,021,463 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6A_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` d5db598f8c368b32c03fc40e6e369d0da7d059eaeff93e20ff7c35bac7857ec8 (548,526 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6A_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 676c8c02491386e6d84f84a997e0d9ead16382adb0dfae5b2dd40b02fdade449 (702,588 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6A_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 167da8e8ed229eac1c445308ccfa51f76a7b8beb5976137bdba2e3ac1408351c (1,616,353 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6A_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 6f37e09312a9693edaca22e0f796f8d5ddecfada087a6a4319314d6bba38de36 (1,008,768 records)

### 6B (fx)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $6.25; commission $4.22 round turn = 0.6752 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.6775, sell 0.6775 ticks (round turn inside a window 2.0302 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.6455 | 0.6455 | 17 | 27 | 0.000 / 0.000 | 0.6455 / 0.6455 | 1.9661 | 12.288 |
| 17:30-18:00 |  | 5/5 |  | 0.6443 | 0.6443 | 30 | 32 | 0.000 / 0.000 | 0.6443 / 0.6443 | 1.9638 | 12.274 |
| 18:00-18:30 |  | 5/5 |  | 0.6210 | 0.6210 | 25 | 30 | 0.000 / 0.000 | 0.6210 / 0.6210 | 1.9172 | 11.983 |
| 18:30-19:00 |  | 5/5 |  | 0.6625 | 0.6625 | 38 | 41 | 0.000 / 0.000 | 0.6625 / 0.6625 | 2.0003 | 12.502 |
| 19:00-19:30 |  | 5/5 |  | 0.6775 | 0.6775 | 38 | 40 | 0.000 / 0.000 | 0.6775 / 0.6775 | 2.0302 | 12.689 |
| 19:30-20:00 |  | 5/5 |  | 0.6687 | 0.6687 | 35 | 36 | 0.000 / 0.000 | 0.6687 / 0.6687 | 2.0126 | 12.578 |
| 20:00-20:30 |  | 5/5 |  | 0.6604 | 0.6604 | 33 | 31 | 0.000 / 0.000 | 0.6604 / 0.6604 | 1.9961 | 12.476 |
| 20:30-21:00 |  | 5/5 |  | 0.6633 | 0.6633 | 30 | 28 | 0.000 / 0.000 | 0.6633 / 0.6633 | 2.0019 | 12.512 |
| 21:00-21:30 |  | 5/5 |  | 0.6553 | 0.6553 | 30 | 32 | 0.000 / 0.000 | 0.6553 / 0.6553 | 1.9858 | 12.411 |
| 21:30-22:00 |  | 5/5 |  | 0.6269 | 0.6269 | 33 | 29 | 0.000 / 0.000 | 0.6269 / 0.6269 | 1.9289 | 12.056 |
| 22:00-22:30 |  | 5/5 |  | 0.6246 | 0.6246 | 27 | 32 | 0.000 / 0.000 | 0.6246 / 0.6246 | 1.9244 | 12.027 |
| 22:30-23:00 |  | 5/5 |  | 0.6661 | 0.6661 | 37 | 32 | 0.000 / 0.000 | 0.6661 / 0.6661 | 2.0073 | 12.546 |
| 23:00-23:30 |  | 5/5 |  | 0.6492 | 0.6492 | 42 | 30 | 0.000 / 0.000 | 0.6492 / 0.6492 | 1.9737 | 12.335 |
| 23:30-00:00 |  | 5/5 |  | 0.6623 | 0.6623 | 41 | 35 | 0.000 / 0.000 | 0.6623 / 0.6623 | 1.9998 | 12.499 |
| 00:00-00:30 |  | 5/5 |  | 0.6448 | 0.6448 | 37 | 33 | 0.000 / 0.000 | 0.6448 / 0.6448 | 1.9648 | 12.280 |
| 00:30-01:00 |  | 5/5 |  | 0.6754 | 0.6754 | 36 | 45 | 0.000 / 0.000 | 0.6754 / 0.6754 | 2.0260 | 12.663 |
| 01:00-01:30 |  | 5/5 |  | 0.6304 | 0.6304 | 30 | 35 | 0.000 / 0.000 | 0.6304 / 0.6304 | 1.9360 | 12.100 |
| 01:30-02:00 |  | 5/5 |  | 0.6509 | 0.6509 | 31 | 35 | 0.000 / 0.000 | 0.6509 / 0.6509 | 1.9769 | 12.356 |
| 02:00-02:30 |  | 5/5 |  | 0.6087 | 0.6087 | 27 | 31 | 0.000 / 0.000 | 0.6087 / 0.6087 | 1.8926 | 11.829 |
| 02:30-03:00 |  | 5/5 |  | 0.6487 | 0.6487 | 38 | 35 | 0.000 / 0.000 | 0.6487 / 0.6487 | 1.9726 | 12.328 |
| 03:00-03:30 |  | 5/5 |  | 0.6458 | 0.6458 | 36 | 38 | 0.000 / 0.000 | 0.6458 / 0.6458 | 1.9668 | 12.292 |
| 03:30-04:00 |  | 5/5 |  | 0.6340 | 0.6340 | 30 | 36 | 0.000 / 0.000 | 0.6340 / 0.6340 | 1.9432 | 12.145 |
| 04:00-04:30 |  | 5/5 |  | 0.6578 | 0.6578 | 40 | 38 | 0.000 / 0.000 | 0.6578 / 0.6578 | 1.9909 | 12.443 |
| 04:30-05:00 |  | 5/5 |  | 0.6250 | 0.6250 | 35 | 34 | 0.000 / 0.000 | 0.6250 / 0.6250 | 1.9252 | 12.032 |
| 05:00-05:30 |  | 5/5 |  | 0.6404 | 0.6404 | 34 | 33 | 0.000 / 0.000 | 0.6404 / 0.6404 | 1.9560 | 12.225 |
| 05:30-06:00 |  | 5/5 |  | 0.6518 | 0.6518 | 36 | 37 | 0.000 / 0.000 | 0.6518 / 0.6518 | 1.9788 | 12.368 |
| 06:00-06:30 |  | 5/5 |  | 0.6249 | 0.6249 | 39 | 31 | 0.000 / 0.000 | 0.6249 / 0.6249 | 1.9250 | 12.031 |
| 06:30-07:00 |  | 5/5 |  | 0.6301 | 0.6301 | 44 | 39 | 0.000 / 0.000 | 0.6301 / 0.6301 | 1.9354 | 12.096 |
| 07:00-07:30 | D | 5/5 |  | 0.6408 | 0.6408 | 42 | 42 | 0.000 / 0.000 | 0.6408 / 0.6408 | 1.9568 | 12.230 |
| 07:30-08:00 | D | 5/5 |  | 0.6485 | 0.6485 | 40 | 44 | 0.000 / 0.000 | 0.6485 / 0.6485 | 1.9722 | 12.326 |
| 08:00-08:30 | D | 5/5 |  | 0.6287 | 0.6287 | 41 | 50 | 0.000 / 0.000 | 0.6287 / 0.6287 | 1.9325 | 12.078 |
| 08:30-09:00 | D | 5/5 |  | 0.6161 | 0.6161 | 39 | 41 | 0.000 / 0.000 | 0.6161 / 0.6161 | 1.9075 | 11.922 |
| 09:00-09:30 | D | 5/5 |  | 0.6199 | 0.6199 | 43 | 35 | 0.000 / 0.000 | 0.6199 / 0.6199 | 1.9151 | 11.969 |
| 09:30-10:00 | D | 5/5 |  | 0.6110 | 0.6110 | 50 | 43 | 0.000 / 0.000 | 0.6110 / 0.6110 | 1.8971 | 11.857 |
| 10:00-10:30 | D | 5/5 |  | 0.6188 | 0.6188 | 53 | 54 | 0.000 / 0.000 | 0.6188 / 0.6188 | 1.9127 | 11.954 |
| 10:30-11:00 | D | 5/5 |  | 0.6131 | 0.6131 | 47 | 48 | 0.000 / 0.000 | 0.6131 / 0.6131 | 1.9014 | 11.884 |
| 11:00-11:30 | D | 5/5 |  | 0.6054 | 0.6054 | 43 | 35 | 0.000 / 0.000 | 0.6054 / 0.6054 | 1.8859 | 11.787 |
| 11:30-12:00 | D | 5/5 |  | 0.6332 | 0.6332 | 60 | 41 | 0.000 / 0.000 | 0.6332 / 0.6332 | 1.9415 | 12.135 |
| 12:00-12:30 | D | 5/5 |  | 0.6213 | 0.6213 | 54 | 45 | 0.000 / 0.000 | 0.6213 / 0.6213 | 1.9179 | 11.987 |
| 12:30-13:00 | D | 5/5 |  | 0.6306 | 0.6306 | 51 | 57 | 0.000 / 0.000 | 0.6306 / 0.6306 | 1.9364 | 12.102 |
| 13:00-13:30 | D | 5/5 |  | 0.6227 | 0.6227 | 56 | 44 | 0.000 / 0.000 | 0.6227 / 0.6227 | 1.9206 | 12.004 |
| 13:30-14:00 | D | 5/5 |  | 0.5756 | 0.5756 | 53 | 45 | 0.000 / 0.000 | 0.5756 / 0.5756 | 1.8264 | 11.415 |
| 14:00-14:30 |  | 5/5 |  | 0.5962 | 0.5962 | 64 | 52 | 0.000 / 0.000 | 0.5962 / 0.5962 | 1.8676 | 11.672 |
| 14:30-15:00 |  | 5/5 |  | 0.6261 | 0.6261 | 58 | 63 | 0.000 / 0.000 | 0.6261 / 0.6261 | 1.9273 | 12.046 |
| 15:00-15:30 |  | 5/5 |  | 0.6256 | 0.6256 | 63 | 56 | 0.000 / 0.000 | 0.6256 / 0.6256 | 1.9264 | 12.040 |
| 15:30-16:00 |  | 5/5 |  | 0.6549 | 0.6549 | 44 | 40 | 0.000 / 0.000 | 0.6549 / 0.6549 | 1.9850 | 12.406 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6B_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` d2ef7053cb74d77a302719d0330e4f825505723089e281a0158323d424d1ab6d (894,460 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6B_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 1544dbed3d6af746b02d80af36cdcf93a4d0c751cc2da4d05b4bf584a0afedc4 (400,872 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6B_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` c7e7831b547d56070f13b86e5d490c056b43a39deb426b64a24eafa018120813 (475,700 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6B_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 488d0917177032179af677f611927e32178c330df32b9f7fec0a1ad8ee9cd623 (868,694 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6B_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 9a46792efea74cb3b4909ca1a86f6165b33625a6a49fb355a261470df4630f4b (646,595 records)

### 6C (fx)

Tick 0.00005 (vendor units 0.00005, factor 1), tick value $5.0; commission $4.22 round turn = 0.8440 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.6851, sell 0.6851 ticks (round turn inside a window 2.2141 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.6767 | 0.6767 | 19 | 21 | 0.000 / 0.000 | 0.6767 / 0.6767 | 2.1974 | 10.987 |
| 17:30-18:00 |  | 5/5 |  | 0.6342 | 0.6342 | 30 | 21 | 0.000 / 0.000 | 0.6342 / 0.6342 | 2.1124 | 10.562 |
| 18:00-18:30 |  | 5/5 |  | 0.6486 | 0.6486 | 21 | 25 | 0.000 / 0.000 | 0.6486 / 0.6486 | 2.1411 | 10.706 |
| 18:30-19:00 |  | 5/5 |  | 0.6121 | 0.6121 | 19 | 28 | 0.000 / 0.000 | 0.6121 / 0.6121 | 2.0683 | 10.341 |
| 19:00-19:30 |  | 5/5 |  | 0.6651 | 0.6651 | 22 | 35 | 0.000 / 0.000 | 0.6651 / 0.6651 | 2.1741 | 10.871 |
| 19:30-20:00 |  | 5/5 |  | 0.6543 | 0.6543 | 30 | 33 | 0.000 / 0.000 | 0.6543 / 0.6543 | 2.1525 | 10.763 |
| 20:00-20:30 |  | 5/5 |  | 0.6437 | 0.6437 | 25 | 30 | 0.000 / 0.000 | 0.6437 / 0.6437 | 2.1314 | 10.657 |
| 20:30-21:00 |  | 5/5 |  | 0.6723 | 0.6723 | 29 | 37 | 0.000 / 0.000 | 0.6723 / 0.6723 | 2.1886 | 10.943 |
| 21:00-21:30 |  | 5/5 |  | 0.6475 | 0.6475 | 29 | 39 | 0.000 / 0.000 | 0.6475 / 0.6475 | 2.1390 | 10.695 |
| 21:30-22:00 |  | 5/5 |  | 0.6464 | 0.6464 | 26 | 38 | 0.000 / 0.000 | 0.6464 / 0.6464 | 2.1367 | 10.684 |
| 22:00-22:30 |  | 5/5 |  | 0.6234 | 0.6234 | 24 | 49 | 0.000 / 0.000 | 0.6234 / 0.6234 | 2.0909 | 10.454 |
| 22:30-23:00 |  | 5/5 |  | 0.6180 | 0.6180 | 26 | 40 | 0.000 / 0.000 | 0.6180 / 0.6180 | 2.0800 | 10.400 |
| 23:00-23:30 |  | 5/5 |  | 0.6791 | 0.6791 | 38 | 44 | 0.000 / 0.000 | 0.6791 / 0.6791 | 2.2021 | 11.011 |
| 23:30-00:00 |  | 5/5 |  | 0.6441 | 0.6441 | 28 | 29 | 0.000 / 0.000 | 0.6441 / 0.6441 | 2.1323 | 10.661 |
| 00:00-00:30 |  | 5/5 |  | 0.6851 | 0.6851 | 46 | 39 | 0.000 / 0.000 | 0.6851 / 0.6851 | 2.2141 | 11.071 |
| 00:30-01:00 |  | 5/5 |  | 0.6499 | 0.6499 | 27 | 33 | 0.000 / 0.000 | 0.6499 / 0.6499 | 2.1438 | 10.719 |
| 01:00-01:30 |  | 5/5 |  | 0.6016 | 0.6016 | 26 | 27 | 0.000 / 0.000 | 0.6016 / 0.6016 | 2.0471 | 10.236 |
| 01:30-02:00 |  | 5/5 |  | 0.6089 | 0.6089 | 31 | 28 | 0.000 / 0.000 | 0.6089 / 0.6089 | 2.0618 | 10.309 |
| 02:00-02:30 |  | 5/5 |  | 0.5752 | 0.5752 | 25 | 35 | 0.000 / 0.000 | 0.5752 / 0.5752 | 1.9943 | 9.972 |
| 02:30-03:00 |  | 5/5 |  | 0.5994 | 0.5994 | 36 | 28 | 0.000 / 0.000 | 0.5994 / 0.5994 | 2.0427 | 10.214 |
| 03:00-03:30 |  | 5/5 |  | 0.5954 | 0.5954 | 31 | 26 | 0.000 / 0.000 | 0.5954 / 0.5954 | 2.0347 | 10.174 |
| 03:30-04:00 |  | 5/5 |  | 0.5977 | 0.5977 | 29 | 27 | 0.000 / 0.000 | 0.5977 / 0.5977 | 2.0393 | 10.197 |
| 04:00-04:30 |  | 5/5 |  | 0.6219 | 0.6219 | 29 | 27 | 0.000 / 0.000 | 0.6219 / 0.6219 | 2.0879 | 10.439 |
| 04:30-05:00 |  | 5/5 |  | 0.6357 | 0.6357 | 37 | 30 | 0.000 / 0.000 | 0.6357 / 0.6357 | 2.1154 | 10.577 |
| 05:00-05:30 |  | 5/5 |  | 0.5945 | 0.5945 | 31 | 24 | 0.000 / 0.000 | 0.5945 / 0.5945 | 2.0330 | 10.165 |
| 05:30-06:00 |  | 5/5 |  | 0.6101 | 0.6101 | 35 | 29 | 0.000 / 0.000 | 0.6101 / 0.6101 | 2.0641 | 10.321 |
| 06:00-06:30 |  | 5/5 |  | 0.6047 | 0.6047 | 32 | 33 | 0.000 / 0.000 | 0.6047 / 0.6047 | 2.0533 | 10.267 |
| 06:30-07:00 |  | 5/5 |  | 0.5848 | 0.5848 | 31 | 35 | 0.000 / 0.000 | 0.5848 / 0.5848 | 2.0136 | 10.068 |
| 07:00-07:30 | D | 5/5 |  | 0.5739 | 0.5739 | 33 | 26 | 0.000 / 0.000 | 0.5739 / 0.5739 | 1.9918 | 9.959 |
| 07:30-08:00 | D | 5/5 |  | 0.5957 | 0.5957 | 30 | 31 | 0.000 / 0.000 | 0.5957 / 0.5957 | 2.0355 | 10.177 |
| 08:00-08:30 | D | 5/5 |  | 0.6124 | 0.6124 | 38 | 43 | 0.000 / 0.000 | 0.6124 / 0.6124 | 2.0688 | 10.344 |
| 08:30-09:00 | D | 5/5 |  | 0.5858 | 0.5858 | 37 | 43 | 0.000 / 0.000 | 0.5858 / 0.5858 | 2.0157 | 10.078 |
| 09:00-09:30 | D | 5/5 |  | 0.5859 | 0.5859 | 42 | 42 | 0.000 / 0.000 | 0.5859 / 0.5859 | 2.0159 | 10.079 |
| 09:30-10:00 | D | 5/5 |  | 0.5868 | 0.5868 | 45 | 46 | 0.000 / 0.000 | 0.5868 / 0.5868 | 2.0177 | 10.088 |
| 10:00-10:30 | D | 5/5 |  | 0.5975 | 0.5975 | 51 | 46 | 0.000 / 0.000 | 0.5975 / 0.5975 | 2.0389 | 10.195 |
| 10:30-11:00 | D | 5/5 |  | 0.6024 | 0.6024 | 46 | 45 | 0.000 / 0.000 | 0.6024 / 0.6024 | 2.0489 | 10.244 |
| 11:00-11:30 | D | 5/5 |  | 0.6088 | 0.6088 | 44 | 43 | 0.000 / 0.000 | 0.6088 / 0.6088 | 2.0617 | 10.308 |
| 11:30-12:00 | D | 5/5 |  | 0.5901 | 0.5901 | 41 | 45 | 0.000 / 0.000 | 0.5901 / 0.5901 | 2.0242 | 10.121 |
| 12:00-12:30 | D | 5/5 |  | 0.5769 | 0.5769 | 51 | 42 | 0.000 / 0.000 | 0.5769 / 0.5769 | 1.9978 | 9.989 |
| 12:30-13:00 | D | 5/5 |  | 0.5910 | 0.5910 | 47 | 49 | 0.000 / 0.000 | 0.5910 / 0.5910 | 2.0259 | 10.130 |
| 13:00-13:30 | D | 5/5 |  | 0.5830 | 0.5830 | 54 | 43 | 0.000 / 0.000 | 0.5830 / 0.5830 | 2.0099 | 10.050 |
| 13:30-14:00 | D | 5/5 |  | 0.5831 | 0.5831 | 54 | 53 | 0.000 / 0.000 | 0.5831 / 0.5831 | 2.0101 | 10.051 |
| 14:00-14:30 |  | 5/5 |  | 0.5812 | 0.5812 | 57 | 64 | 0.000 / 0.000 | 0.5812 / 0.5812 | 2.0064 | 10.032 |
| 14:30-15:00 |  | 5/5 |  | 0.6211 | 0.6211 | 53 | 71 | 0.000 / 0.000 | 0.6211 / 0.6211 | 2.0861 | 10.431 |
| 15:00-15:30 |  | 5/5 |  | 0.6105 | 0.6105 | 49 | 44 | 0.000 / 0.000 | 0.6105 / 0.6105 | 2.0650 | 10.325 |
| 15:30-16:00 |  | 5/5 |  | 0.6800 | 0.6800 | 34 | 39 | 0.000 / 0.000 | 0.6800 / 0.6800 | 2.2041 | 11.020 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6C_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` b66cdb57e2725982bf586793a4c503dc6fc9a30b4a38d0d0e952ab56aa39b4d0 (450,110 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6C_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 4a5a3f853b1b3a820d5fc0717e5b3727c55e48bdee7aa868f15aa115f1e2da6a (252,117 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6C_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` aee493532312138e3279bb673fa1387fa73c0b98a1adecf8ef26ede0d9b5a730 (285,796 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6C_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 935b3d17f2ff3cffccb8b706e117f11567a0a5c2cba7588923b73956fd690040 (690,846 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6C_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` c0d13313f647126a915639ffe4489b488cdc86e10197ca7e01d97ae2b54f192d (329,517 records)

### 6E (fx)

Tick 0.00005 (vendor units 0.00005, factor 1), tick value $6.25; commission $4.22 round turn = 0.6752 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.8151, sell 0.8151 ticks (round turn inside a window 2.3054 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.8151 | 0.8151 | 14 | 13 | 0.000 / 0.000 | 0.8151 / 0.8151 | 2.3054 | 14.409 |
| 17:30-18:00 |  | 5/5 |  | 0.7575 | 0.7575 | 22 | 19 | 0.000 / 0.000 | 0.7575 / 0.7575 | 2.1902 | 13.689 |
| 18:00-18:30 |  | 5/5 |  | 0.7072 | 0.7072 | 19 | 20 | 0.000 / 0.000 | 0.7072 / 0.7072 | 2.0895 | 13.059 |
| 18:30-19:00 |  | 5/5 |  | 0.7257 | 0.7257 | 20 | 21 | 0.000 / 0.000 | 0.7257 / 0.7257 | 2.1266 | 13.291 |
| 19:00-19:30 |  | 5/5 |  | 0.7157 | 0.7157 | 19 | 17 | 0.000 / 0.000 | 0.7157 / 0.7157 | 2.1066 | 13.166 |
| 19:30-20:00 |  | 5/5 |  | 0.6949 | 0.6949 | 22 | 18 | 0.000 / 0.000 | 0.6949 / 0.6949 | 2.0649 | 12.906 |
| 20:00-20:30 |  | 5/5 |  | 0.7135 | 0.7135 | 17 | 20 | 0.000 / 0.000 | 0.7135 / 0.7135 | 2.1021 | 13.138 |
| 20:30-21:00 |  | 5/5 |  | 0.7021 | 0.7021 | 15 | 17 | 0.000 / 0.000 | 0.7021 / 0.7021 | 2.0794 | 12.996 |
| 21:00-21:30 |  | 5/5 |  | 0.6992 | 0.6992 | 16 | 19 | 0.000 / 0.000 | 0.6992 / 0.6992 | 2.0737 | 12.961 |
| 21:30-22:00 |  | 5/5 |  | 0.7242 | 0.7242 | 19 | 21 | 0.000 / 0.000 | 0.7242 / 0.7242 | 2.1236 | 13.273 |
| 22:00-22:30 |  | 5/5 |  | 0.6993 | 0.6993 | 15 | 19 | 0.000 / 0.000 | 0.6993 / 0.6993 | 2.0737 | 12.961 |
| 22:30-23:00 |  | 5/5 |  | 0.6835 | 0.6835 | 17 | 17 | 0.000 / 0.000 | 0.6835 / 0.6835 | 2.0421 | 12.763 |
| 23:00-23:30 |  | 5/5 |  | 0.6786 | 0.6786 | 16 | 16 | 0.000 / 0.000 | 0.6786 / 0.6786 | 2.0324 | 12.703 |
| 23:30-00:00 |  | 5/5 |  | 0.6794 | 0.6794 | 20 | 15 | 0.000 / 0.000 | 0.6794 / 0.6794 | 2.0341 | 12.713 |
| 00:00-00:30 |  | 5/5 |  | 0.6932 | 0.6932 | 21 | 19 | 0.000 / 0.000 | 0.6932 / 0.6932 | 2.0617 | 12.886 |
| 00:30-01:00 |  | 5/5 |  | 0.7018 | 0.7018 | 18 | 21 | 0.000 / 0.000 | 0.7018 / 0.7018 | 2.0788 | 12.992 |
| 01:00-01:30 |  | 5/5 |  | 0.6615 | 0.6615 | 17 | 17 | 0.000 / 0.000 | 0.6615 / 0.6615 | 1.9981 | 12.488 |
| 01:30-02:00 |  | 5/5 |  | 0.6368 | 0.6368 | 14 | 15 | 0.000 / 0.000 | 0.6368 / 0.6368 | 1.9487 | 12.179 |
| 02:00-02:30 |  | 5/5 |  | 0.6635 | 0.6635 | 20 | 17 | 0.000 / 0.000 | 0.6635 / 0.6635 | 2.0022 | 12.514 |
| 02:30-03:00 |  | 5/5 |  | 0.6572 | 0.6572 | 22 | 18 | 0.000 / 0.000 | 0.6572 / 0.6572 | 1.9895 | 12.435 |
| 03:00-03:30 |  | 5/5 |  | 0.6658 | 0.6658 | 21 | 20 | 0.000 / 0.000 | 0.6658 / 0.6658 | 2.0067 | 12.542 |
| 03:30-04:00 |  | 5/5 |  | 0.6642 | 0.6642 | 21 | 19 | 0.000 / 0.000 | 0.6642 / 0.6642 | 2.0035 | 12.522 |
| 04:00-04:30 |  | 5/5 |  | 0.6727 | 0.6727 | 21 | 21 | 0.000 / 0.000 | 0.6727 / 0.6727 | 2.0205 | 12.628 |
| 04:30-05:00 |  | 5/5 |  | 0.6652 | 0.6652 | 21 | 20 | 0.000 / 0.000 | 0.6652 / 0.6652 | 2.0056 | 12.535 |
| 05:00-05:30 |  | 5/5 |  | 0.6622 | 0.6622 | 22 | 22 | 0.000 / 0.000 | 0.6622 / 0.6622 | 1.9997 | 12.498 |
| 05:30-06:00 |  | 5/5 |  | 0.6595 | 0.6595 | 22 | 21 | 0.000 / 0.000 | 0.6595 / 0.6595 | 1.9941 | 12.463 |
| 06:00-06:30 |  | 5/5 |  | 0.6585 | 0.6585 | 21 | 21 | 0.000 / 0.000 | 0.6585 / 0.6585 | 1.9921 | 12.451 |
| 06:30-07:00 |  | 5/5 |  | 0.6559 | 0.6559 | 23 | 20 | 0.000 / 0.000 | 0.6559 / 0.6559 | 1.9870 | 12.419 |
| 07:00-07:30 | D | 5/5 |  | 0.6379 | 0.6379 | 21 | 20 | 0.000 / 0.000 | 0.6379 / 0.6379 | 1.9510 | 12.194 |
| 07:30-08:00 | D | 5/5 |  | 0.6298 | 0.6298 | 17 | 15 | 0.000 / 0.000 | 0.6298 / 0.6298 | 1.9347 | 12.092 |
| 08:00-08:30 | D | 5/5 |  | 0.6329 | 0.6329 | 19 | 20 | 0.000 / 0.000 | 0.6329 / 0.6329 | 1.9410 | 12.131 |
| 08:30-09:00 | D | 5/5 |  | 0.6095 | 0.6095 | 19 | 18 | 0.000 / 0.000 | 0.6095 / 0.6095 | 1.8941 | 11.838 |
| 09:00-09:30 | D | 5/5 |  | 0.6172 | 0.6172 | 20 | 19 | 0.000 / 0.000 | 0.6172 / 0.6172 | 1.9096 | 11.935 |
| 09:30-10:00 | D | 5/5 |  | 0.6212 | 0.6212 | 23 | 22 | 0.000 / 0.000 | 0.6212 / 0.6212 | 1.9175 | 11.984 |
| 10:00-10:30 | D | 5/5 |  | 0.6199 | 0.6199 | 23 | 24 | 0.000 / 0.000 | 0.6199 / 0.6199 | 1.9150 | 11.969 |
| 10:30-11:00 | D | 5/5 |  | 0.6304 | 0.6304 | 24 | 26 | 0.000 / 0.000 | 0.6304 / 0.6304 | 1.9360 | 12.100 |
| 11:00-11:30 | D | 5/5 |  | 0.6343 | 0.6343 | 23 | 26 | 0.000 / 0.000 | 0.6343 / 0.6343 | 1.9437 | 12.148 |
| 11:30-12:00 | D | 5/5 |  | 0.6375 | 0.6375 | 22 | 25 | 0.000 / 0.000 | 0.6375 / 0.6375 | 1.9503 | 12.189 |
| 12:00-12:30 | D | 5/5 |  | 0.6501 | 0.6501 | 24 | 29 | 0.000 / 0.000 | 0.6501 / 0.6501 | 1.9754 | 12.346 |
| 12:30-13:00 | D | 5/5 |  | 0.6215 | 0.6215 | 29 | 25 | 0.000 / 0.000 | 0.6215 / 0.6215 | 1.9183 | 11.989 |
| 13:00-13:30 | D | 5/5 |  | 0.6396 | 0.6396 | 25 | 28 | 0.000 / 0.000 | 0.6396 / 0.6396 | 1.9544 | 12.215 |
| 13:30-14:00 | D | 5/5 |  | 0.6344 | 0.6344 | 28 | 30 | 0.000 / 0.000 | 0.6344 / 0.6344 | 1.9441 | 12.150 |
| 14:00-14:30 |  | 5/5 |  | 0.6353 | 0.6353 | 29 | 29 | 0.000 / 0.000 | 0.6353 / 0.6353 | 1.9459 | 12.162 |
| 14:30-15:00 |  | 5/5 |  | 0.6185 | 0.6185 | 24 | 30 | 0.000 / 0.000 | 0.6185 / 0.6185 | 1.9121 | 11.951 |
| 15:00-15:30 |  | 5/5 |  | 0.6784 | 0.6784 | 28 | 28 | 0.000 / 0.000 | 0.6784 / 0.6784 | 2.0320 | 12.700 |
| 15:30-16:00 |  | 5/5 |  | 0.6703 | 0.6703 | 20 | 19 | 0.000 / 0.000 | 0.6703 / 0.6703 | 2.0157 | 12.598 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6E_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 6eac9fbbeb76bef529070ab634f245f414f356d9315a6cb69af9c743da156667 (1,752,323 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6E_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` f62d1fa1c48c9ebbbca7f534b1ece0bd121b27d76182f306fd87cb606c8c46e8 (820,207 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6E_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 2777c16a782fd8cc5aa72c1098cf2c511af5a7448f3ffb5d76ce1157ec663138 (913,383 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6E_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` c5df07c39f27a5748d584b7262202263cb1131c785b64de8b02d041fc80db7ce (1,842,395 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6E_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 4771e2c46345b61bc06d80ec115ce67708fa1bcfbaacb87472155872d607df96 (1,093,013 records)

### 6J (fx)

Tick 5E-7 (vendor units 5E-7, factor 1), tick value $6.25; commission $4.22 round turn = 0.6752 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.7133, sell 0.7133 ticks (round turn inside a window 2.1017 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.7133 | 0.7133 | 24 | 28 | 0.000 / 0.000 | 0.7133 / 0.7133 | 2.1017 | 13.136 |
| 17:30-18:00 |  | 5/5 |  | 0.5806 | 0.5806 | 33 | 29 | 0.000 / 0.000 | 0.5806 / 0.5806 | 1.8365 | 11.478 |
| 18:00-18:30 |  | 5/5 |  | 0.5826 | 0.5826 | 38 | 34 | 0.000 / 0.000 | 0.5826 / 0.5826 | 1.8404 | 11.503 |
| 18:30-19:00 |  | 5/5 |  | 0.6216 | 0.6216 | 39 | 39 | 0.000 / 0.000 | 0.6216 / 0.6216 | 1.9185 | 11.991 |
| 19:00-19:30 |  | 5/5 |  | 0.5852 | 0.5852 | 32 | 30 | 0.000 / 0.000 | 0.5852 / 0.5852 | 1.8455 | 11.535 |
| 19:30-20:00 |  | 5/5 |  | 0.6125 | 0.6125 | 39 | 38 | 0.000 / 0.000 | 0.6125 / 0.6125 | 1.9001 | 11.876 |
| 20:00-20:30 |  | 5/5 |  | 0.6033 | 0.6033 | 33 | 33 | 0.000 / 0.000 | 0.6033 / 0.6033 | 1.8819 | 11.762 |
| 20:30-21:00 |  | 5/5 |  | 0.5920 | 0.5920 | 37 | 30 | 0.000 / 0.000 | 0.5920 / 0.5920 | 1.8593 | 11.620 |
| 21:00-21:30 |  | 5/5 |  | 0.6162 | 0.6162 | 41 | 38 | 0.000 / 0.000 | 0.6162 / 0.6162 | 1.9076 | 11.923 |
| 21:30-22:00 |  | 5/5 |  | 0.5958 | 0.5958 | 38 | 43 | 0.000 / 0.000 | 0.5958 / 0.5958 | 1.8667 | 11.667 |
| 22:00-22:30 |  | 5/5 |  | 0.6018 | 0.6018 | 42 | 37 | 0.000 / 0.000 | 0.6018 / 0.6018 | 1.8788 | 11.742 |
| 22:30-23:00 |  | 5/5 |  | 0.6095 | 0.6095 | 45 | 34 | 0.000 / 0.000 | 0.6095 / 0.6095 | 1.8942 | 11.839 |
| 23:00-23:30 |  | 5/5 |  | 0.6098 | 0.6098 | 41 | 40 | 0.000 / 0.000 | 0.6098 / 0.6098 | 1.8948 | 11.843 |
| 23:30-00:00 |  | 5/5 |  | 0.6133 | 0.6133 | 41 | 34 | 0.000 / 0.000 | 0.6133 / 0.6133 | 1.9019 | 11.887 |
| 00:00-00:30 |  | 5/5 |  | 0.6140 | 0.6140 | 35 | 48 | 0.000 / 0.000 | 0.6140 / 0.6140 | 1.9033 | 11.895 |
| 00:30-01:00 |  | 5/5 |  | 0.5969 | 0.5969 | 38 | 39 | 0.000 / 0.000 | 0.5969 / 0.5969 | 1.8690 | 11.682 |
| 01:00-01:30 |  | 5/5 |  | 0.6439 | 0.6439 | 48 | 45 | 0.000 / 0.000 | 0.6439 / 0.6439 | 1.9630 | 12.268 |
| 01:30-02:00 |  | 5/5 |  | 0.6280 | 0.6280 | 45 | 49 | 0.000 / 0.000 | 0.6280 / 0.6280 | 1.9312 | 12.070 |
| 02:00-02:30 |  | 5/5 |  | 0.6127 | 0.6127 | 45 | 47 | 0.000 / 0.000 | 0.6127 / 0.6127 | 1.9005 | 11.878 |
| 02:30-03:00 |  | 5/5 |  | 0.6352 | 0.6352 | 46 | 54 | 0.000 / 0.000 | 0.6352 / 0.6352 | 1.9456 | 12.160 |
| 03:00-03:30 |  | 5/5 |  | 0.6322 | 0.6322 | 46 | 43 | 0.000 / 0.000 | 0.6322 / 0.6322 | 1.9396 | 12.123 |
| 03:30-04:00 |  | 5/5 |  | 0.6447 | 0.6447 | 46 | 47 | 0.000 / 0.000 | 0.6447 / 0.6447 | 1.9647 | 12.279 |
| 04:00-04:30 |  | 5/5 |  | 0.6262 | 0.6262 | 49 | 41 | 0.000 / 0.000 | 0.6262 / 0.6262 | 1.9277 | 12.048 |
| 04:30-05:00 |  | 5/5 |  | 0.6269 | 0.6269 | 51 | 45 | 0.000 / 0.000 | 0.6269 / 0.6269 | 1.9289 | 12.056 |
| 05:00-05:30 |  | 5/5 |  | 0.6214 | 0.6214 | 47 | 48 | 0.000 / 0.000 | 0.6214 / 0.6214 | 1.9180 | 11.987 |
| 05:30-06:00 |  | 5/5 |  | 0.6326 | 0.6326 | 59 | 43 | 0.000 / 0.000 | 0.6326 / 0.6326 | 1.9405 | 12.128 |
| 06:00-06:30 |  | 5/5 |  | 0.6298 | 0.6298 | 45 | 49 | 0.000 / 0.000 | 0.6298 / 0.6298 | 1.9348 | 12.093 |
| 06:30-07:00 |  | 5/5 |  | 0.6458 | 0.6458 | 55 | 56 | 0.000 / 0.000 | 0.6458 / 0.6458 | 1.9667 | 12.292 |
| 07:00-07:30 | D | 5/5 |  | 0.6222 | 0.6222 | 57 | 42 | 0.000 / 0.000 | 0.6222 / 0.6222 | 1.9197 | 11.998 |
| 07:30-08:00 | D | 5/5 |  | 0.6260 | 0.6260 | 36 | 33 | 0.000 / 0.000 | 0.6260 / 0.6260 | 1.9271 | 12.045 |
| 08:00-08:30 | D | 5/5 |  | 0.6199 | 0.6199 | 46 | 41 | 0.000 / 0.000 | 0.6199 / 0.6199 | 1.9149 | 11.968 |
| 08:30-09:00 | D | 5/5 |  | 0.6163 | 0.6163 | 45 | 39 | 0.000 / 0.000 | 0.6163 / 0.6163 | 1.9079 | 11.924 |
| 09:00-09:30 | D | 5/5 |  | 0.6052 | 0.6052 | 42 | 38 | 0.000 / 0.000 | 0.6052 / 0.6052 | 1.8856 | 11.785 |
| 09:30-10:00 | D | 5/5 |  | 0.5909 | 0.5909 | 44 | 41 | 0.000 / 0.000 | 0.5909 / 0.5909 | 1.8569 | 11.606 |
| 10:00-10:30 | D | 5/5 |  | 0.5999 | 0.5999 | 51 | 48 | 0.000 / 0.000 | 0.5999 / 0.5999 | 1.8749 | 11.718 |
| 10:30-11:00 | D | 5/5 |  | 0.6114 | 0.6114 | 47 | 53 | 0.000 / 0.000 | 0.6114 / 0.6114 | 1.8979 | 11.862 |
| 11:00-11:30 | D | 5/5 |  | 0.6085 | 0.6085 | 45 | 44 | 0.000 / 0.000 | 0.6085 / 0.6085 | 1.8922 | 11.826 |
| 11:30-12:00 | D | 5/5 |  | 0.6023 | 0.6023 | 43 | 50 | 0.000 / 0.000 | 0.6023 / 0.6023 | 1.8797 | 11.748 |
| 12:00-12:30 | D | 5/5 |  | 0.5976 | 0.5976 | 47 | 49 | 0.000 / 0.000 | 0.5976 / 0.5976 | 1.8704 | 11.690 |
| 12:30-13:00 | D | 5/5 |  | 0.6055 | 0.6055 | 53 | 53 | 0.000 / 0.000 | 0.6055 / 0.6055 | 1.8863 | 11.789 |
| 13:00-13:30 | D | 5/5 |  | 0.6017 | 0.6017 | 41 | 55 | 0.000 / 0.000 | 0.6017 / 0.6017 | 1.8785 | 11.741 |
| 13:30-14:00 | D | 5/5 |  | 0.5960 | 0.5960 | 54 | 66 | 0.000 / 0.000 | 0.5960 / 0.5960 | 1.8671 | 11.669 |
| 14:00-14:30 |  | 5/5 |  | 0.6088 | 0.6088 | 63 | 69 | 0.000 / 0.000 | 0.6088 / 0.6088 | 1.8929 | 11.830 |
| 14:30-15:00 |  | 5/5 |  | 0.6508 | 0.6508 | 73 | 81 | 0.000 / 0.000 | 0.6508 / 0.6508 | 1.9767 | 12.354 |
| 15:00-15:30 |  | 5/5 |  | 0.6555 | 0.6555 | 40 | 52 | 0.000 / 0.000 | 0.6555 / 0.6555 | 1.9861 | 12.413 |
| 15:30-16:00 |  | 5/5 |  | 0.6744 | 0.6744 | 33 | 30 | 0.000 / 0.000 | 0.6744 / 0.6744 | 2.0240 | 12.650 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6J_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` ccb1d8140b96a6de20185415867044bd982c0c120233c22032ec6919f4580cb5 (1,747,989 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6J_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` eb3597f21d7665fac617a6c7a7899b98acfd7fd528e6f8c2f9bfc472d7373983 (788,330 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6J_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` aeea1fa79dadb59490466bff9e851d9d8a7a1fb85e3e4812c7e825f6f14d0b66 (889,203 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6J_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` b68748655627fa4414486d1152e9619defd3770fc61671d91ea4f245ff8c1137 (1,850,815 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6J_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 9f68607d58772cb01e815bee02a0d0af3f18f484452b275b794fd7821b66ff85 (656,083 records)

### 6N (fx)

Tick 0.00005 (vendor units 0.00005, factor 1), tick value $5.0; commission $4.22 round turn = 0.8440 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.8873, sell 0.8873 ticks (round turn inside a window 2.6186 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.8873 | 0.8873 | 11 | 8 | 0.000 / 0.000 | 0.8873 / 0.8873 | 2.6186 | 13.093 |
| 17:30-18:00 |  | 5/5 |  | 0.7328 | 0.7328 | 14 | 14 | 0.000 / 0.000 | 0.7328 / 0.7328 | 2.3096 | 11.548 |
| 18:00-18:30 |  | 5/5 |  | 0.7253 | 0.7253 | 13 | 14 | 0.000 / 0.000 | 0.7253 / 0.7253 | 2.2945 | 11.473 |
| 18:30-19:00 |  | 5/5 |  | 0.7918 | 0.7918 | 15 | 17 | 0.000 / 0.000 | 0.7918 / 0.7918 | 2.4276 | 12.138 |
| 19:00-19:30 |  | 5/5 |  | 0.7672 | 0.7672 | 16 | 15 | 0.000 / 0.000 | 0.7672 / 0.7672 | 2.3785 | 11.892 |
| 19:30-20:00 |  | 5/5 |  | 0.7703 | 0.7703 | 14 | 17 | 0.000 / 0.000 | 0.7703 / 0.7703 | 2.3846 | 11.923 |
| 20:00-20:30 |  | 5/5 |  | 0.7852 | 0.7852 | 16 | 15 | 0.000 / 0.000 | 0.7852 / 0.7852 | 2.4143 | 12.072 |
| 20:30-21:00 |  | 5/5 |  | 0.7751 | 0.7751 | 12 | 15 | 0.000 / 0.000 | 0.7751 / 0.7751 | 2.3942 | 11.971 |
| 21:00-21:30 |  | 5/5 |  | 0.7548 | 0.7548 | 12 | 14 | 0.000 / 0.000 | 0.7548 / 0.7548 | 2.3536 | 11.768 |
| 21:30-22:00 |  | 5/5 |  | 0.7687 | 0.7687 | 16 | 15 | 0.000 / 0.000 | 0.7687 / 0.7687 | 2.3815 | 11.907 |
| 22:00-22:30 |  | 5/5 |  | 0.8027 | 0.8027 | 14 | 15 | 0.000 / 0.000 | 0.8027 / 0.8027 | 2.4493 | 12.247 |
| 22:30-23:00 |  | 5/5 |  | 0.7431 | 0.7431 | 14 | 15 | 0.000 / 0.000 | 0.7431 / 0.7431 | 2.3302 | 11.651 |
| 23:00-23:30 |  | 5/5 |  | 0.7362 | 0.7362 | 12 | 14 | 0.000 / 0.000 | 0.7362 / 0.7362 | 2.3163 | 11.582 |
| 23:30-00:00 |  | 5/5 |  | 0.7590 | 0.7590 | 17 | 14 | 0.000 / 0.000 | 0.7590 / 0.7590 | 2.3619 | 11.810 |
| 00:00-00:30 |  | 5/5 |  | 0.7835 | 0.7835 | 18 | 18 | 0.000 / 0.000 | 0.7835 / 0.7835 | 2.4109 | 12.055 |
| 00:30-01:00 |  | 5/5 |  | 0.7553 | 0.7553 | 16 | 16 | 0.000 / 0.000 | 0.7553 / 0.7553 | 2.3546 | 11.773 |
| 01:00-01:30 |  | 5/5 |  | 0.7615 | 0.7615 | 17 | 16 | 0.000 / 0.000 | 0.7615 / 0.7615 | 2.3670 | 11.835 |
| 01:30-02:00 |  | 5/5 |  | 0.7442 | 0.7442 | 15 | 16 | 0.000 / 0.000 | 0.7442 / 0.7442 | 2.3325 | 11.662 |
| 02:00-02:30 |  | 5/5 |  | 0.6919 | 0.6919 | 16 | 13 | 0.000 / 0.000 | 0.6919 / 0.6919 | 2.2278 | 11.139 |
| 02:30-03:00 |  | 5/5 |  | 0.7105 | 0.7105 | 17 | 16 | 0.000 / 0.000 | 0.7105 / 0.7105 | 2.2650 | 11.325 |
| 03:00-03:30 |  | 5/5 |  | 0.7511 | 0.7511 | 19 | 19 | 0.000 / 0.000 | 0.7511 / 0.7511 | 2.3462 | 11.731 |
| 03:30-04:00 |  | 5/5 |  | 0.7339 | 0.7339 | 19 | 14 | 0.000 / 0.000 | 0.7339 / 0.7339 | 2.3118 | 11.559 |
| 04:00-04:30 |  | 5/5 |  | 0.7324 | 0.7324 | 20 | 13 | 0.000 / 0.000 | 0.7324 / 0.7324 | 2.3089 | 11.544 |
| 04:30-05:00 |  | 5/5 |  | 0.7377 | 0.7377 | 20 | 16 | 0.000 / 0.000 | 0.7377 / 0.7377 | 2.3194 | 11.597 |
| 05:00-05:30 |  | 5/5 |  | 0.7355 | 0.7355 | 18 | 17 | 0.000 / 0.000 | 0.7355 / 0.7355 | 2.3151 | 11.575 |
| 05:30-06:00 |  | 5/5 |  | 0.7292 | 0.7292 | 18 | 18 | 0.000 / 0.000 | 0.7292 / 0.7292 | 2.3024 | 11.512 |
| 06:00-06:30 |  | 5/5 |  | 0.6958 | 0.6958 | 22 | 17 | 0.000 / 0.000 | 0.6958 / 0.6958 | 2.2356 | 11.178 |
| 06:30-07:00 |  | 5/5 |  | 0.7192 | 0.7192 | 19 | 18 | 0.000 / 0.000 | 0.7192 / 0.7192 | 2.2824 | 11.412 |
| 07:00-07:30 | D | 5/5 |  | 0.7022 | 0.7022 | 17 | 16 | 0.000 / 0.000 | 0.7022 / 0.7022 | 2.2485 | 11.242 |
| 07:30-08:00 | D | 5/5 |  | 0.7119 | 0.7119 | 16 | 14 | 0.000 / 0.000 | 0.7119 / 0.7119 | 2.2678 | 11.339 |
| 08:00-08:30 | D | 5/5 |  | 0.7183 | 0.7183 | 20 | 18 | 0.000 / 0.000 | 0.7183 / 0.7183 | 2.2805 | 11.403 |
| 08:30-09:00 | D | 5/5 |  | 0.7278 | 0.7278 | 18 | 15 | 0.000 / 0.000 | 0.7278 / 0.7278 | 2.2997 | 11.498 |
| 09:00-09:30 | D | 5/5 |  | 0.7163 | 0.7163 | 17 | 17 | 0.000 / 0.000 | 0.7163 / 0.7163 | 2.2766 | 11.383 |
| 09:30-10:00 | D | 5/5 |  | 0.6899 | 0.6899 | 19 | 20 | 0.000 / 0.000 | 0.6899 / 0.6899 | 2.2239 | 11.119 |
| 10:00-10:30 | D | 5/5 |  | 0.7283 | 0.7283 | 25 | 29 | 0.000 / 0.000 | 0.7283 / 0.7283 | 2.3006 | 11.503 |
| 10:30-11:00 | D | 5/5 |  | 0.7036 | 0.7036 | 20 | 24 | 0.000 / 0.000 | 0.7036 / 0.7036 | 2.2513 | 11.256 |
| 11:00-11:30 | D | 5/5 |  | 0.7183 | 0.7183 | 24 | 24 | 0.000 / 0.000 | 0.7183 / 0.7183 | 2.2806 | 11.403 |
| 11:30-12:00 | D | 5/5 |  | 0.7039 | 0.7039 | 18 | 19 | 0.000 / 0.000 | 0.7039 / 0.7039 | 2.2518 | 11.259 |
| 12:00-12:30 | D | 5/5 |  | 0.7111 | 0.7111 | 22 | 21 | 0.000 / 0.000 | 0.7111 / 0.7111 | 2.2663 | 11.331 |
| 12:30-13:00 | D | 5/5 |  | 0.6755 | 0.6755 | 21 | 20 | 0.000 / 0.000 | 0.6755 / 0.6755 | 2.1950 | 10.975 |
| 13:00-13:30 | D | 5/5 |  | 0.6937 | 0.6937 | 19 | 23 | 0.000 / 0.000 | 0.6937 / 0.6937 | 2.2313 | 11.157 |
| 13:30-14:00 | D | 5/5 |  | 0.6552 | 0.6552 | 21 | 25 | 0.000 / 0.000 | 0.6552 / 0.6552 | 2.1544 | 10.772 |
| 14:00-14:30 |  | 5/5 |  | 0.6888 | 0.6888 | 26 | 31 | 0.000 / 0.000 | 0.6888 / 0.6888 | 2.2215 | 11.108 |
| 14:30-15:00 |  | 5/5 |  | 0.7296 | 0.7296 | 27 | 31 | 0.000 / 0.000 | 0.7296 / 0.7296 | 2.3033 | 11.516 |
| 15:00-15:30 |  | 5/5 |  | 0.7254 | 0.7254 | 27 | 27 | 0.000 / 0.000 | 0.7254 / 0.7254 | 2.2949 | 11.474 |
| 15:30-16:00 |  | 5/5 |  | 0.7460 | 0.7460 | 19 | 21 | 0.000 / 0.000 | 0.7460 / 0.7460 | 2.3360 | 11.680 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6N_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` b7be8e8bc140d07bebd4a6cbf575cd7c50623a3bc3f7f10e29169df29f174c1d (499,167 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6N_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 906988c51f9c74a0b33d52a15116e5a2c845abc430fc083c7053d663a442858e (323,270 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6N_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 2a9f289a30d496e2827e72504756fffc034c5c7e161be0bc14c257247f22db73 (284,863 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6N_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` ec4dcac01432de90a0d6a48cd3c8d87e2ce96fa0414f7e1f7cec6cd338c2b6c6 (787,815 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6N_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 9b2c1db87621dbdf3281590b7e1fbb7720756ab1e1679589ee2f5d3a429b722c (485,336 records)

### 6S (fx)

Tick 0.00005 (vendor units 0.00005, factor 1), tick value $6.25; commission $4.22 round turn = 0.6752 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 1.6539, sell 1.6539 ticks (round turn inside a window 3.9830 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.6539 | 1.6539 | 4 | 4 | 0.000 / 0.000 | 1.6539 / 1.6539 | 3.9830 | 24.894 |
| 17:30-18:00 |  | 5/5 |  | 1.0581 | 1.0581 | 3 | 3 | 0.000 / 0.000 | 1.0581 / 1.0581 | 2.7913 | 17.446 |
| 18:00-18:30 |  | 5/5 |  | 1.0747 | 1.0747 | 2 | 2 | 0.000 / 0.000 | 1.0747 / 1.0747 | 2.8247 | 17.654 |
| 18:30-19:00 |  | 5/5 |  | 1.1266 | 1.1266 | 2 | 2 | 0.000 / 0.000 | 1.1266 / 1.1266 | 2.9283 | 18.302 |
| 19:00-19:30 |  | 5/5 |  | 1.0962 | 1.0962 | 2 | 2 | 0.000 / 0.000 | 1.0962 / 1.0962 | 2.8675 | 17.922 |
| 19:30-20:00 |  | 5/5 |  | 1.1350 | 1.1350 | 2 | 2 | 0.000 / 0.000 | 1.1350 / 1.1350 | 2.9453 | 18.408 |
| 20:00-20:30 |  | 5/5 |  | 1.1820 | 1.1820 | 2 | 2 | 0.000 / 0.000 | 1.1820 / 1.1820 | 3.0393 | 18.995 |
| 20:30-21:00 |  | 5/5 |  | 1.1423 | 1.1423 | 2 | 2 | 0.000 / 0.000 | 1.1423 / 1.1423 | 2.9598 | 18.499 |
| 21:00-21:30 |  | 5/5 |  | 1.1041 | 1.1041 | 2 | 2 | 0.000 / 0.000 | 1.1041 / 1.1041 | 2.8834 | 18.021 |
| 21:30-22:00 |  | 5/5 |  | 1.1189 | 1.1189 | 2 | 2 | 0.000 / 0.000 | 1.1189 / 1.1189 | 2.9130 | 18.206 |
| 22:00-22:30 |  | 5/5 |  | 1.1134 | 1.1134 | 2 | 2 | 0.000 / 0.000 | 1.1134 / 1.1134 | 2.9020 | 18.138 |
| 22:30-23:00 |  | 5/5 |  | 1.1456 | 1.1456 | 2 | 2 | 0.000 / 0.000 | 1.1456 / 1.1456 | 2.9664 | 18.540 |
| 23:00-23:30 |  | 5/5 |  | 1.1306 | 1.1306 | 2 | 2 | 0.000 / 0.000 | 1.1306 / 1.1306 | 2.9363 | 18.352 |
| 23:30-00:00 |  | 5/5 |  | 1.1337 | 1.1337 | 2 | 2 | 0.000 / 0.000 | 1.1337 / 1.1337 | 2.9425 | 18.391 |
| 00:00-00:30 |  | 5/5 |  | 1.1138 | 1.1138 | 2 | 2 | 0.000 / 0.000 | 1.1138 / 1.1138 | 2.9027 | 18.142 |
| 00:30-01:00 |  | 5/5 |  | 1.0979 | 1.0979 | 2 | 2 | 0.000 / 0.000 | 1.0979 / 1.0979 | 2.8711 | 17.944 |
| 01:00-01:30 |  | 5/5 |  | 1.0429 | 1.0429 | 2 | 2 | 0.000 / 0.000 | 1.0429 / 1.0429 | 2.7609 | 17.256 |
| 01:30-02:00 |  | 5/5 |  | 1.0203 | 1.0203 | 2 | 2 | 0.000 / 0.000 | 1.0203 / 1.0203 | 2.7158 | 16.974 |
| 02:00-02:30 |  | 5/5 |  | 1.0257 | 1.0257 | 2 | 2 | 0.000 / 0.000 | 1.0257 / 1.0257 | 2.7265 | 17.041 |
| 02:30-03:00 |  | 5/5 |  | 1.0142 | 1.0142 | 2 | 2 | 0.000 / 0.000 | 1.0142 / 1.0142 | 2.7036 | 16.898 |
| 03:00-03:30 |  | 5/5 |  | 1.0356 | 1.0356 | 2 | 3 | 0.000 / 0.000 | 1.0356 / 1.0356 | 2.7465 | 17.165 |
| 03:30-04:00 |  | 5/5 |  | 1.0773 | 1.0773 | 2 | 2 | 0.000 / 0.000 | 1.0773 / 1.0773 | 2.8298 | 17.686 |
| 04:00-04:30 |  | 5/5 |  | 1.0894 | 1.0894 | 2 | 2 | 0.000 / 0.000 | 1.0894 / 1.0894 | 2.8540 | 17.838 |
| 04:30-05:00 |  | 5/5 |  | 1.0666 | 1.0666 | 2 | 2 | 0.000 / 0.000 | 1.0666 / 1.0666 | 2.8085 | 17.553 |
| 05:00-05:30 |  | 5/5 |  | 1.0730 | 1.0730 | 2 | 2 | 0.000 / 0.000 | 1.0730 / 1.0730 | 2.8212 | 17.632 |
| 05:30-06:00 |  | 5/5 |  | 1.0501 | 1.0501 | 2 | 2 | 0.000 / 0.000 | 1.0501 / 1.0501 | 2.7754 | 17.346 |
| 06:00-06:30 |  | 5/5 |  | 1.0653 | 1.0653 | 3 | 3 | 0.000 / 0.000 | 1.0653 / 1.0653 | 2.8059 | 17.537 |
| 06:30-07:00 |  | 5/5 |  | 1.0408 | 1.0408 | 3 | 3 | 0.000 / 0.000 | 1.0408 / 1.0408 | 2.7569 | 17.231 |
| 07:00-07:30 | D | 5/5 |  | 1.0201 | 1.0201 | 3 | 3 | 0.000 / 0.000 | 1.0201 / 1.0201 | 2.7153 | 16.971 |
| 07:30-08:00 | D | 5/5 |  | 1.0655 | 1.0655 | 3 | 3 | 0.000 / 0.000 | 1.0655 / 1.0655 | 2.8063 | 17.539 |
| 08:00-08:30 | D | 5/5 |  | 1.0165 | 1.0165 | 3 | 3 | 0.000 / 0.000 | 1.0165 / 1.0165 | 2.7081 | 16.926 |
| 08:30-09:00 | D | 5/5 |  | 1.0300 | 1.0300 | 3 | 3 | 0.000 / 0.000 | 1.0300 / 1.0300 | 2.7351 | 17.095 |
| 09:00-09:30 | D | 5/5 |  | 1.0396 | 1.0396 | 3 | 3 | 0.000 / 0.000 | 1.0396 / 1.0396 | 2.7544 | 17.215 |
| 09:30-10:00 | D | 5/5 |  | 0.9638 | 0.9638 | 3 | 3 | 0.000 / 0.000 | 0.9638 / 0.9638 | 2.6028 | 16.267 |
| 10:00-10:30 | D | 5/5 |  | 0.9631 | 0.9631 | 3 | 3 | 0.000 / 0.000 | 0.9631 / 0.9631 | 2.6013 | 16.258 |
| 10:30-11:00 | D | 5/5 |  | 0.9622 | 0.9622 | 3 | 3 | 0.000 / 0.000 | 0.9622 / 0.9622 | 2.5996 | 16.247 |
| 11:00-11:30 | D | 5/5 |  | 0.9630 | 0.9630 | 3 | 3 | 0.000 / 0.000 | 0.9630 / 0.9630 | 2.6012 | 16.257 |
| 11:30-12:00 | D | 5/5 |  | 0.9888 | 0.9888 | 3 | 3 | 0.000 / 0.000 | 0.9888 / 0.9888 | 2.6527 | 16.579 |
| 12:00-12:30 | D | 5/5 |  | 1.0112 | 1.0112 | 3 | 3 | 0.000 / 0.000 | 1.0112 / 1.0112 | 2.6976 | 16.860 |
| 12:30-13:00 | D | 5/5 |  | 0.9196 | 0.9196 | 3 | 3 | 0.000 / 0.000 | 0.9196 / 0.9196 | 2.5144 | 15.715 |
| 13:00-13:30 | D | 5/5 |  | 0.9666 | 0.9666 | 3 | 4 | 0.000 / 0.000 | 0.9666 / 0.9666 | 2.6083 | 16.302 |
| 13:30-14:00 | D | 5/5 |  | 0.9163 | 0.9163 | 3 | 4 | 0.000 / 0.000 | 0.9163 / 0.9163 | 2.5078 | 15.674 |
| 14:00-14:30 |  | 5/5 |  | 0.9307 | 0.9307 | 5 | 4 | 0.000 / 0.000 | 0.9307 / 0.9307 | 2.5365 | 15.853 |
| 14:30-15:00 |  | 5/5 |  | 0.9527 | 0.9527 | 4 | 4 | 0.000 / 0.000 | 0.9527 / 0.9527 | 2.5806 | 16.129 |
| 15:00-15:30 |  | 5/5 |  | 0.9489 | 0.9489 | 4 | 5 | 0.000 / 0.000 | 0.9489 / 0.9489 | 2.5729 | 16.081 |
| 15:30-16:00 |  | 5/5 |  | 1.0054 | 1.0054 | 3 | 3 | 0.000 / 0.000 | 1.0054 / 1.0054 | 2.6860 | 16.787 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/6S_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` d6e22330ff1872c0078186bcffb8771c4b792fb76e1ef331d4835acb160b86d7 (343,766 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6S_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 93e0536071593934b65209b5d735728fde0d65e6255b38eab9a71fe37a5d15dd (188,234 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6S_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` f75d75d7a546615782df46de778b16c512e7a80944a14fc9cc0a6ba1b66620d0 (254,002 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6S_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 2095ef10ccf5d88992db7efe009c7bf30df8cae927692545011708d4f0c89f43 (431,780 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/6S_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 76ee3620b8b25e61c2bd31e147d53ceca9390d5a9dd45d6e9bc6c3a83ec6daa7 (307,068 records)

### CL (energy)

Tick 0.01 (vendor units 0.01, factor 1), tick value $10.0; commission $4.02 round turn = 0.4020 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 1.3192, sell 1.3192 ticks (round turn inside a window 3.0403 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.0667 | 1.0667 | 4 | 4 | 0.000 / 0.000 | 1.0667 / 1.0667 | 2.5354 | 25.354 |
| 17:30-18:00 |  | 5/5 |  | 0.9455 | 0.9455 | 4 | 4 | 0.000 / 0.000 | 0.9455 / 0.9455 | 2.2930 | 22.930 |
| 18:00-18:30 |  | 5/5 |  | 0.8782 | 0.8782 | 4 | 4 | 0.000 / 0.000 | 0.8782 / 0.8782 | 2.1584 | 21.584 |
| 18:30-19:00 |  | 5/5 |  | 1.3192 | 1.3222 | 3 | 4 | 0.000 / 0.000 | 1.3192 / 1.3192 | 3.0403 | 30.403 |
| 19:00-19:30 |  | 5/5 |  | 0.8964 | 0.8964 | 4 | 5 | 0.000 / 0.000 | 0.8964 / 0.8964 | 2.1948 | 21.948 |
| 19:30-20:00 |  | 5/5 |  | 0.7949 | 0.7949 | 5 | 5 | 0.000 / 0.000 | 0.7949 / 0.7949 | 1.9919 | 19.919 |
| 20:00-20:30 |  | 5/5 |  | 0.7730 | 0.7730 | 4 | 5 | 0.000 / 0.000 | 0.7730 / 0.7730 | 1.9480 | 19.480 |
| 20:30-21:00 |  | 5/5 |  | 0.7344 | 0.7344 | 5 | 5 | 0.000 / 0.000 | 0.7344 / 0.7344 | 1.8707 | 18.707 |
| 21:00-21:30 |  | 5/5 |  | 0.7240 | 0.7240 | 5 | 5 | 0.000 / 0.000 | 0.7240 / 0.7240 | 1.8501 | 18.501 |
| 21:30-22:00 |  | 5/5 |  | 0.6855 | 0.6855 | 5 | 5 | 0.000 / 0.000 | 0.6855 / 0.6855 | 1.7730 | 17.730 |
| 22:00-22:30 |  | 5/5 |  | 0.6781 | 0.6781 | 5 | 5 | 0.000 / 0.000 | 0.6781 / 0.6781 | 1.7581 | 17.581 |
| 22:30-23:00 |  | 5/5 |  | 0.6640 | 0.6640 | 7 | 6 | 0.000 / 0.000 | 0.6640 / 0.6640 | 1.7299 | 17.299 |
| 23:00-23:30 |  | 5/5 |  | 0.6755 | 0.6755 | 6 | 5 | 0.000 / 0.000 | 0.6755 / 0.6755 | 1.7530 | 17.530 |
| 23:30-00:00 |  | 5/5 |  | 0.6413 | 0.6413 | 6 | 5 | 0.000 / 0.000 | 0.6413 / 0.6413 | 1.6845 | 16.845 |
| 00:00-00:30 |  | 5/5 |  | 0.7138 | 0.7138 | 5 | 5 | 0.000 / 0.000 | 0.7138 / 0.7138 | 1.8295 | 18.295 |
| 00:30-01:00 |  | 5/5 |  | 0.7476 | 0.7476 | 5 | 6 | 0.000 / 0.000 | 0.7476 / 0.7476 | 1.8972 | 18.972 |
| 01:00-01:30 |  | 5/5 |  | 0.7348 | 0.7348 | 5 | 5 | 0.000 / 0.000 | 0.7348 / 0.7348 | 1.8716 | 18.716 |
| 01:30-02:00 |  | 5/5 |  | 0.6968 | 0.6968 | 6 | 6 | 0.000 / 0.000 | 0.6968 / 0.6968 | 1.7957 | 17.957 |
| 02:00-02:30 |  | 5/5 |  | 0.6868 | 0.6868 | 6 | 6 | 0.000 / 0.000 | 0.6868 / 0.6868 | 1.7757 | 17.757 |
| 02:30-03:00 |  | 5/5 |  | 0.6774 | 0.6774 | 6 | 6 | 0.000 / 0.000 | 0.6774 / 0.6774 | 1.7569 | 17.569 |
| 03:00-03:30 |  | 5/5 |  | 0.6798 | 0.6798 | 6 | 6 | 0.000 / 0.000 | 0.6798 / 0.6798 | 1.7615 | 17.615 |
| 03:30-04:00 |  | 5/5 |  | 0.6741 | 0.6741 | 7 | 6 | 0.000 / 0.000 | 0.6741 / 0.6741 | 1.7502 | 17.502 |
| 04:00-04:30 |  | 5/5 |  | 0.6801 | 0.6801 | 6 | 6 | 0.000 / 0.000 | 0.6801 / 0.6801 | 1.7622 | 17.622 |
| 04:30-05:00 |  | 5/5 |  | 0.6684 | 0.6684 | 6 | 6 | 0.000 / 0.000 | 0.6684 / 0.6684 | 1.7389 | 17.389 |
| 05:00-05:30 |  | 5/5 |  | 0.6819 | 0.6819 | 7 | 6 | 0.000 / 0.000 | 0.6819 / 0.6819 | 1.7657 | 17.657 |
| 05:30-06:00 |  | 5/5 |  | 0.6813 | 0.6813 | 7 | 6 | 0.000 / 0.000 | 0.6813 / 0.6813 | 1.7645 | 17.645 |
| 06:00-06:30 |  | 5/5 |  | 0.6876 | 0.6876 | 7 | 7 | 0.000 / 0.000 | 0.6876 / 0.6876 | 1.7772 | 17.772 |
| 06:30-07:00 |  | 5/5 |  | 0.7049 | 0.7049 | 6 | 6 | 0.000 / 0.000 | 0.7049 / 0.7049 | 1.8118 | 18.118 |
| 07:00-07:30 |  | 5/5 |  | 0.7168 | 0.7168 | 6 | 7 | 0.000 / 0.000 | 0.7168 / 0.7168 | 1.8355 | 18.355 |
| 07:30-08:00 |  | 5/5 |  | 0.6743 | 0.6743 | 7 | 7 | 0.000 / 0.000 | 0.6743 / 0.6743 | 1.7505 | 17.505 |
| 08:00-08:30 | D | 5/5 |  | 0.6570 | 0.6570 | 8 | 8 | 0.000 / 0.000 | 0.6570 / 0.6570 | 1.7160 | 17.160 |
| 08:30-09:00 | D | 5/5 |  | 0.6566 | 0.6566 | 7 | 8 | 0.000 / 0.000 | 0.6566 / 0.6566 | 1.7153 | 17.153 |
| 09:00-09:30 | D | 5/5 |  | 0.6831 | 0.6831 | 7 | 7 | 0.000 / 0.000 | 0.6831 / 0.6831 | 1.7682 | 17.682 |
| 09:30-10:00 | D | 5/5 |  | 0.6723 | 0.6723 | 7 | 7 | 0.000 / 0.000 | 0.6723 / 0.6723 | 1.7466 | 17.466 |
| 10:00-10:30 | D | 5/5 |  | 0.6618 | 0.6618 | 7 | 7 | 0.000 / 0.000 | 0.6618 / 0.6618 | 1.7256 | 17.256 |
| 10:30-11:00 | D | 5/5 |  | 0.6548 | 0.6548 | 7 | 7 | 0.000 / 0.000 | 0.6548 / 0.6548 | 1.7116 | 17.116 |
| 11:00-11:30 | D | 5/5 |  | 0.6592 | 0.6592 | 7 | 7 | 0.000 / 0.000 | 0.6592 / 0.6592 | 1.7204 | 17.204 |
| 11:30-12:00 | D | 5/5 |  | 0.6538 | 0.6538 | 7 | 7 | 0.000 / 0.000 | 0.6538 / 0.6538 | 1.7097 | 17.097 |
| 12:00-12:30 | D | 5/5 |  | 0.6484 | 0.6484 | 8 | 7 | 0.000 / 0.000 | 0.6484 / 0.6484 | 1.6988 | 16.988 |
| 12:30-13:00 | D | 5/5 |  | 0.6634 | 0.6634 | 8 | 9 | 0.000 / 0.000 | 0.6634 / 0.6634 | 1.7287 | 17.287 |
| 13:00-13:30 | D | 5/5 |  | 0.6828 | 0.6828 | 8 | 8 | 0.000 / 0.000 | 0.6828 / 0.6828 | 1.7677 | 17.677 |
| 13:30-14:00 |  | 5/5 |  | 0.6383 | 0.6383 | 10 | 10 | 0.000 / 0.000 | 0.6383 / 0.6383 | 1.6786 | 16.786 |
| 14:00-14:30 |  | 5/5 |  | 0.6524 | 0.6524 | 9 | 8 | 0.000 / 0.000 | 0.6524 / 0.6524 | 1.7067 | 17.067 |
| 14:30-15:00 |  | 5/5 |  | 0.6439 | 0.6439 | 10 | 9 | 0.000 / 0.000 | 0.6439 / 0.6439 | 1.6899 | 16.899 |
| 15:00-15:30 |  | 5/5 |  | 0.6946 | 0.6946 | 8 | 6 | 0.000 / 0.000 | 0.6946 / 0.6946 | 1.7912 | 17.912 |
| 15:30-16:00 |  | 5/5 |  | 0.7630 | 0.7630 | 6 | 6 | 0.000 / 0.000 | 0.7630 / 0.7630 | 1.9281 | 19.281 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` c0c7ce554fb8d414971366e2c7826517269e3873ae849e19e4cc67d4b24ec3a1 (1,055,063 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 39ab09cbc6b9f2248e9a277993dac20e3f2da593f55ea6220d72ec5323e4bf64 (1,049,295 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` ae62b46fc0f8da951650695e6e5a4b31afda3e6afa36a7f5c1735f3b9d12b12e (1,466,667 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 43187777219f8089786ef919bfcb05d0f90c5d08b6cdcf6436418ccef1dc2b16 (1,584,474 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/CL_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 613e448876d050a37255932f288b5da5c8d3269be914cec804c8801baf64f862 (1,475,856 records)

### E7 (fx)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $6.25; commission $2.72 round turn = 0.4352 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.7806, sell 0.7806 ticks (round turn inside a window 1.9964 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.7806 | 0.7806 | 5 | 4 | 0.000 / 0.000 | 0.7806 / 0.7806 | 1.9964 | 12.478 |
| 17:30-18:00 |  | 5/5 |  | 0.6551 | 0.6551 | 5 | 6 | 0.000 / 0.000 | 0.6551 / 0.6551 | 1.7454 | 10.909 |
| 18:00-18:30 |  | 5/5 |  | 0.6389 | 0.6389 | 5 | 5 | 0.000 / 0.000 | 0.6389 / 0.6389 | 1.7129 | 10.706 |
| 18:30-19:00 |  | 5/5 |  | 0.6230 | 0.6230 | 5 | 5 | 0.000 / 0.000 | 0.6230 / 0.6230 | 1.6813 | 10.508 |
| 19:00-19:30 |  | 5/5 |  | 0.6141 | 0.6141 | 5 | 5 | 0.000 / 0.000 | 0.6141 / 0.6141 | 1.6635 | 10.397 |
| 19:30-20:00 |  | 5/5 |  | 0.6347 | 0.6347 | 5 | 6 | 0.000 / 0.000 | 0.6347 / 0.6347 | 1.7045 | 10.653 |
| 20:00-20:30 |  | 5/5 |  | 0.6271 | 0.6271 | 5 | 5 | 0.000 / 0.000 | 0.6271 / 0.6271 | 1.6895 | 10.559 |
| 20:30-21:00 |  | 5/5 |  | 0.6191 | 0.6191 | 5 | 5 | 0.000 / 0.000 | 0.6191 / 0.6191 | 1.6734 | 10.459 |
| 21:00-21:30 |  | 5/5 |  | 0.6078 | 0.6078 | 5 | 5 | 0.000 / 0.000 | 0.6078 / 0.6078 | 1.6509 | 10.318 |
| 21:30-22:00 |  | 5/5 |  | 0.6147 | 0.6147 | 5 | 5 | 0.000 / 0.000 | 0.6147 / 0.6147 | 1.6647 | 10.404 |
| 22:00-22:30 |  | 5/5 |  | 0.5968 | 0.5968 | 5 | 5 | 0.000 / 0.000 | 0.5968 / 0.5968 | 1.6289 | 10.180 |
| 22:30-23:00 |  | 5/5 |  | 0.6016 | 0.6016 | 5 | 6 | 0.000 / 0.000 | 0.6016 / 0.6016 | 1.6385 | 10.241 |
| 23:00-23:30 |  | 5/5 |  | 0.6284 | 0.6284 | 6 | 5 | 0.000 / 0.000 | 0.6284 / 0.6284 | 1.6920 | 10.575 |
| 23:30-00:00 |  | 5/5 |  | 0.6436 | 0.6436 | 6 | 6 | 0.000 / 0.000 | 0.6436 / 0.6436 | 1.7223 | 10.765 |
| 00:00-00:30 |  | 5/5 |  | 0.6271 | 0.6271 | 6 | 5 | 0.000 / 0.000 | 0.6271 / 0.6271 | 1.6895 | 10.559 |
| 00:30-01:00 |  | 5/5 |  | 0.6345 | 0.6345 | 5 | 5 | 0.000 / 0.000 | 0.6345 / 0.6345 | 1.7041 | 10.651 |
| 01:00-01:30 |  | 5/5 |  | 0.6384 | 0.6384 | 5 | 5 | 0.000 / 0.000 | 0.6384 / 0.6384 | 1.7120 | 10.700 |
| 01:30-02:00 |  | 5/5 |  | 0.6177 | 0.6177 | 5 | 5 | 0.000 / 0.000 | 0.6177 / 0.6177 | 1.6706 | 10.441 |
| 02:00-02:30 |  | 5/5 |  | 0.6335 | 0.6335 | 5 | 5 | 0.000 / 0.000 | 0.6335 / 0.6335 | 1.7023 | 10.639 |
| 02:30-03:00 |  | 5/5 |  | 0.6374 | 0.6374 | 6 | 5 | 0.000 / 0.000 | 0.6374 / 0.6374 | 1.7099 | 10.687 |
| 03:00-03:30 |  | 5/5 |  | 0.6321 | 0.6321 | 6 | 5 | 0.000 / 0.000 | 0.6321 / 0.6321 | 1.6993 | 10.621 |
| 03:30-04:00 |  | 5/5 |  | 0.6391 | 0.6391 | 5 | 5 | 0.000 / 0.000 | 0.6391 / 0.6391 | 1.7134 | 10.709 |
| 04:00-04:30 |  | 5/5 |  | 0.6355 | 0.6355 | 5 | 6 | 0.000 / 0.000 | 0.6355 / 0.6355 | 1.7063 | 10.664 |
| 04:30-05:00 |  | 5/5 |  | 0.6286 | 0.6286 | 6 | 5 | 0.000 / 0.000 | 0.6286 / 0.6286 | 1.6925 | 10.578 |
| 05:00-05:30 |  | 5/5 |  | 0.6386 | 0.6386 | 6 | 6 | 0.000 / 0.000 | 0.6386 / 0.6386 | 1.7124 | 10.703 |
| 05:30-06:00 |  | 5/5 |  | 0.6121 | 0.6121 | 5 | 6 | 0.000 / 0.000 | 0.6121 / 0.6121 | 1.6594 | 10.371 |
| 06:00-06:30 |  | 5/5 |  | 0.6326 | 0.6326 | 6 | 6 | 0.000 / 0.000 | 0.6326 / 0.6326 | 1.7005 | 10.628 |
| 06:30-07:00 |  | 5/5 |  | 0.6345 | 0.6345 | 6 | 6 | 0.000 / 0.000 | 0.6345 / 0.6345 | 1.7041 | 10.651 |
| 07:00-07:30 | D | 5/5 |  | 0.6671 | 0.6671 | 5 | 5 | 0.000 / 0.000 | 0.6671 / 0.6671 | 1.7694 | 11.059 |
| 07:30-08:00 | D | 5/5 |  | 0.6731 | 0.6731 | 5 | 5 | 0.000 / 0.000 | 0.6731 / 0.6731 | 1.7813 | 11.133 |
| 08:00-08:30 | D | 5/5 |  | 0.6311 | 0.6311 | 5 | 5 | 0.000 / 0.000 | 0.6311 / 0.6311 | 1.6973 | 10.608 |
| 08:30-09:00 | D | 5/5 |  | 0.6498 | 0.6498 | 5 | 5 | 0.000 / 0.000 | 0.6498 / 0.6498 | 1.7348 | 10.843 |
| 09:00-09:30 | D | 5/5 |  | 0.6431 | 0.6431 | 5 | 5 | 0.000 / 0.000 | 0.6431 / 0.6431 | 1.7214 | 10.759 |
| 09:30-10:00 | D | 5/5 |  | 0.6394 | 0.6394 | 5 | 5 | 0.000 / 0.000 | 0.6394 / 0.6394 | 1.7139 | 10.712 |
| 10:00-10:30 | D | 5/5 |  | 0.6366 | 0.6366 | 5 | 5 | 0.000 / 0.000 | 0.6366 / 0.6366 | 1.7083 | 10.677 |
| 10:30-11:00 | D | 5/5 |  | 0.6207 | 0.6207 | 5 | 5 | 0.000 / 0.000 | 0.6207 / 0.6207 | 1.6767 | 10.479 |
| 11:00-11:30 | D | 5/5 |  | 0.6365 | 0.6365 | 5 | 5 | 0.000 / 0.000 | 0.6365 / 0.6365 | 1.7083 | 10.677 |
| 11:30-12:00 | D | 5/5 |  | 0.6339 | 0.6339 | 5 | 5 | 0.000 / 0.000 | 0.6339 / 0.6339 | 1.7030 | 10.644 |
| 12:00-12:30 | D | 5/5 |  | 0.6232 | 0.6232 | 5 | 5 | 0.000 / 0.000 | 0.6232 / 0.6232 | 1.6816 | 10.510 |
| 12:30-13:00 | D | 5/5 |  | 0.6333 | 0.6333 | 5 | 5 | 0.000 / 0.000 | 0.6333 / 0.6333 | 1.7017 | 10.636 |
| 13:00-13:30 | D | 5/5 |  | 0.6235 | 0.6235 | 5 | 5 | 0.000 / 0.000 | 0.6235 / 0.6235 | 1.6822 | 10.514 |
| 13:30-14:00 | D | 5/5 |  | 0.6277 | 0.6277 | 5 | 6 | 0.000 / 0.000 | 0.6277 / 0.6277 | 1.6905 | 10.566 |
| 14:00-14:30 |  | 5/5 |  | 0.6154 | 0.6154 | 5 | 5 | 0.000 / 0.000 | 0.6154 / 0.6154 | 1.6660 | 10.412 |
| 14:30-15:00 |  | 5/5 |  | 0.6295 | 0.6295 | 6 | 6 | 0.000 / 0.000 | 0.6295 / 0.6295 | 1.6942 | 10.589 |
| 15:00-15:30 |  | 5/5 |  | 0.6235 | 0.6235 | 5 | 6 | 0.000 / 0.000 | 0.6235 / 0.6235 | 1.6822 | 10.513 |
| 15:30-16:00 |  | 5/5 |  | 0.6734 | 0.6734 | 5 | 5 | 0.000 / 0.000 | 0.6734 / 0.6734 | 1.7821 | 11.138 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/E7_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` fe82d7add080aec24ef807c0cbe0843127b23a5b0859b0ce332f977b48f10a32 (353,017 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/E7_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` e45ee72e7de7bd1ac879d82c222463e2b372adec510dd4121734e620ef79c58d (235,630 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/E7_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` e31686305b0e3dcaee4f01c09f3875d938562451bbf8a1dc3d18c4e60a5772d0 (128,697 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/E7_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 6fa1cc60718492ff80b10dbbcfb58d54c3ca60e9a935f39b9eba0d109768413a (314,997 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/E7_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 68d7d17e5f99ff6ee893d6b9268c567077a654475d41ace5b72fa439bf06a382 (223,420 records)

### GC (metals)

Tick 0.10 (vendor units 0.10, factor 1), tick value $10.0; commission $4.32 round turn = 0.4320 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-12:30 CT.

Event-window one-side slippage: buy 3.0739, sell 3.0739 ticks (round turn inside a window 6.5799 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 3.0739 | 3.0739 | 2 | 2 | 0.000 / 0.000 | 3.0739 / 3.0739 | 6.5799 | 65.799 |
| 17:30-18:00 |  | 5/5 |  | 2.3486 | 2.3486 | 2 | 2 | 0.000 / 0.000 | 2.3486 / 2.3486 | 5.1292 | 51.292 |
| 18:00-18:30 |  | 5/5 |  | 2.3558 | 2.3558 | 2 | 2 | 0.000 / 0.000 | 2.3558 / 2.3558 | 5.1436 | 51.436 |
| 18:30-19:00 |  | 5/5 |  | 2.4717 | 2.4717 | 2 | 2 | 0.000 / 0.000 | 2.4717 / 2.4717 | 5.3754 | 53.754 |
| 19:00-19:30 |  | 5/5 |  | 2.4432 | 2.4432 | 2 | 2 | 0.000 / 0.000 | 2.4432 / 2.4432 | 5.3184 | 53.184 |
| 19:30-20:00 |  | 5/5 |  | 2.2741 | 2.2741 | 2 | 2 | 0.000 / 0.000 | 2.2741 / 2.2741 | 4.9802 | 49.802 |
| 20:00-20:30 |  | 5/5 |  | 2.2716 | 2.2716 | 2 | 2 | 0.000 / 0.000 | 2.2716 / 2.2716 | 4.9751 | 49.751 |
| 20:30-21:00 |  | 5/5 |  | 2.2506 | 2.2506 | 2 | 2 | 0.000 / 0.000 | 2.2506 / 2.2506 | 4.9331 | 49.331 |
| 21:00-21:30 |  | 5/5 |  | 2.1515 | 2.1515 | 2 | 2 | 0.000 / 0.000 | 2.1515 / 2.1515 | 4.7350 | 47.350 |
| 21:30-22:00 |  | 5/5 |  | 2.1362 | 2.1362 | 2 | 2 | 0.000 / 0.000 | 2.1362 / 2.1362 | 4.7045 | 47.045 |
| 22:00-22:30 |  | 5/5 |  | 2.0557 | 2.0557 | 2 | 2 | 0.000 / 0.000 | 2.0557 / 2.0557 | 4.5434 | 45.434 |
| 22:30-23:00 |  | 5/5 |  | 1.9793 | 1.9793 | 2 | 2 | 0.000 / 0.000 | 1.9793 / 1.9793 | 4.3906 | 43.906 |
| 23:00-23:30 |  | 5/5 |  | 2.0218 | 2.0218 | 2 | 2 | 0.000 / 0.000 | 2.0218 / 2.0218 | 4.4756 | 44.756 |
| 23:30-00:00 |  | 5/5 |  | 1.9840 | 1.9840 | 2 | 2 | 0.000 / 0.000 | 1.9840 / 1.9840 | 4.4000 | 44.000 |
| 00:00-00:30 |  | 5/5 |  | 2.0927 | 2.0927 | 2 | 2 | 0.000 / 0.000 | 2.0927 / 2.0927 | 4.6173 | 46.173 |
| 00:30-01:00 |  | 5/5 |  | 2.1406 | 2.1406 | 2 | 2 | 0.000 / 0.000 | 2.1406 / 2.1406 | 4.7132 | 47.132 |
| 01:00-01:30 |  | 5/5 |  | 1.9233 | 1.9233 | 2 | 2 | 0.000 / 0.000 | 1.9233 / 1.9233 | 4.2785 | 42.785 |
| 01:30-02:00 |  | 5/5 |  | 1.9205 | 1.9205 | 2 | 2 | 0.000 / 0.000 | 1.9205 / 1.9205 | 4.2729 | 42.729 |
| 02:00-02:30 |  | 5/5 |  | 1.8302 | 1.8302 | 2 | 2 | 0.000 / 0.000 | 1.8302 / 1.8302 | 4.0923 | 40.923 |
| 02:30-03:00 |  | 5/5 |  | 1.8299 | 1.8299 | 2 | 2 | 0.000 / 0.000 | 1.8299 / 1.8299 | 4.0917 | 40.917 |
| 03:00-03:30 |  | 5/5 |  | 1.8141 | 1.8141 | 2 | 2 | 0.000 / 0.000 | 1.8141 / 1.8141 | 4.0602 | 40.602 |
| 03:30-04:00 |  | 5/5 |  | 1.8704 | 1.8704 | 2 | 2 | 0.000 / 0.000 | 1.8704 / 1.8704 | 4.1727 | 41.727 |
| 04:00-04:30 |  | 5/5 |  | 1.9411 | 1.9415 | 2 | 2 | 0.000 / 0.000 | 1.9411 / 1.9411 | 4.3141 | 43.141 |
| 04:30-05:00 |  | 5/5 |  | 2.0467 | 2.0541 | 2 | 2 | 0.000 / 0.000 | 2.0467 / 2.0467 | 4.5254 | 45.254 |
| 05:00-05:30 |  | 5/5 |  | 1.9468 | 1.9468 | 2 | 2 | 0.000 / 0.000 | 1.9468 / 1.9468 | 4.3256 | 43.256 |
| 05:30-06:00 |  | 5/5 |  | 1.9607 | 1.9607 | 2 | 2 | 0.000 / 0.000 | 1.9607 / 1.9607 | 4.3534 | 43.534 |
| 06:00-06:30 |  | 5/5 |  | 1.8856 | 1.8856 | 2 | 2 | 0.000 / 0.000 | 1.8856 / 1.8856 | 4.2031 | 42.031 |
| 06:30-07:00 |  | 5/5 |  | 1.9840 | 1.9866 | 2 | 2 | 0.000 / 0.000 | 1.9840 / 1.9840 | 4.4001 | 44.001 |
| 07:00-07:30 | D | 5/5 |  | 2.0776 | 2.0776 | 2 | 2 | 0.000 / 0.000 | 2.0776 / 2.0776 | 4.5872 | 45.872 |
| 07:30-08:00 | D | 5/5 |  | 2.2680 | 2.2680 | 2 | 2 | 0.000 / 0.000 | 2.2680 / 2.2680 | 4.9680 | 49.680 |
| 08:00-08:30 | D | 5/5 |  | 1.9757 | 1.9757 | 2 | 2 | 0.000 / 0.000 | 1.9757 / 1.9757 | 4.3834 | 43.834 |
| 08:30-09:00 | D | 5/5 |  | 2.0819 | 2.0819 | 2 | 2 | 0.000 / 0.000 | 2.0819 / 2.0819 | 4.5957 | 45.957 |
| 09:00-09:30 | D | 5/5 |  | 2.0275 | 2.0275 | 2 | 2 | 0.000 / 0.000 | 2.0275 / 2.0275 | 4.4871 | 44.871 |
| 09:30-10:00 | D | 5/5 |  | 2.0101 | 2.0101 | 2 | 2 | 0.000 / 0.000 | 2.0101 / 2.0101 | 4.4521 | 44.521 |
| 10:00-10:30 | D | 5/5 |  | 2.0095 | 2.0095 | 2 | 2 | 0.000 / 0.000 | 2.0095 / 2.0095 | 4.4511 | 44.511 |
| 10:30-11:00 | D | 5/5 |  | 1.8400 | 1.8400 | 2 | 2 | 0.000 / 0.000 | 1.8400 / 1.8400 | 4.1119 | 41.119 |
| 11:00-11:30 | D | 5/5 |  | 1.7117 | 1.7117 | 2 | 2 | 0.000 / 0.000 | 1.7117 / 1.7117 | 3.8553 | 38.553 |
| 11:30-12:00 | D | 5/5 |  | 1.7439 | 1.7439 | 2 | 2 | 0.000 / 0.000 | 1.7439 / 1.7439 | 3.9199 | 39.199 |
| 12:00-12:30 | D | 5/5 |  | 1.8110 | 1.8110 | 2 | 2 | 0.000 / 0.000 | 1.8110 / 1.8110 | 4.0541 | 40.541 |
| 12:30-13:00 |  | 5/5 |  | 1.7727 | 1.7727 | 2 | 2 | 0.000 / 0.000 | 1.7727 / 1.7727 | 3.9774 | 39.774 |
| 13:00-13:30 |  | 5/5 |  | 1.8354 | 1.8354 | 2 | 2 | 0.000 / 0.000 | 1.8354 / 1.8354 | 4.1029 | 41.029 |
| 13:30-14:00 |  | 5/5 |  | 1.8155 | 1.8155 | 2 | 2 | 0.000 / 0.000 | 1.8155 / 1.8155 | 4.0630 | 40.630 |
| 14:00-14:30 |  | 5/5 |  | 1.8117 | 1.8117 | 2 | 2 | 0.000 / 0.000 | 1.8117 / 1.8117 | 4.0554 | 40.554 |
| 14:30-15:00 |  | 5/5 |  | 1.7418 | 1.7418 | 2 | 2 | 0.000 / 0.000 | 1.7418 / 1.7418 | 3.9156 | 39.156 |
| 15:00-15:30 |  | 5/5 |  | 1.8324 | 1.8324 | 2 | 2 | 0.000 / 0.000 | 1.8324 / 1.8324 | 4.0968 | 40.968 |
| 15:30-16:00 |  | 5/5 |  | 2.0957 | 2.0957 | 2 | 2 | 0.000 / 0.000 | 2.0957 / 2.0957 | 4.6234 | 46.234 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/GC_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 2073acba2f782afc4e662fe94eaa0f68c0a3071d8d70fc833b79498c2e6b2a33 (1,635,181 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/GC_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 702fec51acd48cae603ed7fa89ee0abcc53ed4b447a9f4ff206c8496f66b91f0 (853,795 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/GC_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 4feb6a301d9cef04f3f5e70685601d2a4600889530580a60e883483b7b90e2ea (2,178,159 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/GC_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` c6e268247d0a35a7e8e41f60a6fc61d2db01286efea617b8ef19b260ed7a4189 (1,509,111 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/GC_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 593cece7b76c35fd95c01110df4464d7236a366b440d0ae583551447c5e0964f (1,469,440 records)

### HE (livestock)

Tick 0.00025 (vendor units 0.02500, factor 100), tick value $10.0; commission $5.22 round turn = 0.5220 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:00 CT.

Event-window one-side slippage: buy 0.7215, sell 0.7215 ticks (round turn inside a window 1.9650 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 08:30-09:00 | D | 5/5 |  | 0.7215 | 0.7215 | 4 | 4 | 0.000 / 0.000 | 0.7215 / 0.7215 | 1.9650 | 19.650 |
| 09:00-09:30 | D | 5/5 |  | 0.6737 | 0.6737 | 4 | 5 | 0.000 / 0.000 | 0.6737 / 0.6737 | 1.8694 | 18.694 |
| 09:30-10:00 | D | 5/5 |  | 0.6608 | 0.6608 | 4 | 5 | 0.000 / 0.000 | 0.6608 / 0.6608 | 1.8436 | 18.436 |
| 10:00-10:30 | D | 5/5 |  | 0.6628 | 0.6628 | 4 | 5 | 0.000 / 0.000 | 0.6628 / 0.6628 | 1.8477 | 18.477 |
| 10:30-11:00 | D | 5/5 |  | 0.6757 | 0.6757 | 4 | 5 | 0.000 / 0.000 | 0.6757 / 0.6757 | 1.8734 | 18.734 |
| 11:00-11:30 | D | 5/5 |  | 0.6969 | 0.6969 | 4 | 6 | 0.000 / 0.000 | 0.6969 / 0.6969 | 1.9158 | 19.158 |
| 11:30-12:00 | D | 5/5 |  | 0.6558 | 0.6558 | 4 | 5 | 0.000 / 0.000 | 0.6558 / 0.6558 | 1.8337 | 18.337 |
| 12:00-12:30 | D | 5/5 |  | 0.6584 | 0.6584 | 5 | 6 | 0.000 / 0.000 | 0.6584 / 0.6584 | 1.8387 | 18.387 |
| 12:30-13:00 | D | 5/5 |  | 0.6150 | 0.6150 | 6 | 8 | 0.000 / 0.000 | 0.6150 / 0.6150 | 1.7520 | 17.520 |
| 13:00-13:05 |  | 5/5 |  | 0.5936 | 0.5936 | 8 | 10 | 0.000 / 0.000 | 0.5936 / 0.5936 | 1.7093 | 17.093 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/HE_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 8632cd719aad6b6a50a8716aa5b65089bddf95c5d741bda9e1e55c219349b35c (54,164 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HE_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 0b02d1a272bf52f7c9a24d354461b91c590eae60e1d57567649cacf0bcba170d (54,696 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HE_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 2d2f92ac38b33918cf8d4a3b517f50012fe53e11a72bda84b17e8aa53bd5ad67 (43,958 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HE_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` cd4f69a4cf177f17bafcab9d5bc5f5b6a8fc9feeb85546be694065f7d84a001f (49,857 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HE_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 1ca0a22b93568b4500655c0d501d8c583a125413686003434cf22e0a651e2156 (43,902 records)

### HG (metals)

Tick 0.0005 (vendor units 0.0005, factor 1), tick value $12.5; commission $4.32 round turn = 0.3456 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:10-12:00 CT.

Event-window one-side slippage: buy 1.5748, sell 1.5748 ticks (round turn inside a window 3.4953 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.5748 | 1.5748 | 2 | 3 | 0.000 / 0.000 | 1.5748 / 1.5748 | 3.4953 | 43.691 |
| 17:30-18:00 |  | 5/5 |  | 1.3873 | 1.3873 | 2 | 2 | 0.000 / 0.000 | 1.3873 / 1.3873 | 3.1201 | 39.002 |
| 18:00-18:30 |  | 5/5 |  | 1.2861 | 1.2861 | 2 | 2 | 0.000 / 0.000 | 1.2861 / 1.2861 | 2.9179 | 36.474 |
| 18:30-19:00 |  | 5/5 |  | 1.3116 | 1.3116 | 2 | 3 | 0.000 / 0.000 | 1.3116 / 1.3116 | 2.9689 | 37.111 |
| 19:00-19:30 |  | 5/5 |  | 1.2439 | 1.2439 | 2 | 2 | 0.000 / 0.000 | 1.2439 / 1.2439 | 2.8333 | 35.417 |
| 19:30-20:00 |  | 5/5 |  | 1.1775 | 1.1775 | 3 | 2 | 0.000 / 0.000 | 1.1775 / 1.1775 | 2.7007 | 33.758 |
| 20:00-20:30 |  | 5/5 |  | 1.2554 | 1.2554 | 2 | 2 | 0.000 / 0.000 | 1.2554 / 1.2554 | 2.8565 | 35.706 |
| 20:30-21:00 |  | 5/5 |  | 1.3681 | 1.3681 | 2 | 2 | 0.000 / 0.000 | 1.3681 / 1.3681 | 3.0818 | 38.523 |
| 21:00-21:30 |  | 5/5 |  | 1.3510 | 1.3510 | 2 | 2 | 0.000 / 0.000 | 1.3510 / 1.3510 | 3.0475 | 38.094 |
| 21:30-22:00 |  | 5/5 |  | 1.3241 | 1.3241 | 2 | 2 | 0.000 / 0.000 | 1.3241 / 1.3241 | 2.9938 | 37.422 |
| 22:00-22:30 |  | 5/5 |  | 1.2596 | 1.2596 | 2 | 2 | 0.000 / 0.000 | 1.2596 / 1.2596 | 2.8647 | 35.809 |
| 22:30-23:00 |  | 5/5 |  | 1.1886 | 1.1886 | 2 | 2 | 0.000 / 0.000 | 1.1886 / 1.1886 | 2.7229 | 34.036 |
| 23:00-23:30 |  | 5/5 |  | 1.2294 | 1.2294 | 3 | 2 | 0.000 / 0.000 | 1.2294 / 1.2294 | 2.8044 | 35.055 |
| 23:30-00:00 |  | 5/5 |  | 1.3024 | 1.3024 | 2 | 2 | 0.000 / 0.000 | 1.3024 / 1.3024 | 2.9504 | 36.880 |
| 00:00-00:30 |  | 5/5 |  | 1.2610 | 1.2610 | 2 | 2 | 0.000 / 0.000 | 1.2610 / 1.2610 | 2.8675 | 35.844 |
| 00:30-01:00 |  | 5/5 |  | 1.2811 | 1.2811 | 2 | 2 | 0.000 / 0.000 | 1.2811 / 1.2811 | 2.9077 | 36.347 |
| 01:00-01:30 |  | 5/5 |  | 1.2108 | 1.2108 | 2 | 2 | 0.000 / 0.000 | 1.2108 / 1.2108 | 2.7672 | 34.590 |
| 01:30-02:00 |  | 5/5 |  | 1.3185 | 1.3185 | 2 | 2 | 0.000 / 0.000 | 1.3185 / 1.3185 | 2.9826 | 37.283 |
| 02:00-02:30 |  | 5/5 |  | 1.2847 | 1.2847 | 2 | 2 | 0.000 / 0.000 | 1.2847 / 1.2847 | 2.9151 | 36.439 |
| 02:30-03:00 |  | 5/5 |  | 1.2370 | 1.2370 | 2 | 2 | 0.000 / 0.000 | 1.2370 / 1.2370 | 2.8196 | 35.246 |
| 03:00-03:30 |  | 5/5 |  | 1.2298 | 1.2298 | 2 | 2 | 0.000 / 0.000 | 1.2298 / 1.2298 | 2.8051 | 35.064 |
| 03:30-04:00 |  | 5/5 |  | 1.2500 | 1.2500 | 2 | 2 | 0.000 / 0.000 | 1.2500 / 1.2500 | 2.8455 | 35.569 |
| 04:00-04:30 |  | 5/5 |  | 1.2481 | 1.2481 | 2 | 2 | 0.000 / 0.000 | 1.2481 / 1.2481 | 2.8418 | 35.522 |
| 04:30-05:00 |  | 5/5 |  | 1.2256 | 1.2256 | 2 | 2 | 0.000 / 0.000 | 1.2256 / 1.2256 | 2.7967 | 34.959 |
| 05:00-05:30 |  | 5/5 |  | 1.2110 | 1.2110 | 2 | 2 | 0.000 / 0.000 | 1.2110 / 1.2110 | 2.7675 | 34.594 |
| 05:30-06:00 |  | 5/5 |  | 1.2051 | 1.2051 | 2 | 2 | 0.000 / 0.000 | 1.2051 / 1.2051 | 2.7557 | 34.447 |
| 06:00-06:30 |  | 5/5 |  | 1.1899 | 1.1899 | 2 | 2 | 0.000 / 0.000 | 1.1899 / 1.1899 | 2.7254 | 34.067 |
| 06:30-07:00 |  | 5/5 |  | 1.2262 | 1.2262 | 2 | 2 | 0.000 / 0.000 | 1.2262 / 1.2262 | 2.7981 | 34.976 |
| 07:00-07:30 | D | 5/5 |  | 1.2337 | 1.2339 | 2 | 2 | 0.000 / 0.000 | 1.2337 / 1.2337 | 2.8130 | 35.162 |
| 07:30-08:00 | D | 5/5 |  | 1.2280 | 1.2280 | 2 | 2 | 0.000 / 0.000 | 1.2280 / 1.2280 | 2.8016 | 35.020 |
| 08:00-08:30 | D | 5/5 |  | 1.1933 | 1.1933 | 2 | 2 | 0.000 / 0.000 | 1.1933 / 1.1933 | 2.7321 | 34.151 |
| 08:30-09:00 | D | 5/5 |  | 1.1332 | 1.1332 | 2 | 2 | 0.000 / 0.000 | 1.1332 / 1.1332 | 2.6120 | 32.650 |
| 09:00-09:30 | D | 5/5 |  | 1.0839 | 1.0839 | 2 | 2 | 0.000 / 0.000 | 1.0839 / 1.0839 | 2.5133 | 31.416 |
| 09:30-10:00 | D | 5/5 |  | 1.0689 | 1.0689 | 3 | 2 | 0.000 / 0.000 | 1.0689 / 1.0689 | 2.4833 | 31.042 |
| 10:00-10:30 | D | 5/5 |  | 1.0897 | 1.0897 | 2 | 2 | 0.000 / 0.000 | 1.0897 / 1.0897 | 2.5249 | 31.562 |
| 10:30-11:00 | D | 5/5 |  | 1.0962 | 1.0962 | 2 | 2 | 0.000 / 0.000 | 1.0962 / 1.0962 | 2.5380 | 31.725 |
| 11:00-11:30 | D | 5/5 |  | 1.0413 | 1.0413 | 3 | 3 | 0.000 / 0.000 | 1.0413 / 1.0413 | 2.4282 | 30.352 |
| 11:30-12:00 | D | 5/5 |  | 1.0426 | 1.0426 | 3 | 3 | 0.000 / 0.000 | 1.0426 / 1.0426 | 2.4309 | 30.386 |
| 12:00-12:30 |  | 5/5 |  | 1.0436 | 1.0436 | 3 | 3 | 0.000 / 0.000 | 1.0436 / 1.0436 | 2.4328 | 30.410 |
| 12:30-13:00 |  | 5/5 |  | 1.0996 | 1.0996 | 3 | 3 | 0.000 / 0.000 | 1.0996 / 1.0996 | 2.5449 | 31.811 |
| 13:00-13:30 |  | 5/5 |  | 1.1096 | 1.1096 | 3 | 3 | 0.000 / 0.000 | 1.1096 / 1.1096 | 2.5648 | 32.061 |
| 13:30-14:00 |  | 5/5 |  | 1.0699 | 1.0699 | 3 | 2 | 0.000 / 0.000 | 1.0699 / 1.0699 | 2.4853 | 31.067 |
| 14:00-14:30 |  | 5/5 |  | 1.0724 | 1.0724 | 3 | 2 | 0.000 / 0.000 | 1.0724 / 1.0724 | 2.4903 | 31.129 |
| 14:30-15:00 |  | 5/5 |  | 1.0713 | 1.0713 | 3 | 3 | 0.000 / 0.000 | 1.0713 / 1.0713 | 2.4882 | 31.103 |
| 15:00-15:30 |  | 5/5 |  | 1.0467 | 1.0467 | 4 | 4 | 0.000 / 0.000 | 1.0467 / 1.0467 | 2.4389 | 30.486 |
| 15:30-16:00 |  | 5/5 |  | 0.9412 | 0.9412 | 3 | 3 | 0.000 / 0.000 | 0.9412 / 0.9412 | 2.2279 | 27.849 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/HG_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 6d8545d4867b86b082a32bba8b101d6490ab02ca1a4429b838a5e3bdca799334 (245,078 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HG_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 0dcac1ab4344b5e98f311f63b036edb7827d59128ef21c33b3c7670f17e70496 (130,467 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HG_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 4cbbcce6e7190063b72925681003debf02f32d6f8dc89fe96f131e468f6ff123 (259,999 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HG_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 9753977ff5278a4f80773d30b08134519fb9c1464196d7c1cf5781553a980000 (785,942 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HG_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` b433ae890fd2d50a4a8511cefd1b9a65033d8c802b08630b2a31b8e7c546f5a0 (484,618 records)

### HO (energy)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $4.2; commission $4.02 round turn = 0.9571 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 24.1333, sell 24.1333 ticks (round turn inside a window 49.2237 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 24.1333 | 24.1333 | 2 | 2 | 0.000 / 0.000 | 24.1333 / 24.1333 | 49.2237 | 206.740 |
| 17:30-18:00 |  | 5/5 |  | 10.8007 | 10.8007 | 2 | 2 | 0.000 / 0.000 | 10.8007 / 10.8007 | 22.5585 | 94.746 |
| 18:00-18:30 |  | 5/5 |  | 11.3130 | 11.3130 | 2 | 2 | 0.000 / 0.000 | 11.3130 / 11.3130 | 23.5831 | 99.049 |
| 18:30-19:00 |  | 5/5 |  | 13.2359 | 13.2359 | 2 | 1 | 0.000 / 0.000 | 13.2359 / 13.2359 | 27.4289 | 115.202 |
| 19:00-19:30 |  | 5/5 |  | 8.0676 | 8.0676 | 2 | 1 | 0.000 / 0.000 | 8.0676 / 8.0676 | 17.0923 | 71.788 |
| 19:30-20:00 |  | 5/5 |  | 7.4271 | 7.4271 | 2 | 1 | 0.000 / 0.000 | 7.4271 / 7.4271 | 15.8113 | 66.408 |
| 20:00-20:30 |  | 5/5 |  | 7.4490 | 7.4490 | 2 | 1 | 0.000 / 0.000 | 7.4490 / 7.4490 | 15.8552 | 66.592 |
| 20:30-21:00 |  | 5/5 |  | 7.7098 | 7.7098 | 2 | 1 | 0.000 / 0.000 | 7.7098 / 7.7098 | 16.3768 | 68.782 |
| 21:00-21:30 |  | 5/5 |  | 7.8357 | 7.8357 | 1 | 1 | 0.000 / 0.000 | 7.8357 / 7.8357 | 16.6285 | 69.840 |
| 21:30-22:00 |  | 5/5 |  | 8.7079 | 8.7079 | 2 | 1 | 0.000 / 0.000 | 8.7079 / 8.7079 | 18.3729 | 77.166 |
| 22:00-22:30 |  | 5/5 |  | 7.7682 | 7.7682 | 1 | 1 | 0.000 / 0.000 | 7.7682 / 7.7682 | 16.4934 | 69.272 |
| 22:30-23:00 |  | 5/5 |  | 7.8915 | 7.8915 | 1 | 1 | 0.000 / 0.000 | 7.8915 / 7.8915 | 16.7401 | 70.309 |
| 23:00-23:30 |  | 5/5 |  | 6.8554 | 6.8554 | 1 | 2 | 0.000 / 0.000 | 6.8554 / 6.8554 | 14.6680 | 61.606 |
| 23:30-00:00 |  | 5/5 |  | 7.4149 | 7.4149 | 2 | 1 | 0.000 / 0.000 | 7.4149 / 7.4149 | 15.7870 | 66.305 |
| 00:00-00:30 |  | 5/5 |  | 7.8753 | 7.8753 | 2 | 1 | 0.000 / 0.000 | 7.8753 / 7.8753 | 16.7077 | 70.172 |
| 00:30-01:00 |  | 5/5 |  | 8.1499 | 8.1499 | 2 | 1 | 0.000 / 0.000 | 8.1499 / 8.1499 | 17.2569 | 72.479 |
| 01:00-01:30 |  | 5/5 |  | 7.0509 | 7.0509 | 2 | 1 | 0.000 / 0.000 | 7.0509 / 7.0509 | 15.0589 | 63.247 |
| 01:30-02:00 |  | 5/5 |  | 7.4434 | 7.4434 | 2 | 1 | 0.000 / 0.000 | 7.4434 / 7.4434 | 15.8439 | 66.544 |
| 02:00-02:30 |  | 5/5 |  | 8.2277 | 8.2277 | 2 | 1 | 0.000 / 0.000 | 8.2277 / 8.2277 | 17.4126 | 73.133 |
| 02:30-03:00 |  | 5/5 |  | 8.0837 | 8.0837 | 2 | 1 | 0.000 / 0.000 | 8.0837 / 8.0837 | 17.1246 | 71.923 |
| 03:00-03:30 |  | 5/5 |  | 7.1284 | 7.1284 | 1 | 1 | 0.000 / 0.000 | 7.1284 / 7.1284 | 15.2139 | 63.898 |
| 03:30-04:00 |  | 5/5 |  | 6.6676 | 6.6676 | 2 | 1 | 0.000 / 0.000 | 6.6676 / 6.6676 | 14.2922 | 60.027 |
| 04:00-04:30 |  | 5/5 |  | 7.2080 | 7.2080 | 1 | 1 | 0.000 / 0.000 | 7.2080 / 7.2080 | 15.3732 | 64.567 |
| 04:30-05:00 |  | 5/5 |  | 6.4686 | 6.4686 | 1 | 1 | 0.000 / 0.000 | 6.4686 / 6.4686 | 13.8944 | 58.356 |
| 05:00-05:30 |  | 5/5 |  | 6.8884 | 6.8884 | 1 | 1 | 0.000 / 0.000 | 6.8884 / 6.8884 | 14.7339 | 61.883 |
| 05:30-06:00 |  | 5/5 |  | 6.8024 | 6.8024 | 1 | 1 | 0.000 / 0.000 | 6.8024 / 6.8024 | 14.5619 | 61.160 |
| 06:00-06:30 |  | 5/5 |  | 5.6979 | 5.6979 | 1 | 2 | 0.000 / 0.000 | 5.6979 / 5.6979 | 12.3529 | 51.882 |
| 06:30-07:00 |  | 5/5 |  | 6.9359 | 6.9359 | 1 | 2 | 0.000 / 0.000 | 6.9359 / 6.9359 | 14.8289 | 62.281 |
| 07:00-07:30 |  | 5/5 |  | 6.0566 | 6.0566 | 1 | 1 | 0.000 / 0.000 | 6.0566 / 6.0566 | 13.0704 | 54.896 |
| 07:30-08:00 |  | 5/5 |  | 5.8356 | 5.8356 | 1 | 1 | 0.000 / 0.000 | 5.8356 / 5.8356 | 12.6284 | 53.039 |
| 08:00-08:30 | D | 5/5 |  | 4.6124 | 4.6124 | 1 | 1 | 0.000 / 0.000 | 4.6124 / 4.6124 | 10.1819 | 42.764 |
| 08:30-09:00 | D | 5/5 |  | 4.4017 | 4.4017 | 1 | 1 | 0.000 / 0.000 | 4.4017 / 4.4017 | 9.7606 | 40.995 |
| 09:00-09:30 | D | 5/5 |  | 5.1941 | 5.1941 | 1 | 1 | 0.000 / 0.000 | 5.1941 / 5.1941 | 11.3453 | 47.650 |
| 09:30-10:00 | D | 5/5 |  | 5.3336 | 5.3336 | 1 | 1 | 0.000 / 0.000 | 5.3336 / 5.3336 | 11.6243 | 48.822 |
| 10:00-10:30 | D | 5/5 |  | 4.9278 | 4.9278 | 1 | 1 | 0.000 / 0.000 | 4.9278 / 4.9278 | 10.8127 | 45.413 |
| 10:30-11:00 | D | 5/5 |  | 4.7084 | 4.7084 | 1 | 1 | 0.000 / 0.000 | 4.7084 / 4.7084 | 10.3739 | 43.570 |
| 11:00-11:30 | D | 5/5 |  | 3.7917 | 3.7917 | 1 | 2 | 0.000 / 0.000 | 3.7917 / 3.7917 | 8.5405 | 35.870 |
| 11:30-12:00 | D | 5/5 |  | 4.2586 | 4.2586 | 1 | 1 | 0.000 / 0.000 | 4.2586 / 4.2586 | 9.4743 | 39.792 |
| 12:00-12:30 | D | 5/5 |  | 3.7207 | 3.7207 | 1 | 2 | 0.000 / 0.000 | 3.7207 / 3.7207 | 8.3985 | 35.274 |
| 12:30-13:00 | D | 5/5 |  | 4.1931 | 4.1931 | 1 | 1 | 0.000 / 0.000 | 4.1931 / 4.1931 | 9.3434 | 39.242 |
| 13:00-13:30 | D | 5/5 |  | 3.6419 | 3.6419 | 1 | 1 | 0.000 / 0.000 | 3.6419 / 3.6419 | 8.2410 | 34.612 |
| 13:30-14:00 |  | 5/5 |  | 3.8706 | 3.8706 | 2 | 1 | 0.000 / 0.000 | 3.8706 / 3.8706 | 8.6983 | 36.533 |
| 14:00-14:30 |  | 5/5 |  | 3.8791 | 3.8791 | 2 | 2 | 0.000 / 0.000 | 3.8791 / 3.8791 | 8.7153 | 36.604 |
| 14:30-15:00 |  | 5/5 |  | 4.5327 | 4.5327 | 2 | 2 | 0.000 / 0.000 | 4.5327 / 4.5327 | 10.0225 | 42.094 |
| 15:00-15:30 |  | 5/5 |  | 4.1896 | 4.1896 | 2 | 2 | 0.000 / 0.000 | 4.1896 / 4.1896 | 9.3364 | 39.213 |
| 15:30-16:00 |  | 5/5 |  | 5.3033 | 5.3033 | 2 | 2 | 0.000 / 0.000 | 5.3033 / 5.3033 | 11.5637 | 48.567 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/HO_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` b6f404664a3568c8ee723af385e22a436548e91cacd612d37ddb24c80bab2dd0 (326,903 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HO_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` d05f989b82b67fd3c409522c124f5c4a9f39c3c02690836a823141a71613aed4 (358,851 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HO_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` b02814b74963a96a2e238e29213b4be4a9f1dc46b188cddba6fe2af8d8340eae (369,878 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HO_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` ca54afb37c735a81a71039ea0d82a3dfde3d65d65e0ce5518fcd23f5462d2d45 (492,428 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/HO_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 6468c2ee819b4e9527b4bbd8731b0871cf051020c49bbfcb6f43bb4f3436b04a (976,432 records)

### LE (livestock)

Tick 0.00025 (vendor units 0.02500, factor 100), tick value $10.0; commission $5.22 round turn = 0.5220 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:00 CT.

Event-window one-side slippage: buy 0.9879, sell 0.9879 ticks (round turn inside a window 2.4979 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 08:30-09:00 | D | 5/5 |  | 0.9358 | 0.9358 | 2 | 2 | 0.000 / 0.000 | 0.9358 / 0.9358 | 2.3936 | 23.936 |
| 09:00-09:30 | D | 5/5 |  | 0.9394 | 0.9394 | 2 | 2 | 0.000 / 0.000 | 0.9394 / 0.9394 | 2.4007 | 24.007 |
| 09:30-10:00 | D | 5/5 |  | 0.9005 | 0.9005 | 2 | 2 | 0.000 / 0.000 | 0.9005 / 0.9005 | 2.3229 | 23.229 |
| 10:00-10:30 | D | 5/5 |  | 0.8541 | 0.8541 | 3 | 2 | 0.000 / 0.000 | 0.8541 / 0.8541 | 2.2302 | 22.302 |
| 10:30-11:00 | D | 5/5 |  | 0.9855 | 0.9855 | 2 | 2 | 0.000 / 0.000 | 0.9855 / 0.9855 | 2.4931 | 24.931 |
| 11:00-11:30 | D | 5/5 |  | 0.9383 | 0.9383 | 2 | 2 | 0.000 / 0.000 | 0.9383 / 0.9383 | 2.3986 | 23.986 |
| 11:30-12:00 | D | 5/5 |  | 0.9473 | 0.9473 | 2 | 2 | 0.000 / 0.000 | 0.9473 / 0.9473 | 2.4166 | 24.166 |
| 12:00-12:30 | D | 5/5 |  | 0.9879 | 0.9879 | 2 | 2 | 0.000 / 0.000 | 0.9879 / 0.9879 | 2.4979 | 24.979 |
| 12:30-13:00 | D | 5/5 |  | 0.9318 | 0.9318 | 2 | 2 | 0.000 / 0.000 | 0.9318 / 0.9318 | 2.3857 | 23.857 |
| 13:00-13:05 |  | 5/5 |  | 0.8708 | 0.8708 | 3 | 3 | 0.000 / 0.000 | 0.8708 / 0.8708 | 2.2636 | 22.636 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/LE_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` bb575bce7d431ee20b6cb76ccd05eded40422afe6981a86e9e1543c4b83d87d3 (104,570 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/LE_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 2ea26eb6840257b9e744b9e47c2c242cb6ddd35771fb145a8943ea5760e82f7c (96,165 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/LE_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` bce4e60ea1bad187b3a5aec2b93b70f4e7caa5b2c71c907bfafee80b33a0750c (101,887 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/LE_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 5ac8fd1de84ad2b4fb9839bec7bce252eff06d2c4800e01fb916a30d1f0bcf8f (64,532 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/LE_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` b7e140e9e6c6a8f8b86536ec1478f23e84696ac64454c17d493512108f0cc7de (60,299 records)

### M2K (equity)

Tick 0.10 (vendor units 0.10, factor 1), tick value $0.5; commission $1.22 round turn = 2.4400 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 3; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 1.9531, sell 1.9531 ticks (round turn inside a window 6.3462 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.6198 | 1.6198 | 2 | 2 | 0.333 / 0.333 | 1.9531 / 1.9531 | 6.3462 | 3.173 |
| 17:30-18:00 |  | 5/5 |  | 0.9470 | 0.9470 | 3 | 3 | 0.000 / 0.000 | 0.9470 / 0.9470 | 4.3339 | 2.167 |
| 18:00-18:30 |  | 5/5 |  | 0.9203 | 0.9203 | 3 | 3 | 0.000 / 0.000 | 0.9203 / 0.9203 | 4.2805 | 2.140 |
| 18:30-19:00 |  | 5/5 |  | 0.9053 | 0.9053 | 3 | 3 | 0.000 / 0.000 | 0.9053 / 0.9053 | 4.2506 | 2.125 |
| 19:00-19:30 |  | 5/5 |  | 0.9236 | 0.9236 | 3 | 3 | 0.000 / 0.000 | 0.9236 / 0.9236 | 4.2872 | 2.144 |
| 19:30-20:00 |  | 5/5 |  | 0.8790 | 0.8790 | 3 | 3 | 0.000 / 0.000 | 0.8790 / 0.8790 | 4.1981 | 2.099 |
| 20:00-20:30 |  | 5/5 |  | 0.9011 | 0.9011 | 3 | 3 | 0.000 / 0.000 | 0.9011 / 0.9011 | 4.2421 | 2.121 |
| 20:30-21:00 |  | 5/5 |  | 0.9053 | 0.9053 | 3 | 3 | 0.000 / 0.000 | 0.9053 / 0.9053 | 4.2505 | 2.125 |
| 21:00-21:30 |  | 5/5 |  | 0.8847 | 0.8847 | 3 | 3 | 0.000 / 0.000 | 0.8847 / 0.8847 | 4.2094 | 2.105 |
| 21:30-22:00 |  | 5/5 |  | 0.8869 | 0.8869 | 3 | 3 | 0.000 / 0.000 | 0.8869 / 0.8869 | 4.2138 | 2.107 |
| 22:00-22:30 |  | 5/5 |  | 0.8689 | 0.8689 | 3 | 3 | 0.000 / 0.000 | 0.8689 / 0.8689 | 4.1778 | 2.089 |
| 22:30-23:00 |  | 5/5 |  | 0.9107 | 0.9107 | 3 | 3 | 0.000 / 0.000 | 0.9107 / 0.9107 | 4.2613 | 2.131 |
| 23:00-23:30 |  | 5/5 |  | 0.8909 | 0.8909 | 3 | 3 | 0.000 / 0.000 | 0.8909 / 0.8909 | 4.2218 | 2.111 |
| 23:30-00:00 |  | 5/5 |  | 0.8827 | 0.8827 | 3 | 3 | 0.000 / 0.000 | 0.8827 / 0.8827 | 4.2054 | 2.103 |
| 00:00-00:30 |  | 5/5 |  | 0.9186 | 0.9186 | 3 | 3 | 0.000 / 0.000 | 0.9186 / 0.9186 | 4.2772 | 2.139 |
| 00:30-01:00 |  | 5/5 |  | 0.9170 | 0.9170 | 4 | 3 | 0.000 / 0.000 | 0.9170 / 0.9170 | 4.2740 | 2.137 |
| 01:00-01:30 |  | 5/5 |  | 0.9291 | 0.9291 | 4 | 3 | 0.000 / 0.000 | 0.9291 / 0.9291 | 4.2983 | 2.149 |
| 01:30-02:00 |  | 5/5 |  | 0.9177 | 0.9177 | 3 | 3 | 0.000 / 0.000 | 0.9177 / 0.9177 | 4.2754 | 2.138 |
| 02:00-02:30 |  | 5/5 |  | 0.9238 | 0.9238 | 3 | 3 | 0.000 / 0.000 | 0.9238 / 0.9238 | 4.2876 | 2.144 |
| 02:30-03:00 |  | 5/5 |  | 0.9429 | 0.9429 | 3 | 3 | 0.000 / 0.000 | 0.9429 / 0.9429 | 4.3258 | 2.163 |
| 03:00-03:30 |  | 5/5 |  | 0.9400 | 0.9400 | 3 | 3 | 0.000 / 0.000 | 0.9400 / 0.9400 | 4.3200 | 2.160 |
| 03:30-04:00 |  | 5/5 |  | 0.9594 | 0.9594 | 4 | 3 | 0.000 / 0.000 | 0.9594 / 0.9594 | 4.3588 | 2.179 |
| 04:00-04:30 |  | 5/5 |  | 0.9768 | 0.9768 | 3 | 3 | 0.000 / 0.000 | 0.9768 / 0.9768 | 4.3936 | 2.197 |
| 04:30-05:00 |  | 5/5 |  | 0.9774 | 0.9774 | 3 | 3 | 0.000 / 0.000 | 0.9774 / 0.9774 | 4.3949 | 2.197 |
| 05:00-05:30 |  | 5/5 |  | 0.9438 | 0.9438 | 3 | 3 | 0.000 / 0.000 | 0.9438 / 0.9438 | 4.3277 | 2.164 |
| 05:30-06:00 |  | 5/5 |  | 0.9588 | 0.9588 | 3 | 3 | 0.000 / 0.000 | 0.9588 / 0.9588 | 4.3576 | 2.179 |
| 06:00-06:30 |  | 5/5 |  | 0.9298 | 0.9298 | 3 | 3 | 0.000 / 0.000 | 0.9298 / 0.9298 | 4.2996 | 2.150 |
| 06:30-07:00 |  | 5/5 |  | 1.0074 | 1.0074 | 3 | 3 | 0.000 / 0.000 | 1.0074 / 1.0074 | 4.4548 | 2.227 |
| 07:00-07:30 |  | 5/5 |  | 0.9824 | 0.9824 | 3 | 3 | 0.000 / 0.000 | 0.9824 / 0.9824 | 4.4048 | 2.202 |
| 07:30-08:00 |  | 5/5 |  | 0.9614 | 0.9614 | 3 | 3 | 0.000 / 0.000 | 0.9614 / 0.9614 | 4.3627 | 2.181 |
| 08:00-08:30 |  | 5/5 |  | 0.8661 | 0.8661 | 4 | 4 | 0.000 / 0.000 | 0.8661 / 0.8661 | 4.1723 | 2.086 |
| 08:30-09:00 | D | 5/5 |  | 0.8237 | 0.8237 | 3 | 3 | 0.000 / 0.000 | 0.8237 / 0.8237 | 4.0875 | 2.044 |
| 09:00-09:30 | D | 5/5 |  | 0.7921 | 0.7921 | 3 | 3 | 0.000 / 0.000 | 0.7921 / 0.7921 | 4.0242 | 2.012 |
| 09:30-10:00 | D | 5/5 |  | 0.7678 | 0.7678 | 4 | 3 | 0.000 / 0.000 | 0.7678 / 0.7678 | 3.9755 | 1.988 |
| 10:00-10:30 | D | 5/5 |  | 0.7487 | 0.7487 | 4 | 4 | 0.000 / 0.000 | 0.7487 / 0.7487 | 3.9374 | 1.969 |
| 10:30-11:00 | D | 5/5 |  | 0.7508 | 0.7508 | 3 | 4 | 0.000 / 0.000 | 0.7508 / 0.7508 | 3.9416 | 1.971 |
| 11:00-11:30 | D | 5/5 |  | 0.7499 | 0.7499 | 4 | 4 | 0.000 / 0.000 | 0.7499 / 0.7499 | 3.9398 | 1.970 |
| 11:30-12:00 | D | 5/5 |  | 0.7585 | 0.7585 | 4 | 4 | 0.000 / 0.000 | 0.7585 / 0.7585 | 3.9571 | 1.979 |
| 12:00-12:30 | D | 5/5 |  | 0.7477 | 0.7477 | 4 | 4 | 0.000 / 0.000 | 0.7477 / 0.7477 | 3.9355 | 1.968 |
| 12:30-13:00 | D | 5/5 |  | 0.7484 | 0.7484 | 4 | 4 | 0.000 / 0.000 | 0.7484 / 0.7484 | 3.9368 | 1.968 |
| 13:00-13:30 | D | 5/5 |  | 0.7526 | 0.7526 | 4 | 4 | 0.000 / 0.000 | 0.7526 / 0.7526 | 3.9451 | 1.973 |
| 13:30-14:00 | D | 5/5 |  | 0.7340 | 0.7340 | 5 | 4 | 0.000 / 0.000 | 0.7340 / 0.7340 | 3.9080 | 1.954 |
| 14:00-14:30 | D | 5/5 |  | 0.7331 | 0.7331 | 5 | 5 | 0.000 / 0.000 | 0.7331 / 0.7331 | 3.9063 | 1.953 |
| 14:30-15:00 | D | 5/5 |  | 0.7336 | 0.7336 | 5 | 5 | 0.000 / 0.000 | 0.7336 / 0.7336 | 3.9072 | 1.954 |
| 15:00-15:30 |  | 5/5 |  | 0.9523 | 0.9523 | 5 | 5 | 0.000 / 0.000 | 0.9523 / 0.9523 | 4.3446 | 2.172 |
| 15:30-16:00 |  | 5/5 |  | 0.9091 | 0.9091 | 5 | 5 | 0.000 / 0.000 | 0.9091 / 0.9091 | 4.2582 | 2.129 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/M2K_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` c094a247ec67fafcf3ae11d7f43a2ac5931fdf97c7f40e1b3e8c93e63d7233ad (1,376,893 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M2K_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 8cdf667597e74af6526c2905adb759256b8ca69973367294a871c62a02e27c9d (1,176,194 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M2K_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 3bd31b4a7384e43bcd4ea84f09e873ff672d1f0f58860c669df3bd604f1b1595 (2,058,075 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M2K_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 0612ad5cc06ba93ef67b4289e9ca5a742e49528d1e248f7695559eeed3d81ccc (3,757,099 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M2K_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 90da6bbe2d196dda4c82de14d67f8d4a70cbd02ebb60cddb4a2c8346ec301c87 (1,598,444 records)

### M6A (fx)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $1.0; commission $1.00 round turn = 1.0000 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 10; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.6131, sell 0.6131 ticks (round turn inside a window 2.2262 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5709 | 0.5709 | 22 | 15 | 0.000 / 0.000 | 0.5709 / 0.5709 | 2.1417 | 2.142 |
| 17:30-18:00 |  | 5/5 |  | 0.5938 | 0.5938 | 37 | 28 | 0.000 / 0.000 | 0.5938 / 0.5938 | 2.1877 | 2.188 |
| 18:00-18:30 |  | 5/5 |  | 0.5799 | 0.5799 | 32 | 27 | 0.000 / 0.000 | 0.5799 / 0.5799 | 2.1598 | 2.160 |
| 18:30-19:00 |  | 5/5 |  | 0.5735 | 0.5735 | 34 | 30 | 0.000 / 0.000 | 0.5735 / 0.5735 | 2.1469 | 2.147 |
| 19:00-19:30 |  | 5/5 |  | 0.5755 | 0.5755 | 22 | 26 | 0.000 / 0.000 | 0.5755 / 0.5755 | 2.1509 | 2.151 |
| 19:30-20:00 |  | 5/5 |  | 0.5755 | 0.5755 | 22 | 25 | 0.000 / 0.000 | 0.5755 / 0.5755 | 2.1510 | 2.151 |
| 20:00-20:30 |  | 5/5 |  | 0.5759 | 0.5759 | 21 | 24 | 0.000 / 0.000 | 0.5759 / 0.5759 | 2.1518 | 2.152 |
| 20:30-21:00 |  | 5/5 |  | 0.5893 | 0.5893 | 22 | 30 | 0.000 / 0.000 | 0.5893 / 0.5893 | 2.1786 | 2.179 |
| 21:00-21:30 |  | 5/5 |  | 0.5930 | 0.5930 | 25 | 26 | 0.000 / 0.000 | 0.5930 / 0.5930 | 2.1860 | 2.186 |
| 21:30-22:00 |  | 5/5 |  | 0.5812 | 0.5812 | 24 | 30 | 0.000 / 0.000 | 0.5812 / 0.5812 | 2.1625 | 2.162 |
| 22:00-22:30 |  | 5/5 |  | 0.5642 | 0.5642 | 26 | 20 | 0.000 / 0.000 | 0.5642 / 0.5642 | 2.1285 | 2.128 |
| 22:30-23:00 |  | 5/5 |  | 0.5975 | 0.5975 | 21 | 30 | 0.000 / 0.000 | 0.5975 / 0.5975 | 2.1950 | 2.195 |
| 23:00-23:30 |  | 5/5 |  | 0.5842 | 0.5842 | 23 | 28 | 0.000 / 0.000 | 0.5842 / 0.5842 | 2.1685 | 2.168 |
| 23:30-00:00 |  | 5/5 |  | 0.5816 | 0.5816 | 21 | 31 | 0.000 / 0.000 | 0.5816 / 0.5816 | 2.1632 | 2.163 |
| 00:00-00:30 |  | 5/5 |  | 0.5735 | 0.5735 | 23 | 27 | 0.000 / 0.000 | 0.5735 / 0.5735 | 2.1470 | 2.147 |
| 00:30-01:00 |  | 5/5 |  | 0.5705 | 0.5705 | 24 | 28 | 0.000 / 0.000 | 0.5705 / 0.5705 | 2.1409 | 2.141 |
| 01:00-01:30 |  | 5/5 |  | 0.5882 | 0.5882 | 23 | 29 | 0.000 / 0.000 | 0.5882 / 0.5882 | 2.1764 | 2.176 |
| 01:30-02:00 |  | 5/5 |  | 0.6131 | 0.6131 | 26 | 30 | 0.000 / 0.000 | 0.6131 / 0.6131 | 2.2262 | 2.226 |
| 02:00-02:30 |  | 5/5 |  | 0.5755 | 0.5755 | 26 | 23 | 0.000 / 0.000 | 0.5755 / 0.5755 | 2.1510 | 2.151 |
| 02:30-03:00 |  | 5/5 |  | 0.5943 | 0.5943 | 26 | 28 | 0.000 / 0.000 | 0.5943 / 0.5943 | 2.1885 | 2.189 |
| 03:00-03:30 |  | 5/5 |  | 0.5898 | 0.5898 | 28 | 26 | 0.000 / 0.000 | 0.5898 / 0.5898 | 2.1795 | 2.180 |
| 03:30-04:00 |  | 5/5 |  | 0.5785 | 0.5785 | 26 | 25 | 0.000 / 0.000 | 0.5785 / 0.5785 | 2.1570 | 2.157 |
| 04:00-04:30 |  | 5/5 |  | 0.5896 | 0.5896 | 31 | 25 | 0.000 / 0.000 | 0.5896 / 0.5896 | 2.1792 | 2.179 |
| 04:30-05:00 |  | 5/5 |  | 0.5805 | 0.5805 | 31 | 22 | 0.000 / 0.000 | 0.5805 / 0.5805 | 2.1610 | 2.161 |
| 05:00-05:30 |  | 5/5 |  | 0.5899 | 0.5899 | 28 | 31 | 0.000 / 0.000 | 0.5899 / 0.5899 | 2.1799 | 2.180 |
| 05:30-06:00 |  | 5/5 |  | 0.5979 | 0.5979 | 27 | 29 | 0.000 / 0.000 | 0.5979 / 0.5979 | 2.1958 | 2.196 |
| 06:00-06:30 |  | 5/5 |  | 0.5808 | 0.5808 | 28 | 24 | 0.000 / 0.000 | 0.5808 / 0.5808 | 2.1616 | 2.162 |
| 06:30-07:00 |  | 5/5 |  | 0.5775 | 0.5775 | 27 | 29 | 0.000 / 0.000 | 0.5775 / 0.5775 | 2.1550 | 2.155 |
| 07:00-07:30 | D | 5/5 |  | 0.5957 | 0.5957 | 26 | 24 | 0.000 / 0.000 | 0.5957 / 0.5957 | 2.1914 | 2.191 |
| 07:30-08:00 | D | 5/5 |  | 0.5952 | 0.5952 | 24 | 21 | 0.000 / 0.000 | 0.5952 / 0.5952 | 2.1904 | 2.190 |
| 08:00-08:30 | D | 5/5 |  | 0.5845 | 0.5845 | 25 | 25 | 0.000 / 0.000 | 0.5845 / 0.5845 | 2.1690 | 2.169 |
| 08:30-09:00 | D | 5/5 |  | 0.5823 | 0.5823 | 25 | 23 | 0.000 / 0.000 | 0.5823 / 0.5823 | 2.1647 | 2.165 |
| 09:00-09:30 | D | 5/5 |  | 0.5838 | 0.5838 | 24 | 24 | 0.000 / 0.000 | 0.5838 / 0.5838 | 2.1675 | 2.168 |
| 09:30-10:00 | D | 5/5 |  | 0.5839 | 0.5839 | 24 | 24 | 0.000 / 0.000 | 0.5839 / 0.5839 | 2.1679 | 2.168 |
| 10:00-10:30 | D | 5/5 |  | 0.5777 | 0.5777 | 25 | 24 | 0.000 / 0.000 | 0.5777 / 0.5777 | 2.1554 | 2.155 |
| 10:30-11:00 | D | 5/5 |  | 0.5974 | 0.5974 | 24 | 24 | 0.000 / 0.000 | 0.5974 / 0.5974 | 2.1948 | 2.195 |
| 11:00-11:30 | D | 5/5 |  | 0.5890 | 0.5890 | 23 | 25 | 0.000 / 0.000 | 0.5890 / 0.5890 | 2.1780 | 2.178 |
| 11:30-12:00 | D | 5/5 |  | 0.5861 | 0.5861 | 22 | 26 | 0.000 / 0.000 | 0.5861 / 0.5861 | 2.1723 | 2.172 |
| 12:00-12:30 | D | 5/5 |  | 0.5778 | 0.5778 | 23 | 30 | 0.000 / 0.000 | 0.5778 / 0.5778 | 2.1557 | 2.156 |
| 12:30-13:00 | D | 5/5 |  | 0.5778 | 0.5778 | 26 | 36 | 0.000 / 0.000 | 0.5778 / 0.5778 | 2.1556 | 2.156 |
| 13:00-13:30 | D | 5/5 |  | 0.5888 | 0.5888 | 28 | 30 | 0.000 / 0.000 | 0.5888 / 0.5888 | 2.1776 | 2.178 |
| 13:30-14:00 | D | 5/5 |  | 0.5822 | 0.5822 | 31 | 28 | 0.000 / 0.000 | 0.5822 / 0.5822 | 2.1645 | 2.164 |
| 14:00-14:30 |  | 5/5 |  | 0.5736 | 0.5736 | 27 | 33 | 0.000 / 0.000 | 0.5736 / 0.5736 | 2.1471 | 2.147 |
| 14:30-15:00 |  | 5/5 |  | 0.5955 | 0.5955 | 31 | 31 | 0.000 / 0.000 | 0.5955 / 0.5955 | 2.1910 | 2.191 |
| 15:00-15:30 |  | 5/5 |  | 0.5620 | 0.5620 | 25 | 31 | 0.000 / 0.000 | 0.5620 / 0.5620 | 2.1239 | 2.124 |
| 15:30-16:00 |  | 5/5 |  | 0.6117 | 0.6117 | 28 | 31 | 0.000 / 0.000 | 0.6117 / 0.6117 | 2.2233 | 2.223 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/M6A_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 3b1a7bd5625d55f88e41bef2c29c2292bfa1f759e7332b60945a92e1c255cd91 (234,697 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6A_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 4878286d8a0f1bc6b127189ae1ff269b5c64b896e75c46087395feb522f19eb0 (99,098 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6A_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 82b70d60a74385262ca5029c239b2c3624a0cf37508e93e096e0f49812d34811 (87,885 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6A_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 6e9b9afa3be22b57ff1617a27364ad2bdb55d348730626d736be71855553f760 (270,103 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6A_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` fefbafa1d653934de580c35a46b14c1b695af7aac46d1f34ba541aa232f8385c (100,935 records)

### M6B (fx)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $0.625; commission $1.00 round turn = 1.6000 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 10; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 1.4869, sell 1.5869 ticks (round turn inside a window 4.6737 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.9869 | 0.9869 | 4 | 5 | 0.500 / 0.600 | 1.4869 / 1.5869 | 4.6737 | 2.921 |
| 17:30-18:00 |  | 5/5 |  | 0.7233 | 0.7233 | 9 | 6 | 0.400 / 0.100 | 1.1233 / 0.8233 | 3.5466 | 2.217 |
| 18:00-18:30 |  | 5/5 |  | 0.7424 | 0.7424 | 10 | 9 | 0.100 / 0.000 | 0.8424 / 0.7424 | 3.1849 | 1.991 |
| 18:30-19:00 |  | 5/5 |  | 0.7215 | 0.7215 | 9 | 9 | 0.100 / 0.100 | 0.8215 / 0.8215 | 3.2431 | 2.027 |
| 19:00-19:30 |  | 5/5 |  | 0.7407 | 0.7407 | 9 | 10 | 0.000 / 0.100 | 0.7407 / 0.8407 | 3.1815 | 1.988 |
| 19:30-20:00 |  | 5/5 |  | 0.7327 | 0.7327 | 12 | 6 | 0.400 / 0.000 | 1.1327 / 0.7327 | 3.4653 | 2.166 |
| 20:00-20:30 |  | 5/5 |  | 0.7054 | 0.7054 | 6 | 7 | 0.300 / 0.400 | 1.0054 / 1.1054 | 3.7109 | 2.319 |
| 20:30-21:00 |  | 5/5 |  | 0.6984 | 0.6984 | 10 | 8 | 0.200 / 0.000 | 0.8984 / 0.6984 | 3.1967 | 1.998 |
| 21:00-21:30 |  | 5/5 |  | 0.7071 | 0.7071 | 8 | 8 | 0.200 / 0.200 | 0.9071 / 0.9071 | 3.4143 | 2.134 |
| 21:30-22:00 |  | 5/5 |  | 0.6947 | 0.6947 | 6 | 10 | 0.000 / 0.400 | 0.6947 / 1.0947 | 3.3893 | 2.118 |
| 22:00-22:30 |  | 5/5 |  | 0.6916 | 0.6916 | 9 | 9 | 0.100 / 0.100 | 0.7916 / 0.7916 | 3.1831 | 1.989 |
| 22:30-23:00 |  | 5/5 |  | 0.6992 | 0.6992 | 6 | 11 | 0.000 / 0.400 | 0.6992 / 1.0992 | 3.3985 | 2.124 |
| 23:00-23:30 |  | 5/5 |  | 0.7031 | 0.7031 | 11 | 10 | 0.000 / 0.000 | 0.7031 / 0.7031 | 3.0063 | 1.879 |
| 23:30-00:00 |  | 5/5 |  | 0.7167 | 0.7167 | 13 | 7 | 0.300 / 0.000 | 1.0167 / 0.7167 | 3.3334 | 2.083 |
| 00:00-00:30 |  | 5/5 |  | 0.7035 | 0.7035 | 11 | 7 | 0.300 / 0.000 | 1.0035 / 0.7035 | 3.3070 | 2.067 |
| 00:30-01:00 |  | 5/5 |  | 0.7174 | 0.7174 | 8 | 11 | 0.000 / 0.200 | 0.7174 / 0.9174 | 3.2347 | 2.022 |
| 01:00-01:30 |  | 5/5 |  | 0.7311 | 0.7311 | 9 | 12 | 0.000 / 0.100 | 0.7311 / 0.8311 | 3.1621 | 1.976 |
| 01:30-02:00 |  | 5/5 |  | 0.7254 | 0.7254 | 10 | 9 | 0.100 / 0.000 | 0.8254 / 0.7254 | 3.1507 | 1.969 |
| 02:00-02:30 |  | 5/5 |  | 0.7077 | 0.7077 | 9 | 6 | 0.400 / 0.100 | 1.1077 / 0.8077 | 3.5155 | 2.197 |
| 02:30-03:00 |  | 5/5 |  | 0.7122 | 0.7122 | 10 | 7 | 0.300 / 0.000 | 1.0122 / 0.7122 | 3.3244 | 2.078 |
| 03:00-03:30 |  | 5/5 |  | 0.7316 | 0.7316 | 8 | 10 | 0.000 / 0.200 | 0.7316 / 0.9316 | 3.2633 | 2.040 |
| 03:30-04:00 |  | 5/5 |  | 0.7221 | 0.7221 | 10 | 8 | 0.200 / 0.000 | 0.9221 / 0.7221 | 3.2442 | 2.028 |
| 04:00-04:30 |  | 5/5 |  | 0.7371 | 0.7371 | 11 | 10 | 0.000 / 0.000 | 0.7371 / 0.7371 | 3.0742 | 1.921 |
| 04:30-05:00 |  | 5/5 |  | 0.7305 | 0.7305 | 10 | 10 | 0.000 / 0.000 | 0.7305 / 0.7305 | 3.0610 | 1.913 |
| 05:00-05:30 |  | 5/5 |  | 0.7533 | 0.7533 | 11 | 13 | 0.000 / 0.000 | 0.7533 / 0.7533 | 3.1066 | 1.942 |
| 05:30-06:00 |  | 5/5 |  | 0.7472 | 0.7472 | 11 | 7 | 0.300 / 0.000 | 1.0472 / 0.7472 | 3.3944 | 2.121 |
| 06:00-06:30 |  | 5/5 |  | 0.7207 | 0.7207 | 7 | 10 | 0.000 / 0.300 | 0.7207 / 1.0207 | 3.3414 | 2.088 |
| 06:30-07:00 |  | 5/5 |  | 0.7134 | 0.7134 | 6 | 9 | 0.100 / 0.400 | 0.8134 / 1.1134 | 3.5268 | 2.204 |
| 07:00-07:30 | D | 5/5 |  | 0.8466 | 0.8466 | 8 | 10 | 0.000 / 0.200 | 0.8466 / 1.0466 | 3.4932 | 2.183 |
| 07:30-08:00 | D | 5/5 |  | 0.8600 | 0.8600 | 6 | 10 | 0.000 / 0.400 | 0.8600 / 1.2600 | 3.7201 | 2.325 |
| 08:00-08:30 | D | 5/5 |  | 0.7569 | 0.7569 | 7 | 12 | 0.000 / 0.300 | 0.7569 / 1.0569 | 3.4138 | 2.134 |
| 08:30-09:00 | D | 5/5 |  | 0.7493 | 0.7493 | 7 | 11 | 0.000 / 0.300 | 0.7493 / 1.0493 | 3.3986 | 2.124 |
| 09:00-09:30 | D | 5/5 |  | 0.7397 | 0.7397 | 11 | 10 | 0.000 / 0.000 | 0.7397 / 0.7397 | 3.0793 | 1.925 |
| 09:30-10:00 | D | 5/5 |  | 0.7359 | 0.7359 | 9 | 11 | 0.000 / 0.100 | 0.7359 / 0.8359 | 3.1718 | 1.982 |
| 10:00-10:30 | D | 5/5 |  | 0.7470 | 0.7470 | 11 | 11 | 0.000 / 0.000 | 0.7470 / 0.7470 | 3.0940 | 1.934 |
| 10:30-11:00 | D | 5/5 |  | 0.7416 | 0.7416 | 7 | 10 | 0.000 / 0.300 | 0.7416 / 1.0416 | 3.3831 | 2.114 |
| 11:00-11:30 | D | 5/5 |  | 0.7417 | 0.7417 | 11 | 6 | 0.400 / 0.000 | 1.1417 / 0.7417 | 3.4834 | 2.177 |
| 11:30-12:00 | D | 5/5 |  | 0.7467 | 0.7467 | 12 | 6 | 0.400 / 0.000 | 1.1467 / 0.7467 | 3.4933 | 2.183 |
| 12:00-12:30 | D | 5/5 |  | 0.7480 | 0.7480 | 6 | 13 | 0.000 / 0.400 | 0.7480 / 1.1480 | 3.4961 | 2.185 |
| 12:30-13:00 | D | 5/5 |  | 0.7272 | 0.7272 | 8 | 12 | 0.000 / 0.200 | 0.7272 / 0.9272 | 3.2544 | 2.034 |
| 13:00-13:30 | D | 5/5 |  | 0.7600 | 0.7600 | 12 | 12 | 0.000 / 0.000 | 0.7600 / 0.7600 | 3.1200 | 1.950 |
| 13:30-14:00 | D | 5/5 |  | 0.7247 | 0.7247 | 9 | 8 | 0.200 / 0.100 | 0.9247 / 0.8247 | 3.3494 | 2.093 |
| 14:00-14:30 |  | 5/5 |  | 0.7331 | 0.7331 | 11 | 7 | 0.300 / 0.000 | 1.0331 / 0.7331 | 3.3662 | 2.104 |
| 14:30-15:00 |  | 5/5 |  | 0.7231 | 0.7231 | 11 | 10 | 0.000 / 0.000 | 0.7231 / 0.7231 | 3.0462 | 1.904 |
| 15:00-15:30 |  | 5/5 |  | 0.6942 | 0.6942 | 9 | 7 | 0.300 / 0.100 | 0.9942 / 0.7942 | 3.3883 | 2.118 |
| 15:30-16:00 |  | 5/5 |  | 0.7347 | 0.7347 | 6 | 7 | 0.300 / 0.400 | 1.0347 / 1.1347 | 3.7695 | 2.356 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/M6B_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 25b06af140c6aac079fa30f266613a999642ab0d850122e446bb858401bcff80 (198,455 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6B_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 0beed422afa8a74c38f411dc9746620490c297f8ca64706c765bb0392f258cc1 (95,240 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6B_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` b798a114eb98d176aee9b5b1c51310fdaecb97200225e69955fcd2d7e0d0736b (99,793 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6B_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 7764e9437c5b7a7944cdc1998aa489f5c12c5c89e26261e0a06036a7eeb89918 (225,821 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6B_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 5ea365a365d98fbbaca4cd9271edb7679a2d10767f8cf90a7abbbc2fd209e040 (145,066 records)

### M6E (fx)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $1.25; commission $1.00 round turn = 0.8000 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 10; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.6090, sell 0.6090 ticks (round turn inside a window 2.0179 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.6066 | 0.6066 | 13 | 16 | 0.000 / 0.000 | 0.6066 / 0.6066 | 2.0131 | 2.516 |
| 17:30-18:00 |  | 5/5 |  | 0.5777 | 0.5777 | 25 | 28 | 0.000 / 0.000 | 0.5777 / 0.5777 | 1.9554 | 2.444 |
| 18:00-18:30 |  | 5/5 |  | 0.5576 | 0.5576 | 28 | 27 | 0.000 / 0.000 | 0.5576 / 0.5576 | 1.9151 | 2.394 |
| 18:30-19:00 |  | 5/5 |  | 0.5693 | 0.5693 | 28 | 26 | 0.000 / 0.000 | 0.5693 / 0.5693 | 1.9386 | 2.423 |
| 19:00-19:30 |  | 5/5 |  | 0.5746 | 0.5746 | 26 | 29 | 0.000 / 0.000 | 0.5746 / 0.5746 | 1.9492 | 2.437 |
| 19:30-20:00 |  | 5/5 |  | 0.5846 | 0.5846 | 29 | 28 | 0.000 / 0.000 | 0.5846 / 0.5846 | 1.9693 | 2.462 |
| 20:00-20:30 |  | 5/5 |  | 0.5848 | 0.5848 | 28 | 32 | 0.000 / 0.000 | 0.5848 / 0.5848 | 1.9696 | 2.462 |
| 20:30-21:00 |  | 5/5 |  | 0.5758 | 0.5758 | 28 | 27 | 0.000 / 0.000 | 0.5758 / 0.5758 | 1.9515 | 2.439 |
| 21:00-21:30 |  | 5/5 |  | 0.5693 | 0.5693 | 29 | 30 | 0.000 / 0.000 | 0.5693 / 0.5693 | 1.9387 | 2.423 |
| 21:30-22:00 |  | 5/5 |  | 0.5818 | 0.5818 | 30 | 30 | 0.000 / 0.000 | 0.5818 / 0.5818 | 1.9636 | 2.454 |
| 22:00-22:30 |  | 5/5 |  | 0.5608 | 0.5608 | 29 | 30 | 0.000 / 0.000 | 0.5608 / 0.5608 | 1.9215 | 2.402 |
| 22:30-23:00 |  | 5/5 |  | 0.5595 | 0.5595 | 26 | 31 | 0.000 / 0.000 | 0.5595 / 0.5595 | 1.9189 | 2.399 |
| 23:00-23:30 |  | 5/5 |  | 0.5853 | 0.5853 | 30 | 16 | 0.000 / 0.000 | 0.5853 / 0.5853 | 1.9706 | 2.463 |
| 23:30-00:00 |  | 5/5 |  | 0.5925 | 0.5925 | 30 | 23 | 0.000 / 0.000 | 0.5925 / 0.5925 | 1.9849 | 2.481 |
| 00:00-00:30 |  | 5/5 |  | 0.5851 | 0.5851 | 31 | 22 | 0.000 / 0.000 | 0.5851 / 0.5851 | 1.9701 | 2.463 |
| 00:30-01:00 |  | 5/5 |  | 0.5776 | 0.5776 | 29 | 26 | 0.000 / 0.000 | 0.5776 / 0.5776 | 1.9552 | 2.444 |
| 01:00-01:30 |  | 5/5 |  | 0.5641 | 0.5641 | 28 | 26 | 0.000 / 0.000 | 0.5641 / 0.5641 | 1.9282 | 2.410 |
| 01:30-02:00 |  | 5/5 |  | 0.5569 | 0.5569 | 32 | 23 | 0.000 / 0.000 | 0.5569 / 0.5569 | 1.9138 | 2.392 |
| 02:00-02:30 |  | 5/5 |  | 0.5626 | 0.5626 | 27 | 25 | 0.000 / 0.000 | 0.5626 / 0.5626 | 1.9251 | 2.406 |
| 02:30-03:00 |  | 5/5 |  | 0.5744 | 0.5744 | 33 | 28 | 0.000 / 0.000 | 0.5744 / 0.5744 | 1.9487 | 2.436 |
| 03:00-03:30 |  | 5/5 |  | 0.5744 | 0.5744 | 31 | 28 | 0.000 / 0.000 | 0.5744 / 0.5744 | 1.9487 | 2.436 |
| 03:30-04:00 |  | 5/5 |  | 0.5558 | 0.5558 | 26 | 28 | 0.000 / 0.000 | 0.5558 / 0.5558 | 1.9116 | 2.390 |
| 04:00-04:30 |  | 5/5 |  | 0.5640 | 0.5640 | 26 | 33 | 0.000 / 0.000 | 0.5640 / 0.5640 | 1.9281 | 2.410 |
| 04:30-05:00 |  | 5/5 |  | 0.5705 | 0.5705 | 29 | 32 | 0.000 / 0.000 | 0.5705 / 0.5705 | 1.9409 | 2.426 |
| 05:00-05:30 |  | 5/5 |  | 0.5607 | 0.5607 | 33 | 31 | 0.000 / 0.000 | 0.5607 / 0.5607 | 1.9214 | 2.402 |
| 05:30-06:00 |  | 5/5 |  | 0.5619 | 0.5619 | 32 | 27 | 0.000 / 0.000 | 0.5619 / 0.5619 | 1.9238 | 2.405 |
| 06:00-06:30 |  | 5/5 |  | 0.5578 | 0.5578 | 30 | 33 | 0.000 / 0.000 | 0.5578 / 0.5578 | 1.9156 | 2.394 |
| 06:30-07:00 |  | 5/5 |  | 0.5679 | 0.5679 | 32 | 29 | 0.000 / 0.000 | 0.5679 / 0.5679 | 1.9358 | 2.420 |
| 07:00-07:30 | D | 5/5 |  | 0.5643 | 0.5643 | 28 | 30 | 0.000 / 0.000 | 0.5643 / 0.5643 | 1.9286 | 2.411 |
| 07:30-08:00 | D | 5/5 |  | 0.5807 | 0.5807 | 20 | 21 | 0.000 / 0.000 | 0.5807 / 0.5807 | 1.9615 | 2.452 |
| 08:00-08:30 | D | 5/5 |  | 0.5570 | 0.5570 | 28 | 25 | 0.000 / 0.000 | 0.5570 / 0.5570 | 1.9139 | 2.392 |
| 08:30-09:00 | D | 5/5 |  | 0.5625 | 0.5625 | 33 | 24 | 0.000 / 0.000 | 0.5625 / 0.5625 | 1.9249 | 2.406 |
| 09:00-09:30 | D | 5/5 |  | 0.5623 | 0.5623 | 30 | 29 | 0.000 / 0.000 | 0.5623 / 0.5623 | 1.9247 | 2.406 |
| 09:30-10:00 | D | 5/5 |  | 0.5532 | 0.5532 | 32 | 29 | 0.000 / 0.000 | 0.5532 / 0.5532 | 1.9064 | 2.383 |
| 10:00-10:30 | D | 5/5 |  | 0.5664 | 0.5664 | 34 | 33 | 0.000 / 0.000 | 0.5664 / 0.5664 | 1.9329 | 2.416 |
| 10:30-11:00 | D | 5/5 |  | 0.5534 | 0.5534 | 39 | 27 | 0.000 / 0.000 | 0.5534 / 0.5534 | 1.9069 | 2.384 |
| 11:00-11:30 | D | 5/5 |  | 0.5614 | 0.5614 | 30 | 29 | 0.000 / 0.000 | 0.5614 / 0.5614 | 1.9228 | 2.403 |
| 11:30-12:00 | D | 5/5 |  | 0.5681 | 0.5681 | 35 | 32 | 0.000 / 0.000 | 0.5681 / 0.5681 | 1.9363 | 2.420 |
| 12:00-12:30 | D | 5/5 |  | 0.5574 | 0.5574 | 28 | 36 | 0.000 / 0.000 | 0.5574 / 0.5574 | 1.9148 | 2.393 |
| 12:30-13:00 | D | 5/5 |  | 0.5589 | 0.5589 | 32 | 29 | 0.000 / 0.000 | 0.5589 / 0.5589 | 1.9177 | 2.397 |
| 13:00-13:30 | D | 5/5 |  | 0.5606 | 0.5606 | 30 | 35 | 0.000 / 0.000 | 0.5606 / 0.5606 | 1.9212 | 2.402 |
| 13:30-14:00 | D | 5/5 |  | 0.5475 | 0.5475 | 29 | 33 | 0.000 / 0.000 | 0.5475 / 0.5475 | 1.8950 | 2.369 |
| 14:00-14:30 |  | 5/5 |  | 0.5545 | 0.5545 | 41 | 39 | 0.000 / 0.000 | 0.5545 / 0.5545 | 1.9090 | 2.386 |
| 14:30-15:00 |  | 5/5 |  | 0.5723 | 0.5723 | 41 | 39 | 0.000 / 0.000 | 0.5723 / 0.5723 | 1.9445 | 2.431 |
| 15:00-15:30 |  | 5/5 |  | 0.5747 | 0.5747 | 37 | 34 | 0.000 / 0.000 | 0.5747 / 0.5747 | 1.9494 | 2.437 |
| 15:30-16:00 |  | 5/5 |  | 0.6090 | 0.6090 | 26 | 19 | 0.000 / 0.000 | 0.6090 / 0.6090 | 2.0179 | 2.522 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/M6E_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 7314361a013473a302a8816f6778105f387c02ab560c15e962f337e6252e8f92 (714,191 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6E_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` db4304781e38c38dce797daf064af17dae93d6ef50df9bed1e417378be826c3f (306,371 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6E_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 1ac7dbb28e725bcea5f62cc52b5613755c350df0f5cb64d34a2180fa6add902e (218,588 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6E_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 4c176e7d41caaa91a010a34b5a641ebab10028a74cbd1d6fefd03ab0fd8b417b (515,783 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/M6E_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` af943e0924d2683e82eea14246c05203f8fcb08529bea344d74530ef362abaa9 (156,164 records)

### MBT (crypto)

Tick 5.00 (vendor units 5.00, factor 1), tick value $0.5; commission $2.82 round turn = 5.6400 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 2.6132, sell 2.6132 ticks (round turn inside a window 10.8664 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 2.6132 | 2.6132 | 2 | 2 | 0.000 / 0.000 | 2.6132 / 2.6132 | 10.8664 | 5.433 |
| 17:30-18:00 |  | 5/5 |  | 2.2323 | 2.2323 | 2 | 2 | 0.000 / 0.000 | 2.2323 / 2.2323 | 10.1046 | 5.052 |
| 18:00-18:30 |  | 5/5 |  | 2.0988 | 2.0988 | 2 | 2 | 0.000 / 0.000 | 2.0988 / 2.0988 | 9.8375 | 4.919 |
| 18:30-19:00 |  | 5/5 |  | 1.8887 | 1.8887 | 2 | 2 | 0.000 / 0.000 | 1.8887 / 1.8887 | 9.4174 | 4.709 |
| 19:00-19:30 |  | 5/5 |  | 1.8893 | 1.8893 | 2 | 2 | 0.000 / 0.000 | 1.8893 / 1.8893 | 9.4187 | 4.709 |
| 19:30-20:00 |  | 5/5 |  | 1.9336 | 1.9336 | 2 | 2 | 0.000 / 0.000 | 1.9336 / 1.9336 | 9.5073 | 4.754 |
| 20:00-20:30 |  | 5/5 |  | 1.9356 | 1.9356 | 2 | 2 | 0.000 / 0.000 | 1.9356 / 1.9356 | 9.5113 | 4.756 |
| 20:30-21:00 |  | 5/5 |  | 1.8229 | 1.8229 | 2 | 2 | 0.000 / 0.000 | 1.8229 / 1.8229 | 9.2858 | 4.643 |
| 21:00-21:30 |  | 5/5 |  | 1.8394 | 1.8394 | 2 | 2 | 0.000 / 0.000 | 1.8394 / 1.8394 | 9.3188 | 4.659 |
| 21:30-22:00 |  | 5/5 |  | 1.8252 | 1.8252 | 2 | 2 | 0.000 / 0.000 | 1.8252 / 1.8252 | 9.2904 | 4.645 |
| 22:00-22:30 |  | 5/5 |  | 1.8676 | 1.8676 | 2 | 2 | 0.000 / 0.000 | 1.8676 / 1.8676 | 9.3753 | 4.688 |
| 22:30-23:00 |  | 5/5 |  | 1.8957 | 1.8957 | 2 | 2 | 0.000 / 0.000 | 1.8957 / 1.8957 | 9.4314 | 4.716 |
| 23:00-23:30 |  | 5/5 |  | 1.8710 | 1.8710 | 2 | 2 | 0.000 / 0.000 | 1.8710 / 1.8710 | 9.3820 | 4.691 |
| 23:30-00:00 |  | 5/5 |  | 1.8573 | 1.8573 | 2 | 2 | 0.000 / 0.000 | 1.8573 / 1.8573 | 9.3545 | 4.677 |
| 00:00-00:30 |  | 5/5 |  | 1.7815 | 1.7815 | 2 | 2 | 0.000 / 0.000 | 1.7815 / 1.7815 | 9.2030 | 4.601 |
| 00:30-01:00 |  | 5/5 |  | 1.9332 | 1.9332 | 2 | 2 | 0.000 / 0.000 | 1.9332 / 1.9332 | 9.5063 | 4.753 |
| 01:00-01:30 |  | 5/5 |  | 1.8704 | 1.8704 | 2 | 2 | 0.000 / 0.000 | 1.8704 / 1.8704 | 9.3807 | 4.690 |
| 01:30-02:00 |  | 5/5 |  | 1.8166 | 1.8166 | 2 | 2 | 0.000 / 0.000 | 1.8166 / 1.8166 | 9.2731 | 4.637 |
| 02:00-02:30 |  | 5/5 |  | 1.7968 | 1.7968 | 2 | 2 | 0.000 / 0.000 | 1.7968 / 1.7968 | 9.2336 | 4.617 |
| 02:30-03:00 |  | 5/5 |  | 1.7358 | 1.7358 | 2 | 2 | 0.000 / 0.000 | 1.7358 / 1.7358 | 9.1116 | 4.556 |
| 03:00-03:30 |  | 5/5 |  | 1.8466 | 1.8466 | 2 | 2 | 0.000 / 0.000 | 1.8466 / 1.8466 | 9.3333 | 4.667 |
| 03:30-04:00 |  | 5/5 |  | 1.8674 | 1.8674 | 2 | 2 | 0.000 / 0.000 | 1.8674 / 1.8674 | 9.3747 | 4.687 |
| 04:00-04:30 |  | 5/5 |  | 1.8556 | 1.8556 | 2 | 2 | 0.000 / 0.000 | 1.8556 / 1.8556 | 9.3512 | 4.676 |
| 04:30-05:00 |  | 5/5 |  | 1.8487 | 1.8487 | 2 | 2 | 0.000 / 0.000 | 1.8487 / 1.8487 | 9.3374 | 4.669 |
| 05:00-05:30 |  | 5/5 |  | 1.9296 | 1.9296 | 2 | 2 | 0.000 / 0.000 | 1.9296 / 1.9296 | 9.4991 | 4.750 |
| 05:30-06:00 |  | 5/5 |  | 1.9198 | 1.9198 | 2 | 2 | 0.000 / 0.000 | 1.9198 / 1.9198 | 9.4796 | 4.740 |
| 06:00-06:30 |  | 5/5 |  | 1.7706 | 1.7706 | 2 | 2 | 0.000 / 0.000 | 1.7706 / 1.7706 | 9.1813 | 4.591 |
| 06:30-07:00 |  | 5/5 |  | 1.7521 | 1.7521 | 2 | 2 | 0.000 / 0.000 | 1.7521 / 1.7521 | 9.1442 | 4.572 |
| 07:00-07:30 |  | 5/5 |  | 1.7294 | 1.7294 | 2 | 2 | 0.000 / 0.000 | 1.7294 / 1.7294 | 9.0987 | 4.549 |
| 07:30-08:00 |  | 5/5 |  | 1.7037 | 1.7037 | 2 | 2 | 0.000 / 0.000 | 1.7037 / 1.7037 | 9.0475 | 4.524 |
| 08:00-08:30 |  | 5/5 |  | 1.6456 | 1.6456 | 2 | 2 | 0.000 / 0.000 | 1.6456 / 1.6456 | 8.9312 | 4.466 |
| 08:30-09:00 | D | 5/5 |  | 1.6106 | 1.6106 | 2 | 2 | 0.000 / 0.000 | 1.6106 / 1.6106 | 8.8612 | 4.431 |
| 09:00-09:30 | D | 5/5 |  | 1.6849 | 1.6849 | 2 | 2 | 0.000 / 0.000 | 1.6849 / 1.6849 | 9.0097 | 4.505 |
| 09:30-10:00 | D | 5/5 |  | 1.6098 | 1.6098 | 2 | 2 | 0.000 / 0.000 | 1.6098 / 1.6098 | 8.8595 | 4.430 |
| 10:00-10:30 | D | 5/5 |  | 1.6834 | 1.6834 | 2 | 2 | 0.000 / 0.000 | 1.6834 / 1.6834 | 9.0068 | 4.503 |
| 10:30-11:00 | D | 5/5 |  | 1.5869 | 1.5869 | 2 | 2 | 0.000 / 0.000 | 1.5869 / 1.5869 | 8.8139 | 4.407 |
| 11:00-11:30 | D | 5/5 |  | 1.6497 | 1.6497 | 2 | 2 | 0.000 / 0.000 | 1.6497 / 1.6497 | 8.9394 | 4.470 |
| 11:30-12:00 | D | 5/5 |  | 1.6706 | 1.6706 | 2 | 2 | 0.000 / 0.000 | 1.6706 / 1.6706 | 8.9813 | 4.491 |
| 12:00-12:30 | D | 5/5 |  | 1.6299 | 1.6299 | 2 | 2 | 0.000 / 0.000 | 1.6299 / 1.6299 | 8.8998 | 4.450 |
| 12:30-13:00 | D | 5/5 |  | 1.5786 | 1.5786 | 2 | 2 | 0.000 / 0.000 | 1.5786 / 1.5786 | 8.7972 | 4.399 |
| 13:00-13:30 | D | 5/5 |  | 1.5684 | 1.5684 | 2 | 2 | 0.000 / 0.000 | 1.5684 / 1.5684 | 8.7768 | 4.388 |
| 13:30-14:00 | D | 5/5 |  | 1.5967 | 1.5967 | 2 | 2 | 0.000 / 0.000 | 1.5967 / 1.5967 | 8.8333 | 4.417 |
| 14:00-14:30 | D | 5/5 |  | 1.5124 | 1.5124 | 2 | 2 | 0.000 / 0.000 | 1.5124 / 1.5124 | 8.6648 | 4.332 |
| 14:30-15:00 | D | 5/5 |  | 1.4571 | 1.4571 | 2 | 2 | 0.000 / 0.000 | 1.4571 / 1.4571 | 8.5542 | 4.277 |
| 15:00-15:30 |  | 5/5 |  | 1.9961 | 1.9961 | 2 | 2 | 0.000 / 0.000 | 1.9961 / 1.9961 | 9.6322 | 4.816 |
| 15:30-16:00 |  | 5/5 |  | 2.3103 | 2.3103 | 3 | 3 | 0.000 / 0.000 | 2.3103 / 2.3103 | 10.2606 | 5.130 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MBT_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` bcd93e7410876a87a815273802a96447f1c5fd68396cea3ad84879f3e81a51a2 (997,761 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MBT_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` f821f81388b77c511b4ed45e28af69eee5c66fad6a15d8ab91f19d66adb18178 (1,429,039 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MBT_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` e0b16e9cf82a462323e0475055f1effa2755fccee212659822be85aff2ef6671 (1,577,435 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MBT_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 7b0272564975db15cf019759d26d0a04e7c94b110423b73e4ef8e546a1f567bf (3,580,827 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MBT_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` a43cc8418081eb5de02379538d7ca4ce575271112a492a6c6e11258866fd9b24 (1,386,221 records)

### MCL (energy)

Tick 0.01 (vendor units 0.01, factor 1), tick value $1.0; commission $1.72 round turn = 1.7200 ticks (reports/stage_e0_topstep_facts.json F3.7 + F3.6 (+$0.20 round turn from the 2026-10-01 trading day, applied now per D8)); q_c 4; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 1.3132, sell 1.3132 ticks (round turn inside a window 4.3465 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.0632 | 1.0632 | 3 | 3 | 0.250 / 0.250 | 1.3132 / 1.3132 | 4.3465 | 4.346 |
| 17:30-18:00 |  | 5/5 |  | 0.8985 | 0.8985 | 3 | 3 | 0.250 / 0.250 | 1.1485 / 1.1485 | 4.0169 | 4.017 |
| 18:00-18:30 |  | 5/5 |  | 0.8321 | 0.8321 | 3 | 3 | 0.250 / 0.250 | 1.0821 / 1.0821 | 3.8842 | 3.884 |
| 18:30-19:00 |  | 5/5 |  | 1.0524 | 1.0544 | 4 | 3 | 0.250 / 0.000 | 1.3024 / 1.0524 | 4.0748 | 4.075 |
| 19:00-19:30 |  | 5/5 |  | 0.8234 | 0.8234 | 5 | 5 | 0.000 / 0.000 | 0.8234 / 0.8234 | 3.3668 | 3.367 |
| 19:30-20:00 |  | 5/5 |  | 0.7049 | 0.7049 | 6 | 5 | 0.000 / 0.000 | 0.7049 / 0.7049 | 3.1299 | 3.130 |
| 20:00-20:30 |  | 5/5 |  | 0.7260 | 0.7260 | 6 | 5 | 0.000 / 0.000 | 0.7260 / 0.7260 | 3.1719 | 3.172 |
| 20:30-21:00 |  | 5/5 |  | 0.7261 | 0.7261 | 6 | 6 | 0.000 / 0.000 | 0.7261 / 0.7261 | 3.1722 | 3.172 |
| 21:00-21:30 |  | 5/5 |  | 0.7441 | 0.7441 | 6 | 6 | 0.000 / 0.000 | 0.7441 / 0.7441 | 3.2083 | 3.208 |
| 21:30-22:00 |  | 5/5 |  | 0.6830 | 0.6830 | 6 | 6 | 0.000 / 0.000 | 0.6830 / 0.6830 | 3.0861 | 3.086 |
| 22:00-22:30 |  | 5/5 |  | 0.6797 | 0.6797 | 6 | 6 | 0.000 / 0.000 | 0.6797 / 0.6797 | 3.0793 | 3.079 |
| 22:30-23:00 |  | 5/5 |  | 0.6824 | 0.6824 | 6 | 6 | 0.000 / 0.000 | 0.6824 / 0.6824 | 3.0847 | 3.085 |
| 23:00-23:30 |  | 5/5 |  | 0.6863 | 0.6863 | 6 | 5 | 0.000 / 0.000 | 0.6863 / 0.6863 | 3.0927 | 3.093 |
| 23:30-00:00 |  | 5/5 |  | 0.7094 | 0.7094 | 6 | 5 | 0.000 / 0.000 | 0.7094 / 0.7094 | 3.1387 | 3.139 |
| 00:00-00:30 |  | 5/5 |  | 0.7233 | 0.7233 | 6 | 6 | 0.000 / 0.000 | 0.7233 / 0.7233 | 3.1665 | 3.167 |
| 00:30-01:00 |  | 5/5 |  | 0.7460 | 0.7460 | 6 | 6 | 0.000 / 0.000 | 0.7460 / 0.7460 | 3.2121 | 3.212 |
| 01:00-01:30 |  | 5/5 |  | 0.7255 | 0.7255 | 5 | 5 | 0.000 / 0.000 | 0.7255 / 0.7255 | 3.1711 | 3.171 |
| 01:30-02:00 |  | 5/5 |  | 0.7200 | 0.7200 | 5 | 5 | 0.000 / 0.000 | 0.7200 / 0.7200 | 3.1600 | 3.160 |
| 02:00-02:30 |  | 5/5 |  | 0.7424 | 0.7424 | 4 | 4 | 0.000 / 0.000 | 0.7424 / 0.7424 | 3.2048 | 3.205 |
| 02:30-03:00 |  | 5/5 |  | 0.7432 | 0.7432 | 4 | 4 | 0.000 / 0.000 | 0.7432 / 0.7432 | 3.2064 | 3.206 |
| 03:00-03:30 |  | 5/5 |  | 0.7273 | 0.7273 | 4 | 4 | 0.000 / 0.000 | 0.7273 / 0.7273 | 3.1745 | 3.175 |
| 03:30-04:00 |  | 5/5 |  | 0.7333 | 0.7333 | 5 | 4 | 0.000 / 0.000 | 0.7333 / 0.7333 | 3.1867 | 3.187 |
| 04:00-04:30 |  | 5/5 |  | 0.7409 | 0.7409 | 5 | 4 | 0.000 / 0.000 | 0.7409 / 0.7409 | 3.2019 | 3.202 |
| 04:30-05:00 |  | 5/5 |  | 0.7220 | 0.7220 | 5 | 4 | 0.000 / 0.000 | 0.7220 / 0.7220 | 3.1639 | 3.164 |
| 05:00-05:30 |  | 5/5 |  | 0.7174 | 0.7174 | 5 | 5 | 0.000 / 0.000 | 0.7174 / 0.7174 | 3.1548 | 3.155 |
| 05:30-06:00 |  | 5/5 |  | 0.7272 | 0.7272 | 5 | 5 | 0.000 / 0.000 | 0.7272 / 0.7272 | 3.1744 | 3.174 |
| 06:00-06:30 |  | 5/5 |  | 0.7585 | 0.7585 | 5 | 5 | 0.000 / 0.000 | 0.7585 / 0.7585 | 3.2369 | 3.237 |
| 06:30-07:00 |  | 5/5 |  | 0.7568 | 0.7568 | 5 | 4 | 0.000 / 0.000 | 0.7568 / 0.7568 | 3.2336 | 3.234 |
| 07:00-07:30 |  | 5/5 |  | 0.7570 | 0.7570 | 5 | 6 | 0.000 / 0.000 | 0.7570 / 0.7570 | 3.2340 | 3.234 |
| 07:30-08:00 |  | 5/5 |  | 0.7513 | 0.7513 | 6 | 6 | 0.000 / 0.000 | 0.7513 / 0.7513 | 3.2226 | 3.223 |
| 08:00-08:30 | D | 5/5 |  | 0.7164 | 0.7164 | 6 | 6 | 0.000 / 0.000 | 0.7164 / 0.7164 | 3.1527 | 3.153 |
| 08:30-09:00 | D | 5/5 |  | 0.7280 | 0.7280 | 6 | 6 | 0.000 / 0.000 | 0.7280 / 0.7280 | 3.1760 | 3.176 |
| 09:00-09:30 | D | 5/5 |  | 0.7511 | 0.7511 | 6 | 7 | 0.000 / 0.000 | 0.7511 / 0.7511 | 3.2222 | 3.222 |
| 09:30-10:00 | D | 5/5 |  | 0.7415 | 0.7415 | 6 | 6 | 0.000 / 0.000 | 0.7415 / 0.7415 | 3.2030 | 3.203 |
| 10:00-10:30 | D | 5/5 |  | 0.7233 | 0.7233 | 6 | 6 | 0.000 / 0.000 | 0.7233 / 0.7233 | 3.1665 | 3.167 |
| 10:30-11:00 | D | 5/5 |  | 0.7140 | 0.7140 | 7 | 6 | 0.000 / 0.000 | 0.7140 / 0.7140 | 3.1480 | 3.148 |
| 11:00-11:30 | D | 5/5 |  | 0.7265 | 0.7265 | 6 | 6 | 0.000 / 0.000 | 0.7265 / 0.7265 | 3.1730 | 3.173 |
| 11:30-12:00 | D | 5/5 |  | 0.7116 | 0.7116 | 6 | 6 | 0.000 / 0.000 | 0.7116 / 0.7116 | 3.1431 | 3.143 |
| 12:00-12:30 | D | 5/5 |  | 0.7265 | 0.7265 | 6 | 7 | 0.000 / 0.000 | 0.7265 / 0.7265 | 3.1731 | 3.173 |
| 12:30-13:00 | D | 5/5 |  | 0.7011 | 0.7011 | 6 | 7 | 0.000 / 0.000 | 0.7011 / 0.7011 | 3.1221 | 3.122 |
| 13:00-13:30 | D | 5/5 |  | 0.7183 | 0.7183 | 6 | 6 | 0.000 / 0.000 | 0.7183 / 0.7183 | 3.1566 | 3.157 |
| 13:30-14:00 |  | 5/5 |  | 0.7129 | 0.7129 | 6 | 6 | 0.000 / 0.000 | 0.7129 / 0.7129 | 3.1457 | 3.146 |
| 14:00-14:30 |  | 5/5 |  | 0.7205 | 0.7205 | 6 | 6 | 0.000 / 0.000 | 0.7205 / 0.7205 | 3.1609 | 3.161 |
| 14:30-15:00 |  | 5/5 |  | 0.7061 | 0.7061 | 6 | 6 | 0.000 / 0.000 | 0.7061 / 0.7061 | 3.1322 | 3.132 |
| 15:00-15:30 |  | 5/5 |  | 0.7249 | 0.7249 | 6 | 6 | 0.000 / 0.000 | 0.7249 / 0.7249 | 3.1697 | 3.170 |
| 15:30-16:00 |  | 5/5 |  | 0.7669 | 0.7669 | 5 | 5 | 0.000 / 0.000 | 0.7669 / 0.7669 | 3.2538 | 3.254 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MCL_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 6efdaf28b414146c93b4173de4bc3b814ab9243ca3665e862c277fd65641367c (583,992 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MCL_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 8f19bd579c4381222217ee8d47fb0ae32960c435458b94153fa23da92c009b02 (534,841 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MCL_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 60685c3135cad4c217cfb2665d1396869ddd99c90a38809126103eec661c71e8 (562,262 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MCL_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 06431b745c6b67d5517b9ef502ec021f7d63e103fa81b18e7c23a57008c2a219 (818,238 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MCL_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 1acef72132b5776228270d893664b295132654616ca7b2306f3d1f0b97d24f99 (2,308,208 records)

### MGC (metals)

Tick 0.10 (vendor units 0.10, factor 1), tick value $1.0; commission $1.92 round turn = 1.9200 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-12:30 CT.

Event-window one-side slippage: buy 1.8385, sell 1.8385 ticks (round turn inside a window 5.5969 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.8385 | 1.8385 | 2 | 2 | 0.000 / 0.000 | 1.8385 / 1.8385 | 5.5969 | 5.597 |
| 17:30-18:00 |  | 5/5 |  | 1.2769 | 1.2769 | 2 | 2 | 0.000 / 0.000 | 1.2769 / 1.2769 | 4.4738 | 4.474 |
| 18:00-18:30 |  | 5/5 |  | 1.2552 | 1.2552 | 2 | 3 | 0.000 / 0.000 | 1.2552 / 1.2552 | 4.4303 | 4.430 |
| 18:30-19:00 |  | 5/5 |  | 1.2437 | 1.2437 | 2 | 3 | 0.000 / 0.000 | 1.2437 / 1.2437 | 4.4073 | 4.407 |
| 19:00-19:30 |  | 5/5 |  | 1.2124 | 1.2124 | 3 | 3 | 0.000 / 0.000 | 1.2124 / 1.2124 | 4.3449 | 4.345 |
| 19:30-20:00 |  | 5/5 |  | 1.1368 | 1.1368 | 3 | 3 | 0.000 / 0.000 | 1.1368 / 1.1368 | 4.1935 | 4.194 |
| 20:00-20:30 |  | 5/5 |  | 1.1961 | 1.1961 | 3 | 3 | 0.000 / 0.000 | 1.1961 / 1.1961 | 4.3123 | 4.312 |
| 20:30-21:00 |  | 5/5 |  | 1.1396 | 1.1396 | 3 | 3 | 0.000 / 0.000 | 1.1396 / 1.1396 | 4.1993 | 4.199 |
| 21:00-21:30 |  | 5/5 |  | 1.1030 | 1.1030 | 3 | 3 | 0.000 / 0.000 | 1.1030 / 1.1030 | 4.1260 | 4.126 |
| 21:30-22:00 |  | 5/5 |  | 1.1167 | 1.1167 | 3 | 3 | 0.000 / 0.000 | 1.1167 / 1.1167 | 4.1535 | 4.153 |
| 22:00-22:30 |  | 5/5 |  | 1.1035 | 1.1035 | 3 | 3 | 0.000 / 0.000 | 1.1035 / 1.1035 | 4.1270 | 4.127 |
| 22:30-23:00 |  | 5/5 |  | 1.0432 | 1.0432 | 3 | 3 | 0.000 / 0.000 | 1.0432 / 1.0432 | 4.0064 | 4.006 |
| 23:00-23:30 |  | 5/5 |  | 1.0238 | 1.0238 | 3 | 3 | 0.000 / 0.000 | 1.0238 / 1.0238 | 3.9675 | 3.968 |
| 23:30-00:00 |  | 5/5 |  | 1.0247 | 1.0247 | 3 | 3 | 0.000 / 0.000 | 1.0247 / 1.0247 | 3.9693 | 3.969 |
| 00:00-00:30 |  | 5/5 |  | 1.0396 | 1.0396 | 3 | 3 | 0.000 / 0.000 | 1.0396 / 1.0396 | 3.9993 | 3.999 |
| 00:30-01:00 |  | 5/5 |  | 1.0908 | 1.0908 | 3 | 3 | 0.000 / 0.000 | 1.0908 / 1.0908 | 4.1016 | 4.102 |
| 01:00-01:30 |  | 5/5 |  | 1.0739 | 1.0739 | 3 | 3 | 0.000 / 0.000 | 1.0739 / 1.0739 | 4.0678 | 4.068 |
| 01:30-02:00 |  | 5/5 |  | 1.0812 | 1.0812 | 3 | 3 | 0.000 / 0.000 | 1.0812 / 1.0812 | 4.0824 | 4.082 |
| 02:00-02:30 |  | 5/5 |  | 1.0823 | 1.0823 | 3 | 3 | 0.000 / 0.000 | 1.0823 / 1.0823 | 4.0847 | 4.085 |
| 02:30-03:00 |  | 5/5 |  | 1.0793 | 1.0793 | 3 | 3 | 0.000 / 0.000 | 1.0793 / 1.0793 | 4.0787 | 4.079 |
| 03:00-03:30 |  | 5/5 |  | 1.0650 | 1.0650 | 3 | 3 | 0.000 / 0.000 | 1.0650 / 1.0650 | 4.0500 | 4.050 |
| 03:30-04:00 |  | 5/5 |  | 1.0762 | 1.0762 | 3 | 3 | 0.000 / 0.000 | 1.0762 / 1.0762 | 4.0725 | 4.072 |
| 04:00-04:30 |  | 5/5 |  | 1.0983 | 1.0985 | 3 | 3 | 0.000 / 0.000 | 1.0983 / 1.0983 | 4.1165 | 4.117 |
| 04:30-05:00 |  | 5/5 |  | 1.1715 | 1.1729 | 3 | 3 | 0.000 / 0.000 | 1.1715 / 1.1715 | 4.2630 | 4.263 |
| 05:00-05:30 |  | 5/5 |  | 1.1064 | 1.1064 | 3 | 3 | 0.000 / 0.000 | 1.1064 / 1.1064 | 4.1328 | 4.133 |
| 05:30-06:00 |  | 5/5 |  | 1.0881 | 1.0881 | 3 | 3 | 0.000 / 0.000 | 1.0881 / 1.0881 | 4.0962 | 4.096 |
| 06:00-06:30 |  | 5/5 |  | 1.0767 | 1.0767 | 3 | 3 | 0.000 / 0.000 | 1.0767 / 1.0767 | 4.0735 | 4.073 |
| 06:30-07:00 |  | 5/5 |  | 1.1425 | 1.1432 | 3 | 3 | 0.000 / 0.000 | 1.1425 / 1.1425 | 4.2051 | 4.205 |
| 07:00-07:30 | D | 5/5 |  | 1.1636 | 1.1636 | 3 | 3 | 0.000 / 0.000 | 1.1636 / 1.1636 | 4.2473 | 4.247 |
| 07:30-08:00 | D | 5/5 |  | 1.2472 | 1.2482 | 3 | 3 | 0.000 / 0.000 | 1.2472 / 1.2472 | 4.4144 | 4.414 |
| 08:00-08:30 | D | 5/5 |  | 1.0871 | 1.0871 | 3 | 3 | 0.000 / 0.000 | 1.0871 / 1.0871 | 4.0942 | 4.094 |
| 08:30-09:00 | D | 5/5 |  | 1.0814 | 1.0814 | 3 | 3 | 0.000 / 0.000 | 1.0814 / 1.0814 | 4.0828 | 4.083 |
| 09:00-09:30 | D | 5/5 |  | 1.0911 | 1.0911 | 3 | 3 | 0.000 / 0.000 | 1.0911 / 1.0911 | 4.1022 | 4.102 |
| 09:30-10:00 | D | 5/5 |  | 1.0264 | 1.0264 | 3 | 3 | 0.000 / 0.000 | 1.0264 / 1.0264 | 3.9729 | 3.973 |
| 10:00-10:30 | D | 5/5 |  | 1.0575 | 1.0575 | 3 | 3 | 0.000 / 0.000 | 1.0575 / 1.0575 | 4.0351 | 4.035 |
| 10:30-11:00 | D | 5/5 |  | 1.0290 | 1.0290 | 3 | 3 | 0.000 / 0.000 | 1.0290 / 1.0290 | 3.9781 | 3.978 |
| 11:00-11:30 | D | 5/5 |  | 1.0211 | 1.0211 | 4 | 4 | 0.000 / 0.000 | 1.0211 / 1.0211 | 3.9621 | 3.962 |
| 11:30-12:00 | D | 5/5 |  | 1.0129 | 1.0129 | 3 | 3 | 0.000 / 0.000 | 1.0129 / 1.0129 | 3.9459 | 3.946 |
| 12:00-12:30 | D | 5/5 |  | 1.0973 | 1.0973 | 3 | 3 | 0.000 / 0.000 | 1.0973 / 1.0973 | 4.1147 | 4.115 |
| 12:30-13:00 |  | 5/5 |  | 1.0722 | 1.0722 | 3 | 3 | 0.000 / 0.000 | 1.0722 / 1.0722 | 4.0643 | 4.064 |
| 13:00-13:30 |  | 5/5 |  | 1.1185 | 1.1185 | 3 | 3 | 0.000 / 0.000 | 1.1185 / 1.1185 | 4.1570 | 4.157 |
| 13:30-14:00 |  | 5/5 |  | 1.1019 | 1.1019 | 3 | 3 | 0.000 / 0.000 | 1.1019 / 1.1019 | 4.1237 | 4.124 |
| 14:00-14:30 |  | 5/5 |  | 1.0803 | 1.0803 | 3 | 3 | 0.000 / 0.000 | 1.0803 / 1.0803 | 4.0806 | 4.081 |
| 14:30-15:00 |  | 5/5 |  | 1.0547 | 1.0547 | 3 | 3 | 0.000 / 0.000 | 1.0547 / 1.0547 | 4.0293 | 4.029 |
| 15:00-15:30 |  | 5/5 |  | 1.0671 | 1.0671 | 3 | 3 | 0.000 / 0.000 | 1.0671 / 1.0671 | 4.0542 | 4.054 |
| 15:30-16:00 |  | 5/5 |  | 1.2145 | 1.2145 | 3 | 3 | 0.000 / 0.000 | 1.2145 / 1.2145 | 4.3491 | 4.349 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MGC_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` d44b928de02d54f75b03fc7df779047911183959057e7d97d68f4cb55bf18104 (3,470,096 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MGC_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 68bcf1af1eda552563357f5f4d53b7f5b397e0e2e99e09940a6d22718e8ec7c9 (1,517,709 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MGC_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` ae1168eeb06b433a94fec823b134b8cde27fabbd53305466cb6b8da24e14cbe2 (5,200,459 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MGC_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 02d85193f80facf27ac15150db8f9f23f6078df89d248cae4d4d61292211b6ae (3,699,557 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MGC_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 033f82e660dd6954e53f7bef1a077eb0975e088f9c84ea5ad22ab53fb06357b1 (3,215,446 records)

### MHG (metals)

Tick 0.0005 (vendor units 0.0005, factor 1), tick value $1.25; commission $1.92 round turn = 1.5360 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 2; D6 day session 07:10-12:00 CT.

Event-window one-side slippage: buy 1.7393, sell 1.7393 ticks (round turn inside a window 5.0147 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.7393 | 1.7393 | 2 | 2 | 0.000 / 0.000 | 1.7393 / 1.7393 | 5.0147 | 6.268 |
| 17:30-18:00 |  | 5/5 |  | 1.2005 | 1.2005 | 2 | 3 | 0.000 / 0.000 | 1.2005 / 1.2005 | 3.9371 | 4.921 |
| 18:00-18:30 |  | 5/5 |  | 1.0240 | 1.0240 | 2 | 3 | 0.000 / 0.000 | 1.0240 / 1.0240 | 3.5840 | 4.480 |
| 18:30-19:00 |  | 5/5 |  | 1.0543 | 1.0543 | 2 | 2 | 0.000 / 0.000 | 1.0543 / 1.0543 | 3.6446 | 4.556 |
| 19:00-19:30 |  | 5/5 |  | 1.0369 | 1.0369 | 2 | 2 | 0.000 / 0.000 | 1.0369 / 1.0369 | 3.6099 | 4.512 |
| 19:30-20:00 |  | 5/5 |  | 1.0090 | 1.0090 | 2 | 2 | 0.000 / 0.000 | 1.0090 / 1.0090 | 3.5539 | 4.442 |
| 20:00-20:30 |  | 5/5 |  | 1.0281 | 1.0281 | 2 | 2 | 0.000 / 0.000 | 1.0281 / 1.0281 | 3.5921 | 4.490 |
| 20:30-21:00 |  | 5/5 |  | 1.0297 | 1.0297 | 2 | 2 | 0.000 / 0.000 | 1.0297 / 1.0297 | 3.5955 | 4.494 |
| 21:00-21:30 |  | 5/5 |  | 1.0303 | 1.0303 | 2 | 2 | 0.000 / 0.000 | 1.0303 / 1.0303 | 3.5967 | 4.496 |
| 21:30-22:00 |  | 5/5 |  | 1.0172 | 1.0172 | 2 | 2 | 0.000 / 0.000 | 1.0172 / 1.0172 | 3.5703 | 4.463 |
| 22:00-22:30 |  | 5/5 |  | 0.9925 | 0.9925 | 2 | 2 | 0.000 / 0.000 | 0.9925 / 0.9925 | 3.5210 | 4.401 |
| 22:30-23:00 |  | 5/5 |  | 1.0458 | 1.0458 | 2 | 2 | 0.000 / 0.000 | 1.0458 / 1.0458 | 3.6276 | 4.535 |
| 23:00-23:30 |  | 5/5 |  | 1.1362 | 1.1362 | 2 | 2 | 0.000 / 0.000 | 1.1362 / 1.1362 | 3.8084 | 4.761 |
| 23:30-00:00 |  | 5/5 |  | 1.0532 | 1.0532 | 2 | 2 | 0.000 / 0.000 | 1.0532 / 1.0532 | 3.6424 | 4.553 |
| 00:00-00:30 |  | 5/5 |  | 1.0301 | 1.0301 | 2 | 2 | 0.000 / 0.000 | 1.0301 / 1.0301 | 3.5962 | 4.495 |
| 00:30-01:00 |  | 5/5 |  | 0.9978 | 0.9978 | 2 | 2 | 0.000 / 0.000 | 0.9978 / 0.9978 | 3.5317 | 4.415 |
| 01:00-01:30 |  | 5/5 |  | 1.0194 | 1.0194 | 2 | 2 | 0.000 / 0.000 | 1.0194 / 1.0194 | 3.5747 | 4.468 |
| 01:30-02:00 |  | 5/5 |  | 1.0790 | 1.0790 | 2 | 2 | 0.000 / 0.000 | 1.0790 / 1.0790 | 3.6940 | 4.617 |
| 02:00-02:30 |  | 5/5 |  | 1.0967 | 1.0967 | 2 | 2 | 0.000 / 0.000 | 1.0967 / 1.0967 | 3.7294 | 4.662 |
| 02:30-03:00 |  | 5/5 |  | 1.0502 | 1.0502 | 2 | 2 | 0.000 / 0.000 | 1.0502 / 1.0502 | 3.6363 | 4.545 |
| 03:00-03:30 |  | 5/5 |  | 1.0552 | 1.0552 | 2 | 2 | 0.000 / 0.000 | 1.0552 / 1.0552 | 3.6463 | 4.558 |
| 03:30-04:00 |  | 5/5 |  | 1.0743 | 1.0743 | 2 | 2 | 0.000 / 0.000 | 1.0743 / 1.0743 | 3.6846 | 4.606 |
| 04:00-04:30 |  | 5/5 |  | 1.0583 | 1.0583 | 2 | 2 | 0.000 / 0.000 | 1.0583 / 1.0583 | 3.6526 | 4.566 |
| 04:30-05:00 |  | 5/5 |  | 1.0519 | 1.0519 | 2 | 2 | 0.000 / 0.000 | 1.0519 / 1.0519 | 3.6397 | 4.550 |
| 05:00-05:30 |  | 5/5 |  | 1.0928 | 1.0928 | 2 | 2 | 0.000 / 0.000 | 1.0928 / 1.0928 | 3.7215 | 4.652 |
| 05:30-06:00 |  | 5/5 |  | 1.0996 | 1.0996 | 2 | 2 | 0.000 / 0.000 | 1.0996 / 1.0996 | 3.7353 | 4.669 |
| 06:00-06:30 |  | 5/5 |  | 1.1271 | 1.1271 | 2 | 2 | 0.000 / 0.000 | 1.1271 / 1.1271 | 3.7901 | 4.738 |
| 06:30-07:00 |  | 5/5 |  | 1.1284 | 1.1284 | 2 | 2 | 0.000 / 0.000 | 1.1284 / 1.1284 | 3.7928 | 4.741 |
| 07:00-07:30 | D | 5/5 |  | 1.2798 | 1.2800 | 2 | 2 | 0.000 / 0.000 | 1.2798 / 1.2798 | 4.0955 | 5.119 |
| 07:30-08:00 | D | 5/5 |  | 1.1172 | 1.1172 | 2 | 2 | 0.000 / 0.000 | 1.1172 / 1.1172 | 3.7705 | 4.713 |
| 08:00-08:30 | D | 5/5 |  | 1.0308 | 1.0308 | 2 | 2 | 0.000 / 0.000 | 1.0308 / 1.0308 | 3.5977 | 4.497 |
| 08:30-09:00 | D | 5/5 |  | 1.0575 | 1.0575 | 2 | 2 | 0.000 / 0.000 | 1.0575 / 1.0575 | 3.6511 | 4.564 |
| 09:00-09:30 | D | 5/5 |  | 1.1020 | 1.1020 | 2 | 2 | 0.000 / 0.000 | 1.1020 / 1.1020 | 3.7400 | 4.675 |
| 09:30-10:00 | D | 5/5 |  | 1.1333 | 1.1333 | 2 | 2 | 0.000 / 0.000 | 1.1333 / 1.1333 | 3.8026 | 4.753 |
| 10:00-10:30 | D | 5/5 |  | 1.0656 | 1.0656 | 2 | 2 | 0.000 / 0.000 | 1.0656 / 1.0656 | 3.6671 | 4.584 |
| 10:30-11:00 | D | 5/5 |  | 1.0411 | 1.0411 | 2 | 2 | 0.000 / 0.000 | 1.0411 / 1.0411 | 3.6182 | 4.523 |
| 11:00-11:30 | D | 5/5 |  | 0.9763 | 0.9763 | 2 | 3 | 0.000 / 0.000 | 0.9763 / 0.9763 | 3.4886 | 4.361 |
| 11:30-12:00 | D | 5/5 |  | 1.0199 | 1.0199 | 2 | 2 | 0.000 / 0.000 | 1.0199 / 1.0199 | 3.5758 | 4.470 |
| 12:00-12:30 |  | 5/5 |  | 1.0036 | 1.0036 | 2 | 2 | 0.000 / 0.000 | 1.0036 / 1.0036 | 3.5433 | 4.429 |
| 12:30-13:00 |  | 5/5 |  | 1.0276 | 1.0276 | 2 | 2 | 0.000 / 0.000 | 1.0276 / 1.0276 | 3.5913 | 4.489 |
| 13:00-13:30 |  | 5/5 |  | 1.0097 | 1.0097 | 2 | 2 | 0.000 / 0.000 | 1.0097 / 1.0097 | 3.5553 | 4.444 |
| 13:30-14:00 |  | 5/5 |  | 1.0546 | 1.0546 | 2 | 2 | 0.000 / 0.000 | 1.0546 / 1.0546 | 3.6451 | 4.556 |
| 14:00-14:30 |  | 5/5 |  | 1.0297 | 1.0297 | 2 | 3 | 0.000 / 0.000 | 1.0297 / 1.0297 | 3.5954 | 4.494 |
| 14:30-15:00 |  | 5/5 |  | 1.0099 | 1.0099 | 2 | 2 | 0.000 / 0.000 | 1.0099 / 1.0099 | 3.5558 | 4.445 |
| 15:00-15:30 |  | 5/5 |  | 1.0759 | 1.0759 | 2 | 2 | 0.000 / 0.000 | 1.0759 / 1.0759 | 3.6878 | 4.610 |
| 15:30-16:00 |  | 5/5 |  | 1.2700 | 1.2700 | 2 | 2 | 0.000 / 0.000 | 1.2700 / 1.2700 | 4.0759 | 5.095 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MHG_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` baf429556ada7a9c280cb8db633841149c6e04e3fc189a172fbd539b3218dea7 (312,788 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MHG_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 83555febcb4e346b84d5ab8b006001f5fb6872630d38b4428654e5663bbde440 (127,241 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MHG_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 7d8ac13bb3fa5611bec2ad7899c65f6a2afdbd8677001363dd8f2ca9b49a3411 (234,285 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MHG_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 0e44a9d489b430e95332b26ab8ba050ca75f4711da5fdf9edc62919de80f4bde (914,978 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MHG_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` e8f3df286997b792db0267e6de079fd50761cf6522a34896e38c9aa0834f28d4 (497,699 records)

### MNG (energy)

Tick 0.001 (vendor units 0.001, factor 1), tick value $1.0; commission $1.92 round turn = 1.9200 ticks (reports/stage_e0_topstep_facts.json F3.7 + F3.6 (+$0.20 round turn from the 2026-10-01 trading day, applied now per D8)); q_c 6; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 3.2195, sell 3.2195 ticks (round turn inside a window 8.3590 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 2.4127 | 2.4127 | 2 | 3 | 0.500 / 0.667 | 2.9127 / 3.0793 | 7.9120 | 7.912 |
| 17:30-18:00 |  | 5/5 |  | 1.4675 | 1.4675 | 3 | 3 | 0.500 / 0.500 | 1.9675 / 1.9675 | 5.8549 | 5.855 |
| 18:00-18:30 |  | 5/5 |  | 1.3079 | 1.3079 | 3 | 3 | 0.500 / 0.500 | 1.8079 / 1.8079 | 5.5359 | 5.536 |
| 18:30-19:00 |  | 5/5 |  | 1.4603 | 1.4603 | 3 | 3 | 0.500 / 0.500 | 1.9603 / 1.9603 | 5.8405 | 5.841 |
| 19:00-19:30 |  | 5/5 |  | 1.4314 | 1.4314 | 3 | 3 | 0.500 / 0.500 | 1.9314 / 1.9314 | 5.7828 | 5.783 |
| 19:30-20:00 |  | 5/5 |  | 1.2676 | 1.2676 | 3 | 2 | 0.667 / 0.500 | 1.9342 / 1.7676 | 5.6218 | 5.622 |
| 20:00-20:30 |  | 5/5 |  | 1.3306 | 1.3306 | 3 | 2 | 0.667 / 0.500 | 1.9972 / 1.8306 | 5.7478 | 5.748 |
| 20:30-21:00 |  | 5/5 |  | 1.3230 | 1.3230 | 3 | 3 | 0.500 / 0.500 | 1.8230 / 1.8230 | 5.5661 | 5.566 |
| 21:00-21:30 |  | 5/5 |  | 1.3273 | 1.3273 | 3 | 3 | 0.500 / 0.500 | 1.8273 / 1.8273 | 5.5746 | 5.575 |
| 21:30-22:00 |  | 5/5 |  | 1.4489 | 1.4489 | 3 | 3 | 0.500 / 0.500 | 1.9489 / 1.9489 | 5.8177 | 5.818 |
| 22:00-22:30 |  | 5/5 |  | 1.2729 | 1.2729 | 2 | 3 | 0.500 / 0.667 | 1.7729 / 1.9395 | 5.6324 | 5.632 |
| 22:30-23:00 |  | 5/5 |  | 1.3293 | 1.3293 | 3 | 3 | 0.500 / 0.500 | 1.8293 / 1.8293 | 5.5785 | 5.579 |
| 23:00-23:30 |  | 5/5 |  | 1.3986 | 1.3986 | 3 | 2 | 0.667 / 0.500 | 2.0653 / 1.8986 | 5.8839 | 5.884 |
| 23:30-00:00 |  | 5/5 |  | 1.3716 | 1.3716 | 3 | 2 | 0.667 / 0.500 | 2.0383 / 1.8716 | 5.8298 | 5.830 |
| 00:00-00:30 |  | 5/5 |  | 1.4145 | 1.4145 | 3 | 3 | 0.500 / 0.500 | 1.9145 / 1.9145 | 5.7489 | 5.749 |
| 00:30-01:00 |  | 5/5 |  | 1.2274 | 1.2274 | 3 | 3 | 0.500 / 0.500 | 1.7274 / 1.7274 | 5.3748 | 5.375 |
| 01:00-01:30 |  | 5/5 |  | 1.3042 | 1.3042 | 3 | 3 | 0.500 / 0.500 | 1.8042 / 1.8042 | 5.5284 | 5.528 |
| 01:30-02:00 |  | 5/5 |  | 1.2745 | 1.2745 | 3 | 2 | 0.667 / 0.500 | 1.9411 / 1.7745 | 5.6356 | 5.636 |
| 02:00-02:30 |  | 5/5 |  | 1.2443 | 1.2443 | 2 | 3 | 0.500 / 0.667 | 1.7443 / 1.9110 | 5.5753 | 5.575 |
| 02:30-03:00 |  | 5/5 |  | 1.3544 | 1.3544 | 3 | 2 | 0.667 / 0.500 | 2.0211 / 1.8544 | 5.7955 | 5.795 |
| 03:00-03:30 |  | 5/5 |  | 1.2758 | 1.2758 | 3 | 3 | 0.500 / 0.500 | 1.7758 / 1.7758 | 5.4717 | 5.472 |
| 03:30-04:00 |  | 5/5 |  | 1.2366 | 1.2366 | 2 | 2 | 0.667 / 0.667 | 1.9033 / 1.9033 | 5.7266 | 5.727 |
| 04:00-04:30 |  | 5/5 |  | 1.1690 | 1.1690 | 2 | 3 | 0.500 / 0.667 | 1.6690 / 1.8357 | 5.4246 | 5.425 |
| 04:30-05:00 |  | 5/5 |  | 1.2039 | 1.2039 | 2 | 3 | 0.500 / 0.667 | 1.7039 / 1.8706 | 5.4944 | 5.494 |
| 05:00-05:30 |  | 5/5 |  | 1.2450 | 1.2450 | 3 | 3 | 0.500 / 0.500 | 1.7450 / 1.7450 | 5.4101 | 5.410 |
| 05:30-06:00 |  | 5/5 |  | 1.1983 | 1.1983 | 2 | 3 | 0.500 / 0.667 | 1.6983 / 1.8650 | 5.4833 | 5.483 |
| 06:00-06:30 |  | 5/5 |  | 1.2425 | 1.2425 | 2 | 3 | 0.500 / 0.667 | 1.7425 / 1.9091 | 5.5716 | 5.572 |
| 06:30-07:00 |  | 5/5 |  | 1.2294 | 1.2294 | 2 | 3 | 0.500 / 0.667 | 1.7294 / 1.8961 | 5.5455 | 5.545 |
| 07:00-07:30 |  | 5/5 |  | 1.2470 | 1.2470 | 2 | 3 | 0.500 / 0.667 | 1.7470 / 1.9137 | 5.5807 | 5.581 |
| 07:30-08:00 |  | 5/5 |  | 1.2399 | 1.2399 | 2 | 3 | 0.500 / 0.667 | 1.7399 / 1.9066 | 5.5665 | 5.567 |
| 08:00-08:30 | D | 5/5 |  | 1.1720 | 1.1720 | 3 | 3 | 0.500 / 0.500 | 1.6720 / 1.6720 | 5.2640 | 5.264 |
| 08:30-09:00 | D | 5/5 |  | 1.1947 | 1.1947 | 3 | 3 | 0.500 / 0.500 | 1.6947 / 1.6947 | 5.3094 | 5.309 |
| 09:00-09:30 | D | 5/5 |  | 1.1707 | 1.1707 | 3 | 3 | 0.500 / 0.500 | 1.6707 / 1.6707 | 5.2614 | 5.261 |
| 09:30-10:00 | D | 5/5 |  | 1.1798 | 1.1798 | 3 | 3 | 0.500 / 0.500 | 1.6798 / 1.6798 | 5.2796 | 5.280 |
| 10:00-10:30 | D | 5/5 |  | 1.1613 | 1.1613 | 3 | 3 | 0.500 / 0.500 | 1.6613 / 1.6613 | 5.2426 | 5.243 |
| 10:30-11:00 | D | 5/5 |  | 1.1965 | 1.1965 | 3 | 3 | 0.500 / 0.500 | 1.6965 / 1.6965 | 5.3130 | 5.313 |
| 11:00-11:30 | D | 5/5 |  | 1.2494 | 1.2494 | 3 | 3 | 0.500 / 0.500 | 1.7494 / 1.7494 | 5.4189 | 5.419 |
| 11:30-12:00 | D | 5/5 |  | 1.2399 | 1.2399 | 3 | 3 | 0.500 / 0.500 | 1.7399 / 1.7399 | 5.3997 | 5.400 |
| 12:00-12:30 | D | 5/5 |  | 1.2400 | 1.2400 | 3 | 3 | 0.500 / 0.500 | 1.7400 / 1.7400 | 5.4001 | 5.400 |
| 12:30-13:00 | D | 5/5 |  | 1.2175 | 1.2175 | 3 | 3 | 0.500 / 0.500 | 1.7175 / 1.7175 | 5.3549 | 5.355 |
| 13:00-13:30 | D | 5/5 |  | 1.2576 | 1.2576 | 2 | 3 | 0.500 / 0.667 | 1.7576 / 1.9243 | 5.6019 | 5.602 |
| 13:30-14:00 |  | 5/5 |  | 1.2375 | 1.2375 | 3 | 3 | 0.500 / 0.500 | 1.7375 / 1.7375 | 5.3951 | 5.395 |
| 14:00-14:30 |  | 5/5 |  | 1.1417 | 1.1417 | 3 | 3 | 0.500 / 0.500 | 1.6417 / 1.6417 | 5.2035 | 5.203 |
| 14:30-15:00 |  | 5/5 |  | 1.2100 | 1.2100 | 3 | 3 | 0.500 / 0.500 | 1.7100 / 1.7100 | 5.3400 | 5.340 |
| 15:00-15:30 |  | 5/5 |  | 1.8047 | 1.8047 | 3 | 3 | 0.500 / 0.500 | 2.3047 / 2.3047 | 6.5294 | 6.529 |
| 15:30-16:00 |  | 5/5 |  | 2.5528 | 2.5528 | 2 | 2 | 0.667 / 0.667 | 3.2195 / 3.2195 | 8.3590 | 8.359 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MNG_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` c91c2a8177ac39936401b9022d768977d0f7c2f615777316c9e81efb3cbffaae (171,230 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNG_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` d791cd20d1447ac1ec44287f2cd1452a5d9181ffe193e1afaa6dff85765d64bb (137,301 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNG_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` bd67a7347c158a0e105121aad6507f8802102b17cb46ac2bf64c7dc6db413589 (301,633 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNG_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` fb1160cdfb025c2828d28a1c72f746c0d75395007504bf43dbf13441dfe0252a (221,362 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNG_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` ae103f2eb7814c311685aa19f4beedc6d47d7a3c203674dbc12e57a1316f4c3e (115,195 records)

### MNQ (equity)

Tick 0.25 (vendor units 0.25, factor 1), tick value $0.5; commission $1.22 round turn = 2.4400 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 1.4859, sell 1.4859 ticks (round turn inside a window 5.4118 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.4859 | 1.4859 | 3 | 2 | 0.000 / 0.000 | 1.4859 / 1.4859 | 5.4118 | 2.706 |
| 17:30-18:00 |  | 5/5 |  | 1.2037 | 1.2037 | 3 | 3 | 0.000 / 0.000 | 1.2037 / 1.2037 | 4.8474 | 2.424 |
| 18:00-18:30 |  | 5/5 |  | 1.1297 | 1.1297 | 3 | 3 | 0.000 / 0.000 | 1.1297 / 1.1297 | 4.6995 | 2.350 |
| 18:30-19:00 |  | 5/5 |  | 1.1002 | 1.1002 | 3 | 3 | 0.000 / 0.000 | 1.1002 / 1.1002 | 4.6403 | 2.320 |
| 19:00-19:30 |  | 5/5 |  | 1.0663 | 1.0663 | 3 | 3 | 0.000 / 0.000 | 1.0663 / 1.0663 | 4.5726 | 2.286 |
| 19:30-20:00 |  | 5/5 |  | 1.0342 | 1.0342 | 3 | 3 | 0.000 / 0.000 | 1.0342 / 1.0342 | 4.5083 | 2.254 |
| 20:00-20:30 |  | 5/5 |  | 1.0202 | 1.0202 | 3 | 3 | 0.000 / 0.000 | 1.0202 / 1.0202 | 4.4804 | 2.240 |
| 20:30-21:00 |  | 5/5 |  | 1.0095 | 1.0095 | 3 | 3 | 0.000 / 0.000 | 1.0095 / 1.0095 | 4.4590 | 2.230 |
| 21:00-21:30 |  | 5/5 |  | 0.9997 | 0.9997 | 3 | 3 | 0.000 / 0.000 | 0.9997 / 0.9997 | 4.4394 | 2.220 |
| 21:30-22:00 |  | 5/5 |  | 1.0103 | 1.0103 | 3 | 3 | 0.000 / 0.000 | 1.0103 / 1.0103 | 4.4606 | 2.230 |
| 22:00-22:30 |  | 5/5 |  | 1.0146 | 1.0146 | 3 | 3 | 0.000 / 0.000 | 1.0146 / 1.0146 | 4.4692 | 2.235 |
| 22:30-23:00 |  | 5/5 |  | 1.0046 | 1.0046 | 3 | 3 | 0.000 / 0.000 | 1.0046 / 1.0046 | 4.4492 | 2.225 |
| 23:00-23:30 |  | 5/5 |  | 1.0106 | 1.0106 | 3 | 3 | 0.000 / 0.000 | 1.0106 / 1.0106 | 4.4612 | 2.231 |
| 23:30-00:00 |  | 5/5 |  | 1.0088 | 1.0088 | 3 | 3 | 0.000 / 0.000 | 1.0088 / 1.0088 | 4.4577 | 2.229 |
| 00:00-00:30 |  | 5/5 |  | 1.0495 | 1.0495 | 3 | 3 | 0.000 / 0.000 | 1.0495 / 1.0495 | 4.5390 | 2.270 |
| 00:30-01:00 |  | 5/5 |  | 1.0357 | 1.0357 | 3 | 3 | 0.000 / 0.000 | 1.0357 / 1.0357 | 4.5114 | 2.256 |
| 01:00-01:30 |  | 5/5 |  | 1.0461 | 1.0461 | 3 | 3 | 0.000 / 0.000 | 1.0461 / 1.0461 | 4.5323 | 2.266 |
| 01:30-02:00 |  | 5/5 |  | 1.0768 | 1.0768 | 3 | 3 | 0.000 / 0.000 | 1.0768 / 1.0768 | 4.5937 | 2.297 |
| 02:00-02:30 |  | 5/5 |  | 1.1077 | 1.1077 | 3 | 3 | 0.000 / 0.000 | 1.1077 / 1.1077 | 4.6554 | 2.328 |
| 02:30-03:00 |  | 5/5 |  | 1.1048 | 1.1048 | 3 | 3 | 0.000 / 0.000 | 1.1048 / 1.1048 | 4.6496 | 2.325 |
| 03:00-03:30 |  | 5/5 |  | 1.1286 | 1.1286 | 3 | 3 | 0.000 / 0.000 | 1.1286 / 1.1286 | 4.6972 | 2.349 |
| 03:30-04:00 |  | 5/5 |  | 1.0968 | 1.0968 | 3 | 3 | 0.000 / 0.000 | 1.0968 / 1.0968 | 4.6335 | 2.317 |
| 04:00-04:30 |  | 5/5 |  | 1.1666 | 1.1666 | 3 | 3 | 0.000 / 0.000 | 1.1666 / 1.1666 | 4.7732 | 2.387 |
| 04:30-05:00 |  | 5/5 |  | 1.1246 | 1.1246 | 3 | 3 | 0.000 / 0.000 | 1.1246 / 1.1246 | 4.6892 | 2.345 |
| 05:00-05:30 |  | 5/5 |  | 1.1062 | 1.1062 | 3 | 3 | 0.000 / 0.000 | 1.1062 / 1.1062 | 4.6525 | 2.326 |
| 05:30-06:00 |  | 5/5 |  | 1.1255 | 1.1255 | 3 | 3 | 0.000 / 0.000 | 1.1255 / 1.1255 | 4.6910 | 2.346 |
| 06:00-06:30 |  | 5/5 |  | 1.1255 | 1.1255 | 3 | 3 | 0.000 / 0.000 | 1.1255 / 1.1255 | 4.6911 | 2.346 |
| 06:30-07:00 |  | 5/5 |  | 1.1463 | 1.1463 | 3 | 3 | 0.000 / 0.000 | 1.1463 / 1.1463 | 4.7327 | 2.366 |
| 07:00-07:30 |  | 5/5 |  | 1.1424 | 1.1424 | 3 | 3 | 0.000 / 0.000 | 1.1424 / 1.1424 | 4.7248 | 2.362 |
| 07:30-08:00 |  | 5/5 |  | 1.1123 | 1.1123 | 3 | 3 | 0.000 / 0.000 | 1.1123 / 1.1123 | 4.6646 | 2.332 |
| 08:00-08:30 |  | 5/5 |  | 0.9373 | 0.9373 | 4 | 4 | 0.000 / 0.000 | 0.9373 / 0.9373 | 4.3147 | 2.157 |
| 08:30-09:00 | D | 5/5 |  | 0.9693 | 0.9693 | 4 | 4 | 0.000 / 0.000 | 0.9693 / 0.9693 | 4.3786 | 2.189 |
| 09:00-09:30 | D | 5/5 |  | 0.9031 | 0.9031 | 5 | 5 | 0.000 / 0.000 | 0.9031 / 0.9031 | 4.2463 | 2.123 |
| 09:30-10:00 | D | 5/5 |  | 0.8567 | 0.8567 | 6 | 6 | 0.000 / 0.000 | 0.8567 / 0.8567 | 4.1535 | 2.077 |
| 10:00-10:30 | D | 5/5 |  | 0.8279 | 0.8279 | 6 | 6 | 0.000 / 0.000 | 0.8279 / 0.8279 | 4.0958 | 2.048 |
| 10:30-11:00 | D | 5/5 |  | 0.8194 | 0.8194 | 6 | 6 | 0.000 / 0.000 | 0.8194 / 0.8194 | 4.0788 | 2.039 |
| 11:00-11:30 | D | 5/5 |  | 0.8160 | 0.8160 | 6 | 6 | 0.000 / 0.000 | 0.8160 / 0.8160 | 4.0720 | 2.036 |
| 11:30-12:00 | D | 5/5 |  | 0.8192 | 0.8192 | 6 | 6 | 0.000 / 0.000 | 0.8192 / 0.8192 | 4.0784 | 2.039 |
| 12:00-12:30 | D | 5/5 |  | 0.8231 | 0.8231 | 6 | 6 | 0.000 / 0.000 | 0.8231 / 0.8231 | 4.0861 | 2.043 |
| 12:30-13:00 | D | 5/5 |  | 0.8138 | 0.8138 | 6 | 6 | 0.000 / 0.000 | 0.8138 / 0.8138 | 4.0675 | 2.034 |
| 13:00-13:30 | D | 5/5 |  | 0.8104 | 0.8104 | 6 | 6 | 0.000 / 0.000 | 0.8104 / 0.8104 | 4.0608 | 2.030 |
| 13:30-14:00 | D | 5/5 |  | 0.8198 | 0.8198 | 6 | 6 | 0.000 / 0.000 | 0.8198 / 0.8198 | 4.0795 | 2.040 |
| 14:00-14:30 | D | 5/5 |  | 0.8166 | 0.8166 | 6 | 6 | 0.000 / 0.000 | 0.8166 / 0.8166 | 4.0733 | 2.037 |
| 14:30-15:00 | D | 5/5 |  | 0.8174 | 0.8174 | 6 | 6 | 0.000 / 0.000 | 0.8174 / 0.8174 | 4.0748 | 2.037 |
| 15:00-15:30 |  | 5/5 |  | 0.8717 | 0.8717 | 4 | 4 | 0.000 / 0.000 | 0.8717 / 0.8717 | 4.1834 | 2.092 |
| 15:30-16:00 |  | 5/5 |  | 0.9173 | 0.9173 | 4 | 4 | 0.000 / 0.000 | 0.9173 / 0.9173 | 4.2746 | 2.137 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` a9de289664f038afeea81c195a3f72afa2ba9255fbfb84c4046e29c08747f975 (15,213,902 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` f7f45e81376dfa14e5e483e4945aaabc110081e2241896bf39eff0c418a3dddc (12,099,238 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2025-11-11T230000Z_2025-11-12T103000Z.dbn.zst` 9ac08237f8a6b4f06174fa30072072a596abd999e01daf4f0d978a34424d06ff (2,039,415 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2025-11-12T103000Z_2025-11-12T161500Z.dbn.zst` b914b108688d6ba0395bdd0aa315673904f751d0ea80d0af0fb86d362e4cecdb (9,164,849 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2025-11-12T161500Z_2025-11-12T220000Z.dbn.zst` 6c1bf01b9f33583d3d3513738853affae63707875623b41935c1b820576da323 (14,194,766 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2026-02-10T230000Z_2026-02-11T103000Z.dbn.zst` 5338c2a4007c3ec89f1029f93d6ad33aab7ff7260eae2d0ad3db4ab007b362c5 (2,373,832 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2026-02-11T103000Z_2026-02-11T161500Z.dbn.zst` 1c153bdb9bf9beed72d3f58e860bb04e8832bf0f3545a444befd1877aa05a469 (14,823,622 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2026-02-11T161500Z_2026-02-11T220000Z.dbn.zst` 10d56e107e350c61f53c1b6af443b7583b065f738a697ef579609107f69bb90d (13,676,032 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MNQ_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 07cc6260515e0db45afdcbfe2539afbb0fb52380270854724ea49a515ac277d9 (16,755,592 records)

### MYM (equity)

Tick 1.0 (vendor units 1.0, factor 1), tick value $0.5; commission $1.22 round turn = 2.4400 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 3; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 2.2079, sell 2.5413 ticks (round turn inside a window 7.1892 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 2.2079 | 2.2079 | 2 | 3 | 0.000 / 0.333 | 2.2079 / 2.5413 | 7.1892 | 3.595 |
| 17:30-18:00 |  | 5/5 |  | 1.4175 | 1.4175 | 3 | 3 | 0.000 / 0.000 | 1.4175 / 1.4175 | 5.2751 | 2.638 |
| 18:00-18:30 |  | 5/5 |  | 1.2110 | 1.2110 | 2 | 3 | 0.000 / 0.333 | 1.2110 / 1.5443 | 5.1952 | 2.598 |
| 18:30-19:00 |  | 5/5 |  | 1.1668 | 1.1668 | 2 | 3 | 0.000 / 0.333 | 1.1668 / 1.5001 | 5.1069 | 2.553 |
| 19:00-19:30 |  | 5/5 |  | 1.1830 | 1.1830 | 3 | 2 | 0.333 / 0.000 | 1.5163 / 1.1830 | 5.1394 | 2.570 |
| 19:30-20:00 |  | 5/5 |  | 1.0956 | 1.0956 | 3 | 3 | 0.000 / 0.000 | 1.0956 / 1.0956 | 4.6312 | 2.316 |
| 20:00-20:30 |  | 5/5 |  | 1.0917 | 1.0917 | 3 | 3 | 0.000 / 0.000 | 1.0917 / 1.0917 | 4.6233 | 2.312 |
| 20:30-21:00 |  | 5/5 |  | 1.1288 | 1.1288 | 3 | 3 | 0.000 / 0.000 | 1.1288 / 1.1288 | 4.6976 | 2.349 |
| 21:00-21:30 |  | 5/5 |  | 1.0981 | 1.0981 | 3 | 3 | 0.000 / 0.000 | 1.0981 / 1.0981 | 4.6363 | 2.318 |
| 21:30-22:00 |  | 5/5 |  | 1.0669 | 1.0669 | 3 | 3 | 0.000 / 0.000 | 1.0669 / 1.0669 | 4.5738 | 2.287 |
| 22:00-22:30 |  | 5/5 |  | 1.0490 | 1.0490 | 3 | 3 | 0.000 / 0.000 | 1.0490 / 1.0490 | 4.5380 | 2.269 |
| 22:30-23:00 |  | 5/5 |  | 1.0869 | 1.0869 | 3 | 3 | 0.000 / 0.000 | 1.0869 / 1.0869 | 4.6137 | 2.307 |
| 23:00-23:30 |  | 5/5 |  | 1.1162 | 1.1162 | 3 | 3 | 0.000 / 0.000 | 1.1162 / 1.1162 | 4.6724 | 2.336 |
| 23:30-00:00 |  | 5/5 |  | 1.0271 | 1.0271 | 3 | 3 | 0.000 / 0.000 | 1.0271 / 1.0271 | 4.4942 | 2.247 |
| 00:00-00:30 |  | 5/5 |  | 1.0764 | 1.0764 | 3 | 3 | 0.000 / 0.000 | 1.0764 / 1.0764 | 4.5928 | 2.296 |
| 00:30-01:00 |  | 5/5 |  | 1.0573 | 1.0573 | 3 | 3 | 0.000 / 0.000 | 1.0573 / 1.0573 | 4.5547 | 2.277 |
| 01:00-01:30 |  | 5/5 |  | 1.0893 | 1.0893 | 3 | 3 | 0.000 / 0.000 | 1.0893 / 1.0893 | 4.6186 | 2.309 |
| 01:30-02:00 |  | 5/5 |  | 1.1368 | 1.1368 | 3 | 2 | 0.333 / 0.000 | 1.4701 / 1.1368 | 5.0470 | 2.523 |
| 02:00-02:30 |  | 5/5 |  | 1.1103 | 1.1103 | 3 | 3 | 0.000 / 0.000 | 1.1103 / 1.1103 | 4.6606 | 2.330 |
| 02:30-03:00 |  | 5/5 |  | 1.1133 | 1.1133 | 3 | 3 | 0.000 / 0.000 | 1.1133 / 1.1133 | 4.6666 | 2.333 |
| 03:00-03:30 |  | 5/5 |  | 1.1008 | 1.1008 | 3 | 3 | 0.000 / 0.000 | 1.1008 / 1.1008 | 4.6417 | 2.321 |
| 03:30-04:00 |  | 5/5 |  | 1.0807 | 1.0807 | 3 | 2 | 0.333 / 0.000 | 1.4140 / 1.0807 | 4.9347 | 2.467 |
| 04:00-04:30 |  | 5/5 |  | 1.1437 | 1.1437 | 3 | 2 | 0.333 / 0.000 | 1.4770 / 1.1437 | 5.0606 | 2.530 |
| 04:30-05:00 |  | 5/5 |  | 1.1061 | 1.1061 | 3 | 3 | 0.000 / 0.000 | 1.1061 / 1.1061 | 4.6523 | 2.326 |
| 05:00-05:30 |  | 5/5 |  | 1.1537 | 1.1537 | 3 | 2 | 0.333 / 0.000 | 1.4870 / 1.1537 | 5.0807 | 2.540 |
| 05:30-06:00 |  | 5/5 |  | 1.0988 | 1.0988 | 3 | 3 | 0.000 / 0.000 | 1.0988 / 1.0988 | 4.6377 | 2.319 |
| 06:00-06:30 |  | 5/5 |  | 1.0960 | 1.0960 | 3 | 3 | 0.000 / 0.000 | 1.0960 / 1.0960 | 4.6320 | 2.316 |
| 06:30-07:00 |  | 5/5 |  | 1.1262 | 1.1262 | 2 | 3 | 0.000 / 0.333 | 1.1262 / 1.4596 | 5.0258 | 2.513 |
| 07:00-07:30 |  | 5/5 |  | 1.1134 | 1.1134 | 3 | 3 | 0.000 / 0.000 | 1.1134 / 1.1134 | 4.6667 | 2.333 |
| 07:30-08:00 |  | 5/5 |  | 1.0994 | 1.0994 | 3 | 3 | 0.000 / 0.000 | 1.0994 / 1.0994 | 4.6387 | 2.319 |
| 08:00-08:30 |  | 5/5 |  | 0.8976 | 0.8976 | 3 | 3 | 0.000 / 0.000 | 0.8976 / 0.8976 | 4.2351 | 2.118 |
| 08:30-09:00 | D | 5/5 |  | 0.8275 | 0.8275 | 4 | 4 | 0.000 / 0.000 | 0.8275 / 0.8275 | 4.0949 | 2.047 |
| 09:00-09:30 | D | 5/5 |  | 0.7885 | 0.7885 | 4 | 4 | 0.000 / 0.000 | 0.7885 / 0.7885 | 4.0170 | 2.008 |
| 09:30-10:00 | D | 5/5 |  | 0.7820 | 0.7820 | 4 | 4 | 0.000 / 0.000 | 0.7820 / 0.7820 | 4.0040 | 2.002 |
| 10:00-10:30 | D | 5/5 |  | 0.7886 | 0.7886 | 4 | 4 | 0.000 / 0.000 | 0.7886 / 0.7886 | 4.0171 | 2.009 |
| 10:30-11:00 | D | 5/5 |  | 0.7808 | 0.7808 | 4 | 4 | 0.000 / 0.000 | 0.7808 / 0.7808 | 4.0016 | 2.001 |
| 11:00-11:30 | D | 5/5 |  | 0.7562 | 0.7562 | 4 | 4 | 0.000 / 0.000 | 0.7562 / 0.7562 | 3.9525 | 1.976 |
| 11:30-12:00 | D | 5/5 |  | 0.7599 | 0.7599 | 4 | 4 | 0.000 / 0.000 | 0.7599 / 0.7599 | 3.9597 | 1.980 |
| 12:00-12:30 | D | 5/5 |  | 0.7577 | 0.7577 | 4 | 4 | 0.000 / 0.000 | 0.7577 / 0.7577 | 3.9553 | 1.978 |
| 12:30-13:00 | D | 5/5 |  | 0.7637 | 0.7637 | 4 | 4 | 0.000 / 0.000 | 0.7637 / 0.7637 | 3.9674 | 1.984 |
| 13:00-13:30 | D | 5/5 |  | 0.7604 | 0.7604 | 4 | 4 | 0.000 / 0.000 | 0.7604 / 0.7604 | 3.9608 | 1.980 |
| 13:30-14:00 | D | 5/5 |  | 0.7517 | 0.7517 | 4 | 4 | 0.000 / 0.000 | 0.7517 / 0.7517 | 3.9435 | 1.972 |
| 14:00-14:30 | D | 5/5 |  | 0.7376 | 0.7376 | 4 | 4 | 0.000 / 0.000 | 0.7376 / 0.7376 | 3.9152 | 1.958 |
| 14:30-15:00 | D | 5/5 |  | 0.7719 | 0.7719 | 4 | 4 | 0.000 / 0.000 | 0.7719 / 0.7719 | 3.9839 | 1.992 |
| 15:00-15:30 |  | 5/5 |  | 1.0312 | 1.0312 | 3 | 3 | 0.000 / 0.000 | 1.0312 / 1.0312 | 4.5024 | 2.251 |
| 15:30-16:00 |  | 5/5 |  | 1.1288 | 1.1288 | 3 | 3 | 0.000 / 0.000 | 1.1288 / 1.1288 | 4.6975 | 2.349 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/MYM_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 86db7546e259613832d843823ba8f3ee99257ebc59fda8dbf860d260380165c4 (3,073,420 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MYM_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 54c96695f1706f5f31fbeaddbaab5ff01553d5965b9cdfb7ec194f52ae3c55af (2,072,193 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MYM_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 596b4c7b6d9b1d566beee37fcb86577f2e6333ddc96af80224b402140e9beede (4,123,555 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MYM_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` fe499f8cbee134833ed412ab8488387d6c1a2318f86d6b8c3121782aadc1d3f7 (6,428,538 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/MYM_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 22574474b55c7e460f64c45cd9d69f03f7e8b38a44b0fe43727f96a9112d8cea (2,930,528 records)

### NG (energy)

Tick 0.001 (vendor units 0.001, factor 1), tick value $10.0; commission $4.22 round turn = 0.4220 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 0.9928, sell 0.9928 ticks (round turn inside a window 2.4076 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.9928 | 0.9928 | 3 | 3 | 0.000 / 0.000 | 0.9928 / 0.9928 | 2.4076 | 24.076 |
| 17:30-18:00 |  | 5/5 |  | 0.8193 | 0.8193 | 3 | 3 | 0.000 / 0.000 | 0.8193 / 0.8193 | 2.0605 | 20.605 |
| 18:00-18:30 |  | 5/5 |  | 0.8044 | 0.8044 | 3 | 3 | 0.000 / 0.000 | 0.8044 / 0.8044 | 2.0308 | 20.308 |
| 18:30-19:00 |  | 5/5 |  | 0.8185 | 0.8185 | 3 | 3 | 0.000 / 0.000 | 0.8185 / 0.8185 | 2.0590 | 20.590 |
| 19:00-19:30 |  | 5/5 |  | 0.8752 | 0.8752 | 3 | 3 | 0.000 / 0.000 | 0.8752 / 0.8752 | 2.1724 | 21.724 |
| 19:30-20:00 |  | 5/5 |  | 0.8730 | 0.8730 | 3 | 3 | 0.000 / 0.000 | 0.8730 / 0.8730 | 2.1680 | 21.680 |
| 20:00-20:30 |  | 5/5 |  | 0.8359 | 0.8359 | 3 | 3 | 0.000 / 0.000 | 0.8359 / 0.8359 | 2.0938 | 20.938 |
| 20:30-21:00 |  | 5/5 |  | 0.7245 | 0.7245 | 3 | 3 | 0.000 / 0.000 | 0.7245 / 0.7245 | 1.8709 | 18.709 |
| 21:00-21:30 |  | 5/5 |  | 0.7980 | 0.7980 | 3 | 3 | 0.000 / 0.000 | 0.7980 / 0.7980 | 2.0181 | 20.181 |
| 21:30-22:00 |  | 5/5 |  | 0.7446 | 0.7446 | 3 | 3 | 0.000 / 0.000 | 0.7446 / 0.7446 | 1.9112 | 19.112 |
| 22:00-22:30 |  | 5/5 |  | 0.7467 | 0.7467 | 3 | 3 | 0.000 / 0.000 | 0.7467 / 0.7467 | 1.9153 | 19.153 |
| 22:30-23:00 |  | 5/5 |  | 0.7394 | 0.7394 | 4 | 4 | 0.000 / 0.000 | 0.7394 / 0.7394 | 1.9007 | 19.007 |
| 23:00-23:30 |  | 5/5 |  | 0.7103 | 0.7103 | 4 | 3 | 0.000 / 0.000 | 0.7103 / 0.7103 | 1.8427 | 18.427 |
| 23:30-00:00 |  | 5/5 |  | 0.7167 | 0.7167 | 4 | 4 | 0.000 / 0.000 | 0.7167 / 0.7167 | 1.8554 | 18.554 |
| 00:00-00:30 |  | 5/5 |  | 0.7508 | 0.7508 | 3 | 3 | 0.000 / 0.000 | 0.7508 / 0.7508 | 1.9236 | 19.236 |
| 00:30-01:00 |  | 5/5 |  | 0.7526 | 0.7526 | 3 | 4 | 0.000 / 0.000 | 0.7526 / 0.7526 | 1.9273 | 19.273 |
| 01:00-01:30 |  | 5/5 |  | 0.8126 | 0.8126 | 3 | 3 | 0.000 / 0.000 | 0.8126 / 0.8126 | 2.0471 | 20.471 |
| 01:30-02:00 |  | 5/5 |  | 0.8119 | 0.8119 | 3 | 3 | 0.000 / 0.000 | 0.8119 / 0.8119 | 2.0459 | 20.459 |
| 02:00-02:30 |  | 5/5 |  | 0.7838 | 0.7838 | 3 | 4 | 0.000 / 0.000 | 0.7838 / 0.7838 | 1.9896 | 19.896 |
| 02:30-03:00 |  | 5/5 |  | 0.7331 | 0.7331 | 4 | 4 | 0.000 / 0.000 | 0.7331 / 0.7331 | 1.8882 | 18.882 |
| 03:00-03:30 |  | 5/5 |  | 0.7529 | 0.7529 | 4 | 4 | 0.000 / 0.000 | 0.7529 / 0.7529 | 1.9278 | 19.278 |
| 03:30-04:00 |  | 5/5 |  | 0.7683 | 0.7683 | 4 | 4 | 0.000 / 0.000 | 0.7683 / 0.7683 | 1.9587 | 19.587 |
| 04:00-04:30 |  | 5/5 |  | 0.7615 | 0.7615 | 4 | 4 | 0.000 / 0.000 | 0.7615 / 0.7615 | 1.9450 | 19.450 |
| 04:30-05:00 |  | 5/5 |  | 0.7495 | 0.7495 | 3 | 4 | 0.000 / 0.000 | 0.7495 / 0.7495 | 1.9209 | 19.209 |
| 05:00-05:30 |  | 5/5 |  | 0.7267 | 0.7267 | 4 | 4 | 0.000 / 0.000 | 0.7267 / 0.7267 | 1.8754 | 18.754 |
| 05:30-06:00 |  | 5/5 |  | 0.7662 | 0.7662 | 3 | 4 | 0.000 / 0.000 | 0.7662 / 0.7662 | 1.9545 | 19.545 |
| 06:00-06:30 |  | 5/5 |  | 0.7140 | 0.7140 | 3 | 4 | 0.000 / 0.000 | 0.7140 / 0.7140 | 1.8500 | 18.500 |
| 06:30-07:00 |  | 5/5 |  | 0.7145 | 0.7145 | 3 | 4 | 0.000 / 0.000 | 0.7145 / 0.7145 | 1.8511 | 18.511 |
| 07:00-07:30 |  | 5/5 |  | 0.7043 | 0.7043 | 4 | 4 | 0.000 / 0.000 | 0.7043 / 0.7043 | 1.8305 | 18.305 |
| 07:30-08:00 |  | 5/5 |  | 0.6937 | 0.6937 | 4 | 4 | 0.000 / 0.000 | 0.6937 / 0.6937 | 1.8094 | 18.094 |
| 08:00-08:30 | D | 5/5 |  | 0.6235 | 0.6235 | 5 | 5 | 0.000 / 0.000 | 0.6235 / 0.6235 | 1.6690 | 16.690 |
| 08:30-09:00 | D | 5/5 |  | 0.6315 | 0.6315 | 4 | 5 | 0.000 / 0.000 | 0.6315 / 0.6315 | 1.6849 | 16.849 |
| 09:00-09:30 | D | 5/5 |  | 0.6147 | 0.6147 | 5 | 5 | 0.000 / 0.000 | 0.6147 / 0.6147 | 1.6514 | 16.514 |
| 09:30-10:00 | D | 5/5 |  | 0.6250 | 0.6250 | 5 | 5 | 0.000 / 0.000 | 0.6250 / 0.6250 | 1.6719 | 16.719 |
| 10:00-10:30 | D | 5/5 |  | 0.6044 | 0.6044 | 5 | 5 | 0.000 / 0.000 | 0.6044 / 0.6044 | 1.6308 | 16.308 |
| 10:30-11:00 | D | 5/5 |  | 0.6296 | 0.6296 | 5 | 5 | 0.000 / 0.000 | 0.6296 / 0.6296 | 1.6813 | 16.813 |
| 11:00-11:30 | D | 5/5 |  | 0.6321 | 0.6321 | 5 | 5 | 0.000 / 0.000 | 0.6321 / 0.6321 | 1.6862 | 16.862 |
| 11:30-12:00 | D | 5/5 |  | 0.6320 | 0.6320 | 5 | 5 | 0.000 / 0.000 | 0.6320 / 0.6320 | 1.6860 | 16.860 |
| 12:00-12:30 | D | 5/5 |  | 0.6270 | 0.6270 | 5 | 5 | 0.000 / 0.000 | 0.6270 / 0.6270 | 1.6759 | 16.759 |
| 12:30-13:00 | D | 5/5 |  | 0.6242 | 0.6242 | 5 | 5 | 0.000 / 0.000 | 0.6242 / 0.6242 | 1.6704 | 16.704 |
| 13:00-13:30 | D | 5/5 |  | 0.6312 | 0.6312 | 6 | 5 | 0.000 / 0.000 | 0.6312 / 0.6312 | 1.6844 | 16.844 |
| 13:30-14:00 |  | 5/5 |  | 0.6059 | 0.6059 | 6 | 6 | 0.000 / 0.000 | 0.6059 / 0.6059 | 1.6338 | 16.338 |
| 14:00-14:30 |  | 5/5 |  | 0.6152 | 0.6152 | 5 | 6 | 0.000 / 0.000 | 0.6152 / 0.6152 | 1.6523 | 16.523 |
| 14:30-15:00 |  | 5/5 |  | 0.6153 | 0.6153 | 6 | 7 | 0.000 / 0.000 | 0.6153 / 0.6153 | 1.6526 | 16.526 |
| 15:00-15:30 |  | 5/5 |  | 0.7104 | 0.7104 | 4 | 5 | 0.000 / 0.000 | 0.7104 / 0.7104 | 1.8429 | 18.429 |
| 15:30-16:00 |  | 5/5 |  | 0.7030 | 0.7030 | 4 | 4 | 0.000 / 0.000 | 0.7030 / 0.7030 | 1.8280 | 18.280 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/NG_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 589c120f88c87fbc54e55f4deff45d4cfae09a70f8b673ed98175625151bccaf (444,290 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NG_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 7dff5e08d545fe55bd17dff8cfc9c728d98f0c78fbc893f6eee9cf7ee6d5c5f3 (330,226 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NG_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` defda75b8b704f2c9a5fbc28f333c97e7f88bd12eed1996e97037c1d4b65adf6 (534,475 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NG_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 5a1ea2df0d90340657945de13c5d4fb163e9f15c785e34d78e78778dd4fc7127 (362,006 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NG_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` e59e99dfa957c8c8024ef5fde7f23d4a6bc295c3ebc89a1b84e99574fd293f7c (224,736 records)

### NQ (equity)

Tick 0.25 (vendor units 0.25, factor 1), tick value $5.0; commission $3.78 round turn = 0.7560 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 2.2998, sell 2.2998 ticks (round turn inside a window 5.3557 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 2.2998 | 2.2998 | 2 | 1 | 0.000 / 0.000 | 2.2998 / 2.2998 | 5.3557 | 26.778 |
| 17:30-18:00 |  | 5/5 |  | 1.5956 | 1.5956 | 1 | 1 | 0.000 / 0.000 | 1.5956 / 1.5956 | 3.9472 | 19.736 |
| 18:00-18:30 |  | 5/5 |  | 1.5681 | 1.5681 | 1 | 1 | 0.000 / 0.000 | 1.5681 / 1.5681 | 3.8922 | 19.461 |
| 18:30-19:00 |  | 5/5 |  | 1.5522 | 1.5522 | 1 | 1 | 0.000 / 0.000 | 1.5522 / 1.5522 | 3.8605 | 19.302 |
| 19:00-19:30 |  | 5/5 |  | 1.5639 | 1.5639 | 1 | 1 | 0.000 / 0.000 | 1.5639 / 1.5639 | 3.8837 | 19.419 |
| 19:30-20:00 |  | 5/5 |  | 1.4816 | 1.4816 | 1 | 1 | 0.000 / 0.000 | 1.4816 / 1.4816 | 3.7192 | 18.596 |
| 20:00-20:30 |  | 5/5 |  | 1.4502 | 1.4502 | 1 | 1 | 0.000 / 0.000 | 1.4502 / 1.4502 | 3.6564 | 18.282 |
| 20:30-21:00 |  | 5/5 |  | 1.4971 | 1.4971 | 1 | 1 | 0.000 / 0.000 | 1.4971 / 1.4971 | 3.7503 | 18.751 |
| 21:00-21:30 |  | 5/5 |  | 1.4345 | 1.4345 | 1 | 1 | 0.000 / 0.000 | 1.4345 / 1.4345 | 3.6250 | 18.125 |
| 21:30-22:00 |  | 5/5 |  | 1.4169 | 1.4169 | 1 | 1 | 0.000 / 0.000 | 1.4169 / 1.4169 | 3.5898 | 17.949 |
| 22:00-22:30 |  | 5/5 |  | 1.4395 | 1.4395 | 1 | 1 | 0.000 / 0.000 | 1.4395 / 1.4395 | 3.6351 | 18.175 |
| 22:30-23:00 |  | 5/5 |  | 1.4519 | 1.4519 | 1 | 1 | 0.000 / 0.000 | 1.4519 / 1.4519 | 3.6598 | 18.299 |
| 23:00-23:30 |  | 5/5 |  | 1.4917 | 1.4917 | 1 | 1 | 0.000 / 0.000 | 1.4917 / 1.4917 | 3.7394 | 18.697 |
| 23:30-00:00 |  | 5/5 |  | 1.4376 | 1.4376 | 1 | 1 | 0.000 / 0.000 | 1.4376 / 1.4376 | 3.6312 | 18.156 |
| 00:00-00:30 |  | 5/5 |  | 1.5121 | 1.5121 | 1 | 1 | 0.000 / 0.000 | 1.5121 / 1.5121 | 3.7803 | 18.901 |
| 00:30-01:00 |  | 5/5 |  | 1.4395 | 1.4395 | 1 | 1 | 0.000 / 0.000 | 1.4395 / 1.4395 | 3.6350 | 18.175 |
| 01:00-01:30 |  | 5/5 |  | 1.4694 | 1.4694 | 1 | 1 | 0.000 / 0.000 | 1.4694 / 1.4694 | 3.6949 | 18.474 |
| 01:30-02:00 |  | 5/5 |  | 1.4843 | 1.4843 | 1 | 1 | 0.000 / 0.000 | 1.4843 / 1.4843 | 3.7245 | 18.623 |
| 02:00-02:30 |  | 5/5 |  | 1.4756 | 1.4756 | 1 | 1 | 0.000 / 0.000 | 1.4756 / 1.4756 | 3.7073 | 18.536 |
| 02:30-03:00 |  | 5/5 |  | 1.4982 | 1.4982 | 1 | 1 | 0.000 / 0.000 | 1.4982 / 1.4982 | 3.7523 | 18.762 |
| 03:00-03:30 |  | 5/5 |  | 1.5358 | 1.5358 | 1 | 1 | 0.000 / 0.000 | 1.5358 / 1.5358 | 3.8276 | 19.138 |
| 03:30-04:00 |  | 5/5 |  | 1.4910 | 1.4910 | 1 | 1 | 0.000 / 0.000 | 1.4910 / 1.4910 | 3.7380 | 18.690 |
| 04:00-04:30 |  | 5/5 |  | 1.6059 | 1.6059 | 1 | 1 | 0.000 / 0.000 | 1.6059 / 1.6059 | 3.9678 | 19.839 |
| 04:30-05:00 |  | 5/5 |  | 1.5097 | 1.5097 | 1 | 1 | 0.000 / 0.000 | 1.5097 / 1.5097 | 3.7754 | 18.877 |
| 05:00-05:30 |  | 5/5 |  | 1.4895 | 1.4895 | 1 | 1 | 0.000 / 0.000 | 1.4895 / 1.4895 | 3.7349 | 18.675 |
| 05:30-06:00 |  | 5/5 |  | 1.5141 | 1.5141 | 1 | 1 | 0.000 / 0.000 | 1.5141 / 1.5141 | 3.7841 | 18.921 |
| 06:00-06:30 |  | 5/5 |  | 1.5037 | 1.5037 | 1 | 1 | 0.000 / 0.000 | 1.5037 / 1.5037 | 3.7634 | 18.817 |
| 06:30-07:00 |  | 5/5 |  | 1.5533 | 1.5533 | 1 | 1 | 0.000 / 0.000 | 1.5533 / 1.5533 | 3.8625 | 19.313 |
| 07:00-07:30 |  | 5/5 |  | 1.4510 | 1.4510 | 1 | 1 | 0.000 / 0.000 | 1.4510 / 1.4510 | 3.6580 | 18.290 |
| 07:30-08:00 |  | 5/5 |  | 1.4026 | 1.4026 | 2 | 2 | 0.000 / 0.000 | 1.4026 / 1.4026 | 3.5613 | 17.806 |
| 08:00-08:30 |  | 5/5 |  | 1.2218 | 1.2218 | 2 | 2 | 0.000 / 0.000 | 1.2218 / 1.2218 | 3.1995 | 15.998 |
| 08:30-09:00 | D | 5/5 |  | 1.3878 | 1.3878 | 2 | 2 | 0.000 / 0.000 | 1.3878 / 1.3878 | 3.5317 | 17.658 |
| 09:00-09:30 | D | 5/5 |  | 1.2798 | 1.2798 | 2 | 2 | 0.000 / 0.000 | 1.2798 / 1.2798 | 3.3156 | 16.578 |
| 09:30-10:00 | D | 5/5 |  | 1.2413 | 1.2413 | 2 | 2 | 0.000 / 0.000 | 1.2413 / 1.2413 | 3.2387 | 16.193 |
| 10:00-10:30 | D | 5/5 |  | 1.2115 | 1.2115 | 2 | 2 | 0.000 / 0.000 | 1.2115 / 1.2115 | 3.1791 | 15.895 |
| 10:30-11:00 | D | 5/5 |  | 1.1848 | 1.1848 | 3 | 3 | 0.000 / 0.000 | 1.1848 / 1.1848 | 3.1255 | 15.628 |
| 11:00-11:30 | D | 5/5 |  | 1.1776 | 1.1776 | 3 | 3 | 0.000 / 0.000 | 1.1776 / 1.1776 | 3.1112 | 15.556 |
| 11:30-12:00 | D | 5/5 |  | 1.1438 | 1.1438 | 3 | 3 | 0.000 / 0.000 | 1.1438 / 1.1438 | 3.0437 | 15.218 |
| 12:00-12:30 | D | 5/5 |  | 1.1558 | 1.1558 | 3 | 3 | 0.000 / 0.000 | 1.1558 / 1.1558 | 3.0676 | 15.338 |
| 12:30-13:00 | D | 5/5 |  | 1.1103 | 1.1103 | 3 | 3 | 0.000 / 0.000 | 1.1103 / 1.1103 | 2.9766 | 14.883 |
| 13:00-13:30 | D | 5/5 |  | 1.1096 | 1.1096 | 3 | 3 | 0.000 / 0.000 | 1.1096 / 1.1096 | 2.9753 | 14.876 |
| 13:30-14:00 | D | 5/5 |  | 1.1141 | 1.1141 | 3 | 3 | 0.000 / 0.000 | 1.1141 / 1.1141 | 2.9843 | 14.921 |
| 14:00-14:30 | D | 5/5 |  | 1.0911 | 1.0911 | 3 | 3 | 0.000 / 0.000 | 1.0911 / 1.0911 | 2.9383 | 14.691 |
| 14:30-15:00 | D | 5/5 |  | 1.0961 | 1.0961 | 3 | 3 | 0.000 / 0.000 | 1.0961 / 1.0961 | 2.9481 | 14.741 |
| 15:00-15:30 |  | 5/5 |  | 1.1087 | 1.1087 | 3 | 3 | 0.000 / 0.000 | 1.1087 / 1.1087 | 2.9734 | 14.867 |
| 15:30-16:00 |  | 5/5 |  | 1.1368 | 1.1368 | 2 | 2 | 0.000 / 0.000 | 1.1368 / 1.1368 | 3.0295 | 15.148 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/NQ_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` c19716b43d07c47b3819a32ed9db3b2a7886f6ece602a31695894f1e75079e3b (6,682,205 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NQ_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 2a0bcd049436fd527c9d740e703339ca575a301e29f38a15446cc315c5a5c499 (5,415,772 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NQ_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 3108ffbfc867894fa2d6ef3e7668ec6bf2b1a4f5345ac49e58f6a7c2b6745a0a (12,787,396 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NQ_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 4e741c09248f82f6b348d5dc2177193989ba800e4bd3c54485ae590d1add9b24 (11,241,308 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/NQ_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 7aeb8d80269e014e01a0dfbaa9fd33e23977b7d59c207145b041e66459fb29e1 (8,049,830 records)

### QG (energy)

Tick 0.005 (vendor units 0.005, factor 1), tick value $12.5; commission $2.02 round turn = 0.1616 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 0.7736, sell 0.7736 ticks (round turn inside a window 1.7088 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.7736 | 0.7736 | 6 | 4 | 0.000 / 0.000 | 0.7736 / 0.7736 | 1.7088 | 21.360 |
| 17:30-18:00 |  | 5/5 |  | 0.6082 | 0.6082 | 7 | 7 | 0.000 / 0.000 | 0.6082 / 0.6082 | 1.3781 | 17.226 |
| 18:00-18:30 |  | 5/5 |  | 0.6518 | 0.6518 | 8 | 8 | 0.000 / 0.000 | 0.6518 / 0.6518 | 1.4652 | 18.315 |
| 18:30-19:00 |  | 5/5 |  | 0.6644 | 0.6644 | 7 | 6 | 0.000 / 0.000 | 0.6644 / 0.6644 | 1.4903 | 18.629 |
| 19:00-19:30 |  | 5/5 |  | 0.6657 | 0.6657 | 7 | 6 | 0.000 / 0.000 | 0.6657 / 0.6657 | 1.4929 | 18.661 |
| 19:30-20:00 |  | 5/5 |  | 0.6166 | 0.6166 | 7 | 6 | 0.000 / 0.000 | 0.6166 / 0.6166 | 1.3948 | 17.435 |
| 20:00-20:30 |  | 5/5 |  | 0.5973 | 0.5973 | 7 | 7 | 0.000 / 0.000 | 0.5973 / 0.5973 | 1.3561 | 16.952 |
| 20:30-21:00 |  | 5/5 |  | 0.6313 | 0.6313 | 9 | 7 | 0.000 / 0.000 | 0.6313 / 0.6313 | 1.4241 | 17.801 |
| 21:00-21:30 |  | 5/5 |  | 0.7158 | 0.7158 | 12 | 7 | 0.000 / 0.000 | 0.7158 / 0.7158 | 1.5932 | 19.915 |
| 21:30-22:00 |  | 5/5 |  | 0.6730 | 0.6730 | 7 | 8 | 0.000 / 0.000 | 0.6730 / 0.6730 | 1.5076 | 18.845 |
| 22:00-22:30 |  | 5/5 |  | 0.6551 | 0.6551 | 9 | 7 | 0.000 / 0.000 | 0.6551 / 0.6551 | 1.4718 | 18.398 |
| 22:30-23:00 |  | 5/5 |  | 0.6474 | 0.6474 | 8 | 8 | 0.000 / 0.000 | 0.6474 / 0.6474 | 1.4563 | 18.204 |
| 23:00-23:30 |  | 5/5 |  | 0.6663 | 0.6663 | 9 | 8 | 0.000 / 0.000 | 0.6663 / 0.6663 | 1.4942 | 18.678 |
| 23:30-00:00 |  | 5/5 |  | 0.6016 | 0.6016 | 8 | 6 | 0.000 / 0.000 | 0.6016 / 0.6016 | 1.3648 | 17.060 |
| 00:00-00:30 |  | 5/5 |  | 0.6391 | 0.6391 | 6 | 7 | 0.000 / 0.000 | 0.6391 / 0.6391 | 1.4398 | 17.998 |
| 00:30-01:00 |  | 5/5 |  | 0.7054 | 0.7054 | 6 | 8 | 0.000 / 0.000 | 0.7054 / 0.7054 | 1.5724 | 19.655 |
| 01:00-01:30 |  | 5/5 |  | 0.6357 | 0.6357 | 7 | 6 | 0.000 / 0.000 | 0.6357 / 0.6357 | 1.4331 | 17.913 |
| 01:30-02:00 |  | 5/5 |  | 0.6313 | 0.6313 | 7 | 9 | 0.000 / 0.000 | 0.6313 / 0.6313 | 1.4243 | 17.804 |
| 02:00-02:30 |  | 5/5 |  | 0.5991 | 0.5991 | 9 | 9 | 0.000 / 0.000 | 0.5991 / 0.5991 | 1.3599 | 16.998 |
| 02:30-03:00 |  | 5/5 |  | 0.6079 | 0.6079 | 8 | 8 | 0.000 / 0.000 | 0.6079 / 0.6079 | 1.3774 | 17.217 |
| 03:00-03:30 |  | 5/5 |  | 0.5907 | 0.5907 | 8 | 8 | 0.000 / 0.000 | 0.5907 / 0.5907 | 1.3431 | 16.788 |
| 03:30-04:00 |  | 5/5 |  | 0.6023 | 0.6023 | 8 | 8 | 0.000 / 0.000 | 0.6023 / 0.6023 | 1.3662 | 17.077 |
| 04:00-04:30 |  | 5/5 |  | 0.6239 | 0.6239 | 9 | 9 | 0.000 / 0.000 | 0.6239 / 0.6239 | 1.4093 | 17.617 |
| 04:30-05:00 |  | 5/5 |  | 0.5950 | 0.5950 | 10 | 8 | 0.000 / 0.000 | 0.5950 / 0.5950 | 1.3516 | 16.894 |
| 05:00-05:30 |  | 5/5 |  | 0.6108 | 0.6108 | 8 | 9 | 0.000 / 0.000 | 0.6108 / 0.6108 | 1.3832 | 17.290 |
| 05:30-06:00 |  | 5/5 |  | 0.5887 | 0.5887 | 8 | 8 | 0.000 / 0.000 | 0.5887 / 0.5887 | 1.3389 | 16.737 |
| 06:00-06:30 |  | 5/5 |  | 0.6191 | 0.6191 | 9 | 9 | 0.000 / 0.000 | 0.6191 / 0.6191 | 1.3997 | 17.496 |
| 06:30-07:00 |  | 5/5 |  | 0.6390 | 0.6390 | 9 | 9 | 0.000 / 0.000 | 0.6390 / 0.6390 | 1.4396 | 17.994 |
| 07:00-07:30 |  | 5/5 |  | 0.6203 | 0.6203 | 9 | 8 | 0.000 / 0.000 | 0.6203 / 0.6203 | 1.4023 | 17.528 |
| 07:30-08:00 |  | 5/5 |  | 0.6040 | 0.6040 | 9 | 8 | 0.000 / 0.000 | 0.6040 / 0.6040 | 1.3697 | 17.121 |
| 08:00-08:30 | D | 5/5 |  | 0.6132 | 0.6132 | 9 | 10 | 0.000 / 0.000 | 0.6132 / 0.6132 | 1.3879 | 17.349 |
| 08:30-09:00 | D | 5/5 |  | 0.5865 | 0.5865 | 9 | 10 | 0.000 / 0.000 | 0.5865 / 0.5865 | 1.3347 | 16.683 |
| 09:00-09:30 | D | 5/5 |  | 0.5884 | 0.5884 | 10 | 10 | 0.000 / 0.000 | 0.5884 / 0.5884 | 1.3384 | 16.731 |
| 09:30-10:00 | D | 5/5 |  | 0.6207 | 0.6207 | 10 | 10 | 0.000 / 0.000 | 0.6207 / 0.6207 | 1.4030 | 17.538 |
| 10:00-10:30 | D | 5/5 |  | 0.6244 | 0.6244 | 10 | 11 | 0.000 / 0.000 | 0.6244 / 0.6244 | 1.4105 | 17.631 |
| 10:30-11:00 | D | 5/5 |  | 0.6106 | 0.6106 | 10 | 9 | 0.000 / 0.000 | 0.6106 / 0.6106 | 1.3828 | 17.285 |
| 11:00-11:30 | D | 5/5 |  | 0.6104 | 0.6104 | 10 | 9 | 0.000 / 0.000 | 0.6104 / 0.6104 | 1.3823 | 17.279 |
| 11:30-12:00 | D | 5/5 |  | 0.5991 | 0.5991 | 9 | 10 | 0.000 / 0.000 | 0.5991 / 0.5991 | 1.3599 | 16.998 |
| 12:00-12:30 | D | 5/5 |  | 0.6308 | 0.6308 | 10 | 9 | 0.000 / 0.000 | 0.6308 / 0.6308 | 1.4232 | 17.790 |
| 12:30-13:00 | D | 5/5 |  | 0.6101 | 0.6101 | 10 | 11 | 0.000 / 0.000 | 0.6101 / 0.6101 | 1.3817 | 17.272 |
| 13:00-13:30 | D | 5/5 |  | 0.6148 | 0.6148 | 10 | 10 | 0.000 / 0.000 | 0.6148 / 0.6148 | 1.3912 | 17.389 |
| 13:30-14:00 |  | 5/5 |  | 0.5962 | 0.5962 | 11 | 11 | 0.000 / 0.000 | 0.5962 / 0.5962 | 1.3540 | 16.924 |
| 14:00-14:30 |  | 5/5 |  | 0.5946 | 0.5946 | 10 | 9 | 0.000 / 0.000 | 0.5946 / 0.5946 | 1.3509 | 16.886 |
| 14:30-15:00 |  | 5/5 |  | 0.5962 | 0.5962 | 10 | 10 | 0.000 / 0.000 | 0.5962 / 0.5962 | 1.3540 | 16.925 |
| 15:00-15:30 |  | 5/5 |  | 0.6711 | 0.6711 | 11 | 9 | 0.000 / 0.000 | 0.6711 / 0.6711 | 1.5037 | 18.796 |
| 15:30-16:00 |  | 5/5 |  | 0.6618 | 0.6618 | 8 | 8 | 0.000 / 0.000 | 0.6618 / 0.6618 | 1.4852 | 18.565 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/QG_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` a3189c8bdbbbb8b80c1884d11055a2b369aadb90abe957b7e5bf564155341310 (78,532 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QG_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 7360e0e739541feea6c3245c4946a535c2517af0eed4e349153cd46f1054fc9a (58,105 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QG_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 0a9279c6bd31599a849d3498d1f259eefdfe8eef266a4820398bef4638a69e6b (129,859 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QG_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` c8f18a5f0b31af2f9156fb9022db33fec236155ad7472807d3c5e23c52e4c4f6 (72,936 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QG_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` e090ba49f89c0be5302ef37996ba0ec51c4f2e0e500dfaebf24664f5f922b088 (46,008 records)

### QM (energy)

Tick 0.025 (vendor units 0.025, factor 1), tick value $12.5; commission $3.42 round turn = 0.2736 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 1.3232, sell 1.3232 ticks (round turn inside a window 2.9201 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.1279 | 1.1279 | 2 | 3 | 0.000 / 0.000 | 1.1279 / 1.1279 | 2.5293 | 31.617 |
| 17:30-18:00 |  | 5/5 |  | 0.9394 | 0.9394 | 3 | 3 | 0.000 / 0.000 | 0.9394 / 0.9394 | 2.1524 | 26.905 |
| 18:00-18:30 |  | 5/5 |  | 0.8404 | 0.8404 | 3 | 3 | 0.000 / 0.000 | 0.8404 / 0.8404 | 1.9545 | 24.431 |
| 18:30-19:00 |  | 5/5 |  | 1.3232 | 1.3244 | 3 | 3 | 0.000 / 0.000 | 1.3232 / 1.3232 | 2.9201 | 36.501 |
| 19:00-19:30 |  | 5/5 |  | 0.8472 | 0.8472 | 4 | 3 | 0.000 / 0.000 | 0.8472 / 0.8472 | 1.9680 | 24.600 |
| 19:30-20:00 |  | 5/5 |  | 0.7682 | 0.7682 | 4 | 3 | 0.000 / 0.000 | 0.7682 / 0.7682 | 1.8100 | 22.625 |
| 20:00-20:30 |  | 5/5 |  | 0.6959 | 0.6959 | 3 | 3 | 0.000 / 0.000 | 0.6959 / 0.6959 | 1.6654 | 20.817 |
| 20:30-21:00 |  | 5/5 |  | 0.7006 | 0.7006 | 4 | 3 | 0.000 / 0.000 | 0.7006 / 0.7006 | 1.6747 | 20.934 |
| 21:00-21:30 |  | 5/5 |  | 0.6632 | 0.6632 | 4 | 3 | 0.000 / 0.000 | 0.6632 / 0.6632 | 1.6000 | 20.000 |
| 21:30-22:00 |  | 5/5 |  | 0.6987 | 0.6987 | 4 | 4 | 0.000 / 0.000 | 0.6987 / 0.6987 | 1.6710 | 20.888 |
| 22:00-22:30 |  | 5/5 |  | 0.6752 | 0.6752 | 4 | 3 | 0.000 / 0.000 | 0.6752 / 0.6752 | 1.6240 | 20.300 |
| 22:30-23:00 |  | 5/5 |  | 0.6606 | 0.6606 | 4 | 4 | 0.000 / 0.000 | 0.6606 / 0.6606 | 1.5949 | 19.936 |
| 23:00-23:30 |  | 5/5 |  | 0.6383 | 0.6383 | 3 | 4 | 0.000 / 0.000 | 0.6383 / 0.6383 | 1.5502 | 19.377 |
| 23:30-00:00 |  | 5/5 |  | 0.6558 | 0.6558 | 3 | 3 | 0.000 / 0.000 | 0.6558 / 0.6558 | 1.5851 | 19.814 |
| 00:00-00:30 |  | 5/5 |  | 0.6773 | 0.6773 | 4 | 3 | 0.000 / 0.000 | 0.6773 / 0.6773 | 1.6281 | 20.351 |
| 00:30-01:00 |  | 5/5 |  | 0.6667 | 0.6667 | 3 | 3 | 0.000 / 0.000 | 0.6667 / 0.6667 | 1.6070 | 20.087 |
| 01:00-01:30 |  | 5/5 |  | 0.6691 | 0.6691 | 3 | 3 | 0.000 / 0.000 | 0.6691 / 0.6691 | 1.6118 | 20.147 |
| 01:30-02:00 |  | 5/5 |  | 0.6648 | 0.6648 | 3 | 3 | 0.000 / 0.000 | 0.6648 / 0.6648 | 1.6033 | 20.041 |
| 02:00-02:30 |  | 5/5 |  | 0.6628 | 0.6628 | 4 | 4 | 0.000 / 0.000 | 0.6628 / 0.6628 | 1.5992 | 19.990 |
| 02:30-03:00 |  | 5/5 |  | 0.6467 | 0.6467 | 4 | 4 | 0.000 / 0.000 | 0.6467 / 0.6467 | 1.5670 | 19.588 |
| 03:00-03:30 |  | 5/5 |  | 0.6510 | 0.6510 | 4 | 4 | 0.000 / 0.000 | 0.6510 / 0.6510 | 1.5756 | 19.695 |
| 03:30-04:00 |  | 5/5 |  | 0.6456 | 0.6456 | 4 | 4 | 0.000 / 0.000 | 0.6456 / 0.6456 | 1.5648 | 19.560 |
| 04:00-04:30 |  | 5/5 |  | 0.6558 | 0.6558 | 4 | 4 | 0.000 / 0.000 | 0.6558 / 0.6558 | 1.5853 | 19.816 |
| 04:30-05:00 |  | 5/5 |  | 0.6684 | 0.6684 | 4 | 4 | 0.000 / 0.000 | 0.6684 / 0.6684 | 1.6105 | 20.131 |
| 05:00-05:30 |  | 5/5 |  | 0.6599 | 0.6599 | 4 | 4 | 0.000 / 0.000 | 0.6599 / 0.6599 | 1.5933 | 19.917 |
| 05:30-06:00 |  | 5/5 |  | 0.6629 | 0.6629 | 4 | 4 | 0.000 / 0.000 | 0.6629 / 0.6629 | 1.5995 | 19.994 |
| 06:00-06:30 |  | 5/5 |  | 0.6298 | 0.6298 | 4 | 4 | 0.000 / 0.000 | 0.6298 / 0.6298 | 1.5332 | 19.164 |
| 06:30-07:00 |  | 5/5 |  | 0.6652 | 0.6652 | 3 | 4 | 0.000 / 0.000 | 0.6652 / 0.6652 | 1.6041 | 20.051 |
| 07:00-07:30 |  | 5/5 |  | 0.6911 | 0.6911 | 3 | 4 | 0.000 / 0.000 | 0.6911 / 0.6911 | 1.6558 | 20.698 |
| 07:30-08:00 |  | 5/5 |  | 0.6745 | 0.6745 | 4 | 3 | 0.000 / 0.000 | 0.6745 / 0.6745 | 1.6225 | 20.281 |
| 08:00-08:30 | D | 5/5 |  | 0.6579 | 0.6579 | 3 | 3 | 0.000 / 0.000 | 0.6579 / 0.6579 | 1.5894 | 19.867 |
| 08:30-09:00 | D | 5/5 |  | 0.6309 | 0.6309 | 3 | 3 | 0.000 / 0.000 | 0.6309 / 0.6309 | 1.5355 | 19.194 |
| 09:00-09:30 | D | 5/5 |  | 0.6566 | 0.6566 | 3 | 3 | 0.000 / 0.000 | 0.6566 / 0.6566 | 1.5869 | 19.836 |
| 09:30-10:00 | D | 5/5 |  | 0.7044 | 0.7044 | 3 | 3 | 0.000 / 0.000 | 0.7044 / 0.7044 | 1.6825 | 21.031 |
| 10:00-10:30 | D | 5/5 |  | 0.6656 | 0.6656 | 3 | 3 | 0.000 / 0.000 | 0.6656 / 0.6656 | 1.6048 | 20.060 |
| 10:30-11:00 | D | 5/5 |  | 0.6593 | 0.6593 | 3 | 3 | 0.000 / 0.000 | 0.6593 / 0.6593 | 1.5922 | 19.903 |
| 11:00-11:30 | D | 5/5 |  | 0.6388 | 0.6388 | 3 | 3 | 0.000 / 0.000 | 0.6388 / 0.6388 | 1.5512 | 19.390 |
| 11:30-12:00 | D | 5/5 |  | 0.6874 | 0.6874 | 3 | 3 | 0.000 / 0.000 | 0.6874 / 0.6874 | 1.6484 | 20.605 |
| 12:00-12:30 | D | 5/5 |  | 0.6534 | 0.6534 | 4 | 4 | 0.000 / 0.000 | 0.6534 / 0.6534 | 1.5803 | 19.754 |
| 12:30-13:00 | D | 5/5 |  | 0.6651 | 0.6651 | 4 | 4 | 0.000 / 0.000 | 0.6651 / 0.6651 | 1.6038 | 20.048 |
| 13:00-13:30 | D | 5/5 |  | 0.6714 | 0.6714 | 3 | 4 | 0.000 / 0.000 | 0.6714 / 0.6714 | 1.6165 | 20.206 |
| 13:30-14:00 |  | 5/5 |  | 0.6590 | 0.6590 | 3 | 4 | 0.000 / 0.000 | 0.6590 / 0.6590 | 1.5916 | 19.896 |
| 14:00-14:30 |  | 5/5 |  | 0.6540 | 0.6540 | 3 | 3 | 0.000 / 0.000 | 0.6540 / 0.6540 | 1.5815 | 19.769 |
| 14:30-15:00 |  | 5/5 |  | 0.6370 | 0.6370 | 3 | 3 | 0.000 / 0.000 | 0.6370 / 0.6370 | 1.5477 | 19.346 |
| 15:00-15:30 |  | 5/5 |  | 0.7374 | 0.7374 | 3 | 3 | 0.000 / 0.000 | 0.7374 / 0.7374 | 1.7484 | 21.855 |
| 15:30-16:00 |  | 5/5 |  | 0.7433 | 0.7433 | 3 | 3 | 0.000 / 0.000 | 0.7433 / 0.7433 | 1.7601 | 22.002 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 8b34401f50225560aa54c399bef8b9b3b315c3bd33b04d40291444d6d1370f38 (159,105 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` c79a712461096788a31992485cb327275482f79623b0972d60433a6bf81fef01 (137,012 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` c5e6a1072fb72ba173adcef51f7f667b59782ce2e8ac4817b93672d3ec57b4f1 (131,620 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` a275559b3feba95c6da07d62768d467116a8faf7334ff3ead6965bc63ddf4948 (140,014 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` ba0dcabf4f81fdbbf6ba182cf3324cdda5efc9360f94949a08af1e51564eb0f9 (379,745 records)

### RB (energy)

Tick 0.0001 (vendor units 0.0001, factor 1), tick value $4.2; commission $4.02 round turn = 0.9571 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:00-13:30 CT.

Event-window one-side slippage: buy 10.5658, sell 10.5658 ticks (round turn inside a window 22.0887 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 10.5658 | 10.5658 | 2 | 2 | 0.000 / 0.000 | 10.5658 / 10.5658 | 22.0887 | 92.772 |
| 17:30-18:00 |  | 5/5 |  | 6.1231 | 6.1231 | 2 | 2 | 0.000 / 0.000 | 6.1231 / 6.1231 | 13.2034 | 55.454 |
| 18:00-18:30 |  | 5/5 |  | 5.6523 | 5.6523 | 1 | 2 | 0.000 / 0.000 | 5.6523 / 5.6523 | 12.2618 | 51.500 |
| 18:30-19:00 |  | 5/5 |  | 7.4895 | 7.4895 | 1 | 1 | 0.000 / 0.000 | 7.4895 / 7.4895 | 15.9362 | 66.932 |
| 19:00-19:30 |  | 5/5 |  | 4.5998 | 4.5998 | 1 | 1 | 0.000 / 0.000 | 4.5998 / 4.5998 | 10.1568 | 42.658 |
| 19:30-20:00 |  | 5/5 |  | 4.0673 | 4.0673 | 1 | 1 | 0.000 / 0.000 | 4.0673 / 4.0673 | 9.0918 | 38.185 |
| 20:00-20:30 |  | 5/5 |  | 4.2634 | 4.2634 | 1 | 1 | 0.000 / 0.000 | 4.2634 / 4.2634 | 9.4840 | 39.833 |
| 20:30-21:00 |  | 5/5 |  | 3.9607 | 3.9607 | 1 | 2 | 0.000 / 0.000 | 3.9607 / 3.9607 | 8.8785 | 37.290 |
| 21:00-21:30 |  | 5/5 |  | 4.0826 | 4.0826 | 1 | 1 | 0.000 / 0.000 | 4.0826 / 4.0826 | 9.1224 | 38.314 |
| 21:30-22:00 |  | 5/5 |  | 3.5072 | 3.5072 | 1 | 1 | 0.000 / 0.000 | 3.5072 / 3.5072 | 7.9715 | 33.480 |
| 22:00-22:30 |  | 5/5 |  | 3.7620 | 3.7620 | 1 | 1 | 0.000 / 0.000 | 3.7620 / 3.7620 | 8.4812 | 35.621 |
| 22:30-23:00 |  | 5/5 |  | 3.9486 | 3.9486 | 1 | 1 | 0.000 / 0.000 | 3.9486 / 3.9486 | 8.8543 | 37.188 |
| 23:00-23:30 |  | 5/5 |  | 3.9027 | 3.9027 | 1 | 1 | 0.000 / 0.000 | 3.9027 / 3.9027 | 8.7625 | 36.802 |
| 23:30-00:00 |  | 5/5 |  | 3.9004 | 3.9004 | 1 | 1 | 0.000 / 0.000 | 3.9004 / 3.9004 | 8.7580 | 36.784 |
| 00:00-00:30 |  | 5/5 |  | 3.9554 | 3.9554 | 2 | 1 | 0.000 / 0.000 | 3.9554 / 3.9554 | 8.8679 | 37.245 |
| 00:30-01:00 |  | 5/5 |  | 4.0288 | 4.0288 | 1 | 1 | 0.000 / 0.000 | 4.0288 / 4.0288 | 9.0147 | 37.862 |
| 01:00-01:30 |  | 5/5 |  | 3.8060 | 3.8060 | 1 | 1 | 0.000 / 0.000 | 3.8060 / 3.8060 | 8.5691 | 35.990 |
| 01:30-02:00 |  | 5/5 |  | 3.3780 | 3.3780 | 1 | 1 | 0.000 / 0.000 | 3.3780 / 3.3780 | 7.7132 | 32.396 |
| 02:00-02:30 |  | 5/5 |  | 2.9355 | 2.9355 | 1 | 1 | 0.000 / 0.000 | 2.9355 / 2.9355 | 6.8282 | 28.678 |
| 02:30-03:00 |  | 5/5 |  | 3.3690 | 3.3690 | 1 | 1 | 0.000 / 0.000 | 3.3690 / 3.3690 | 7.6951 | 32.319 |
| 03:00-03:30 |  | 5/5 |  | 3.1201 | 3.1201 | 1 | 1 | 0.000 / 0.000 | 3.1201 / 3.1201 | 7.1973 | 30.229 |
| 03:30-04:00 |  | 5/5 |  | 3.0163 | 3.0163 | 1 | 1 | 0.000 / 0.000 | 3.0163 / 3.0163 | 6.9898 | 29.357 |
| 04:00-04:30 |  | 5/5 |  | 3.2926 | 3.2926 | 1 | 1 | 0.000 / 0.000 | 3.2926 / 3.2926 | 7.5424 | 31.678 |
| 04:30-05:00 |  | 5/5 |  | 3.0298 | 3.0298 | 2 | 1 | 0.000 / 0.000 | 3.0298 / 3.0298 | 7.0167 | 29.470 |
| 05:00-05:30 |  | 5/5 |  | 3.2422 | 3.2422 | 2 | 1 | 0.000 / 0.000 | 3.2422 / 3.2422 | 7.4415 | 31.254 |
| 05:30-06:00 |  | 5/5 |  | 3.1570 | 3.1570 | 1 | 1 | 0.000 / 0.000 | 3.1570 / 3.1570 | 7.2712 | 30.539 |
| 06:00-06:30 |  | 5/5 |  | 2.8164 | 2.8164 | 1 | 1 | 0.000 / 0.000 | 2.8164 / 2.8164 | 6.5900 | 27.678 |
| 06:30-07:00 |  | 5/5 |  | 3.1411 | 3.1411 | 1 | 1 | 0.000 / 0.000 | 3.1411 / 3.1411 | 7.2393 | 30.405 |
| 07:00-07:30 |  | 5/5 |  | 2.8625 | 2.8625 | 1 | 1 | 0.000 / 0.000 | 2.8625 / 2.8625 | 6.6821 | 28.065 |
| 07:30-08:00 |  | 5/5 |  | 2.6279 | 2.6279 | 1 | 1 | 0.000 / 0.000 | 2.6279 / 2.6279 | 6.2129 | 26.094 |
| 08:00-08:30 | D | 5/5 |  | 2.2228 | 2.2228 | 1 | 1 | 0.000 / 0.000 | 2.2228 / 2.2228 | 5.4028 | 22.692 |
| 08:30-09:00 | D | 5/5 |  | 2.3108 | 2.3108 | 1 | 1 | 0.000 / 0.000 | 2.3108 / 2.3108 | 5.5787 | 23.431 |
| 09:00-09:30 | D | 5/5 |  | 2.4027 | 2.4027 | 1 | 1 | 0.000 / 0.000 | 2.4027 / 2.4027 | 5.7624 | 24.202 |
| 09:30-10:00 | D | 5/5 |  | 2.5928 | 2.5928 | 1 | 1 | 0.000 / 0.000 | 2.5928 / 2.5928 | 6.1428 | 25.800 |
| 10:00-10:30 | D | 5/5 |  | 2.2258 | 2.2258 | 1 | 1 | 0.000 / 0.000 | 2.2258 / 2.2258 | 5.4087 | 22.717 |
| 10:30-11:00 | D | 5/5 |  | 2.3075 | 2.3075 | 1 | 1 | 0.000 / 0.000 | 2.3075 / 2.3075 | 5.5721 | 23.403 |
| 11:00-11:30 | D | 5/5 |  | 2.3946 | 2.3946 | 1 | 1 | 0.000 / 0.000 | 2.3946 / 2.3946 | 5.7464 | 24.135 |
| 11:30-12:00 | D | 5/5 |  | 2.2830 | 2.2830 | 1 | 1 | 0.000 / 0.000 | 2.2830 / 2.2830 | 5.5232 | 23.197 |
| 12:00-12:30 | D | 5/5 |  | 2.0469 | 2.0469 | 1 | 1 | 0.000 / 0.000 | 2.0469 / 2.0469 | 5.0510 | 21.214 |
| 12:30-13:00 | D | 5/5 |  | 1.9912 | 1.9912 | 1 | 1 | 0.000 / 0.000 | 1.9912 / 1.9912 | 4.9396 | 20.746 |
| 13:00-13:30 | D | 5/5 |  | 2.2881 | 2.2881 | 1 | 1 | 0.000 / 0.000 | 2.2881 / 2.2881 | 5.5334 | 23.240 |
| 13:30-14:00 |  | 5/5 |  | 2.1487 | 2.1487 | 1 | 1 | 0.000 / 0.000 | 2.1487 / 2.1487 | 5.2546 | 22.069 |
| 14:00-14:30 |  | 5/5 |  | 2.3169 | 2.3169 | 1 | 1 | 0.000 / 0.000 | 2.3169 / 2.3169 | 5.5910 | 23.482 |
| 14:30-15:00 |  | 5/5 |  | 2.2688 | 2.2688 | 2 | 1 | 0.000 / 0.000 | 2.2688 / 2.2688 | 5.4947 | 23.078 |
| 15:00-15:30 |  | 5/5 |  | 2.6643 | 2.6643 | 2 | 1 | 0.000 / 0.000 | 2.6643 / 2.6643 | 6.2858 | 26.401 |
| 15:30-16:00 |  | 5/5 |  | 3.0068 | 3.0068 | 2 | 1 | 0.000 / 0.000 | 3.0068 / 3.0068 | 6.9708 | 29.277 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/RB_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 7a17947d9bf55caaf6b32df35f70bfed6a87952d9493817b8232d84cfb4dfaac (389,226 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RB_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 65806de5cf808818561967421f2fac51b3fc886468b3a28630cde0612811d583 (433,554 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RB_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 4f491fa38a8ad5c9447f8c20c5621f2550a16af78d94d7e113641eeab1bf2567 (373,402 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RB_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` eee4e4e1be2af062828c4b3ee7e80343c6f3f2953f07f02f84d4d784ad73ee0f (554,400 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RB_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` f84b401f5971afd9070ade48e4fada9528bf164584ab6d94e71e277b4ab9aef6 (1,423,256 records)

### RTY (equity)

Tick 0.10 (vendor units 0.10, factor 1), tick value $5.0; commission $3.78 round turn = 0.7560 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 1.5897, sell 1.5897 ticks (round turn inside a window 3.9354 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.5897 | 1.5897 | 2 | 2 | 0.000 / 0.000 | 1.5897 / 1.5897 | 3.9354 | 19.677 |
| 17:30-18:00 |  | 5/5 |  | 1.1784 | 1.1784 | 3 | 3 | 0.000 / 0.000 | 1.1784 / 1.1784 | 3.1129 | 15.564 |
| 18:00-18:30 |  | 5/5 |  | 1.1397 | 1.1397 | 3 | 3 | 0.000 / 0.000 | 1.1397 / 1.1397 | 3.0354 | 15.177 |
| 18:30-19:00 |  | 5/5 |  | 1.1213 | 1.1213 | 3 | 3 | 0.000 / 0.000 | 1.1213 / 1.1213 | 2.9985 | 14.993 |
| 19:00-19:30 |  | 5/5 |  | 1.1604 | 1.1604 | 3 | 3 | 0.000 / 0.000 | 1.1604 / 1.1604 | 3.0767 | 15.384 |
| 19:30-20:00 |  | 5/5 |  | 1.1218 | 1.1218 | 3 | 3 | 0.000 / 0.000 | 1.1218 / 1.1218 | 2.9996 | 14.998 |
| 20:00-20:30 |  | 5/5 |  | 1.0831 | 1.0831 | 3 | 3 | 0.000 / 0.000 | 1.0831 / 1.0831 | 2.9222 | 14.611 |
| 20:30-21:00 |  | 5/5 |  | 1.1126 | 1.1126 | 3 | 3 | 0.000 / 0.000 | 1.1126 / 1.1126 | 2.9811 | 14.906 |
| 21:00-21:30 |  | 5/5 |  | 1.0869 | 1.0869 | 3 | 3 | 0.000 / 0.000 | 1.0869 / 1.0869 | 2.9298 | 14.649 |
| 21:30-22:00 |  | 5/5 |  | 1.0861 | 1.0861 | 3 | 3 | 0.000 / 0.000 | 1.0861 / 1.0861 | 2.9281 | 14.641 |
| 22:00-22:30 |  | 5/5 |  | 1.1081 | 1.1081 | 3 | 3 | 0.000 / 0.000 | 1.1081 / 1.1081 | 2.9722 | 14.861 |
| 22:30-23:00 |  | 5/5 |  | 1.1374 | 1.1374 | 3 | 3 | 0.000 / 0.000 | 1.1374 / 1.1374 | 3.0309 | 15.154 |
| 23:00-23:30 |  | 5/5 |  | 1.1185 | 1.1185 | 3 | 3 | 0.000 / 0.000 | 1.1185 / 1.1185 | 2.9931 | 14.965 |
| 23:30-00:00 |  | 5/5 |  | 1.1343 | 1.1343 | 3 | 3 | 0.000 / 0.000 | 1.1343 / 1.1343 | 3.0247 | 15.123 |
| 00:00-00:30 |  | 5/5 |  | 1.1810 | 1.1810 | 3 | 3 | 0.000 / 0.000 | 1.1810 / 1.1810 | 3.1181 | 15.590 |
| 00:30-01:00 |  | 5/5 |  | 1.1211 | 1.1211 | 3 | 2 | 0.000 / 0.000 | 1.1211 / 1.1211 | 2.9983 | 14.991 |
| 01:00-01:30 |  | 5/5 |  | 1.1747 | 1.1747 | 3 | 3 | 0.000 / 0.000 | 1.1747 / 1.1747 | 3.1054 | 15.527 |
| 01:30-02:00 |  | 5/5 |  | 1.1435 | 1.1435 | 3 | 3 | 0.000 / 0.000 | 1.1435 / 1.1435 | 3.0429 | 15.215 |
| 02:00-02:30 |  | 5/5 |  | 1.1210 | 1.1210 | 3 | 3 | 0.000 / 0.000 | 1.1210 / 1.1210 | 2.9979 | 14.990 |
| 02:30-03:00 |  | 5/5 |  | 1.0966 | 1.0966 | 3 | 3 | 0.000 / 0.000 | 1.0966 / 1.0966 | 2.9492 | 14.746 |
| 03:00-03:30 |  | 5/5 |  | 1.1234 | 1.1234 | 3 | 3 | 0.000 / 0.000 | 1.1234 / 1.1234 | 3.0028 | 15.014 |
| 03:30-04:00 |  | 5/5 |  | 1.1386 | 1.1386 | 3 | 3 | 0.000 / 0.000 | 1.1386 / 1.1386 | 3.0333 | 15.166 |
| 04:00-04:30 |  | 5/5 |  | 1.2161 | 1.2161 | 3 | 3 | 0.000 / 0.000 | 1.2161 / 1.2161 | 3.1882 | 15.941 |
| 04:30-05:00 |  | 5/5 |  | 1.1371 | 1.1371 | 3 | 3 | 0.000 / 0.000 | 1.1371 / 1.1371 | 3.0302 | 15.151 |
| 05:00-05:30 |  | 5/5 |  | 1.0959 | 1.0959 | 3 | 3 | 0.000 / 0.000 | 1.0959 / 1.0959 | 2.9479 | 14.739 |
| 05:30-06:00 |  | 5/5 |  | 1.1075 | 1.1075 | 3 | 3 | 0.000 / 0.000 | 1.1075 / 1.1075 | 2.9710 | 14.855 |
| 06:00-06:30 |  | 5/5 |  | 1.1230 | 1.1230 | 3 | 3 | 0.000 / 0.000 | 1.1230 / 1.1230 | 3.0020 | 15.010 |
| 06:30-07:00 |  | 5/5 |  | 1.1255 | 1.1255 | 3 | 3 | 0.000 / 0.000 | 1.1255 / 1.1255 | 3.0070 | 15.035 |
| 07:00-07:30 |  | 5/5 |  | 1.0861 | 1.0861 | 4 | 4 | 0.000 / 0.000 | 1.0861 / 1.0861 | 2.9283 | 14.641 |
| 07:30-08:00 |  | 5/5 |  | 1.1046 | 1.1046 | 4 | 4 | 0.000 / 0.000 | 1.1046 / 1.1046 | 2.9653 | 14.826 |
| 08:00-08:30 |  | 5/5 |  | 0.9448 | 0.9448 | 5 | 5 | 0.000 / 0.000 | 0.9448 / 0.9448 | 2.6455 | 13.228 |
| 08:30-09:00 | D | 5/5 |  | 0.8846 | 0.8846 | 5 | 6 | 0.000 / 0.000 | 0.8846 / 0.8846 | 2.5252 | 12.626 |
| 09:00-09:30 | D | 5/5 |  | 0.8082 | 0.8082 | 5 | 5 | 0.000 / 0.000 | 0.8082 / 0.8082 | 2.3724 | 11.862 |
| 09:30-10:00 | D | 5/5 |  | 0.8304 | 0.8304 | 6 | 6 | 0.000 / 0.000 | 0.8304 / 0.8304 | 2.4168 | 12.084 |
| 10:00-10:30 | D | 5/5 |  | 0.7978 | 0.7978 | 6 | 6 | 0.000 / 0.000 | 0.7978 / 0.7978 | 2.3516 | 11.758 |
| 10:30-11:00 | D | 5/5 |  | 0.7999 | 0.7999 | 7 | 7 | 0.000 / 0.000 | 0.7999 / 0.7999 | 2.3558 | 11.779 |
| 11:00-11:30 | D | 5/5 |  | 0.8085 | 0.8085 | 7 | 6 | 0.000 / 0.000 | 0.8085 / 0.8085 | 2.3730 | 11.865 |
| 11:30-12:00 | D | 5/5 |  | 0.8260 | 0.8260 | 7 | 7 | 0.000 / 0.000 | 0.8260 / 0.8260 | 2.4080 | 12.040 |
| 12:00-12:30 | D | 5/5 |  | 0.8139 | 0.8139 | 7 | 6 | 0.000 / 0.000 | 0.8139 / 0.8139 | 2.3838 | 11.919 |
| 12:30-13:00 | D | 5/5 |  | 0.8003 | 0.8003 | 7 | 7 | 0.000 / 0.000 | 0.8003 / 0.8003 | 2.3566 | 11.783 |
| 13:00-13:30 | D | 5/5 |  | 0.7867 | 0.7867 | 7 | 7 | 0.000 / 0.000 | 0.7867 / 0.7867 | 2.3293 | 11.647 |
| 13:30-14:00 | D | 5/5 |  | 0.7677 | 0.7677 | 8 | 8 | 0.000 / 0.000 | 0.7677 / 0.7677 | 2.2914 | 11.457 |
| 14:00-14:30 | D | 5/5 |  | 0.7542 | 0.7542 | 8 | 8 | 0.000 / 0.000 | 0.7542 / 0.7542 | 2.2645 | 11.322 |
| 14:30-15:00 | D | 5/5 |  | 0.7425 | 0.7425 | 10 | 10 | 0.000 / 0.000 | 0.7425 / 0.7425 | 2.2410 | 11.205 |
| 15:00-15:30 |  | 5/5 |  | 0.7531 | 0.7531 | 10 | 10 | 0.000 / 0.000 | 0.7531 / 0.7531 | 2.2622 | 11.311 |
| 15:30-16:00 |  | 5/5 |  | 0.8433 | 0.8433 | 8 | 8 | 0.000 / 0.000 | 0.8433 / 0.8433 | 2.4426 | 12.213 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/RTY_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 45a1e2e5eff1dd07cd63289e52d1b029c7095573220a7a19e66373e3a36c0395 (2,639,910 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RTY_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 940fc3927294e6636a0b841bec71f4e78b4192f62d349349ba286fbf89dbff6d (2,272,169 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RTY_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` b65d5a836ad20f341fbd50f07099f5c8ff4e8de11441e59b8b9757d0103e0075 (3,493,922 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RTY_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 211533de0aae4a4b9a6726f9ef31615b3f9bceefad322be482f99770238a0f18 (3,474,661 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/RTY_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 8fed3d7917460f6e1ff42c62949a612c7056c0033f3408e89398816e381fdcbd (2,007,622 records)

### SI (metals)

Tick 0.005 (vendor units 0.005, factor 1), tick value $25.0; commission $4.32 round turn = 0.1728 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-12:25 CT.

Event-window one-side slippage: buy 2.5122, sell 2.5122 ticks (round turn inside a window 5.1972 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 2.5122 | 2.5122 | 2 | 2 | 0.000 / 0.000 | 2.5122 / 2.5122 | 5.1972 | 129.930 |
| 17:30-18:00 |  | 5/5 |  | 1.9923 | 1.9923 | 3 | 2 | 0.000 / 0.000 | 1.9923 / 1.9923 | 4.1574 | 103.935 |
| 18:00-18:30 |  | 5/5 |  | 1.9567 | 1.9567 | 3 | 3 | 0.000 / 0.000 | 1.9567 / 1.9567 | 4.0862 | 102.154 |
| 18:30-19:00 |  | 5/5 |  | 2.0330 | 2.0330 | 3 | 3 | 0.000 / 0.000 | 2.0330 / 2.0330 | 4.2387 | 105.968 |
| 19:00-19:30 |  | 5/5 |  | 2.2761 | 2.2761 | 2 | 2 | 0.000 / 0.000 | 2.2761 / 2.2761 | 4.7249 | 118.123 |
| 19:30-20:00 |  | 5/5 |  | 2.1673 | 2.1673 | 2 | 2 | 0.000 / 0.000 | 2.1673 / 2.1673 | 4.5074 | 112.684 |
| 20:00-20:30 |  | 5/5 |  | 2.0926 | 2.0926 | 2 | 2 | 0.000 / 0.000 | 2.0926 / 2.0926 | 4.3580 | 108.949 |
| 20:30-21:00 |  | 5/5 |  | 2.1463 | 2.1463 | 2 | 2 | 0.000 / 0.000 | 2.1463 / 2.1463 | 4.4655 | 111.637 |
| 21:00-21:30 |  | 5/5 |  | 2.1349 | 2.1349 | 2 | 2 | 0.000 / 0.000 | 2.1349 / 2.1349 | 4.4427 | 111.066 |
| 21:30-22:00 |  | 5/5 |  | 2.0549 | 2.0549 | 2 | 3 | 0.000 / 0.000 | 2.0549 / 2.0549 | 4.2825 | 107.063 |
| 22:00-22:30 |  | 5/5 |  | 2.0318 | 2.0318 | 2 | 3 | 0.000 / 0.000 | 2.0318 / 2.0318 | 4.2364 | 105.910 |
| 22:30-23:00 |  | 5/5 |  | 2.0545 | 2.0545 | 2 | 3 | 0.000 / 0.000 | 2.0545 / 2.0545 | 4.2817 | 107.043 |
| 23:00-23:30 |  | 5/5 |  | 2.0918 | 2.0918 | 2 | 3 | 0.000 / 0.000 | 2.0918 / 2.0918 | 4.3563 | 108.909 |
| 23:30-00:00 |  | 5/5 |  | 1.9364 | 1.9364 | 3 | 3 | 0.000 / 0.000 | 1.9364 / 1.9364 | 4.0456 | 101.140 |
| 00:00-00:30 |  | 5/5 |  | 1.9568 | 1.9568 | 3 | 3 | 0.000 / 0.000 | 1.9568 / 1.9568 | 4.0865 | 102.162 |
| 00:30-01:00 |  | 5/5 |  | 2.0116 | 2.0116 | 3 | 3 | 0.000 / 0.000 | 2.0116 / 2.0116 | 4.1959 | 104.898 |
| 01:00-01:30 |  | 5/5 |  | 1.8768 | 1.8768 | 3 | 3 | 0.000 / 0.000 | 1.8768 / 1.8768 | 3.9265 | 98.162 |
| 01:30-02:00 |  | 5/5 |  | 1.9451 | 1.9451 | 3 | 3 | 0.000 / 0.000 | 1.9451 / 1.9451 | 4.0630 | 101.575 |
| 02:00-02:30 |  | 5/5 |  | 1.8025 | 1.8025 | 3 | 3 | 0.000 / 0.000 | 1.8025 / 1.8025 | 3.7778 | 94.446 |
| 02:30-03:00 |  | 5/5 |  | 1.7429 | 1.7429 | 3 | 3 | 0.000 / 0.000 | 1.7429 / 1.7429 | 3.6585 | 91.463 |
| 03:00-03:30 |  | 5/5 |  | 1.7025 | 1.7025 | 3 | 3 | 0.000 / 0.000 | 1.7025 / 1.7025 | 3.5778 | 89.445 |
| 03:30-04:00 |  | 5/5 |  | 1.6963 | 1.6963 | 3 | 3 | 0.000 / 0.000 | 1.6963 / 1.6963 | 3.5654 | 89.134 |
| 04:00-04:30 |  | 5/5 |  | 1.8675 | 1.8675 | 3 | 3 | 0.000 / 0.000 | 1.8675 / 1.8675 | 3.9078 | 97.695 |
| 04:30-05:00 |  | 5/5 |  | 1.8131 | 1.8131 | 3 | 3 | 0.000 / 0.000 | 1.8131 / 1.8131 | 3.7991 | 94.977 |
| 05:00-05:30 |  | 5/5 |  | 1.7069 | 1.7069 | 3 | 3 | 0.000 / 0.000 | 1.7069 / 1.7069 | 3.5867 | 89.667 |
| 05:30-06:00 |  | 5/5 |  | 1.7754 | 1.7754 | 3 | 3 | 0.000 / 0.000 | 1.7754 / 1.7754 | 3.7235 | 93.088 |
| 06:00-06:30 |  | 5/5 |  | 1.7643 | 1.7643 | 3 | 3 | 0.000 / 0.000 | 1.7643 / 1.7643 | 3.7015 | 92.537 |
| 06:30-07:00 |  | 5/5 |  | 1.7926 | 1.7926 | 3 | 3 | 0.000 / 0.000 | 1.7926 / 1.7926 | 3.7580 | 93.951 |
| 07:00-07:30 | D | 5/5 |  | 1.8439 | 1.8439 | 3 | 3 | 0.000 / 0.000 | 1.8439 / 1.8439 | 3.8607 | 96.517 |
| 07:30-08:00 | D | 5/5 |  | 1.9232 | 1.9232 | 3 | 3 | 0.000 / 0.000 | 1.9232 / 1.9232 | 4.0192 | 100.481 |
| 08:00-08:30 | D | 5/5 |  | 1.7684 | 1.7684 | 3 | 3 | 0.000 / 0.000 | 1.7684 / 1.7684 | 3.7096 | 92.741 |
| 08:30-09:00 | D | 5/5 |  | 1.7803 | 1.7803 | 3 | 3 | 0.000 / 0.000 | 1.7803 / 1.7803 | 3.7334 | 93.334 |
| 09:00-09:30 | D | 5/5 |  | 1.6956 | 1.6956 | 3 | 3 | 0.000 / 0.000 | 1.6956 / 1.6956 | 3.5640 | 89.099 |
| 09:30-10:00 | D | 5/5 |  | 1.7266 | 1.7266 | 3 | 3 | 0.000 / 0.000 | 1.7266 / 1.7266 | 3.6260 | 90.649 |
| 10:00-10:30 | D | 5/5 |  | 1.7131 | 1.7133 | 3 | 3 | 0.000 / 0.000 | 1.7131 / 1.7131 | 3.5991 | 89.976 |
| 10:30-11:00 | D | 5/5 |  | 1.5574 | 1.5576 | 3 | 3 | 0.000 / 0.000 | 1.5574 / 1.5574 | 3.2876 | 82.190 |
| 11:00-11:30 | D | 5/5 |  | 1.5481 | 1.5481 | 3 | 3 | 0.000 / 0.000 | 1.5481 / 1.5481 | 3.2689 | 81.723 |
| 11:30-12:00 | D | 5/5 |  | 1.5200 | 1.5200 | 3 | 3 | 0.000 / 0.000 | 1.5200 / 1.5200 | 3.2128 | 80.321 |
| 12:00-12:30 | D | 5/5 |  | 1.5049 | 1.5049 | 4 | 3 | 0.000 / 0.000 | 1.5049 / 1.5049 | 3.1826 | 79.564 |
| 12:30-13:00 |  | 5/5 |  | 1.5877 | 1.5877 | 3 | 3 | 0.000 / 0.000 | 1.5877 / 1.5877 | 3.3482 | 83.705 |
| 13:00-13:30 |  | 5/5 |  | 1.6389 | 1.6389 | 3 | 3 | 0.000 / 0.000 | 1.6389 / 1.6389 | 3.4506 | 86.266 |
| 13:30-14:00 |  | 5/5 |  | 1.5679 | 1.5679 | 3 | 3 | 0.000 / 0.000 | 1.5679 / 1.5679 | 3.3086 | 82.715 |
| 14:00-14:30 |  | 5/5 |  | 1.6057 | 1.6057 | 3 | 3 | 0.000 / 0.000 | 1.6057 / 1.6057 | 3.3841 | 84.603 |
| 14:30-15:00 |  | 5/5 |  | 1.5764 | 1.5764 | 3 | 3 | 0.000 / 0.000 | 1.5764 / 1.5764 | 3.3256 | 83.141 |
| 15:00-15:30 |  | 5/5 |  | 1.5898 | 1.5898 | 3 | 3 | 0.000 / 0.000 | 1.5898 / 1.5898 | 3.3525 | 83.812 |
| 15:30-16:00 |  | 5/5 |  | 1.8167 | 1.8167 | 3 | 3 | 0.000 / 0.000 | 1.8167 / 1.8167 | 3.8062 | 95.155 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/SI_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 34258750638e55a7e279eb17f45222c3e18af63e6b1c08e63b92e529a9c7d5a9 (648,877 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SI_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 9bbb3ab8eb1819803e6bfe87f313636420d543650ff073805d7f7421c47a94d6 (454,485 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SI_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 615ef37aed923a563fe58be1bb60b013235d3175d19bd274c95471b1ff6bd64c (1,332,117 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SI_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` ffa966d2eccc9648d9319c9e99cce5cb1513a1c2a9fdeb4c284eb795564024ec (1,027,773 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SI_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` df79e4865f1dab49b512e8d918fce327f8af9c2d1bb467bce1798b6281d57ae5 (843,759 records)

### SIL (metals)

Tick 0.005 (vendor units 0.005, factor 1), tick value $5.0; commission $2.72 round turn = 0.5440 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-12:25 CT.

Event-window one-side slippage: buy 1.8740, sell 1.8740 ticks (round turn inside a window 4.2920 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.8740 | 1.8740 | 2 | 2 | 0.000 / 0.000 | 1.8740 / 1.8740 | 4.2920 | 21.460 |
| 17:30-18:00 |  | 5/5 |  | 1.2001 | 1.2001 | 2 | 2 | 0.000 / 0.000 | 1.2001 / 1.2001 | 2.9442 | 14.721 |
| 18:00-18:30 |  | 5/5 |  | 1.1886 | 1.1886 | 2 | 2 | 0.000 / 0.000 | 1.1886 / 1.1886 | 2.9212 | 14.606 |
| 18:30-19:00 |  | 5/5 |  | 1.1299 | 1.1299 | 2 | 2 | 0.000 / 0.000 | 1.1299 / 1.1299 | 2.8039 | 14.019 |
| 19:00-19:30 |  | 5/5 |  | 1.0896 | 1.0896 | 2 | 2 | 0.000 / 0.000 | 1.0896 / 1.0896 | 2.7231 | 13.616 |
| 19:30-20:00 |  | 5/5 |  | 1.0485 | 1.0485 | 2 | 2 | 0.000 / 0.000 | 1.0485 / 1.0485 | 2.6410 | 13.205 |
| 20:00-20:30 |  | 5/5 |  | 1.1022 | 1.1022 | 2 | 2 | 0.000 / 0.000 | 1.1022 / 1.1022 | 2.7484 | 13.742 |
| 20:30-21:00 |  | 5/5 |  | 1.0726 | 1.0726 | 2 | 2 | 0.000 / 0.000 | 1.0726 / 1.0726 | 2.6893 | 13.446 |
| 21:00-21:30 |  | 5/5 |  | 1.0805 | 1.0805 | 2 | 2 | 0.000 / 0.000 | 1.0805 / 1.0805 | 2.7050 | 13.525 |
| 21:30-22:00 |  | 5/5 |  | 1.1031 | 1.1031 | 2 | 2 | 0.000 / 0.000 | 1.1031 / 1.1031 | 2.7502 | 13.751 |
| 22:00-22:30 |  | 5/5 |  | 1.0639 | 1.0639 | 2 | 2 | 0.000 / 0.000 | 1.0639 / 1.0639 | 2.6718 | 13.359 |
| 22:30-23:00 |  | 5/5 |  | 1.0514 | 1.0514 | 3 | 2 | 0.000 / 0.000 | 1.0514 / 1.0514 | 2.6468 | 13.234 |
| 23:00-23:30 |  | 5/5 |  | 1.0298 | 1.0298 | 2 | 2 | 0.000 / 0.000 | 1.0298 / 1.0298 | 2.6036 | 13.018 |
| 23:30-00:00 |  | 5/5 |  | 1.0782 | 1.0782 | 2 | 2 | 0.000 / 0.000 | 1.0782 / 1.0782 | 2.7005 | 13.502 |
| 00:00-00:30 |  | 5/5 |  | 1.0899 | 1.0899 | 2 | 2 | 0.000 / 0.000 | 1.0899 / 1.0899 | 2.7238 | 13.619 |
| 00:30-01:00 |  | 5/5 |  | 1.0844 | 1.0844 | 2 | 2 | 0.000 / 0.000 | 1.0844 / 1.0844 | 2.7129 | 13.564 |
| 01:00-01:30 |  | 5/5 |  | 1.0915 | 1.0915 | 2 | 2 | 0.000 / 0.000 | 1.0915 / 1.0915 | 2.7270 | 13.635 |
| 01:30-02:00 |  | 5/5 |  | 1.0724 | 1.0724 | 2 | 2 | 0.000 / 0.000 | 1.0724 / 1.0724 | 2.6887 | 13.444 |
| 02:00-02:30 |  | 5/5 |  | 1.0918 | 1.0918 | 2 | 2 | 0.000 / 0.000 | 1.0918 / 1.0918 | 2.7276 | 13.638 |
| 02:30-03:00 |  | 5/5 |  | 1.1076 | 1.1076 | 2 | 2 | 0.000 / 0.000 | 1.1076 / 1.1076 | 2.7592 | 13.796 |
| 03:00-03:30 |  | 5/5 |  | 1.0970 | 1.0970 | 2 | 2 | 0.000 / 0.000 | 1.0970 / 1.0970 | 2.7381 | 13.690 |
| 03:30-04:00 |  | 5/5 |  | 1.0754 | 1.0754 | 2 | 2 | 0.000 / 0.000 | 1.0754 / 1.0754 | 2.6949 | 13.474 |
| 04:00-04:30 |  | 5/5 |  | 1.1015 | 1.1015 | 2 | 2 | 0.000 / 0.000 | 1.1015 / 1.1015 | 2.7469 | 13.735 |
| 04:30-05:00 |  | 5/5 |  | 1.0929 | 1.0929 | 2 | 2 | 0.000 / 0.000 | 1.0929 / 1.0929 | 2.7298 | 13.649 |
| 05:00-05:30 |  | 5/5 |  | 1.0799 | 1.0799 | 2 | 2 | 0.000 / 0.000 | 1.0799 / 1.0799 | 2.7039 | 13.519 |
| 05:30-06:00 |  | 5/5 |  | 1.0863 | 1.0863 | 2 | 2 | 0.000 / 0.000 | 1.0863 / 1.0863 | 2.7167 | 13.583 |
| 06:00-06:30 |  | 5/5 |  | 1.0904 | 1.0904 | 2 | 2 | 0.000 / 0.000 | 1.0904 / 1.0904 | 2.7248 | 13.624 |
| 06:30-07:00 |  | 5/5 |  | 1.1106 | 1.1106 | 2 | 2 | 0.000 / 0.000 | 1.1106 / 1.1106 | 2.7652 | 13.826 |
| 07:00-07:30 | D | 5/5 |  | 1.2400 | 1.2400 | 2 | 2 | 0.000 / 0.000 | 1.2400 / 1.2400 | 3.0239 | 15.120 |
| 07:30-08:00 | D | 5/5 |  | 1.3567 | 1.3576 | 2 | 2 | 0.000 / 0.000 | 1.3567 / 1.3567 | 3.2574 | 16.287 |
| 08:00-08:30 | D | 5/5 |  | 1.1175 | 1.1175 | 2 | 2 | 0.000 / 0.000 | 1.1175 / 1.1175 | 2.7790 | 13.895 |
| 08:30-09:00 | D | 5/5 |  | 1.0946 | 1.0946 | 2 | 2 | 0.000 / 0.000 | 1.0946 / 1.0946 | 2.7331 | 13.666 |
| 09:00-09:30 | D | 5/5 |  | 1.1145 | 1.1145 | 2 | 2 | 0.000 / 0.000 | 1.1145 / 1.1145 | 2.7731 | 13.865 |
| 09:30-10:00 | D | 5/5 |  | 1.0933 | 1.0933 | 2 | 2 | 0.000 / 0.000 | 1.0933 / 1.0933 | 2.7306 | 13.653 |
| 10:00-10:30 | D | 5/5 |  | 1.0991 | 1.0992 | 2 | 2 | 0.000 / 0.000 | 1.0991 / 1.0991 | 2.7423 | 13.711 |
| 10:30-11:00 | D | 5/5 |  | 1.0705 | 1.0706 | 2 | 2 | 0.000 / 0.000 | 1.0705 / 1.0705 | 2.6850 | 13.425 |
| 11:00-11:30 | D | 5/5 |  | 1.0429 | 1.0429 | 2 | 2 | 0.000 / 0.000 | 1.0429 / 1.0429 | 2.6297 | 13.149 |
| 11:30-12:00 | D | 5/5 |  | 1.0370 | 1.0370 | 2 | 2 | 0.000 / 0.000 | 1.0370 / 1.0370 | 2.6179 | 13.090 |
| 12:00-12:30 | D | 5/5 |  | 1.0918 | 1.0918 | 2 | 2 | 0.000 / 0.000 | 1.0918 / 1.0918 | 2.7277 | 13.638 |
| 12:30-13:00 |  | 5/5 |  | 1.0529 | 1.0529 | 2 | 2 | 0.000 / 0.000 | 1.0529 / 1.0529 | 2.6498 | 13.249 |
| 13:00-13:30 |  | 5/5 |  | 1.0514 | 1.0514 | 2 | 2 | 0.000 / 0.000 | 1.0514 / 1.0514 | 2.6468 | 13.234 |
| 13:30-14:00 |  | 5/5 |  | 1.0200 | 1.0200 | 2 | 2 | 0.000 / 0.000 | 1.0200 / 1.0200 | 2.5840 | 12.920 |
| 14:00-14:30 |  | 5/5 |  | 0.9934 | 0.9934 | 2 | 2 | 0.000 / 0.000 | 0.9934 / 0.9934 | 2.5308 | 12.654 |
| 14:30-15:00 |  | 5/5 |  | 1.0334 | 1.0334 | 2 | 2 | 0.000 / 0.000 | 1.0334 / 1.0334 | 2.6108 | 13.054 |
| 15:00-15:30 |  | 5/5 |  | 1.0404 | 1.0404 | 2 | 2 | 0.000 / 0.000 | 1.0404 / 1.0404 | 2.6248 | 13.124 |
| 15:30-16:00 |  | 5/5 |  | 1.1530 | 1.1530 | 3 | 2 | 0.000 / 0.000 | 1.1530 / 1.1530 | 2.8499 | 14.250 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/SIL_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` ab7fbc3b6791b18f998955a10d524e59102631fe298073cfa5f43dcae4bdf863 (453,867 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SIL_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 6e922d59a40725093062fd380f75df9f524fc9f7aa88cba7c3156e2b64824470 (275,895 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SIL_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` ea747339d1b518a8330b24cd150723b2aab89d186868c9cb028668372f80c9aa (1,336,420 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SIL_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 8bdb5052d262a334dda600f709835e0cb68dc8542eec4db3f8c2c7cbf4863163 (1,662,150 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/SIL_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 43190561a5ed52fb0aee236262712cd2098bbbf92bffc62527dc01866c9f1f6a (1,187,408 records)

### TN (rates)

Tick 0.015625 (vendor units 0.015625, factor 1), tick value $15.625; commission $2.62 round turn = 0.1677 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.5338, sell 0.5338 ticks (round turn inside a window 1.2352 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5189 | 0.5189 | 124 | 98 | 0.000 / 0.000 | 0.5189 / 0.5189 | 1.2054 | 18.834 |
| 17:30-18:00 |  | 5/5 |  | 0.5088 | 0.5088 | 122 | 212 | 0.000 / 0.000 | 0.5088 / 0.5088 | 1.1852 | 18.519 |
| 18:00-18:30 |  | 5/5 |  | 0.5338 | 0.5338 | 251 | 274 | 0.000 / 0.000 | 0.5338 / 0.5338 | 1.2352 | 19.300 |
| 18:30-19:00 |  | 5/5 |  | 0.5187 | 0.5187 | 395 | 279 | 0.000 / 0.000 | 0.5187 / 0.5187 | 1.2050 | 18.829 |
| 19:00-19:30 |  | 5/5 |  | 0.5085 | 0.5085 | 312 | 288 | 0.000 / 0.000 | 0.5085 / 0.5085 | 1.1846 | 18.509 |
| 19:30-20:00 |  | 5/5 |  | 0.5178 | 0.5178 | 282 | 312 | 0.000 / 0.000 | 0.5178 / 0.5178 | 1.2034 | 18.803 |
| 20:00-20:30 |  | 5/5 |  | 0.5041 | 0.5041 | 328 | 391 | 0.000 / 0.000 | 0.5041 / 0.5041 | 1.1759 | 18.373 |
| 20:30-21:00 |  | 5/5 |  | 0.5154 | 0.5154 | 417 | 350 | 0.000 / 0.000 | 0.5154 / 0.5154 | 1.1986 | 18.728 |
| 21:00-21:30 |  | 5/5 |  | 0.5117 | 0.5117 | 436 | 295 | 0.000 / 0.000 | 0.5117 / 0.5117 | 1.1910 | 18.610 |
| 21:30-22:00 |  | 5/5 |  | 0.5109 | 0.5109 | 409 | 372 | 0.000 / 0.000 | 0.5109 / 0.5109 | 1.1894 | 18.585 |
| 22:00-22:30 |  | 5/5 |  | 0.5125 | 0.5125 | 463 | 319 | 0.000 / 0.000 | 0.5125 / 0.5125 | 1.1927 | 18.636 |
| 22:30-23:00 |  | 5/5 |  | 0.5035 | 0.5035 | 493 | 372 | 0.000 / 0.000 | 0.5035 / 0.5035 | 1.1747 | 18.355 |
| 23:00-23:30 |  | 5/5 |  | 0.5145 | 0.5145 | 524 | 378 | 0.000 / 0.000 | 0.5145 / 0.5145 | 1.1966 | 18.697 |
| 23:30-00:00 |  | 5/5 |  | 0.5117 | 0.5117 | 429 | 437 | 0.000 / 0.000 | 0.5117 / 0.5117 | 1.1910 | 18.610 |
| 00:00-00:30 |  | 5/5 |  | 0.5123 | 0.5123 | 356 | 361 | 0.000 / 0.000 | 0.5123 / 0.5123 | 1.1923 | 18.629 |
| 00:30-01:00 |  | 5/5 |  | 0.5144 | 0.5144 | 458 | 576 | 0.000 / 0.000 | 0.5144 / 0.5144 | 1.1965 | 18.696 |
| 01:00-01:30 |  | 5/5 |  | 0.5050 | 0.5050 | 453 | 561 | 0.000 / 0.000 | 0.5050 / 0.5050 | 1.1778 | 18.402 |
| 01:30-02:00 |  | 5/5 |  | 0.5030 | 0.5030 | 514 | 565 | 0.000 / 0.000 | 0.5030 / 0.5030 | 1.1737 | 18.339 |
| 02:00-02:30 |  | 5/5 |  | 0.5047 | 0.5047 | 524 | 538 | 0.000 / 0.000 | 0.5047 / 0.5047 | 1.1771 | 18.393 |
| 02:30-03:00 |  | 5/5 |  | 0.5073 | 0.5073 | 606 | 602 | 0.000 / 0.000 | 0.5073 / 0.5073 | 1.1822 | 18.472 |
| 03:00-03:30 |  | 5/5 |  | 0.5065 | 0.5065 | 750 | 686 | 0.000 / 0.000 | 0.5065 / 0.5065 | 1.1806 | 18.447 |
| 03:30-04:00 |  | 5/5 |  | 0.5037 | 0.5037 | 686 | 609 | 0.000 / 0.000 | 0.5037 / 0.5037 | 1.1752 | 18.362 |
| 04:00-04:30 |  | 5/5 |  | 0.5037 | 0.5037 | 692 | 587 | 0.000 / 0.000 | 0.5037 / 0.5037 | 1.1750 | 18.360 |
| 04:30-05:00 |  | 5/5 |  | 0.5018 | 0.5018 | 706 | 549 | 0.000 / 0.000 | 0.5018 / 0.5018 | 1.1713 | 18.301 |
| 05:00-05:30 |  | 5/5 |  | 0.5059 | 0.5059 | 764 | 711 | 0.000 / 0.000 | 0.5059 / 0.5059 | 1.1795 | 18.429 |
| 05:30-06:00 |  | 5/5 |  | 0.5038 | 0.5038 | 629 | 641 | 0.000 / 0.000 | 0.5038 / 0.5038 | 1.1754 | 18.365 |
| 06:00-06:30 |  | 5/5 |  | 0.5063 | 0.5063 | 604 | 618 | 0.000 / 0.000 | 0.5063 / 0.5063 | 1.1802 | 18.441 |
| 06:30-07:00 |  | 5/5 |  | 0.5051 | 0.5051 | 621 | 679 | 0.000 / 0.000 | 0.5051 / 0.5051 | 1.1778 | 18.403 |
| 07:00-07:30 | D | 5/5 |  | 0.5051 | 0.5051 | 595 | 697 | 0.000 / 0.000 | 0.5051 / 0.5051 | 1.1778 | 18.404 |
| 07:30-08:00 | D | 5/5 |  | 0.5059 | 0.5059 | 600 | 706 | 0.000 / 0.000 | 0.5059 / 0.5059 | 1.1795 | 18.430 |
| 08:00-08:30 | D | 5/5 |  | 0.5049 | 0.5049 | 810 | 775 | 0.000 / 0.000 | 0.5049 / 0.5049 | 1.1775 | 18.399 |
| 08:30-09:00 | D | 5/5 |  | 0.5039 | 0.5039 | 775 | 889 | 0.000 / 0.000 | 0.5039 / 0.5039 | 1.1755 | 18.367 |
| 09:00-09:30 | D | 5/5 |  | 0.5036 | 0.5036 | 779 | 862 | 0.000 / 0.000 | 0.5036 / 0.5036 | 1.1749 | 18.358 |
| 09:30-10:00 | D | 5/5 |  | 0.5046 | 0.5046 | 789 | 940 | 0.000 / 0.000 | 0.5046 / 0.5046 | 1.1769 | 18.389 |
| 10:00-10:30 | D | 5/5 |  | 0.5028 | 0.5028 | 876 | 1057 | 0.000 / 0.000 | 0.5028 / 0.5028 | 1.1732 | 18.332 |
| 10:30-11:00 | D | 5/5 |  | 0.5027 | 0.5027 | 860 | 993 | 0.000 / 0.000 | 0.5027 / 0.5027 | 1.1731 | 18.330 |
| 11:00-11:30 | D | 5/5 |  | 0.5016 | 0.5016 | 976 | 1033 | 0.000 / 0.000 | 0.5016 / 0.5016 | 1.1708 | 18.293 |
| 11:30-12:00 | D | 5/5 |  | 0.5014 | 0.5014 | 1060 | 1120 | 0.000 / 0.000 | 0.5014 / 0.5014 | 1.1705 | 18.289 |
| 12:00-12:30 | D | 5/5 |  | 0.5029 | 0.5029 | 955 | 1054 | 0.000 / 0.000 | 0.5029 / 0.5029 | 1.1735 | 18.336 |
| 12:30-13:00 | D | 5/5 |  | 0.5009 | 0.5009 | 1130 | 1227 | 0.000 / 0.000 | 0.5009 / 0.5009 | 1.1695 | 18.273 |
| 13:00-13:30 | D | 5/5 |  | 0.5019 | 0.5019 | 1200 | 1157 | 0.000 / 0.000 | 0.5019 / 0.5019 | 1.1714 | 18.304 |
| 13:30-14:00 | D | 5/5 |  | 0.5034 | 0.5034 | 1507 | 1301 | 0.000 / 0.000 | 0.5034 / 0.5034 | 1.1744 | 18.351 |
| 14:00-14:30 |  | 5/5 |  | 0.5009 | 0.5009 | 1497 | 1124 | 0.000 / 0.000 | 0.5009 / 0.5009 | 1.1696 | 18.274 |
| 14:30-15:00 |  | 5/5 |  | 0.5015 | 0.5015 | 1324 | 1213 | 0.000 / 0.000 | 0.5015 / 0.5015 | 1.1707 | 18.293 |
| 15:00-15:30 |  | 5/5 |  | 0.5020 | 0.5020 | 1130 | 1105 | 0.000 / 0.000 | 0.5020 / 0.5020 | 1.1717 | 18.307 |
| 15:30-16:00 |  | 5/5 |  | 0.5007 | 0.5007 | 890 | 921 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.1690 | 18.266 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/TN_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 063815406a99454e63fcdc33a82f77ddcef3568e140ab653e1352b467697e0d0 (1,169,005 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/TN_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` a517206ba810aab2f028f9a9920f8c875cdae82a4257b55f516c0a6f657dcf9b (770,131 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/TN_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 396c8cbba5f6d69c05f3b71700f316a17f69facac3d869609b9eb50693bfa8b9 (996,695 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/TN_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 93ed26a3c488b7d0f2b60f53e576f6b2676c5b0e4a0540b74b9ed0b4559adbc7 (1,610,761 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/TN_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 07a38310fb1eb3e716dff1b805543f7c696ecef6bb288de5fa823e81b3e87d14 (1,003,313 records)

### UB (rates)

Tick 0.03125 (vendor units 0.03125, factor 1), tick value $31.25; commission $2.92 round turn = 0.0934 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.5138, sell 0.5138 ticks (round turn inside a window 1.1210 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5134 | 0.5134 | 49 | 69 | 0.000 / 0.000 | 0.5134 / 0.5134 | 1.1201 | 35.005 |
| 17:30-18:00 |  | 5/5 |  | 0.5122 | 0.5122 | 107 | 101 | 0.000 / 0.000 | 0.5122 / 0.5122 | 1.1178 | 34.931 |
| 18:00-18:30 |  | 5/5 |  | 0.5087 | 0.5087 | 115 | 135 | 0.000 / 0.000 | 0.5087 / 0.5087 | 1.1108 | 34.714 |
| 18:30-19:00 |  | 5/5 |  | 0.5071 | 0.5071 | 143 | 178 | 0.000 / 0.000 | 0.5071 / 0.5071 | 1.1077 | 34.615 |
| 19:00-19:30 |  | 5/5 |  | 0.5098 | 0.5098 | 157 | 173 | 0.000 / 0.000 | 0.5098 / 0.5098 | 1.1129 | 34.780 |
| 19:30-20:00 |  | 5/5 |  | 0.5123 | 0.5123 | 156 | 225 | 0.000 / 0.000 | 0.5123 / 0.5123 | 1.1181 | 34.940 |
| 20:00-20:30 |  | 5/5 |  | 0.5135 | 0.5135 | 218 | 208 | 0.000 / 0.000 | 0.5135 / 0.5135 | 1.1205 | 35.015 |
| 20:30-21:00 |  | 5/5 |  | 0.5098 | 0.5098 | 210 | 181 | 0.000 / 0.000 | 0.5098 / 0.5098 | 1.1131 | 34.785 |
| 21:00-21:30 |  | 5/5 |  | 0.5089 | 0.5089 | 229 | 213 | 0.000 / 0.000 | 0.5089 / 0.5089 | 1.1112 | 34.725 |
| 21:30-22:00 |  | 5/5 |  | 0.5043 | 0.5043 | 241 | 207 | 0.000 / 0.000 | 0.5043 / 0.5043 | 1.1020 | 34.438 |
| 22:00-22:30 |  | 5/5 |  | 0.5117 | 0.5117 | 202 | 241 | 0.000 / 0.000 | 0.5117 / 0.5117 | 1.1169 | 34.904 |
| 22:30-23:00 |  | 5/5 |  | 0.5084 | 0.5084 | 173 | 254 | 0.000 / 0.000 | 0.5084 / 0.5084 | 1.1103 | 34.697 |
| 23:00-23:30 |  | 5/5 |  | 0.5003 | 0.5003 | 234 | 251 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.0941 | 34.192 |
| 23:30-00:00 |  | 5/5 |  | 0.5059 | 0.5059 | 205 | 220 | 0.000 / 0.000 | 0.5059 / 0.5059 | 1.1051 | 34.536 |
| 00:00-00:30 |  | 5/5 |  | 0.5110 | 0.5110 | 223 | 223 | 0.000 / 0.000 | 0.5110 / 0.5110 | 1.1155 | 34.860 |
| 00:30-01:00 |  | 5/5 |  | 0.5120 | 0.5120 | 193 | 173 | 0.000 / 0.000 | 0.5120 / 0.5120 | 1.1174 | 34.918 |
| 01:00-01:30 |  | 5/5 |  | 0.5138 | 0.5138 | 161 | 222 | 0.000 / 0.000 | 0.5138 / 0.5138 | 1.1210 | 35.031 |
| 01:30-02:00 |  | 5/5 |  | 0.5064 | 0.5064 | 193 | 223 | 0.000 / 0.000 | 0.5064 / 0.5064 | 1.1062 | 34.570 |
| 02:00-02:30 |  | 5/5 |  | 0.5026 | 0.5026 | 245 | 253 | 0.000 / 0.000 | 0.5026 / 0.5026 | 1.0987 | 34.334 |
| 02:30-03:00 |  | 5/5 |  | 0.5065 | 0.5065 | 232 | 269 | 0.000 / 0.000 | 0.5065 / 0.5065 | 1.1065 | 34.577 |
| 03:00-03:30 |  | 5/5 |  | 0.5059 | 0.5059 | 288 | 227 | 0.000 / 0.000 | 0.5059 / 0.5059 | 1.1051 | 34.536 |
| 03:30-04:00 |  | 5/5 |  | 0.5041 | 0.5041 | 275 | 264 | 0.000 / 0.000 | 0.5041 / 0.5041 | 1.1017 | 34.427 |
| 04:00-04:30 |  | 5/5 |  | 0.5060 | 0.5060 | 302 | 245 | 0.000 / 0.000 | 0.5060 / 0.5060 | 1.1055 | 34.547 |
| 04:30-05:00 |  | 5/5 |  | 0.5076 | 0.5076 | 254 | 259 | 0.000 / 0.000 | 0.5076 / 0.5076 | 1.1087 | 34.646 |
| 05:00-05:30 |  | 5/5 |  | 0.5075 | 0.5075 | 253 | 267 | 0.000 / 0.000 | 0.5075 / 0.5075 | 1.1085 | 34.642 |
| 05:30-06:00 |  | 5/5 |  | 0.5101 | 0.5101 | 221 | 252 | 0.000 / 0.000 | 0.5101 / 0.5101 | 1.1136 | 34.802 |
| 06:00-06:30 |  | 5/5 |  | 0.5073 | 0.5073 | 236 | 265 | 0.000 / 0.000 | 0.5073 / 0.5073 | 1.1080 | 34.626 |
| 06:30-07:00 |  | 5/5 |  | 0.5050 | 0.5050 | 246 | 264 | 0.000 / 0.000 | 0.5050 / 0.5050 | 1.1034 | 34.482 |
| 07:00-07:30 | D | 5/5 |  | 0.5041 | 0.5041 | 272 | 255 | 0.000 / 0.000 | 0.5041 / 0.5041 | 1.1016 | 34.425 |
| 07:30-08:00 | D | 5/5 |  | 0.5068 | 0.5068 | 289 | 267 | 0.000 / 0.000 | 0.5068 / 0.5068 | 1.1070 | 34.594 |
| 08:00-08:30 | D | 5/5 |  | 0.5047 | 0.5047 | 350 | 339 | 0.000 / 0.000 | 0.5047 / 0.5047 | 1.1029 | 34.466 |
| 08:30-09:00 | D | 5/5 |  | 0.5036 | 0.5036 | 387 | 358 | 0.000 / 0.000 | 0.5036 / 0.5036 | 1.1006 | 34.393 |
| 09:00-09:30 | D | 5/5 |  | 0.5017 | 0.5017 | 427 | 367 | 0.000 / 0.000 | 0.5017 / 0.5017 | 1.0968 | 34.275 |
| 09:30-10:00 | D | 5/5 |  | 0.5017 | 0.5017 | 422 | 410 | 0.000 / 0.000 | 0.5017 / 0.5017 | 1.0968 | 34.275 |
| 10:00-10:30 | D | 5/5 |  | 0.5021 | 0.5021 | 453 | 434 | 0.000 / 0.000 | 0.5021 / 0.5021 | 1.0976 | 34.301 |
| 10:30-11:00 | D | 5/5 |  | 0.5035 | 0.5035 | 447 | 509 | 0.000 / 0.000 | 0.5035 / 0.5035 | 1.1005 | 34.390 |
| 11:00-11:30 | D | 5/5 |  | 0.5016 | 0.5016 | 434 | 482 | 0.000 / 0.000 | 0.5016 / 0.5016 | 1.0966 | 34.269 |
| 11:30-12:00 | D | 5/5 |  | 0.5009 | 0.5009 | 525 | 432 | 0.000 / 0.000 | 0.5009 / 0.5009 | 1.0952 | 34.225 |
| 12:00-12:30 | D | 5/5 |  | 0.5024 | 0.5024 | 419 | 448 | 0.000 / 0.000 | 0.5024 / 0.5024 | 1.0981 | 34.317 |
| 12:30-13:00 | D | 5/5 |  | 0.5007 | 0.5007 | 517 | 427 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.0949 | 34.215 |
| 13:00-13:30 | D | 5/5 |  | 0.5013 | 0.5013 | 489 | 514 | 0.000 / 0.000 | 0.5013 / 0.5013 | 1.0960 | 34.251 |
| 13:30-14:00 | D | 5/5 |  | 0.5001 | 0.5001 | 614 | 554 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0936 | 34.176 |
| 14:00-14:30 |  | 5/5 |  | 0.5008 | 0.5008 | 546 | 567 | 0.000 / 0.000 | 0.5008 / 0.5008 | 1.0949 | 34.217 |
| 14:30-15:00 |  | 5/5 |  | 0.5002 | 0.5002 | 646 | 570 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.0938 | 34.180 |
| 15:00-15:30 |  | 5/5 |  | 0.5008 | 0.5008 | 581 | 581 | 0.000 / 0.000 | 0.5008 / 0.5008 | 1.0951 | 34.223 |
| 15:30-16:00 |  | 5/5 |  | 0.5030 | 0.5030 | 462 | 469 | 0.000 / 0.000 | 0.5030 / 0.5030 | 1.0994 | 34.356 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/UB_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` df3b3ccdaa35e543ee805d186b7e58c856199e2af0e1df7a55338e4cedc39b25 (794,130 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/UB_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 6b5bf1126a098dca625b0151f9f6c256f52130bac0050e5110cad5ce21ad0881 (517,721 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/UB_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 0691e9322714e607322d7df56a992f9ca7b5d7215b29f9d9a6474d076b032692 (807,792 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/UB_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 28740d2b6d267daeb4150edfe23b9ad03f2127ccc8de0f684719a1da2a31b353 (1,062,508 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/UB_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` b68d4a37ec4fa8e536183eec60fae6c4ab85825f1327a411f09751e9a37d383c (675,653 records)

### YM (equity)

Tick 1.00 (vendor units 1.00, factor 1), tick value $5.0; commission $3.78 round turn = 0.7560 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-15:00 CT.

Event-window one-side slippage: buy 1.7786, sell 1.7786 ticks (round turn inside a window 4.3131 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 1.7786 | 1.7786 | 2 | 2 | 0.000 / 0.000 | 1.7786 / 1.7786 | 4.3131 | 21.566 |
| 17:30-18:00 |  | 5/5 |  | 1.2855 | 1.2855 | 3 | 3 | 0.000 / 0.000 | 1.2855 / 1.2855 | 3.3269 | 16.635 |
| 18:00-18:30 |  | 5/5 |  | 1.1468 | 1.1468 | 3 | 3 | 0.000 / 0.000 | 1.1468 / 1.1468 | 3.0496 | 15.248 |
| 18:30-19:00 |  | 5/5 |  | 1.1742 | 1.1742 | 3 | 3 | 0.000 / 0.000 | 1.1742 / 1.1742 | 3.1045 | 15.522 |
| 19:00-19:30 |  | 5/5 |  | 1.1449 | 1.1449 | 3 | 3 | 0.000 / 0.000 | 1.1449 / 1.1449 | 3.0458 | 15.229 |
| 19:30-20:00 |  | 5/5 |  | 1.0721 | 1.0721 | 3 | 3 | 0.000 / 0.000 | 1.0721 / 1.0721 | 2.9003 | 14.501 |
| 20:00-20:30 |  | 5/5 |  | 1.0603 | 1.0603 | 3 | 3 | 0.000 / 0.000 | 1.0603 / 1.0603 | 2.8766 | 14.383 |
| 20:30-21:00 |  | 5/5 |  | 1.0905 | 1.0905 | 3 | 3 | 0.000 / 0.000 | 1.0905 / 1.0905 | 2.9369 | 14.685 |
| 21:00-21:30 |  | 5/5 |  | 1.0726 | 1.0726 | 3 | 3 | 0.000 / 0.000 | 1.0726 / 1.0726 | 2.9013 | 14.506 |
| 21:30-22:00 |  | 5/5 |  | 1.0585 | 1.0585 | 3 | 3 | 0.000 / 0.000 | 1.0585 / 1.0585 | 2.8731 | 14.365 |
| 22:00-22:30 |  | 5/5 |  | 1.0672 | 1.0672 | 3 | 3 | 0.000 / 0.000 | 1.0672 / 1.0672 | 2.8904 | 14.452 |
| 22:30-23:00 |  | 5/5 |  | 1.0741 | 1.0741 | 3 | 3 | 0.000 / 0.000 | 1.0741 / 1.0741 | 2.9042 | 14.521 |
| 23:00-23:30 |  | 5/5 |  | 1.0777 | 1.0777 | 3 | 3 | 0.000 / 0.000 | 1.0777 / 1.0777 | 2.9114 | 14.557 |
| 23:30-00:00 |  | 5/5 |  | 1.0458 | 1.0458 | 3 | 3 | 0.000 / 0.000 | 1.0458 / 1.0458 | 2.8477 | 14.238 |
| 00:00-00:30 |  | 5/5 |  | 1.0776 | 1.0776 | 3 | 3 | 0.000 / 0.000 | 1.0776 / 1.0776 | 2.9112 | 14.556 |
| 00:30-01:00 |  | 5/5 |  | 1.0259 | 1.0259 | 3 | 3 | 0.000 / 0.000 | 1.0259 / 1.0259 | 2.8078 | 14.039 |
| 01:00-01:30 |  | 5/5 |  | 1.0909 | 1.0909 | 3 | 3 | 0.000 / 0.000 | 1.0909 / 1.0909 | 2.9378 | 14.689 |
| 01:30-02:00 |  | 5/5 |  | 1.1097 | 1.1097 | 3 | 3 | 0.000 / 0.000 | 1.1097 / 1.1097 | 2.9755 | 14.877 |
| 02:00-02:30 |  | 5/5 |  | 1.0534 | 1.0534 | 3 | 3 | 0.000 / 0.000 | 1.0534 / 1.0534 | 2.8628 | 14.314 |
| 02:30-03:00 |  | 5/5 |  | 1.0801 | 1.0801 | 3 | 3 | 0.000 / 0.000 | 1.0801 / 1.0801 | 2.9162 | 14.581 |
| 03:00-03:30 |  | 5/5 |  | 1.0393 | 1.0393 | 3 | 3 | 0.000 / 0.000 | 1.0393 / 1.0393 | 2.8345 | 14.173 |
| 03:30-04:00 |  | 5/5 |  | 1.0490 | 1.0490 | 3 | 3 | 0.000 / 0.000 | 1.0490 / 1.0490 | 2.8540 | 14.270 |
| 04:00-04:30 |  | 5/5 |  | 1.1188 | 1.1188 | 3 | 3 | 0.000 / 0.000 | 1.1188 / 1.1188 | 2.9936 | 14.968 |
| 04:30-05:00 |  | 5/5 |  | 1.1072 | 1.1072 | 3 | 3 | 0.000 / 0.000 | 1.1072 / 1.1072 | 2.9704 | 14.852 |
| 05:00-05:30 |  | 5/5 |  | 1.1000 | 1.1000 | 3 | 3 | 0.000 / 0.000 | 1.1000 / 1.1000 | 2.9560 | 14.780 |
| 05:30-06:00 |  | 5/5 |  | 1.0798 | 1.0798 | 3 | 3 | 0.000 / 0.000 | 1.0798 / 1.0798 | 2.9157 | 14.578 |
| 06:00-06:30 |  | 5/5 |  | 1.0484 | 1.0484 | 3 | 3 | 0.000 / 0.000 | 1.0484 / 1.0484 | 2.8528 | 14.264 |
| 06:30-07:00 |  | 5/5 |  | 1.1047 | 1.1047 | 3 | 3 | 0.000 / 0.000 | 1.1047 / 1.1047 | 2.9655 | 14.827 |
| 07:00-07:30 |  | 5/5 |  | 1.0628 | 1.0628 | 3 | 3 | 0.000 / 0.000 | 1.0628 / 1.0628 | 2.8817 | 14.408 |
| 07:30-08:00 |  | 5/5 |  | 1.0939 | 1.0939 | 3 | 3 | 0.000 / 0.000 | 1.0939 / 1.0939 | 2.9437 | 14.719 |
| 08:00-08:30 |  | 5/5 |  | 1.0447 | 1.0447 | 3 | 3 | 0.000 / 0.000 | 1.0447 / 1.0447 | 2.8454 | 14.227 |
| 08:30-09:00 | D | 5/5 |  | 1.0614 | 1.0614 | 3 | 3 | 0.000 / 0.000 | 1.0614 / 1.0614 | 2.8788 | 14.394 |
| 09:00-09:30 | D | 5/5 |  | 1.0429 | 1.0429 | 3 | 3 | 0.000 / 0.000 | 1.0429 / 1.0429 | 2.8418 | 14.209 |
| 09:30-10:00 | D | 5/5 |  | 1.0254 | 1.0254 | 4 | 4 | 0.000 / 0.000 | 1.0254 / 1.0254 | 2.8069 | 14.034 |
| 10:00-10:30 | D | 5/5 |  | 1.0156 | 1.0156 | 4 | 4 | 0.000 / 0.000 | 1.0156 / 1.0156 | 2.7873 | 13.936 |
| 10:30-11:00 | D | 5/5 |  | 1.0401 | 1.0401 | 4 | 4 | 0.000 / 0.000 | 1.0401 / 1.0401 | 2.8363 | 14.181 |
| 11:00-11:30 | D | 5/5 |  | 1.0423 | 1.0423 | 4 | 4 | 0.000 / 0.000 | 1.0423 / 1.0423 | 2.8407 | 14.203 |
| 11:30-12:00 | D | 5/5 |  | 1.0418 | 1.0418 | 4 | 4 | 0.000 / 0.000 | 1.0418 / 1.0418 | 2.8396 | 14.198 |
| 12:00-12:30 | D | 5/5 |  | 1.0438 | 1.0438 | 4 | 4 | 0.000 / 0.000 | 1.0438 / 1.0438 | 2.8436 | 14.218 |
| 12:30-13:00 | D | 5/5 |  | 1.0460 | 1.0460 | 4 | 4 | 0.000 / 0.000 | 1.0460 / 1.0460 | 2.8479 | 14.240 |
| 13:00-13:30 | D | 5/5 |  | 1.0277 | 1.0277 | 4 | 4 | 0.000 / 0.000 | 1.0277 / 1.0277 | 2.8114 | 14.057 |
| 13:30-14:00 | D | 5/5 |  | 1.0226 | 1.0226 | 4 | 4 | 0.000 / 0.000 | 1.0226 / 1.0226 | 2.8012 | 14.006 |
| 14:00-14:30 | D | 5/5 |  | 1.0267 | 1.0267 | 4 | 4 | 0.000 / 0.000 | 1.0267 / 1.0267 | 2.8095 | 14.047 |
| 14:30-15:00 | D | 5/5 |  | 1.0014 | 1.0014 | 4 | 4 | 0.000 / 0.000 | 1.0014 / 1.0014 | 2.7589 | 13.794 |
| 15:00-15:30 |  | 5/5 |  | 1.0258 | 1.0258 | 3 | 3 | 0.000 / 0.000 | 1.0258 / 1.0258 | 2.8076 | 14.038 |
| 15:30-16:00 |  | 5/5 |  | 1.0372 | 1.0372 | 4 | 3 | 0.000 / 0.000 | 1.0372 / 1.0372 | 2.8304 | 14.152 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/YM_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 22dbeb54e2a6a430f9a28e652aaf1c520cd138abee8f478d53c9949e6585d1f6 (1,900,930 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/YM_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 69c5644f968cde8985ce058f6ec2ae49d11ce66f3e7a24a51cc71dc70aa3c2c4 (1,732,254 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/YM_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` ed49defb273f0bd8b34fd9bcc09e1b670d3edaf03a9f477e3803fb822f733d9d (2,510,644 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/YM_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` da24aa39b0933e30bee7bb59b18411be4a1e00124fcf0b1cfe9d5500f4510674 (3,546,336 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/YM_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` ef2ee69f5675eff8f4872686fc29357f875d9b7cdf4fcb53668a9d70bad7beef (1,575,874 records)

### ZB (rates)

Tick 0.03125 (vendor units 0.03125, factor 1), tick value $31.25; commission $2.76 round turn = 0.0883 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.5168, sell 0.5168 ticks (round turn inside a window 1.1219 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5004 | 0.5004 | 157 | 129 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.0891 | 34.033 |
| 17:30-18:00 |  | 5/5 |  | 0.5021 | 0.5021 | 195 | 201 | 0.000 / 0.000 | 0.5021 / 0.5021 | 1.0924 | 34.139 |
| 18:00-18:30 |  | 5/5 |  | 0.5001 | 0.5001 | 203 | 252 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0885 | 34.016 |
| 18:30-19:00 |  | 5/5 |  | 0.5168 | 0.5168 | 289 | 240 | 0.000 / 0.000 | 0.5168 / 0.5168 | 1.1219 | 35.061 |
| 19:00-19:30 |  | 5/5 |  | 0.5017 | 0.5017 | 329 | 265 | 0.000 / 0.000 | 0.5017 / 0.5017 | 1.0917 | 34.114 |
| 19:30-20:00 |  | 5/5 |  | 0.5016 | 0.5016 | 310 | 247 | 0.000 / 0.000 | 0.5016 / 0.5016 | 1.0916 | 34.112 |
| 20:00-20:30 |  | 5/5 |  | 0.5047 | 0.5047 | 353 | 295 | 0.000 / 0.000 | 0.5047 / 0.5047 | 1.0977 | 34.302 |
| 20:30-21:00 |  | 5/5 |  | 0.5003 | 0.5003 | 306 | 370 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.0890 | 34.031 |
| 21:00-21:30 |  | 5/5 |  | 0.5010 | 0.5010 | 303 | 388 | 0.000 / 0.000 | 0.5010 / 0.5010 | 1.0903 | 34.072 |
| 21:30-22:00 |  | 5/5 |  | 0.5001 | 0.5001 | 397 | 435 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0885 | 34.016 |
| 22:00-22:30 |  | 5/5 |  | 0.5001 | 0.5001 | 445 | 423 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0886 | 34.018 |
| 22:30-23:00 |  | 5/5 |  | 0.5002 | 0.5002 | 371 | 373 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.0886 | 34.020 |
| 23:00-23:30 |  | 5/5 |  | 0.5005 | 0.5005 | 480 | 404 | 0.000 / 0.000 | 0.5005 / 0.5005 | 1.0894 | 34.044 |
| 23:30-00:00 |  | 5/5 |  | 0.5008 | 0.5008 | 356 | 482 | 0.000 / 0.000 | 0.5008 / 0.5008 | 1.0899 | 34.060 |
| 00:00-00:30 |  | 5/5 |  | 0.5005 | 0.5005 | 334 | 434 | 0.000 / 0.000 | 0.5005 / 0.5005 | 1.0893 | 34.040 |
| 00:30-01:00 |  | 5/5 |  | 0.5014 | 0.5014 | 369 | 385 | 0.000 / 0.000 | 0.5014 / 0.5014 | 1.0910 | 34.095 |
| 01:00-01:30 |  | 5/5 |  | 0.5023 | 0.5023 | 452 | 410 | 0.000 / 0.000 | 0.5023 / 0.5023 | 1.0929 | 34.153 |
| 01:30-02:00 |  | 5/5 |  | 0.5004 | 0.5004 | 406 | 537 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.0890 | 34.032 |
| 02:00-02:30 |  | 5/5 |  | 0.5007 | 0.5007 | 592 | 541 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.0897 | 34.053 |
| 02:30-03:00 |  | 5/5 |  | 0.5005 | 0.5005 | 565 | 630 | 0.000 / 0.000 | 0.5005 / 0.5005 | 1.0893 | 34.041 |
| 03:00-03:30 |  | 5/5 |  | 0.5007 | 0.5007 | 579 | 721 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.0897 | 34.053 |
| 03:30-04:00 |  | 5/5 |  | 0.5011 | 0.5011 | 670 | 704 | 0.000 / 0.000 | 0.5011 / 0.5011 | 1.0905 | 34.077 |
| 04:00-04:30 |  | 5/5 |  | 0.5009 | 0.5009 | 677 | 645 | 0.000 / 0.000 | 0.5009 / 0.5009 | 1.0900 | 34.064 |
| 04:30-05:00 |  | 5/5 |  | 0.5008 | 0.5008 | 569 | 640 | 0.000 / 0.000 | 0.5008 / 0.5008 | 1.0899 | 34.058 |
| 05:00-05:30 |  | 5/5 |  | 0.5033 | 0.5033 | 554 | 607 | 0.000 / 0.000 | 0.5033 / 0.5033 | 1.0950 | 34.219 |
| 05:30-06:00 |  | 5/5 |  | 0.5023 | 0.5023 | 574 | 579 | 0.000 / 0.000 | 0.5023 / 0.5023 | 1.0930 | 34.155 |
| 06:00-06:30 |  | 5/5 |  | 0.5030 | 0.5030 | 479 | 556 | 0.000 / 0.000 | 0.5030 / 0.5030 | 1.0944 | 34.200 |
| 06:30-07:00 |  | 5/5 |  | 0.5010 | 0.5010 | 533 | 596 | 0.000 / 0.000 | 0.5010 / 0.5010 | 1.0904 | 34.075 |
| 07:00-07:30 | D | 5/5 |  | 0.5016 | 0.5016 | 620 | 650 | 0.000 / 0.000 | 0.5016 / 0.5016 | 1.0916 | 34.112 |
| 07:30-08:00 | D | 5/5 |  | 0.5014 | 0.5014 | 665 | 645 | 0.000 / 0.000 | 0.5014 / 0.5014 | 1.0912 | 34.100 |
| 08:00-08:30 | D | 5/5 |  | 0.5003 | 0.5003 | 766 | 784 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.0889 | 34.028 |
| 08:30-09:00 | D | 5/5 |  | 0.5005 | 0.5005 | 801 | 793 | 0.000 / 0.000 | 0.5005 / 0.5005 | 1.0893 | 34.041 |
| 09:00-09:30 | D | 5/5 |  | 0.5017 | 0.5017 | 856 | 863 | 0.000 / 0.000 | 0.5017 / 0.5017 | 1.0917 | 34.114 |
| 09:30-10:00 | D | 5/5 |  | 0.5002 | 0.5002 | 910 | 949 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.0888 | 34.025 |
| 10:00-10:30 | D | 5/5 |  | 0.5003 | 0.5003 | 935 | 957 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.0890 | 34.031 |
| 10:30-11:00 | D | 5/5 |  | 0.5007 | 0.5007 | 955 | 974 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.0897 | 34.055 |
| 11:00-11:30 | D | 5/5 |  | 0.5001 | 0.5001 | 1011 | 1010 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0884 | 34.014 |
| 11:30-12:00 | D | 5/5 |  | 0.5004 | 0.5004 | 1043 | 998 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.0892 | 34.037 |
| 12:00-12:30 | D | 5/5 |  | 0.5004 | 0.5004 | 939 | 966 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.0891 | 34.035 |
| 12:30-13:00 | D | 5/5 |  | 0.5000 | 0.5000 | 1114 | 1034 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.0883 | 34.010 |
| 13:00-13:30 | D | 5/5 |  | 0.5001 | 0.5001 | 1184 | 1118 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0884 | 34.013 |
| 13:30-14:00 | D | 5/5 |  | 0.5000 | 0.5000 | 1222 | 1258 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.0883 | 34.010 |
| 14:00-14:30 |  | 5/5 |  | 0.5002 | 0.5002 | 1273 | 1213 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.0888 | 34.025 |
| 14:30-15:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1426 | 1329 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.0883 | 34.010 |
| 15:00-15:30 |  | 5/5 |  | 0.5001 | 0.5001 | 1099 | 1189 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0884 | 34.014 |
| 15:30-16:00 |  | 5/5 |  | 0.5001 | 0.5001 | 895 | 849 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.0884 | 34.013 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZB_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 65974316d590956defb86d2f4358d0ba0c7b5d2f4e4a92fe99f4959f5839f395 (843,565 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZB_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 912880d99aad3b2bdf4d9349f8cf0518474b278e1ebcd791af25abb2edaef608 (662,660 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZB_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 4b2d00987a64acde950891529cae9e815aebba5a1fcff402663bea6f55e0a005 (889,601 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZB_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` c264f4ac6ef039f3e2e3b6a977de01f98443b1647a04e484e1364b53eb9e41cb (1,344,747 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZB_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` f08bf8231432473a84bcf034cc038b54264f10880d4617338e3197b78d7009ab (739,636 records)

### ZC (grains)

Tick 0.0025 (vendor units 0.2500, factor 100), tick value $12.5; commission $5.28 round turn = 0.4224 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:15 CT.

Event-window one-side slippage: buy 0.5366, sell 0.5366 ticks (round turn inside a window 1.4956 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:00-19:30 |  | 5/5 |  | 0.5114 | 0.5114 | 101 | 95 | 0.000 / 0.000 | 0.5114 / 0.5114 | 1.4451 | 18.064 |
| 19:30-20:00 |  | 5/5 |  | 0.5158 | 0.5158 | 113 | 128 | 0.000 / 0.000 | 0.5158 / 0.5158 | 1.4539 | 18.174 |
| 20:00-20:30 |  | 5/5 |  | 0.5225 | 0.5225 | 101 | 159 | 0.000 / 0.000 | 0.5225 / 0.5225 | 1.4674 | 18.342 |
| 20:30-21:00 |  | 5/5 |  | 0.5143 | 0.5143 | 140 | 144 | 0.000 / 0.000 | 0.5143 / 0.5143 | 1.4510 | 18.137 |
| 21:00-21:30 |  | 5/5 |  | 0.5276 | 0.5276 | 180 | 137 | 0.000 / 0.000 | 0.5276 / 0.5276 | 1.4776 | 18.470 |
| 21:30-22:00 |  | 5/5 |  | 0.5215 | 0.5215 | 112 | 173 | 0.000 / 0.000 | 0.5215 / 0.5215 | 1.4655 | 18.318 |
| 22:00-22:30 |  | 5/5 |  | 0.5045 | 0.5045 | 103 | 204 | 0.000 / 0.000 | 0.5045 / 0.5045 | 1.4313 | 17.891 |
| 22:30-23:00 |  | 5/5 |  | 0.5042 | 0.5042 | 116 | 171 | 0.000 / 0.000 | 0.5042 / 0.5042 | 1.4307 | 17.884 |
| 23:00-23:30 |  | 5/5 |  | 0.5366 | 0.5366 | 151 | 148 | 0.000 / 0.000 | 0.5366 / 0.5366 | 1.4956 | 18.695 |
| 23:30-00:00 |  | 5/5 |  | 0.5259 | 0.5259 | 231 | 123 | 0.000 / 0.000 | 0.5259 / 0.5259 | 1.4743 | 18.429 |
| 00:00-00:30 |  | 5/5 |  | 0.5014 | 0.5014 | 152 | 130 | 0.000 / 0.000 | 0.5014 / 0.5014 | 1.4252 | 17.815 |
| 00:30-01:00 |  | 5/5 |  | 0.5095 | 0.5095 | 207 | 102 | 0.000 / 0.000 | 0.5095 / 0.5095 | 1.4413 | 18.017 |
| 01:00-01:30 |  | 5/5 |  | 0.5112 | 0.5112 | 203 | 139 | 0.000 / 0.000 | 0.5112 / 0.5112 | 1.4449 | 18.061 |
| 01:30-02:00 |  | 5/5 |  | 0.5303 | 0.5303 | 263 | 126 | 0.000 / 0.000 | 0.5303 / 0.5303 | 1.4830 | 18.537 |
| 02:00-02:30 |  | 5/5 |  | 0.5182 | 0.5182 | 206 | 170 | 0.000 / 0.000 | 0.5182 / 0.5182 | 1.4588 | 18.235 |
| 02:30-03:00 |  | 5/5 |  | 0.5277 | 0.5277 | 286 | 87 | 0.000 / 0.000 | 0.5277 / 0.5277 | 1.4778 | 18.472 |
| 03:00-03:30 |  | 5/5 |  | 0.5071 | 0.5071 | 280 | 111 | 0.000 / 0.000 | 0.5071 / 0.5071 | 1.4366 | 17.957 |
| 03:30-04:00 |  | 5/5 |  | 0.5087 | 0.5087 | 169 | 147 | 0.000 / 0.000 | 0.5087 / 0.5087 | 1.4398 | 17.997 |
| 04:00-04:30 |  | 5/5 |  | 0.5319 | 0.5319 | 230 | 131 | 0.000 / 0.000 | 0.5319 / 0.5319 | 1.4862 | 18.578 |
| 04:30-05:00 |  | 5/5 |  | 0.5265 | 0.5265 | 223 | 149 | 0.000 / 0.000 | 0.5265 / 0.5265 | 1.4753 | 18.442 |
| 05:00-05:30 |  | 5/5 |  | 0.5295 | 0.5295 | 246 | 136 | 0.000 / 0.000 | 0.5295 / 0.5295 | 1.4814 | 18.518 |
| 05:30-06:00 |  | 5/5 |  | 0.5159 | 0.5159 | 188 | 162 | 0.000 / 0.000 | 0.5159 / 0.5159 | 1.4542 | 18.178 |
| 06:00-06:30 |  | 5/5 |  | 0.5201 | 0.5201 | 185 | 215 | 0.000 / 0.000 | 0.5201 / 0.5201 | 1.4625 | 18.282 |
| 06:30-07:00 |  | 5/5 |  | 0.5195 | 0.5195 | 219 | 228 | 0.000 / 0.000 | 0.5195 / 0.5195 | 1.4613 | 18.267 |
| 07:00-07:30 |  | 5/5 |  | 0.5125 | 0.5125 | 120 | 266 | 0.000 / 0.000 | 0.5125 / 0.5125 | 1.4473 | 18.091 |
| 07:30-07:45 |  | 5/5 |  | 0.5097 | 0.5097 | 201 | 171 | 0.000 / 0.000 | 0.5097 / 0.5097 | 1.4418 | 18.023 |
| 08:30-09:00 | D | 5/5 |  | 0.5036 | 0.5036 | 222 | 263 | 0.000 / 0.000 | 0.5036 / 0.5036 | 1.4296 | 17.870 |
| 09:00-09:30 | D | 5/5 |  | 0.5014 | 0.5014 | 345 | 313 | 0.000 / 0.000 | 0.5014 / 0.5014 | 1.4252 | 17.815 |
| 09:30-10:00 | D | 5/5 |  | 0.5005 | 0.5005 | 349 | 342 | 0.000 / 0.000 | 0.5005 / 0.5005 | 1.4234 | 17.792 |
| 10:00-10:30 | D | 5/5 |  | 0.5008 | 0.5008 | 279 | 312 | 0.000 / 0.000 | 0.5008 / 0.5008 | 1.4239 | 17.799 |
| 10:30-11:00 | D | 5/5 |  | 0.5016 | 0.5016 | 282 | 496 | 0.000 / 0.000 | 0.5016 / 0.5016 | 1.4256 | 17.820 |
| 11:00-11:30 | D | 5/5 |  | 0.5012 | 0.5012 | 675 | 401 | 0.000 / 0.000 | 0.5012 / 0.5012 | 1.4247 | 17.809 |
| 11:30-12:00 | D | 5/5 |  | 0.5006 | 0.5006 | 426 | 557 | 0.000 / 0.000 | 0.5006 / 0.5006 | 1.4236 | 17.795 |
| 12:00-12:30 | D | 5/5 |  | 0.5010 | 0.5010 | 582 | 379 | 0.000 / 0.000 | 0.5010 / 0.5010 | 1.4244 | 17.805 |
| 12:30-13:00 | D | 5/5 |  | 0.5024 | 0.5024 | 456 | 484 | 0.000 / 0.000 | 0.5024 / 0.5024 | 1.4272 | 17.840 |
| 13:00-13:20 | D | 5/5 |  | 0.5021 | 0.5021 | 511 | 819 | 0.000 / 0.000 | 0.5021 / 0.5021 | 1.4266 | 17.832 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZC_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 5f4bb051cec95125086eb7d737bedb7e39964b4388c80ccf6e060a1d92d3023c (166,055 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZC_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` cfc70b7eca493065f7c4bee43586af0ebf98398f2c2a80f0b36f4dfd7caf8e02 (112,306 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZC_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 227f5f9dbec1c4c81e0ac1a8ab64a9d5402dde1f73c7e1c3cdccf4f39afdf164 (117,541 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZC_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 3a9d9111811032bd34265cf4453b5bcd52c5c46745bdb2a1f231a4a859d9993f (128,057 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZC_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 723e0832831a17301d13750966976712a7e533ce6440fa70d9a3ff1204b64b47 (175,192 records)

### ZF (rates)

Tick 0.0078125 (vendor units 0.0078125, factor 1), tick value $7.8125; commission $2.32 round turn = 0.2970 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.5081, sell 0.5081 ticks (round turn inside a window 1.3132 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5012 | 0.5012 | 235 | 184 | 0.000 / 0.000 | 0.5012 / 0.5012 | 1.2994 | 10.151 |
| 17:30-18:00 |  | 5/5 |  | 0.5000 | 0.5000 | 294 | 305 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 18:00-18:30 |  | 5/5 |  | 0.5000 | 0.5000 | 480 | 389 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 18:30-19:00 |  | 5/5 |  | 0.5081 | 0.5081 | 540 | 426 | 0.000 / 0.000 | 0.5081 / 0.5081 | 1.3132 | 10.259 |
| 19:00-19:30 |  | 5/5 |  | 0.5063 | 0.5063 | 374 | 607 | 0.000 / 0.000 | 0.5063 / 0.5063 | 1.3096 | 10.232 |
| 19:30-20:00 |  | 5/5 |  | 0.5010 | 0.5010 | 607 | 637 | 0.000 / 0.000 | 0.5010 / 0.5010 | 1.2989 | 10.148 |
| 20:00-20:30 |  | 5/5 |  | 0.5004 | 0.5004 | 406 | 765 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.2979 | 10.140 |
| 20:30-21:00 |  | 5/5 |  | 0.5031 | 0.5031 | 583 | 659 | 0.000 / 0.000 | 0.5031 / 0.5031 | 1.3032 | 10.181 |
| 21:00-21:30 |  | 5/5 |  | 0.5030 | 0.5030 | 687 | 570 | 0.000 / 0.000 | 0.5030 / 0.5030 | 1.3030 | 10.180 |
| 21:30-22:00 |  | 5/5 |  | 0.5007 | 0.5007 | 679 | 721 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.2983 | 10.143 |
| 22:00-22:30 |  | 5/5 |  | 0.5000 | 0.5000 | 464 | 772 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 22:30-23:00 |  | 5/5 |  | 0.5007 | 0.5007 | 472 | 740 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.2984 | 10.144 |
| 23:00-23:30 |  | 5/5 |  | 0.5002 | 0.5002 | 670 | 853 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2974 | 10.136 |
| 23:30-00:00 |  | 5/5 |  | 0.5004 | 0.5004 | 744 | 855 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.2978 | 10.139 |
| 00:00-00:30 |  | 5/5 |  | 0.5007 | 0.5007 | 646 | 649 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.2984 | 10.144 |
| 00:30-01:00 |  | 5/5 |  | 0.5019 | 0.5019 | 723 | 718 | 0.000 / 0.000 | 0.5019 / 0.5019 | 1.3008 | 10.162 |
| 01:00-01:30 |  | 5/5 |  | 0.5014 | 0.5014 | 736 | 831 | 0.000 / 0.000 | 0.5014 / 0.5014 | 1.2998 | 10.155 |
| 01:30-02:00 |  | 5/5 |  | 0.5000 | 0.5000 | 858 | 948 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 02:00-02:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1117 | 984 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 02:30-03:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1001 | 1149 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 03:00-03:30 |  | 5/5 |  | 0.5003 | 0.5003 | 1106 | 896 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.2975 | 10.137 |
| 03:30-04:00 |  | 5/5 |  | 0.5004 | 0.5004 | 1051 | 1191 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.2978 | 10.139 |
| 04:00-04:30 |  | 5/5 |  | 0.5002 | 0.5002 | 1109 | 1019 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2974 | 10.136 |
| 04:30-05:00 |  | 5/5 |  | 0.5001 | 0.5001 | 1190 | 1050 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2971 | 10.134 |
| 05:00-05:30 |  | 5/5 |  | 0.5001 | 0.5001 | 1176 | 1015 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2972 | 10.134 |
| 05:30-06:00 |  | 5/5 |  | 0.5003 | 0.5003 | 1051 | 934 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.2975 | 10.137 |
| 06:00-06:30 |  | 5/5 |  | 0.5006 | 0.5006 | 1040 | 1016 | 0.000 / 0.000 | 0.5006 / 0.5006 | 1.2982 | 10.142 |
| 06:30-07:00 |  | 5/5 |  | 0.5003 | 0.5003 | 1052 | 1307 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.2976 | 10.137 |
| 07:00-07:30 | D | 5/5 |  | 0.5016 | 0.5016 | 1149 | 1304 | 0.000 / 0.000 | 0.5016 / 0.5016 | 1.3001 | 10.157 |
| 07:30-08:00 | D | 5/5 |  | 0.5007 | 0.5007 | 1157 | 1150 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.2984 | 10.144 |
| 08:00-08:30 | D | 5/5 |  | 0.5001 | 0.5001 | 1566 | 1514 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2971 | 10.134 |
| 08:30-09:00 | D | 5/5 |  | 0.5001 | 0.5001 | 1410 | 1586 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2972 | 10.134 |
| 09:00-09:30 | D | 5/5 |  | 0.5002 | 0.5002 | 1634 | 1763 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2974 | 10.136 |
| 09:30-10:00 | D | 5/5 |  | 0.5010 | 0.5010 | 1909 | 1700 | 0.000 / 0.000 | 0.5010 / 0.5010 | 1.2990 | 10.148 |
| 10:00-10:30 | D | 5/5 |  | 0.5001 | 0.5001 | 2014 | 1952 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2972 | 10.134 |
| 10:30-11:00 | D | 5/5 |  | 0.5002 | 0.5002 | 2039 | 1931 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2973 | 10.135 |
| 11:00-11:30 | D | 5/5 |  | 0.5003 | 0.5003 | 2191 | 2149 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.2976 | 10.138 |
| 11:30-12:00 | D | 5/5 |  | 0.5006 | 0.5006 | 2190 | 2094 | 0.000 / 0.000 | 0.5006 / 0.5006 | 1.2981 | 10.142 |
| 12:00-12:30 | D | 5/5 |  | 0.5023 | 0.5023 | 1885 | 1859 | 0.000 / 0.000 | 0.5023 / 0.5023 | 1.3015 | 10.168 |
| 12:30-13:00 | D | 5/5 |  | 0.5001 | 0.5001 | 1810 | 2335 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2972 | 10.134 |
| 13:00-13:30 | D | 5/5 |  | 0.5002 | 0.5002 | 1622 | 2265 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2975 | 10.136 |
| 13:30-14:00 | D | 5/5 |  | 0.5000 | 0.5000 | 2667 | 2456 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 14:00-14:30 |  | 5/5 |  | 0.5001 | 0.5001 | 2353 | 2729 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2971 | 10.133 |
| 14:30-15:00 |  | 5/5 |  | 0.5002 | 0.5002 | 2395 | 2790 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2973 | 10.135 |
| 15:00-15:30 |  | 5/5 |  | 0.5004 | 0.5004 | 2331 | 2070 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.2977 | 10.138 |
| 15:30-16:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1984 | 2003 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZF_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` af4ce959efd20131d63c894928d50df42c97e1dc0b9bd36f34ebefbe509f1fc2 (1,761,778 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZF_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 5b301388b0ede16c5320d2ab4008709c5aa43416bf29a57f824f385a1c2803cc (1,202,656 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZF_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` c2a3929ff4bb0cc4ad81a0ff290b745193ef7c91074303945e22b97dcb1f2d7f (1,421,960 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZF_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 7bc3d1c362d4513767121bf3163f81e12fe92bec90877c5e17b02fe00867fb3e (2,073,138 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZF_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 6470d8a096fa3e67bd47c88a219aeb1a19c7e684668740626e4a784023926642 (1,540,112 records)

### ZL (grains)

Tick 0.0001 (vendor units 0.0100, factor 100), tick value $6.0; commission $5.28 round turn = 0.8800 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:15 CT.

Event-window one-side slippage: buy 0.8973, sell 0.8973 ticks (round turn inside a window 2.6746 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:00-19:30 |  | 5/5 |  | 0.8973 | 0.8973 | 3 | 3 | 0.000 / 0.000 | 0.8973 / 0.8973 | 2.6746 | 16.048 |
| 19:30-20:00 |  | 5/5 |  | 0.8143 | 0.8143 | 3 | 3 | 0.000 / 0.000 | 0.8143 / 0.8143 | 2.5086 | 15.052 |
| 20:00-20:30 |  | 5/5 |  | 0.8899 | 0.8899 | 3 | 3 | 0.000 / 0.000 | 0.8899 / 0.8899 | 2.6597 | 15.958 |
| 20:30-21:00 |  | 5/5 |  | 0.8304 | 0.8304 | 3 | 3 | 0.000 / 0.000 | 0.8304 / 0.8304 | 2.5409 | 15.245 |
| 21:00-21:30 |  | 5/5 |  | 0.8006 | 0.8006 | 3 | 3 | 0.000 / 0.000 | 0.8006 / 0.8006 | 2.4812 | 14.887 |
| 21:30-22:00 |  | 5/5 |  | 0.8493 | 0.8493 | 3 | 2 | 0.000 / 0.000 | 0.8493 / 0.8493 | 2.5786 | 15.472 |
| 22:00-22:30 |  | 5/5 |  | 0.8015 | 0.8015 | 4 | 3 | 0.000 / 0.000 | 0.8015 / 0.8015 | 2.4831 | 14.898 |
| 22:30-23:00 |  | 5/5 |  | 0.8143 | 0.8143 | 4 | 3 | 0.000 / 0.000 | 0.8143 / 0.8143 | 2.5086 | 15.052 |
| 23:00-23:30 |  | 5/5 |  | 0.7997 | 0.7997 | 3 | 3 | 0.000 / 0.000 | 0.7997 / 0.7997 | 2.4795 | 14.877 |
| 23:30-00:00 |  | 5/5 |  | 0.7629 | 0.7629 | 4 | 4 | 0.000 / 0.000 | 0.7629 / 0.7629 | 2.4057 | 14.434 |
| 00:00-00:30 |  | 5/5 |  | 0.7698 | 0.7698 | 4 | 4 | 0.000 / 0.000 | 0.7698 / 0.7698 | 2.4195 | 14.517 |
| 00:30-01:00 |  | 5/5 |  | 0.7872 | 0.7872 | 4 | 4 | 0.000 / 0.000 | 0.7872 / 0.7872 | 2.4545 | 14.727 |
| 01:00-01:30 |  | 5/5 |  | 0.7737 | 0.7737 | 4 | 3 | 0.000 / 0.000 | 0.7737 / 0.7737 | 2.4275 | 14.565 |
| 01:30-02:00 |  | 5/5 |  | 0.7854 | 0.7854 | 4 | 3 | 0.000 / 0.000 | 0.7854 / 0.7854 | 2.4507 | 14.704 |
| 02:00-02:30 |  | 5/5 |  | 0.7638 | 0.7638 | 3 | 4 | 0.000 / 0.000 | 0.7638 / 0.7638 | 2.4075 | 14.445 |
| 02:30-03:00 |  | 5/5 |  | 0.7430 | 0.7430 | 3 | 3 | 0.000 / 0.000 | 0.7430 / 0.7430 | 2.3659 | 14.195 |
| 03:00-03:30 |  | 5/5 |  | 0.7762 | 0.7762 | 3 | 3 | 0.000 / 0.000 | 0.7762 / 0.7762 | 2.4325 | 14.595 |
| 03:30-04:00 |  | 5/5 |  | 0.7446 | 0.7446 | 4 | 3 | 0.000 / 0.000 | 0.7446 / 0.7446 | 2.3692 | 14.215 |
| 04:00-04:30 |  | 5/5 |  | 0.7616 | 0.7616 | 4 | 3 | 0.000 / 0.000 | 0.7616 / 0.7616 | 2.4031 | 14.419 |
| 04:30-05:00 |  | 5/5 |  | 0.7621 | 0.7621 | 3 | 3 | 0.000 / 0.000 | 0.7621 / 0.7621 | 2.4042 | 14.425 |
| 05:00-05:30 |  | 5/5 |  | 0.7983 | 0.7983 | 4 | 3 | 0.000 / 0.000 | 0.7983 / 0.7983 | 2.4765 | 14.859 |
| 05:30-06:00 |  | 5/5 |  | 0.7859 | 0.7859 | 3 | 3 | 0.000 / 0.000 | 0.7859 / 0.7859 | 2.4517 | 14.710 |
| 06:00-06:30 |  | 5/5 |  | 0.7792 | 0.7792 | 3 | 3 | 0.000 / 0.000 | 0.7792 / 0.7792 | 2.4385 | 14.631 |
| 06:30-07:00 |  | 5/5 |  | 0.7762 | 0.7762 | 4 | 3 | 0.000 / 0.000 | 0.7762 / 0.7762 | 2.4324 | 14.594 |
| 07:00-07:30 |  | 5/5 |  | 0.7824 | 0.7824 | 4 | 4 | 0.000 / 0.000 | 0.7824 / 0.7824 | 2.4449 | 14.669 |
| 07:30-07:45 |  | 5/5 |  | 0.7761 | 0.7761 | 4 | 4 | 0.000 / 0.000 | 0.7761 / 0.7761 | 2.4323 | 14.594 |
| 08:30-09:00 | D | 5/5 |  | 0.6572 | 0.6572 | 5 | 4 | 0.000 / 0.000 | 0.6572 / 0.6572 | 2.1945 | 13.167 |
| 09:00-09:30 | D | 5/5 |  | 0.6516 | 0.6516 | 5 | 5 | 0.000 / 0.000 | 0.6516 / 0.6516 | 2.1831 | 13.099 |
| 09:30-10:00 | D | 5/5 |  | 0.6404 | 0.6404 | 5 | 5 | 0.000 / 0.000 | 0.6404 / 0.6404 | 2.1608 | 12.965 |
| 10:00-10:30 | D | 5/5 |  | 0.6390 | 0.6390 | 6 | 5 | 0.000 / 0.000 | 0.6390 / 0.6390 | 2.1579 | 12.947 |
| 10:30-11:00 | D | 5/5 |  | 0.6505 | 0.6505 | 6 | 6 | 0.000 / 0.000 | 0.6505 / 0.6505 | 2.1809 | 13.085 |
| 11:00-11:30 | D | 5/5 |  | 0.6649 | 0.6649 | 6 | 6 | 0.000 / 0.000 | 0.6649 / 0.6649 | 2.2098 | 13.259 |
| 11:30-12:00 | D | 5/5 |  | 0.6166 | 0.6166 | 6 | 6 | 0.000 / 0.000 | 0.6166 / 0.6166 | 2.1132 | 12.679 |
| 12:00-12:30 | D | 5/5 |  | 0.6456 | 0.6456 | 8 | 7 | 0.000 / 0.000 | 0.6456 / 0.6456 | 2.1711 | 13.027 |
| 12:30-13:00 | D | 5/5 |  | 0.6427 | 0.6427 | 8 | 7 | 0.000 / 0.000 | 0.6427 / 0.6427 | 2.1655 | 12.993 |
| 13:00-13:20 | D | 5/5 |  | 0.6596 | 0.6596 | 9 | 7 | 0.000 / 0.000 | 0.6596 / 0.6596 | 2.1992 | 13.195 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZL_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 72684f3152ce1f8906abfe14a74a3c75728d785ac327650c56aedefbf87f45cb (262,041 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZL_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 04552b65eb30c7274889b9612120c82ef9b8641a19f0c9dab2f43c79e6b4093c (196,543 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZL_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` e7fad1325ddcd0c9c7d84a0e10f5847dabb85c135370e7fc6ddf619b45432f34 (218,099 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZL_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 20c8033098ba5e5ccb619ab60ec9c0e6699cbb143a531c4d6b9250d1bbec1e5e (239,564 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZL_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` fb9605abdfe7bbbb68050b8d5d04ca34b162fdf3199bef3e3ac080b2089f8e22 (234,939 records)

### ZM (grains)

Tick 0.10 (vendor units 0.10, factor 1), tick value $10.0; commission $5.28 round turn = 0.5280 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:15 CT.

Event-window one-side slippage: buy 0.6317, sell 0.6317 ticks (round turn inside a window 1.7915 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:00-19:30 |  | 5/5 |  | 0.6317 | 0.6317 | 7 | 9 | 0.000 / 0.000 | 0.6317 / 0.6317 | 1.7915 | 17.915 |
| 19:30-20:00 |  | 5/5 |  | 0.5874 | 0.5874 | 9 | 11 | 0.000 / 0.000 | 0.5874 / 0.5874 | 1.7029 | 17.029 |
| 20:00-20:30 |  | 5/5 |  | 0.6053 | 0.6053 | 11 | 9 | 0.000 / 0.000 | 0.6053 / 0.6053 | 1.7385 | 17.385 |
| 20:30-21:00 |  | 5/5 |  | 0.6073 | 0.6073 | 10 | 8 | 0.000 / 0.000 | 0.6073 / 0.6073 | 1.7427 | 17.427 |
| 21:00-21:30 |  | 5/5 |  | 0.5755 | 0.5755 | 12 | 10 | 0.000 / 0.000 | 0.5755 / 0.5755 | 1.6790 | 16.790 |
| 21:30-22:00 |  | 5/5 |  | 0.6015 | 0.6015 | 12 | 12 | 0.000 / 0.000 | 0.6015 / 0.6015 | 1.7310 | 17.310 |
| 22:00-22:30 |  | 5/5 |  | 0.5689 | 0.5689 | 14 | 9 | 0.000 / 0.000 | 0.5689 / 0.5689 | 1.6657 | 16.657 |
| 22:30-23:00 |  | 5/5 |  | 0.6031 | 0.6031 | 15 | 10 | 0.000 / 0.000 | 0.6031 / 0.6031 | 1.7342 | 17.342 |
| 23:00-23:30 |  | 5/5 |  | 0.5665 | 0.5665 | 11 | 11 | 0.000 / 0.000 | 0.5665 / 0.5665 | 1.6610 | 16.610 |
| 23:30-00:00 |  | 5/5 |  | 0.5550 | 0.5550 | 18 | 7 | 0.000 / 0.000 | 0.5550 / 0.5550 | 1.6379 | 16.379 |
| 00:00-00:30 |  | 5/5 |  | 0.5850 | 0.5850 | 12 | 13 | 0.000 / 0.000 | 0.5850 / 0.5850 | 1.6980 | 16.980 |
| 00:30-01:00 |  | 5/5 |  | 0.5650 | 0.5650 | 15 | 10 | 0.000 / 0.000 | 0.5650 / 0.5650 | 1.6580 | 16.580 |
| 01:00-01:30 |  | 5/5 |  | 0.5813 | 0.5813 | 12 | 12 | 0.000 / 0.000 | 0.5813 / 0.5813 | 1.6906 | 16.906 |
| 01:30-02:00 |  | 5/5 |  | 0.5962 | 0.5962 | 14 | 12 | 0.000 / 0.000 | 0.5962 / 0.5962 | 1.7205 | 17.205 |
| 02:00-02:30 |  | 5/5 |  | 0.6168 | 0.6168 | 12 | 13 | 0.000 / 0.000 | 0.6168 / 0.6168 | 1.7616 | 17.616 |
| 02:30-03:00 |  | 5/5 |  | 0.5771 | 0.5771 | 12 | 13 | 0.000 / 0.000 | 0.5771 / 0.5771 | 1.6822 | 16.822 |
| 03:00-03:30 |  | 5/5 |  | 0.6048 | 0.6048 | 11 | 15 | 0.000 / 0.000 | 0.6048 / 0.6048 | 1.7376 | 17.376 |
| 03:30-04:00 |  | 5/5 |  | 0.5778 | 0.5778 | 14 | 13 | 0.000 / 0.000 | 0.5778 / 0.5778 | 1.6836 | 16.836 |
| 04:00-04:30 |  | 5/5 |  | 0.5762 | 0.5762 | 13 | 14 | 0.000 / 0.000 | 0.5762 / 0.5762 | 1.6805 | 16.805 |
| 04:30-05:00 |  | 5/5 |  | 0.5708 | 0.5708 | 11 | 15 | 0.000 / 0.000 | 0.5708 / 0.5708 | 1.6696 | 16.696 |
| 05:00-05:30 |  | 5/5 |  | 0.5697 | 0.5697 | 13 | 11 | 0.000 / 0.000 | 0.5697 / 0.5697 | 1.6673 | 16.673 |
| 05:30-06:00 |  | 5/5 |  | 0.6068 | 0.6068 | 15 | 14 | 0.000 / 0.000 | 0.6068 / 0.6068 | 1.7417 | 17.417 |
| 06:00-06:30 |  | 5/5 |  | 0.5813 | 0.5813 | 16 | 14 | 0.000 / 0.000 | 0.5813 / 0.5813 | 1.6906 | 16.906 |
| 06:30-07:00 |  | 5/5 |  | 0.5991 | 0.5991 | 18 | 17 | 0.000 / 0.000 | 0.5991 / 0.5991 | 1.7262 | 17.262 |
| 07:00-07:30 |  | 5/5 |  | 0.5997 | 0.5997 | 18 | 12 | 0.000 / 0.000 | 0.5997 / 0.5997 | 1.7274 | 17.274 |
| 07:30-07:45 |  | 5/5 |  | 0.5977 | 0.5977 | 16 | 13 | 0.000 / 0.000 | 0.5977 / 0.5977 | 1.7234 | 17.234 |
| 08:30-09:00 | D | 5/5 |  | 0.5482 | 0.5482 | 20 | 17 | 0.000 / 0.000 | 0.5482 / 0.5482 | 1.6244 | 16.244 |
| 09:00-09:30 | D | 5/5 |  | 0.5519 | 0.5519 | 23 | 20 | 0.000 / 0.000 | 0.5519 / 0.5519 | 1.6318 | 16.318 |
| 09:30-10:00 | D | 5/5 |  | 0.5364 | 0.5364 | 26 | 20 | 0.000 / 0.000 | 0.5364 / 0.5364 | 1.6007 | 16.007 |
| 10:00-10:30 | D | 5/5 |  | 0.5400 | 0.5400 | 21 | 22 | 0.000 / 0.000 | 0.5400 / 0.5400 | 1.6081 | 16.081 |
| 10:30-11:00 | D | 5/5 |  | 0.5404 | 0.5404 | 29 | 25 | 0.000 / 0.000 | 0.5404 / 0.5404 | 1.6089 | 16.089 |
| 11:00-11:30 | D | 5/5 |  | 0.5340 | 0.5340 | 25 | 26 | 0.000 / 0.000 | 0.5340 / 0.5340 | 1.5961 | 15.961 |
| 11:30-12:00 | D | 5/5 |  | 0.5284 | 0.5284 | 28 | 25 | 0.000 / 0.000 | 0.5284 / 0.5284 | 1.5847 | 15.847 |
| 12:00-12:30 | D | 5/5 |  | 0.5431 | 0.5431 | 29 | 30 | 0.000 / 0.000 | 0.5431 / 0.5431 | 1.6143 | 16.143 |
| 12:30-13:00 | D | 5/5 |  | 0.5340 | 0.5340 | 28 | 34 | 0.000 / 0.000 | 0.5340 / 0.5340 | 1.5959 | 15.959 |
| 13:00-13:20 | D | 5/5 |  | 0.5453 | 0.5453 | 42 | 45 | 0.000 / 0.000 | 0.5453 / 0.5453 | 1.6187 | 16.187 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZM_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` aa03722f34b94e1b468aed26c460bb59d171e2e26bedcc0ebb2877c6bebcbea5 (179,077 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZM_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` d58ca6dbdab1474c45b207f67b49c8aac7cc37e372f85d32c47e169b830786eb (255,197 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZM_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 474c05b2e4af708fe0b371d2e367d47a0f88240f098bc54ea81f697b49c49543 (176,497 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZM_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 8a4a50a1c3e62e99ee737acfded8473ee72037face648193ae07cb38a2ac3069 (163,386 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZM_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 0a8341e0bd04f234740f653366ad835b6923e649ae2099fef23eb6576268e525 (194,095 records)

### ZN (rates)

Tick 0.015625 (vendor units 0.015625, factor 1), tick value $15.625; commission $2.62 round turn = 0.1677 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.5011, sell 0.5011 ticks (round turn inside a window 1.1698 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5001 | 0.5001 | 515 | 681 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.1679 | 18.248 |
| 17:30-18:00 |  | 5/5 |  | 0.5000 | 0.5000 | 900 | 889 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 18:00-18:30 |  | 5/5 |  | 0.5000 | 0.5000 | 978 | 956 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 18:30-19:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1182 | 1139 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 19:00-19:30 |  | 5/5 |  | 0.5001 | 0.5001 | 1266 | 1103 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.1678 | 18.247 |
| 19:30-20:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1364 | 1002 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 20:00-20:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1160 | 1250 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.246 |
| 20:30-21:00 |  | 5/5 |  | 0.5009 | 0.5009 | 1195 | 1199 | 0.000 / 0.000 | 0.5009 / 0.5009 | 1.1695 | 18.273 |
| 21:00-21:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1319 | 1561 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 21:30-22:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1411 | 1444 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 22:00-22:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1405 | 1643 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 22:30-23:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1436 | 1437 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 23:00-23:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1740 | 1401 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 23:30-00:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1687 | 1751 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 00:00-00:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1615 | 1612 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 00:30-01:00 |  | 5/5 |  | 0.5011 | 0.5011 | 1242 | 1594 | 0.000 / 0.000 | 0.5011 / 0.5011 | 1.1698 | 18.278 |
| 01:00-01:30 |  | 5/5 |  | 0.5004 | 0.5004 | 1429 | 1767 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.1684 | 18.256 |
| 01:30-02:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1712 | 1793 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 02:00-02:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1989 | 1876 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 02:30-03:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1729 | 1859 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 03:00-03:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1732 | 1997 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 03:30-04:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1927 | 2156 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 04:00-04:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1959 | 2080 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 04:30-05:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1850 | 1969 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 05:00-05:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1684 | 1897 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 05:30-06:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1738 | 1749 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 06:00-06:30 |  | 5/5 |  | 0.5000 | 0.5000 | 1835 | 1742 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 06:30-07:00 |  | 5/5 |  | 0.5000 | 0.5000 | 1909 | 1964 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 07:00-07:30 | D | 5/5 |  | 0.5002 | 0.5002 | 2125 | 1975 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.1681 | 18.252 |
| 07:30-08:00 | D | 5/5 |  | 0.5003 | 0.5003 | 2271 | 2065 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.1682 | 18.253 |
| 08:00-08:30 | D | 5/5 |  | 0.5000 | 0.5000 | 2585 | 2436 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 08:30-09:00 | D | 5/5 |  | 0.5000 | 0.5000 | 2474 | 2818 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 09:00-09:30 | D | 5/5 |  | 0.5000 | 0.5000 | 3023 | 2864 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 09:30-10:00 | D | 5/5 |  | 0.5000 | 0.5000 | 3079 | 3133 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 10:00-10:30 | D | 5/5 |  | 0.5000 | 0.5000 | 3168 | 3168 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 10:30-11:00 | D | 5/5 |  | 0.5000 | 0.5000 | 3679 | 3792 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 11:00-11:30 | D | 5/5 |  | 0.5000 | 0.5000 | 3621 | 3482 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 11:30-12:00 | D | 5/5 |  | 0.5000 | 0.5000 | 3532 | 3459 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 12:00-12:30 | D | 5/5 |  | 0.5004 | 0.5004 | 3309 | 3051 | 0.000 / 0.000 | 0.5004 / 0.5004 | 1.1685 | 18.258 |
| 12:30-13:00 | D | 5/5 |  | 0.5000 | 0.5000 | 3238 | 4267 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 13:00-13:30 | D | 5/5 |  | 0.5000 | 0.5000 | 4177 | 3829 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 13:30-14:00 | D | 5/5 |  | 0.5000 | 0.5000 | 5452 | 5307 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 14:00-14:30 |  | 5/5 |  | 0.5000 | 0.5000 | 5391 | 6118 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 14:30-15:00 |  | 5/5 |  | 0.5000 | 0.5000 | 4932 | 5213 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 15:00-15:30 |  | 5/5 |  | 0.5000 | 0.5000 | 4089 | 3724 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |
| 15:30-16:00 |  | 5/5 |  | 0.5000 | 0.5000 | 3395 | 4101 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.1677 | 18.245 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZN_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` e604149aca4599d9092e316df3a68d51b8d5659a6d4052e96533e82d813de6e8 (1,974,107 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZN_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` d8f559b07aba9e9e70664953630342c2311e4335388747410d2037f3c238520b (1,339,822 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZN_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 90c27d9ad24fae8873c759b5134119baff1ebe71342ca735b06e23a052db7c17 (2,019,451 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZN_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 1139264354017f11a3fc3430ba9dd5712fd786c92ab95f498f43d6622a14a8ba (2,660,920 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZN_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` b02d6bf27a91e417493e5f1cabba680519e173a86fcc4127a52425482936b711 (1,801,324 records)

### ZS (grains)

Tick 0.0025 (vendor units 0.2500, factor 100), tick value $12.5; commission $5.28 round turn = 0.4224 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:15 CT.

Event-window one-side slippage: buy 0.6108, sell 0.6108 ticks (round turn inside a window 1.6440 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:00-19:30 |  | 5/5 |  | 0.5865 | 0.5865 | 13 | 15 | 0.000 / 0.000 | 0.5865 / 0.5865 | 1.5953 | 19.942 |
| 19:30-20:00 |  | 5/5 |  | 0.5793 | 0.5793 | 20 | 21 | 0.000 / 0.000 | 0.5793 / 0.5793 | 1.5810 | 19.762 |
| 20:00-20:30 |  | 5/5 |  | 0.5805 | 0.5805 | 17 | 14 | 0.000 / 0.000 | 0.5805 / 0.5805 | 1.5833 | 19.792 |
| 20:30-21:00 |  | 5/5 |  | 0.5575 | 0.5575 | 20 | 19 | 0.000 / 0.000 | 0.5575 / 0.5575 | 1.5374 | 19.218 |
| 21:00-21:30 |  | 5/5 |  | 0.5394 | 0.5394 | 22 | 19 | 0.000 / 0.000 | 0.5394 / 0.5394 | 1.5012 | 18.765 |
| 21:30-22:00 |  | 5/5 |  | 0.5727 | 0.5727 | 23 | 18 | 0.000 / 0.000 | 0.5727 / 0.5727 | 1.5678 | 19.597 |
| 22:00-22:30 |  | 5/5 |  | 0.5410 | 0.5410 | 20 | 18 | 0.000 / 0.000 | 0.5410 / 0.5410 | 1.5044 | 18.805 |
| 22:30-23:00 |  | 5/5 |  | 0.5466 | 0.5466 | 20 | 25 | 0.000 / 0.000 | 0.5466 / 0.5466 | 1.5156 | 18.945 |
| 23:00-23:30 |  | 5/5 |  | 0.5568 | 0.5568 | 23 | 18 | 0.000 / 0.000 | 0.5568 / 0.5568 | 1.5360 | 19.199 |
| 23:30-00:00 |  | 5/5 |  | 0.5524 | 0.5524 | 27 | 22 | 0.000 / 0.000 | 0.5524 / 0.5524 | 1.5272 | 19.089 |
| 00:00-00:30 |  | 5/5 |  | 0.5411 | 0.5411 | 25 | 21 | 0.000 / 0.000 | 0.5411 / 0.5411 | 1.5045 | 18.807 |
| 00:30-01:00 |  | 5/5 |  | 0.5572 | 0.5572 | 33 | 17 | 0.000 / 0.000 | 0.5572 / 0.5572 | 1.5369 | 19.211 |
| 01:00-01:30 |  | 5/5 |  | 0.5618 | 0.5618 | 17 | 20 | 0.000 / 0.000 | 0.5618 / 0.5618 | 1.5460 | 19.325 |
| 01:30-02:00 |  | 5/5 |  | 0.5821 | 0.5821 | 21 | 21 | 0.000 / 0.000 | 0.5821 / 0.5821 | 1.5866 | 19.833 |
| 02:00-02:30 |  | 5/5 |  | 0.5616 | 0.5616 | 20 | 21 | 0.000 / 0.000 | 0.5616 / 0.5616 | 1.5456 | 19.320 |
| 02:30-03:00 |  | 5/5 |  | 0.6108 | 0.6108 | 21 | 24 | 0.000 / 0.000 | 0.6108 / 0.6108 | 1.6440 | 20.549 |
| 03:00-03:30 |  | 5/5 |  | 0.5711 | 0.5711 | 22 | 22 | 0.000 / 0.000 | 0.5711 / 0.5711 | 1.5646 | 19.557 |
| 03:30-04:00 |  | 5/5 |  | 0.5675 | 0.5675 | 20 | 22 | 0.000 / 0.000 | 0.5675 / 0.5675 | 1.5574 | 19.468 |
| 04:00-04:30 |  | 5/5 |  | 0.5749 | 0.5749 | 22 | 17 | 0.000 / 0.000 | 0.5749 / 0.5749 | 1.5721 | 19.651 |
| 04:30-05:00 |  | 5/5 |  | 0.5666 | 0.5666 | 22 | 23 | 0.000 / 0.000 | 0.5666 / 0.5666 | 1.5556 | 19.444 |
| 05:00-05:30 |  | 5/5 |  | 0.5765 | 0.5765 | 20 | 23 | 0.000 / 0.000 | 0.5765 / 0.5765 | 1.5754 | 19.693 |
| 05:30-06:00 |  | 5/5 |  | 0.5553 | 0.5553 | 22 | 19 | 0.000 / 0.000 | 0.5553 / 0.5553 | 1.5329 | 19.162 |
| 06:00-06:30 |  | 5/5 |  | 0.5675 | 0.5675 | 23 | 22 | 0.000 / 0.000 | 0.5675 / 0.5675 | 1.5574 | 19.468 |
| 06:30-07:00 |  | 5/5 |  | 0.5584 | 0.5584 | 21 | 19 | 0.000 / 0.000 | 0.5584 / 0.5584 | 1.5391 | 19.239 |
| 07:00-07:30 |  | 5/5 |  | 0.5778 | 0.5778 | 23 | 20 | 0.000 / 0.000 | 0.5778 / 0.5778 | 1.5780 | 19.725 |
| 07:30-07:45 |  | 5/5 |  | 0.5687 | 0.5687 | 24 | 18 | 0.000 / 0.000 | 0.5687 / 0.5687 | 1.5597 | 19.497 |
| 08:30-09:00 | D | 5/5 |  | 0.5278 | 0.5278 | 35 | 28 | 0.000 / 0.000 | 0.5278 / 0.5278 | 1.4779 | 18.474 |
| 09:00-09:30 | D | 5/5 |  | 0.5272 | 0.5272 | 40 | 28 | 0.000 / 0.000 | 0.5272 / 0.5272 | 1.4769 | 18.461 |
| 09:30-10:00 | D | 5/5 |  | 0.5210 | 0.5210 | 37 | 34 | 0.000 / 0.000 | 0.5210 / 0.5210 | 1.4645 | 18.306 |
| 10:00-10:30 | D | 5/5 |  | 0.5221 | 0.5221 | 37 | 38 | 0.000 / 0.000 | 0.5221 / 0.5221 | 1.4666 | 18.333 |
| 10:30-11:00 | D | 5/5 |  | 0.5188 | 0.5188 | 40 | 41 | 0.000 / 0.000 | 0.5188 / 0.5188 | 1.4600 | 18.250 |
| 11:00-11:30 | D | 5/5 |  | 0.5272 | 0.5272 | 42 | 40 | 0.000 / 0.000 | 0.5272 / 0.5272 | 1.4768 | 18.460 |
| 11:30-12:00 | D | 5/5 |  | 0.5208 | 0.5208 | 45 | 55 | 0.000 / 0.000 | 0.5208 / 0.5208 | 1.4641 | 18.301 |
| 12:00-12:30 | D | 5/5 |  | 0.5192 | 0.5192 | 51 | 56 | 0.000 / 0.000 | 0.5192 / 0.5192 | 1.4607 | 18.259 |
| 12:30-13:00 | D | 5/5 |  | 0.5200 | 0.5200 | 50 | 51 | 0.000 / 0.000 | 0.5200 / 0.5200 | 1.4624 | 18.279 |
| 13:00-13:20 | D | 5/5 |  | 0.5271 | 0.5271 | 67 | 57 | 0.000 / 0.000 | 0.5271 / 0.5271 | 1.4767 | 18.458 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZS_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` 5a76b3e45465e5bb7a1c12c554d2825a6c795e8bc7c3c043b15650bc8a139da2 (337,700 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZS_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 92df3e3ac00bdcf069f973fd95860e70d79dff1ef14d095027ecb1ecf96c513f (396,931 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZS_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` db4c70d5abfb057875df923e7e94f5fd67e702420cd38f83f1108c983138d3c3 (271,258 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZS_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` c5132193b3e9f2af90560209d363b79e74a8b0bd8f6b4c976ac2b06a33f30536 (300,987 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZS_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` f9cecde1fa0c1fcc3bc63b5eff429a772df399dd04f41e3456f8e5f3e9888068 (244,426 records)

### ZT (rates)

Tick 0.00390625 (vendor units 0.00390625, factor 1), tick value $7.8125; commission $2.32 round turn = 0.2970 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 07:20-14:00 CT.

Event-window one-side slippage: buy 0.5129, sell 0.5129 ticks (round turn inside a window 1.3227 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:00-17:30 |  | 5/5 |  | 0.5050 | 0.5050 | 247 | 188 | 0.000 / 0.000 | 0.5050 / 0.5050 | 1.3069 | 10.210 |
| 17:30-18:00 |  | 5/5 |  | 0.5114 | 0.5114 | 464 | 279 | 0.000 / 0.000 | 0.5114 / 0.5114 | 1.3197 | 10.310 |
| 18:00-18:30 |  | 5/5 |  | 0.5100 | 0.5100 | 525 | 412 | 0.000 / 0.000 | 0.5100 / 0.5100 | 1.3169 | 10.289 |
| 18:30-19:00 |  | 5/5 |  | 0.5070 | 0.5070 | 521 | 647 | 0.000 / 0.000 | 0.5070 / 0.5070 | 1.3109 | 10.242 |
| 19:00-19:30 |  | 5/5 |  | 0.5129 | 0.5129 | 1586 | 630 | 0.000 / 0.000 | 0.5129 / 0.5129 | 1.3227 | 10.334 |
| 19:30-20:00 |  | 5/5 |  | 0.5054 | 0.5054 | 641 | 2027 | 0.000 / 0.000 | 0.5054 / 0.5054 | 1.3078 | 10.217 |
| 20:00-20:30 |  | 5/5 |  | 0.5041 | 0.5041 | 2101 | 1593 | 0.000 / 0.000 | 0.5041 / 0.5041 | 1.3051 | 10.196 |
| 20:30-21:00 |  | 5/5 |  | 0.5017 | 0.5017 | 1984 | 824 | 0.000 / 0.000 | 0.5017 / 0.5017 | 1.3005 | 10.160 |
| 21:00-21:30 |  | 5/5 |  | 0.5081 | 0.5081 | 796 | 2467 | 0.000 / 0.000 | 0.5081 / 0.5081 | 1.3131 | 10.258 |
| 21:30-22:00 |  | 5/5 |  | 0.5072 | 0.5072 | 1327 | 1692 | 0.000 / 0.000 | 0.5072 / 0.5072 | 1.3114 | 10.245 |
| 22:00-22:30 |  | 5/5 |  | 0.5043 | 0.5043 | 1925 | 863 | 0.000 / 0.000 | 0.5043 / 0.5043 | 1.3056 | 10.200 |
| 22:30-23:00 |  | 5/5 |  | 0.5040 | 0.5040 | 1773 | 1368 | 0.000 / 0.000 | 0.5040 / 0.5040 | 1.3049 | 10.195 |
| 23:00-23:30 |  | 5/5 |  | 0.5020 | 0.5020 | 2540 | 700 | 0.000 / 0.000 | 0.5020 / 0.5020 | 1.3010 | 10.164 |
| 23:30-00:00 |  | 5/5 |  | 0.5029 | 0.5029 | 2444 | 1296 | 0.000 / 0.000 | 0.5029 / 0.5029 | 1.3027 | 10.177 |
| 00:00-00:30 |  | 5/5 |  | 0.5048 | 0.5048 | 1003 | 2297 | 0.000 / 0.000 | 0.5048 / 0.5048 | 1.3065 | 10.207 |
| 00:30-01:00 |  | 5/5 |  | 0.5015 | 0.5015 | 968 | 3001 | 0.000 / 0.000 | 0.5015 / 0.5015 | 1.2999 | 10.156 |
| 01:00-01:30 |  | 5/5 |  | 0.5035 | 0.5035 | 2372 | 1954 | 0.000 / 0.000 | 0.5035 / 0.5035 | 1.3039 | 10.187 |
| 01:30-02:00 |  | 5/5 |  | 0.5028 | 0.5028 | 1467 | 2239 | 0.000 / 0.000 | 0.5028 / 0.5028 | 1.3025 | 10.176 |
| 02:00-02:30 |  | 5/5 |  | 0.5023 | 0.5023 | 2350 | 2313 | 0.000 / 0.000 | 0.5023 / 0.5023 | 1.3015 | 10.168 |
| 02:30-03:00 |  | 5/5 |  | 0.5018 | 0.5018 | 2118 | 2121 | 0.000 / 0.000 | 0.5018 / 0.5018 | 1.3005 | 10.161 |
| 03:00-03:30 |  | 5/5 |  | 0.5012 | 0.5012 | 2124 | 2337 | 0.000 / 0.000 | 0.5012 / 0.5012 | 1.2993 | 10.151 |
| 03:30-04:00 |  | 5/5 |  | 0.5019 | 0.5019 | 2146 | 2514 | 0.000 / 0.000 | 0.5019 / 0.5019 | 1.3007 | 10.162 |
| 04:00-04:30 |  | 5/5 |  | 0.5045 | 0.5045 | 2115 | 1857 | 0.000 / 0.000 | 0.5045 / 0.5045 | 1.3060 | 10.203 |
| 04:30-05:00 |  | 5/5 |  | 0.5029 | 0.5029 | 2194 | 2182 | 0.000 / 0.000 | 0.5029 / 0.5029 | 1.3028 | 10.178 |
| 05:00-05:30 |  | 5/5 |  | 0.5019 | 0.5019 | 2321 | 2029 | 0.000 / 0.000 | 0.5019 / 0.5019 | 1.3008 | 10.163 |
| 05:30-06:00 |  | 5/5 |  | 0.5012 | 0.5012 | 2124 | 1812 | 0.000 / 0.000 | 0.5012 / 0.5012 | 1.2993 | 10.151 |
| 06:00-06:30 |  | 5/5 |  | 0.5005 | 0.5005 | 2699 | 1525 | 0.000 / 0.000 | 0.5005 / 0.5005 | 1.2980 | 10.141 |
| 06:30-07:00 |  | 5/5 |  | 0.5024 | 0.5024 | 2857 | 1680 | 0.000 / 0.000 | 0.5024 / 0.5024 | 1.3018 | 10.170 |
| 07:00-07:30 | D | 5/5 |  | 0.5017 | 0.5017 | 1855 | 2415 | 0.000 / 0.000 | 0.5017 / 0.5017 | 1.3004 | 10.159 |
| 07:30-08:00 | D | 5/5 |  | 0.5056 | 0.5056 | 1679 | 2176 | 0.000 / 0.000 | 0.5056 / 0.5056 | 1.3082 | 10.220 |
| 08:00-08:30 | D | 5/5 |  | 0.5020 | 0.5020 | 2599 | 2319 | 0.000 / 0.000 | 0.5020 / 0.5020 | 1.3009 | 10.164 |
| 08:30-09:00 | D | 5/5 |  | 0.5029 | 0.5029 | 2301 | 2543 | 0.000 / 0.000 | 0.5029 / 0.5029 | 1.3027 | 10.177 |
| 09:00-09:30 | D | 5/5 |  | 0.5025 | 0.5025 | 2722 | 2595 | 0.000 / 0.000 | 0.5025 / 0.5025 | 1.3019 | 10.171 |
| 09:30-10:00 | D | 5/5 |  | 0.5007 | 0.5007 | 3314 | 2554 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.2984 | 10.144 |
| 10:00-10:30 | D | 5/5 |  | 0.5024 | 0.5024 | 2941 | 2901 | 0.000 / 0.000 | 0.5024 / 0.5024 | 1.3019 | 10.171 |
| 10:30-11:00 | D | 5/5 |  | 0.5026 | 0.5026 | 2891 | 2512 | 0.000 / 0.000 | 0.5026 / 0.5026 | 1.3021 | 10.173 |
| 11:00-11:30 | D | 5/5 |  | 0.5002 | 0.5002 | 3043 | 3205 | 0.000 / 0.000 | 0.5002 / 0.5002 | 1.2974 | 10.136 |
| 11:30-12:00 | D | 5/5 |  | 0.5020 | 0.5020 | 3383 | 2837 | 0.000 / 0.000 | 0.5020 / 0.5020 | 1.3010 | 10.164 |
| 12:00-12:30 | D | 5/5 |  | 0.5054 | 0.5054 | 3279 | 2750 | 0.000 / 0.000 | 0.5054 / 0.5054 | 1.3078 | 10.217 |
| 12:30-13:00 | D | 5/5 |  | 0.5006 | 0.5006 | 3428 | 2606 | 0.000 / 0.000 | 0.5006 / 0.5006 | 1.2981 | 10.142 |
| 13:00-13:30 | D | 5/5 |  | 0.5009 | 0.5009 | 3205 | 3299 | 0.000 / 0.000 | 0.5009 / 0.5009 | 1.2987 | 10.146 |
| 13:30-14:00 | D | 5/5 |  | 0.5001 | 0.5001 | 3560 | 3698 | 0.000 / 0.000 | 0.5001 / 0.5001 | 1.2972 | 10.134 |
| 14:00-14:30 |  | 5/5 |  | 0.5007 | 0.5007 | 3361 | 3926 | 0.000 / 0.000 | 0.5007 / 0.5007 | 1.2983 | 10.143 |
| 14:30-15:00 |  | 5/5 |  | 0.5013 | 0.5013 | 3452 | 3349 | 0.000 / 0.000 | 0.5013 / 0.5013 | 1.2996 | 10.153 |
| 15:00-15:30 |  | 5/5 |  | 0.5000 | 0.5000 | 3456 | 2951 | 0.000 / 0.000 | 0.5000 / 0.5000 | 1.2970 | 10.133 |
| 15:30-16:00 |  | 5/5 |  | 0.5003 | 0.5003 | 2447 | 2859 | 0.000 / 0.000 | 0.5003 / 0.5003 | 1.2977 | 10.138 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZT_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` e1abbb38dea18e168e8f93c6d7d6b89bb9129280d2b05af89658d3c5f3b9baad (1,233,628 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZT_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` b35263bec0063a17eca561091d5279f28a548e9ed397fa2a986933bf2bd5ddc6 (907,959 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZT_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 249a8154bae5fe435756692b4e46877ff8db98f911b26c2f2aac350b5e05903c (1,575,255 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZT_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` de6ce8a6a53c374a29ba62887585256f9a189c68d5090cffeab3fca38c588ed1 (2,336,035 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZT_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 4fa55dc5a3de97f2e920051d7b769a862652626f9c9294e32d14fd1cd5849de8 (1,475,234 records)

### ZW (grains)

Tick 0.0025 (vendor units 0.2500, factor 100), tick value $12.5; commission $5.28 round turn = 0.4224 ticks (reports/stage_e0_topstep_facts.json F3.7); q_c 1; D6 day session 08:30-13:15 CT.

Event-window one-side slippage: buy 0.6357, sell 0.6357 ticks (round turn inside a window 1.6939 ticks).

| Bucket CT | Day | Dates quoted | Fallback | s_b ticks | s_b equal-date | Med. bid | Med. ask | Depth buy / sell | Side buy / sell ticks | RT ticks | RT $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:00-19:30 |  | 5/5 |  | 0.6178 | 0.6178 | 14 | 10 | 0.000 / 0.000 | 0.6178 / 0.6178 | 1.6581 | 20.726 |
| 19:30-20:00 |  | 5/5 |  | 0.5857 | 0.5857 | 17 | 9 | 0.000 / 0.000 | 0.5857 / 0.5857 | 1.5939 | 19.924 |
| 20:00-20:30 |  | 5/5 |  | 0.5904 | 0.5904 | 14 | 11 | 0.000 / 0.000 | 0.5904 / 0.5904 | 1.6031 | 20.039 |
| 20:30-21:00 |  | 5/5 |  | 0.5658 | 0.5658 | 13 | 13 | 0.000 / 0.000 | 0.5658 / 0.5658 | 1.5540 | 19.425 |
| 21:00-21:30 |  | 5/5 |  | 0.5540 | 0.5540 | 13 | 11 | 0.000 / 0.000 | 0.5540 / 0.5540 | 1.5304 | 19.130 |
| 21:30-22:00 |  | 5/5 |  | 0.6357 | 0.6357 | 22 | 12 | 0.000 / 0.000 | 0.6357 / 0.6357 | 1.6939 | 21.173 |
| 22:00-22:30 |  | 5/5 |  | 0.5823 | 0.5823 | 20 | 8 | 0.000 / 0.000 | 0.5823 / 0.5823 | 1.5871 | 19.838 |
| 22:30-23:00 |  | 5/5 |  | 0.5553 | 0.5553 | 20 | 10 | 0.000 / 0.000 | 0.5553 / 0.5553 | 1.5331 | 19.163 |
| 23:00-23:30 |  | 5/5 |  | 0.6082 | 0.6082 | 20 | 18 | 0.000 / 0.000 | 0.6082 / 0.6082 | 1.6389 | 20.486 |
| 23:30-00:00 |  | 5/5 |  | 0.5762 | 0.5762 | 17 | 12 | 0.000 / 0.000 | 0.5762 / 0.5762 | 1.5748 | 19.685 |
| 00:00-00:30 |  | 5/5 |  | 0.5715 | 0.5715 | 12 | 23 | 0.000 / 0.000 | 0.5715 / 0.5715 | 1.5653 | 19.567 |
| 00:30-01:00 |  | 5/5 |  | 0.5949 | 0.5949 | 15 | 23 | 0.000 / 0.000 | 0.5949 / 0.5949 | 1.6121 | 20.152 |
| 01:00-01:30 |  | 5/5 |  | 0.5917 | 0.5917 | 19 | 12 | 0.000 / 0.000 | 0.5917 / 0.5917 | 1.6058 | 20.073 |
| 01:30-02:00 |  | 5/5 |  | 0.5684 | 0.5684 | 23 | 13 | 0.000 / 0.000 | 0.5684 / 0.5684 | 1.5592 | 19.489 |
| 02:00-02:30 |  | 5/5 |  | 0.5887 | 0.5887 | 16 | 17 | 0.000 / 0.000 | 0.5887 / 0.5887 | 1.5998 | 19.998 |
| 02:30-03:00 |  | 5/5 |  | 0.5937 | 0.5937 | 14 | 19 | 0.000 / 0.000 | 0.5937 / 0.5937 | 1.6098 | 20.123 |
| 03:00-03:30 |  | 5/5 |  | 0.5503 | 0.5503 | 17 | 13 | 0.000 / 0.000 | 0.5503 / 0.5503 | 1.5231 | 19.038 |
| 03:30-04:00 |  | 5/5 |  | 0.5954 | 0.5954 | 16 | 15 | 0.000 / 0.000 | 0.5954 / 0.5954 | 1.6132 | 20.165 |
| 04:00-04:30 |  | 5/5 |  | 0.5751 | 0.5751 | 16 | 16 | 0.000 / 0.000 | 0.5751 / 0.5751 | 1.5727 | 19.658 |
| 04:30-05:00 |  | 5/5 |  | 0.5861 | 0.5861 | 26 | 14 | 0.000 / 0.000 | 0.5861 / 0.5861 | 1.5946 | 19.933 |
| 05:00-05:30 |  | 5/5 |  | 0.6062 | 0.6062 | 26 | 23 | 0.000 / 0.000 | 0.6062 / 0.6062 | 1.6348 | 20.435 |
| 05:30-06:00 |  | 5/5 |  | 0.5915 | 0.5915 | 21 | 13 | 0.000 / 0.000 | 0.5915 / 0.5915 | 1.6055 | 20.069 |
| 06:00-06:30 |  | 5/5 |  | 0.5796 | 0.5796 | 19 | 17 | 0.000 / 0.000 | 0.5796 / 0.5796 | 1.5816 | 19.770 |
| 06:30-07:00 |  | 5/5 |  | 0.5906 | 0.5906 | 18 | 29 | 0.000 / 0.000 | 0.5906 / 0.5906 | 1.6037 | 20.046 |
| 07:00-07:30 |  | 5/5 |  | 0.5764 | 0.5764 | 21 | 25 | 0.000 / 0.000 | 0.5764 / 0.5764 | 1.5752 | 19.690 |
| 07:30-07:45 |  | 5/5 |  | 0.5682 | 0.5682 | 20 | 22 | 0.000 / 0.000 | 0.5682 / 0.5682 | 1.5587 | 19.484 |
| 08:30-09:00 | D | 5/5 |  | 0.5381 | 0.5381 | 25 | 26 | 0.000 / 0.000 | 0.5381 / 0.5381 | 1.4985 | 18.731 |
| 09:00-09:30 | D | 5/5 |  | 0.5311 | 0.5311 | 26 | 33 | 0.000 / 0.000 | 0.5311 / 0.5311 | 1.4847 | 18.559 |
| 09:30-10:00 | D | 5/5 |  | 0.5282 | 0.5282 | 26 | 42 | 0.000 / 0.000 | 0.5282 / 0.5282 | 1.4788 | 18.485 |
| 10:00-10:30 | D | 5/5 |  | 0.5273 | 0.5273 | 27 | 44 | 0.000 / 0.000 | 0.5273 / 0.5273 | 1.4770 | 18.462 |
| 10:30-11:00 | D | 5/5 |  | 0.5234 | 0.5234 | 33 | 48 | 0.000 / 0.000 | 0.5234 / 0.5234 | 1.4692 | 18.365 |
| 11:00-11:30 | D | 5/5 |  | 0.5271 | 0.5271 | 31 | 54 | 0.000 / 0.000 | 0.5271 / 0.5271 | 1.4767 | 18.458 |
| 11:30-12:00 | D | 5/5 |  | 0.5201 | 0.5201 | 53 | 33 | 0.000 / 0.000 | 0.5201 / 0.5201 | 1.4626 | 18.283 |
| 12:00-12:30 | D | 5/5 |  | 0.5344 | 0.5344 | 48 | 54 | 0.000 / 0.000 | 0.5344 / 0.5344 | 1.4912 | 18.640 |
| 12:30-13:00 | D | 5/5 |  | 0.5286 | 0.5286 | 42 | 76 | 0.000 / 0.000 | 0.5286 / 0.5286 | 1.4795 | 18.494 |
| 13:00-13:20 | D | 5/5 |  | 0.5261 | 0.5261 | 59 | 71 | 0.000 / 0.000 | 0.5261 / 0.5261 | 1.4747 | 18.434 |

Input files (sha256 verified against reports/stage_e1_purchase.json before decoding):

- `data/vendor/databento/GLBX.MDP3/mbp-1/ZW_v_0/range=2025-05-13T220000Z_2025-05-14T210000Z.dbn.zst` b8031eb1fec19dfbc4200c118202ec783bae45871d8c7c250bc7ef3804d61142 (191,966 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZW_v_0/range=2025-08-12T220000Z_2025-08-13T210000Z.dbn.zst` 5445305f9d127d80089964264166ceba31c5cc40a148b89af98f3d51e8712be8 (110,791 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZW_v_0/range=2025-11-11T230000Z_2025-11-12T220000Z.dbn.zst` 2987c0ee47370208b01755038c0b9f8431b8fc39080a932c97cf24daf7a33ae0 (86,166 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZW_v_0/range=2026-02-10T230000Z_2026-02-11T220000Z.dbn.zst` 056c617d0f8adfeba09c96be080b4f86ba945c444b40a54c51641c7a1dac8691 (142,214 records)
- `data/vendor/databento/GLBX.MDP3/mbp-1/ZW_v_0/range=2026-04-14T220000Z_2026-04-15T210000Z.dbn.zst` 5e905083f0710ace80fda5d6aa07a989e38a386baf00fca63bdffbea9a1d460d (182,097 records)

