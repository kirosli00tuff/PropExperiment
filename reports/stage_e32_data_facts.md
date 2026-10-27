# Stage E.32 Part F: format and size facts of the owned soybean-complex files (2020-12..2024-02)

Worker DataFacts-OpusHigh (ROOT F_data_facts), 2026-10-27 PDT. Written section by section.

Scope and data rule. Only counts, byte sizes, schema field names and types, timestamp
differences (timings) and run timings were computed. No price, order size value, return, markout or
feature value was computed, printed or looked at; no data file was opened by head, cat, less, tail
or hexdump; every file was opened only by my own scripts (below), which print counts and timings.
File names were checked before opening: every file's request range lies inside
2020-11-30T22:00Z..2024-02-29T22:00Z (the first file opens at 16:00 CT on 2020-11-30, the start of
trade date 2020-12-01's window; see section 1.5 for the records whose ts_event predates
2020-12-01, counted only). No Databento API call.

Files read (each directory holds 39 monthly `range=<start>_<end>.dbn.zst` files plus an identical
`manifest.json`, md5 prefix 093cdbcf29b4 in all four; written by E.31's verify31.py on 2026-10-23
12:35 PDT, 156 of 156 files verified, no hard check failed):

| Series | Directory (data/vendor/databento/GLBX.MDP3/...) | Schema | Request symbols (stype_in) |
|---|---|---|---|
| Z1 | mbo/Z1_ZM_v_0-ZM_v_1 | mbo | ZM.v.0, ZM.v.1 (continuous) |
| Z2 | mbp-1/Z2_ZS_v_0 | mbp-1 | ZS.v.0 (continuous) |
| Z3 | mbp-1/Z3_ZL_v_0 | mbp-1 | ZL.v.0 (continuous) |
| Z4 | definition/Z4_ZM_FUT-ZS_FUT-ZL_FUT | definition | ZM.FUT, ZS.FUT, ZL.FUT (parent) |

Scripts (mine, reports/stage_e32_briefs/work/F_data_facts/): `F_scan.py` (one streaming pass per
file: counts by trade date, action, side, instrument and flag; tie and inversion counts; a
ts_recv - ts_event histogram; decompressed byte count; writes `F_scan_out/<series>_<month>.json`),
`F_book_time.py` (section 5 timing), `F_agg.py` (the tables below from the JSON). Logs:
`F_scan_Z4_probe.log`, `F_scan_Z123.log`, `F_book_time.log`. Evidence pages and log.tsv:
reports/stage_e32_briefs/pages/F_data_facts/.

Trade date convention (E.31's, measure31.py `day_bounds`): trade date D is the ts_recv window
[D-1 16:00 CT, D 16:00 CT); "regular trade date" means `data.group_session` grains calendar
`covers(D) and is_trade_date(D)`.

## 1. Schemas, field names and types, record sizes, timestamps, anomaly counts

### 1.1 Schemas and record sizes (measured)

All 156 files carry DBN metadata version 3, dataset GLBX.MDP3, stype_out instrument_id. Record size
= manifest `delivered_record_bytes / records` (identical in every file of a series) and equals the
numpy itemsize of the decoded records (databento 0.82.0, databento-dbn 0.63.0).

| Series | Schema | Record bytes | Fields in order (numpy type) |
|---|---|---|---|
| Z1 ZM | mbo (rtype 160) | 56 | length u8, rtype u8, publisher_id u16, instrument_id u32, ts_event u64, order_id u64, price i64, size u32, flags u8, channel_id u8, action S1, side S1, ts_recv u64, ts_in_delta i32, sequence u32 |
| Z2 ZS, Z3 ZL | mbp-1 (rtype 1) | 80 | length u8, rtype u8, publisher_id u16, instrument_id u32, ts_event u64, price i64, size u32, action S1, side S1, flags u8, depth u8, ts_recv u64, ts_in_delta i32, sequence u32, bid_px_00 i64, ask_px_00 i64, bid_sz_00 u32, ask_sz_00 u32, bid_ct_00 u32, ask_ct_00 u32 |
| Z4 | definition (rtype 19) | 520 | 75 fields: length, rtype, publisher_id, instrument_id, ts_event, ts_recv, min_price_increment, display_factor, expiration, activation, high_limit_price, low_limit_price, max_price_variation, unit_of_measure_qty, min_price_increment_amount, price_ratio, strike_price, raw_instrument_id, leg_price, leg_delta, inst_attrib_value, underlying_id, market_depth_implied, market_depth, market_segment_id, max_trade_vol, min_lot_size, min_lot_size_block, min_lot_size_round_lot, min_trade_vol, contract_multiplier, decay_quantity, original_contract_size, leg_instrument_id, leg_ratio_price_numerator, leg_ratio_price_denominator, leg_ratio_qty_numerator, leg_ratio_qty_denominator, leg_underlying_id, appl_id, maturity_year, decay_start_date, channel_id, leg_count, leg_index, currency S4, settl_currency S4, secsubtype S6, raw_symbol S71, group S21, exchange S5, asset S11, cfi S7, security_type S7, unit_of_measure S31, underlying S21, strike_price_currency S4, leg_raw_symbol S71, instrument_class S1, match_algorithm S1, main_fraction, price_display_format, sub_fraction, underlying_product, security_update_action S1, maturity_month, maturity_day, maturity_week, user_defined_instrument S1, contract_multiplier_unit, flow_schedule_type, tick_rule, leg_instrument_class S1, leg_side S1, _reserved |

All field lists are as decoded by my scan (`F_scan_out/<series>_*.json`, `ndarray_fields`;
identical across months); the action and side fields are 1-byte ASCII codes. Prices are int64 in units of 1e-9 (quote E5). Z4 holds 1,810,372 definition
records over 39 months: 70,131 for outright futures (instrument_class F) and 1,740,241 for spreads
(S); 148 distinct outright instrument ids (ZM 52, ZS 44, ZL 52); match_algorithm is K for every ZM,
ZS and ZL outright; no outright's raw_symbol changed across its definition records.

### 1.2 ts_event and ts_recv (Databento definitions, verbatim; pages saved in my folder)

| # | Claim | Verbatim quote | Saved file |
|---|---|---|---|
| E1 | ts_event = matching-engine receive time (CME tag 60), not adjusted | "Most users will only need the event timestamp, i.e. ts_event . For market data, this represents the time that the event is received by the matching engine (tag 60 in FIX encoding)." ... "Since we do not adjust the publisher's timestamps, any non-monotonicity in the original data will remain." | F_db_common-fields-enums-types.html(.txt) |
| E2 | ts_recv = Databento capture time, PTP/GPS-synchronised, monotonic per symbol | "Databento receive timestamps, i.e. ts_recv , are synchronized against UTC with sub-microsecond accuracy. Moreover, these receive timestamps are always guaranteed to be monotonic for any given symbol. These receive timestamps rely on hardware timestamping on the network adapter and are synchronized against a GPS clock source using PTP." | same |
| E3 | Field types and units (MBO; MBP-1 identical wording) | "ts_recv uint64_t The capture-server-received timestamp expressed as the number of nanoseconds since the UNIX epoch." / "ts_event uint64_t The matching-engine-received timestamp expressed as the number of nanoseconds since the UNIX epoch." / "ts_in_delta int32_t The matching-engine-sending timestamp expressed as the number of nanoseconds before ts_recv ." | F_db_mbo.html(.txt), F_db_mbp-1.html(.txt) |
| E4 | ts_in_delta can be negative | "Since the publisher and Databento are not necessarily synchronized to the same clock source, ts_in_delta may be negative." | F_db_common-fields-enums-types |
| E5 | Price unit | "price int64_t The order price where every 1 unit corresponds to 1e-9, i.e. 1/1,000,000,000 or 0.000000001." | F_db_mbp-1 |
| E6 | Snapshot records carry ts_recv = generation time | "All snapshot records are marked with the F_SNAPSHOT and F_BAD_TS_RECV flags ( ts_recv is set to the snapshot generation timestamp)." | F_db_mbo-snapshot.html(.txt) |
| E7 | Daily synthetic MBO snapshot | "Databento provides a synthetic snapshot of the order book at the start of each UTC day in our historical MBO data" | F_db_mbo |
| E8 | Per-instrument message order is never changed | "Messages for a single instrument_id are never reordered, even if they have the same timestamps." | F_db_glbx-mdp3.html(.txt) |
| E9 | CME tag mapping | "ts_recv N/A The capture-server-received timestamp. ts_event 60-TransactTime The matching-engine-received timestamp. ts_in_delta 52-SendingTime The matching-engine-sending timestamp." | F_db_glbx-mdp3 |
| E10 | Flags | "F_LAST 1 << 7 128 Marks the last record in a single event for a given instrument_id ." ... "F_BAD_TS_RECV 1 << 3 8 The ts_recv value is inaccurate due to clock issues or packet reordering. F_MAYBE_BAD_BOOK 1 << 2 4 An unrecoverable gap was detected in the channel." | F_db_common-fields-enums-types |
| E11 | Action sets | MBO: "action char The event action. Can be A dd, C ancel, M odify, clea R book, T rade, F ill, or N one." MBP-1: "action char The event action. Can be A dd, C ancel, M odify, clea R book, or T rade." | F_db_mbo, F_db_mbp-1 |
| E12 | Continuous ".v." = volume rank | "Volume v Will rank the expirations by the previous day's trading volume. ZN.v.0 refers to the ZN future with the most volume." | F_db_symbology.html(.txt) |

E.31's fuller table of action, side and flag semantics (reports/stage_e31_briefs/research/data_facts.md
a1-a4, quotes from the same Databento pages fetched 2026-10-22) applies unchanged and is not repeated.

### 1.3 Resolution (counts over non-snapshot records)

Both clocks are stored at nanosecond resolution and neither is truncated: a value that is a whole
microsecond occurs about as often as chance (0.1%) or less.

| Series | Non-snapshot records | ts_event a whole us | ts_event a whole ms | ts_recv a whole us |
|---|---|---|---|---|
| Z1 ZM MBO | 698,313,409 | 154,993 (0.022%) | 119,305 (0.017%) | 692,887 (0.099%) |
| Z2 ZS MBP-1 | 248,168,434 | 25,040 (0.010%) | 5,450 (0.002%) | 245,701 (0.099%) |
| Z3 ZL MBP-1 | 158,045,618 | 19,396 (0.012%) | 5,313 (0.003%) | 156,225 (0.099%) |

(The whole-ms ts_event count is far above chance, 1e-6, so a small set of ts_event values sits on
whole milliseconds; which records those are was not examined.)

### 1.4 ts_recv - ts_event (a timing; non-snapshot records)

| Bucket | Z1 ZM MBO | Z2 ZS MBP-1 | Z3 ZL MBP-1 |
|---|---|---|---|
| < 0 (ts_recv < ts_event) | 955,941 (0.137%) | 387,220 (0.156%) | 230,475 (0.146%) |
| [0, 1 us) | 920 | 365 | 262 |
| [1, 10 us) | 8,620 | 3,483 | 2,226 |
| [10, 100 us) | 21,299,956 (3.050%) | 2,643,828 (1.065%) | 1,129,941 (0.715%) |
| [100 us, 1 ms) | 466,728,392 (66.837%) | 172,750,894 (69.610%) | 118,010,944 (74.669%) |
| [1, 10 ms) | 202,693,302 (29.026%) | 70,202,254 (28.288%) | 37,531,720 (23.747%) |
| [10, 100 ms) | 6,407,836 (0.918%) | 2,144,519 (0.864%) | 1,119,697 (0.708%) |
| [100 ms, 1 s) | 218,442 (0.031%) | 35,871 (0.014%) | 20,352 (0.013%) |
| >= 1 s | 0 | 0 | 1 (in [1 s, 60 s)) |
| ts_in_delta < 0 | 1,783,348 (0.255%) | 720,413 (0.290%) | 417,513 (0.264%) |

So ts_recv trails ts_event by 0.1 to 10 ms for about 96% of records in each file, and precedes it
for about 0.14 to 0.16% (two clocks, E1/E2/E4). A sampler or as-of join across ZM, ZS and ZL has to
pick one clock: ts_recv is the one Databento guarantees monotonic per symbol (E2) and is the clock of
the trade-date split; ts_event is the exchange's clock and is the one E.31's `time_axis` uses.

### 1.5 Anomaly and structure counts (whole 39 months)

| Count | Z1 ZM MBO | Z2 ZS MBP-1 | Z3 ZL MBP-1 |
|---|---|---|---|
| Records | 699,094,402 | 248,169,282 | 158,046,466 |
| F_SNAPSHOT records | 780,993 | 848 | 848 |
| F_BAD_TS_RECV records | 781,331 (338 more than snapshots) | 848 | 848 |
| F_MAYBE_BAD_BOOK records | 7,630 | 566 | 476 |
| F_TOB, F_MBP, bit 1, bit 0 records | 0 | 0 | 0 |
| F_LAST records (= events per instrument) | 584,881,539 (1.195 records per event) | 227,090,874 (1.093) | 142,061,153 (1.113) |
| ts_recv < ts_event (all records = non-snapshot) | 955,941 | 387,220 | 230,475 |
| ts_event inversions per instrument in file order (non-snapshot; E.31's `time_axis` count) | 0 | 0 | 0 |
| ts_recv decreases per instrument in file order | 0 | 0 | 0 |
| ts_event ties: record equal to the previous record of the same instrument (non-snapshot) | 113,605,654 (16.27%) | 19,771,490 (7.97%) | 14,688,031 (9.29%) |
| ts_event ties between consecutive F_LAST events of an instrument | 172,088 (0.029% of events) | 4,469 (0.002%) | 2,647 (0.002%) |
| ts_recv ties with the previous record of the same instrument (all records) | 48,972,643 (7.01%) | 1,941,272 (0.78%) | 1,429,801 (0.90%) |
| ts_event before the file's request start (snapshot residue: resting orders' original times) | 47,845 | 3 | 3 |
| of which ts_event before 2020-12-01T00:00Z | 1,157 | 4 | 5 |

Reading: record-level ts_event ties are expected (several records of one matching event share the
event time, E10); the meaningful count is ties between distinct F_LAST events (row above). No
inversions remain in file order, so E.31's `time_axis` monotone fix changes nothing on non-snapshot
records over these 39 months. The 1,157 (Z1), 4 (Z2), 5 (Z3) records whose ts_event precedes
2020-12-01 are snapshot records of orders resting since before the file start (ts_event is the
order's entry time, E6); they were counted, not opened, and they carry ts_recv inside the owned
window. Their count is larger than the file-start count for Z2/Z3 because the comparison bounds
differ (file start 2020-11-30T22:00Z versus 2020-12-01T00:00Z).

## 2. Instrument ids across rolls (metadata only)

Source: the symbology `mappings` in the 117 Z1/Z2/Z3 file headers (copied into the manifests),
resolved per UTC date across the monthly files (the month files overlap by one UTC date at each
boundary; no date had two different ids in two headers: 0 conflicts), joined to `raw_symbol` and
`expiration` from the Z4 definition records (every mapped id is in Z4). Mapping intervals are UTC
dates, end exclusive; a CBOT grain trade date's sessions lie inside UTC day D (E.31 measure31.py
`instrument_on` docstring), so the UTC date is the trade date. `.v.N` ranks expirations by the
previous day's volume (E12), so it can switch back and forth between two contracts around a roll.

| Symbol | Runs (intervals) | Distinct contracts | Runs that return to an earlier contract | Runs of 3 days or less | Runs of 7 days or less |
|---|---|---|---|---|---|
| ZM.v.0 | 24 | 19 | 5 | 4 | 6 |
| ZM.v.1 | 79 | 28 | 51 | 29 | 37 |
| ZS.v.0 | 20 | 18 | 2 | 1 | 2 |
| ZL.v.0 | 26 | 20 | 6 | 6 | 7 |

Short v.0 runs (3 days or less): ZM.v.0 on ZMU1 2021-06-28 (1 day, inside a ZMZ1 run), ZMZ2
2022-06-24..06-26 then ZMN2 2022-06-27..06-29 then ZMZ2, ZMH3 2022-12-12..12-13 (then ZMF3 again
until 12-17); ZS.v.0 on ZSN1 2021-06-28; ZL.v.0 alternating ZLN1/ZLK1 2021-04-04..04-10, ZLQ1
2021-06-29, ZLQ2 2022-06-30. So "front" by volume is not monotone in expiry, and ZM.v.0 sat on a
September contract (ZMU1) for a day inside a December run and on the July contract (ZMN2) for three
days after the December had taken over (and ZMH3 led ZMF3 for two days before ZMF3 returned for four). ZM.v.1 flips far more often (51 returns): it is not a stable "second contract" series.

Full table, ZM.v.0, ZS.v.0, ZL.v.0 (ZM.v.1's 79 runs are in Appendix A):

| Continuous symbol | instrument_id | raw_symbol (Z4) | Mapped from (UTC date) | to (exclusive) | Expiration (Z4, UTC date) |
|---|---|---|---|---|---|
| ZM.v.0 | 504886 | ZMF1 | 2020-11-30 | 2020-12-18 | 2021-01-14 |
| ZM.v.0 | 282089 | ZMH1 | 2020-12-18 | 2021-02-22 | 2021-03-12 |
| ZM.v.0 | 89700 | ZMK1 | 2021-02-22 | 2021-04-16 | 2021-05-14 |
| ZM.v.0 | 156434 | ZMN1 | 2021-04-16 | 2021-06-24 | 2021-07-14 |
| ZM.v.0 | 794459 | ZMZ1 | 2021-06-24 | 2021-06-28 | 2021-12-14 |
| ZM.v.0 | 535389 | ZMU1 | 2021-06-28 | 2021-06-29 | 2021-09-14 |
| ZM.v.0 | 794459 | ZMZ1 | 2021-06-29 | 2021-11-22 | 2021-12-14 |
| ZM.v.0 | 243619 | ZMF2 | 2021-11-22 | 2021-12-22 | 2022-01-14 |
| ZM.v.0 | 689369 | ZMH2 | 2021-12-22 | 2022-02-18 | 2022-03-14 |
| ZM.v.0 | 497002 | ZMK2 | 2022-02-18 | 2022-04-15 | 2022-05-13 |
| ZM.v.0 | 120191 | ZMN2 | 2022-04-15 | 2022-06-24 | 2022-07-14 |
| ZM.v.0 | 697256 | ZMZ2 | 2022-06-24 | 2022-06-27 | 2022-12-14 |
| ZM.v.0 | 120191 | ZMN2 | 2022-06-27 | 2022-06-30 | 2022-07-14 |
| ZM.v.0 | 697256 | ZMZ2 | 2022-06-30 | 2022-11-23 | 2022-12-14 |
| ZM.v.0 | 8352 | ZMF3 | 2022-11-23 | 2022-12-12 | 2023-01-13 |
| ZM.v.0 | 185432 | ZMH3 | 2022-12-12 | 2022-12-14 | 2023-03-14 |
| ZM.v.0 | 8352 | ZMF3 | 2022-12-14 | 2022-12-18 | 2023-01-13 |
| ZM.v.0 | 185432 | ZMH3 | 2022-12-18 | 2023-02-20 | 2023-03-14 |
| ZM.v.0 | 23389 | ZMK3 | 2023-02-20 | 2023-04-16 | 2023-05-12 |
| ZM.v.0 | 658865 | ZMN3 | 2023-04-16 | 2023-06-22 | 2023-07-14 |
| ZM.v.0 | 51239 | ZMZ3 | 2023-06-22 | 2023-11-15 | 2023-12-14 |
| ZM.v.0 | 152114 | ZMF4 | 2023-11-15 | 2023-12-18 | 2024-01-12 |
| ZM.v.0 | 506263 | ZMH4 | 2023-12-18 | 2024-02-16 | 2024-03-14 |
| ZM.v.0 | 759433 | ZMK4 | 2024-02-16 | 2024-03-01 | 2024-05-14 |
| ZS.v.0 | 295951 | ZSF1 | 2020-11-30 | 2020-12-23 | 2021-01-14 |
| ZS.v.0 | 103598 | ZSH1 | 2020-12-23 | 2021-02-24 | 2021-03-12 |
| ZS.v.0 | 741705 | ZSK1 | 2021-02-24 | 2021-04-19 | 2021-05-14 |
| ZS.v.0 | 242521 | ZSN1 | 2021-04-19 | 2021-06-20 | 2021-07-14 |
| ZS.v.0 | 361559 | ZSX1 | 2021-06-20 | 2021-06-28 | 2021-11-12 |
| ZS.v.0 | 242521 | ZSN1 | 2021-06-28 | 2021-06-29 | 2021-07-14 |
| ZS.v.0 | 361559 | ZSX1 | 2021-06-29 | 2021-10-29 | 2021-11-12 |
| ZS.v.0 | 707652 | ZSF2 | 2021-10-29 | 2021-12-23 | 2022-01-14 |
| ZS.v.0 | 100711 | ZSH2 | 2021-12-23 | 2022-02-24 | 2022-03-14 |
| ZS.v.0 | 738158 | ZSK2 | 2022-02-24 | 2022-04-21 | 2022-05-13 |
| ZS.v.0 | 711194 | ZSN2 | 2022-04-21 | 2022-06-26 | 2022-07-14 |
| ZS.v.0 | 518822 | ZSX2 | 2022-06-26 | 2022-10-28 | 2022-11-14 |
| ZS.v.0 | 148557 | ZSF3 | 2022-10-28 | 2022-12-25 | 2023-01-13 |
| ZS.v.0 | 731217 | ZSH3 | 2022-12-25 | 2023-02-23 | 2023-03-14 |
| ZS.v.0 | 385841 | ZSK3 | 2023-02-23 | 2023-04-19 | 2023-05-12 |
| ZS.v.0 | 70327 | ZSN3 | 2023-04-19 | 2023-06-19 | 2023-07-14 |
| ZS.v.0 | 484790 | ZSX3 | 2023-06-19 | 2023-10-29 | 2023-11-14 |
| ZS.v.0 | 291819 | ZSF4 | 2023-10-29 | 2023-12-22 | 2024-01-12 |
| ZS.v.0 | 789231 | ZSH4 | 2023-12-22 | 2024-02-25 | 2024-03-14 |
| ZS.v.0 | 535842 | ZSK4 | 2024-02-25 | 2024-03-01 | 2024-05-14 |
| ZL.v.0 | 544759 | ZLF1 | 2020-11-30 | 2020-12-22 | 2021-01-14 |
| ZL.v.0 | 129522 | ZLH1 | 2020-12-22 | 2021-02-21 | 2021-03-12 |
| ZL.v.0 | 352379 | ZLK1 | 2021-02-21 | 2021-04-04 | 2021-05-14 |
| ZL.v.0 | 571589 | ZLN1 | 2021-04-04 | 2021-04-07 | 2021-07-14 |
| ZL.v.0 | 352379 | ZLK1 | 2021-04-07 | 2021-04-08 | 2021-05-14 |
| ZL.v.0 | 571589 | ZLN1 | 2021-04-08 | 2021-04-09 | 2021-07-14 |
| ZL.v.0 | 352379 | ZLK1 | 2021-04-09 | 2021-04-11 | 2021-05-14 |
| ZL.v.0 | 571589 | ZLN1 | 2021-04-11 | 2021-06-20 | 2021-07-14 |
| ZL.v.0 | 379214 | ZLZ1 | 2021-06-20 | 2021-06-29 | 2021-12-14 |
| ZL.v.0 | 737124 | ZLQ1 | 2021-06-29 | 2021-06-30 | 2021-08-13 |
| ZL.v.0 | 379214 | ZLZ1 | 2021-06-30 | 2021-11-21 | 2021-12-14 |
| ZL.v.0 | 96420 | ZLF2 | 2021-11-21 | 2021-12-16 | 2022-01-14 |
| ZL.v.0 | 704007 | ZLH2 | 2021-12-16 | 2022-02-18 | 2022-03-14 |
| ZL.v.0 | 542130 | ZLK2 | 2022-02-18 | 2022-04-15 | 2022-05-13 |
| ZL.v.0 | 565889 | ZLN2 | 2022-04-15 | 2022-06-24 | 2022-07-14 |
| ZL.v.0 | 150640 | ZLZ2 | 2022-06-24 | 2022-06-30 | 2022-12-14 |
| ZL.v.0 | 288745 | ZLQ2 | 2022-06-30 | 2022-07-01 | 2022-08-12 |
| ZL.v.0 | 150640 | ZLZ2 | 2022-07-01 | 2022-11-20 | 2022-12-14 |
| ZL.v.0 | 276652 | ZLF3 | 2022-11-20 | 2022-12-19 | 2023-01-13 |
| ZL.v.0 | 652024 | ZLH3 | 2022-12-19 | 2023-02-16 | 2023-03-14 |
| ZL.v.0 | 548775 | ZLK3 | 2023-02-16 | 2023-04-14 | 2023-05-12 |
| ZL.v.0 | 673494 | ZLN3 | 2023-04-14 | 2023-06-22 | 2023-07-14 |
| ZL.v.0 | 319302 | ZLZ3 | 2023-06-22 | 2023-11-19 | 2023-12-14 |
| ZL.v.0 | 391369 | ZLF4 | 2023-11-19 | 2023-12-17 | 2024-01-12 |
| ZL.v.0 | 330370 | ZLH4 | 2023-12-17 | 2024-02-22 | 2024-03-14 |
| ZL.v.0 | 567056 | ZLK4 | 2024-02-22 | 2024-03-01 | 2024-05-14 |

## 3. Message counts per day and by action

### 3.1 Per trade date (816 regular grains trade dates, 2020-12-01..2024-02-29, every one present in all three files)

Rule (fixed before reading the result): ascending sort by (count, date); min = first, median =
lower median at index (N-1)//2 = 407, p90 = nearest rank at index ceil(0.9 N) - 1 = 734, max =
last; ties go to the earlier date. "Records" = all records of the file whose ts_recv falls in the
trade date's window (both ZM instruments for Z1; snapshots included). "Events" = F_LAST records.

| Series, count | Min (date) | Median (date) | p90 (date) | Max (date) |
|---|---|---|---|---|
| Z1 ZM MBO, records (ZM.v.0 + ZM.v.1) | 275,079 (2022-11-25) | 827,199 (2022-02-15) | 1,139,174 (2022-07-27) | 1,748,582 (2021-05-07) |
| Z1 ZM MBO, records of the ZM.v.0 instrument only | 167,268 (2022-11-22) | 491,492 (2021-02-09) | 687,518 (2023-06-16) | 1,334,496 (2021-04-27) |
| Z1 ZM MBO, events (F_LAST) | 215,781 (2022-11-25) | 692,349 (2023-08-11) | 957,577 (2021-05-19) | 1,662,843 (2021-05-07) |
| Z1 ZM MBO, T records | 3,330 (2021-06-28) | 19,413 (2022-11-02) | 26,439 (2023-10-26) | 43,754 (2022-02-24) |
| Z1 ZM MBO, F records | 3,624 (2021-06-28) | 29,098 (2021-03-15) | 41,003 (2023-02-28) | 62,315 (2024-01-12) |
| Z1 ZM MBO, A records | 62,767 (2021-06-28) | 192,753 (2023-05-30) | 267,029 (2023-12-08) | 464,763 (2022-02-24) |
| Z1 ZM MBO, C records | 62,594 (2021-06-28) | 191,760 (2022-02-16) | 266,314 (2023-12-08) | 464,166 (2022-02-24) |
| Z1 ZM MBO, M records | 61,378 (2022-11-25) | 303,927 (2023-09-13) | 509,043 (2021-01-27) | 1,037,399 (2021-05-07) |
| Z1 ZM MBO, N records | 323 (2021-08-18) | 78,933 (2023-06-02) | 121,639 (2022-05-12) | 250,829 (2022-02-24) |
| Z2 ZS MBP-1, records | 42,311 (2021-10-28) | 298,946 (2020-12-15) | 397,355 (2023-02-08) | 611,140 (2021-04-27) |
| Z2 ZS MBP-1, events (F_LAST) | 38,269 (2021-10-28) | 272,785 (2022-08-31) | 362,748 (2022-08-01) | 556,368 (2021-04-27) |
| Z2 ZS MBP-1, T records | 4,053 (2021-10-28) | 25,059 (2022-09-16) | 35,122 (2023-09-29) | 70,104 (2022-02-24) |
| Z3 ZL MBP-1, records | 63,170 (2023-06-21) | 188,737 (2022-07-21) | 249,130 (2023-03-10) | 486,639 (2021-01-04) |
| Z3 ZL MBP-1, events (F_LAST) | 54,999 (2023-06-21) | 168,917 (2021-10-06) | 225,487 (2020-12-02) | 448,862 (2021-01-04) |
| Z3 ZL MBP-1, T records | 6,998 (2021-04-05) | 19,195 (2024-01-19) | 25,760 (2022-07-06) | 40,543 (2022-02-24) |

Records on regular trade dates: Z1 698,738,911; Z2 248,167,909; Z3 158,044,028. Records outside
them (ts_recv windows of non-trade dates): Z1 355,491 on 202 dates (169 Sundays 113,737; 22
Mondays, the Monday holidays, 234,568; 6 Fridays 4,105; 3 Thursdays 2,703; 1 Tuesday 363; 1
Saturday 15), Z2 1,373 on 203 dates, Z3 2,438 on 202 dates. No record fell outside its file's month.
Cross-check: my Z1 per-date counts equal E.31's split markers (derived/e31/Z1/<month>.split.json,
`dates`) on all 816 dates (0 differ); my per-file record totals equal the manifest's for all 156
files.

The per-date counts of every date are in `work/F_data_facts/F_agg_summary.json` (`Z1.per_day_rows`:
date, records, events) and per action in `F_scan_out/<series>_<month>.json` (`per_day`).

### 3.2 Totals by action and side (39 months)

| Action:side | Z1 ZM MBO | Z2 ZS MBP-1 | Z3 ZL MBP-1 |
|---|---|---|---|
| A (add) : A ask / B bid / N | 82,320,716 / 81,157,145 / 0 | 52,775,822 / 53,007,287 / 302,493 | 33,613,583 / 33,402,925 / 167,783 |
| C (cancel) : A / B / N | 82,154,747 / 80,545,562 / 0 | 49,024,643 / 49,400,603 / 637,956 | 30,846,133 / 30,804,415 / 348,614 |
| M (modify) : A / B / N | 143,754,269 / 125,350,598 / 0 | 10,037,059 / 11,685,986 / 125,834 | 6,613,222 / 6,016,817 / 47,687 |
| T (trade; side = aggressor) : A / B / N | 7,130,194 / 7,085,635 / 2,136,127 | 9,985,752 / 9,553,113 / 1,559,741 | 7,250,840 / 7,160,339 / 1,608,719 |
| F (fill) : A / B / N | 10,766,758 / 10,449,127 / 3,610,542 | 33,444 / 33,447 / 6,101 | 68,547 / 79,361 / 17,480 |
| R (clear) : N | 2,036 | 1 | 1 |
| N (none) : N | 62,630,946 | 0 | 0 |
| Total | 699,094,402 | 248,169,282 | 158,046,466 |

Notes, counts only: (i) the Z2/Z3 MBP-1 files contain F records (72,992 ZS, 165,388 ZL) although
Databento's MBP-1 page lists only A, C, M, R and T (E11); their meaning in MBP-1 is not documented
on the pages I saved [unverified]; (ii) MBP-1 A/C/M records with side N (two-sided BBO updates per
E.31 data_facts a4) total 1,066,283 for ZS and 564,084 for ZL; (iii) ZM T records with side N
(2,136,127, 13.1% of ZM T records) are trades without an aggressor side, which Databento's GLBX page
attributes to implied trades (E.31 data_facts a2 quote); (iv) Z1 has 2,036 R records; the
split between snapshot clears and channel resets was not counted (MBP-1 marks its 848 snapshot
records per file series with F_SNAPSHOT but has only 1 R record each, so the MBP-1 snapshot is not an
R record). E.31's verify31 checked one snapshot per weekday midnight per mapped instrument (manifest
check `z1_weekday_midnight_snapshot_per_mapped_instrument`, passed).

## 4. Sizes, and the disk and memory needed for a rebuild over 39 months

### 4.1 Compressed (file bytes, zstd) and decompressed (DBN stream bytes, counted by streaming zstd decompression) per month, GB = 1e9 bytes

| Month | ZM MBO compressed GB | ZM MBO decompressed GB | ZS MBP-1 compressed GB | ZS MBP-1 decompressed GB | ZL MBP-1 compressed GB | ZL MBP-1 decompressed GB | definitions compressed GB | definitions decompressed GB |
|---|---|---|---|---|---|---|---|---|
| 2020-12 | 0.351 | 0.915 | 0.144 | 0.507 | 0.114 | 0.398 | 0.001 | 0.031 |
| 2021-01 | 0.415 | 1.062 | 0.117 | 0.410 | 0.112 | 0.385 | 0.001 | 0.028 |
| 2021-02 | 0.363 | 0.933 | 0.114 | 0.396 | 0.085 | 0.291 | 0.001 | 0.025 |
| 2021-03 | 0.495 | 1.283 | 0.167 | 0.581 | 0.085 | 0.292 | 0.001 | 0.027 |
| 2021-04 | 0.490 | 1.282 | 0.168 | 0.586 | 0.087 | 0.298 | 0.001 | 0.025 |
| 2021-05 | 0.526 | 1.377 | 0.170 | 0.588 | 0.077 | 0.262 | 0.001 | 0.024 |
| 2021-06 | 0.386 | 1.000 | 0.176 | 0.612 | 0.100 | 0.343 | 0.001 | 0.024 |
| 2021-07 | 0.309 | 0.818 | 0.140 | 0.482 | 0.082 | 0.281 | 0.001 | 0.023 |
| 2021-08 | 0.279 | 0.736 | 0.139 | 0.487 | 0.100 | 0.343 | 0.001 | 0.022 |
| 2021-09 | 0.305 | 0.830 | 0.118 | 0.414 | 0.088 | 0.305 | 0.001 | 0.019 |
| 2021-10 | 0.293 | 0.801 | 0.109 | 0.379 | 0.094 | 0.328 | 0.001 | 0.018 |
| 2021-11 | 0.261 | 0.695 | 0.123 | 0.431 | 0.081 | 0.278 | 0.001 | 0.021 |
| 2021-12 | 0.317 | 0.835 | 0.124 | 0.432 | 0.073 | 0.249 | 0.001 | 0.031 |
| 2022-01 | 0.354 | 0.934 | 0.148 | 0.519 | 0.074 | 0.256 | 0.001 | 0.028 |
| 2022-02 | 0.388 | 1.025 | 0.143 | 0.498 | 0.102 | 0.351 | 0.001 | 0.025 |
| 2022-03 | 0.459 | 1.190 | 0.154 | 0.538 | 0.099 | 0.344 | 0.001 | 0.027 |
| 2022-04 | 0.353 | 0.910 | 0.116 | 0.404 | 0.089 | 0.307 | 0.001 | 0.024 |
| 2022-05 | 0.401 | 1.041 | 0.132 | 0.461 | 0.067 | 0.231 | 0.001 | 0.025 |
| 2022-06 | 0.460 | 1.202 | 0.131 | 0.455 | 0.081 | 0.277 | 0.001 | 0.023 |
| 2022-07 | 0.425 | 1.132 | 0.150 | 0.524 | 0.085 | 0.294 | 0.001 | 0.023 |
| 2022-08 | 0.465 | 1.230 | 0.154 | 0.537 | 0.093 | 0.321 | 0.001 | 0.021 |
| 2022-09 | 0.354 | 0.941 | 0.150 | 0.527 | 0.105 | 0.365 | 0.001 | 0.019 |
| 2022-10 | 0.349 | 0.917 | 0.146 | 0.511 | 0.105 | 0.362 | 0.001 | 0.018 |
| 2022-11 | 0.293 | 0.773 | 0.148 | 0.516 | 0.113 | 0.393 | 0.001 | 0.021 |
| 2022-12 | 0.332 | 0.872 | 0.142 | 0.494 | 0.098 | 0.342 | 0.001 | 0.030 |
| 2023-01 | 0.323 | 0.859 | 0.169 | 0.590 | 0.085 | 0.294 | 0.001 | 0.029 |
| 2023-02 | 0.310 | 0.822 | 0.148 | 0.511 | 0.091 | 0.316 | 0.001 | 0.025 |
| 2023-03 | 0.471 | 1.245 | 0.181 | 0.630 | 0.122 | 0.425 | 0.001 | 0.028 |
| 2023-04 | 0.312 | 0.828 | 0.130 | 0.452 | 0.080 | 0.277 | 0.001 | 0.024 |
| 2023-05 | 0.438 | 1.170 | 0.189 | 0.657 | 0.120 | 0.423 | 0.001 | 0.025 |
| 2023-06 | 0.423 | 1.127 | 0.191 | 0.667 | 0.106 | 0.368 | 0.001 | 0.024 |
| 2023-07 | 0.426 | 1.136 | 0.165 | 0.581 | 0.102 | 0.354 | 0.001 | 0.023 |
| 2023-08 | 0.403 | 1.076 | 0.162 | 0.569 | 0.106 | 0.370 | 0.001 | 0.022 |
| 2023-09 | 0.313 | 0.840 | 0.155 | 0.544 | 0.103 | 0.360 | 0.001 | 0.018 |
| 2023-10 | 0.466 | 1.247 | 0.162 | 0.567 | 0.114 | 0.398 | 0.001 | 0.018 |
| 2023-11 | 0.390 | 1.036 | 0.154 | 0.537 | 0.094 | 0.327 | 0.001 | 0.021 |
| 2023-12 | 0.346 | 0.910 | 0.114 | 0.395 | 0.065 | 0.226 | 0.001 | 0.030 |
| 2024-01 | 0.429 | 1.143 | 0.137 | 0.478 | 0.086 | 0.299 | 0.001 | 0.029 |
| 2024-02 | 0.368 | 0.975 | 0.111 | 0.385 | 0.089 | 0.309 | 0.001 | 0.026 |
| **Total** | **14.842** | **39.149** | **5.693** | **19.854** | **3.657** | **12.644** | **0.043** | **0.947** |

| Series | Records | Compressed bytes | Decompressed bytes | Ratio | Decompressed minus records x record size (39 metadata headers) |
|---|---|---|---|---|---|
| Z1 ZM MBO | 699,094,402 | 14,842,362,471 | 39,149,317,416 | 2.64 | 30,904 |
| Z2 ZS MBP-1 | 248,169,282 | 5,692,759,621 | 19,853,557,984 | 3.49 | 15,424 |
| Z3 ZL MBP-1 | 158,046,466 | 3,656,692,936 | 12,643,733,176 | 3.46 | 15,896 |
| Z4 definitions | 1,810,372 | 42,892,820 | 947,188,376 | 22.1 | (not computed) |
| All four | 1,107,120,522 | 24,234,707,848 | 72,593,796,952 | 3.00 | |

Manifest notes (counts only): all 156 files passed every hard check; the manifest's exit code 3
comes from quality checks on Z4 only (35 files whose delivered record bytes differ from the quoted
billable bytes, for example 2020-12: 25,818,000 delivered versus 26,861,640 quoted, ratio 0.961;
8 Z4 files with a non-empty `metadata.partial`, parent-symbol combinations listed).

### 4.2 Decode throughput on this machine (my scan, nice 19, one process, 2026-10-27 00:34-00:39 PDT)

| Series | Decode wall s (39 files, incl. my counting) | Decompress-only pass wall s | Peak RSS |
|---|---|---|---|
| Z1 | 151.2 (4.6 M records/s) | 40.5 | 520 MB (whole run, 1 M-record chunks) |
| Z2 | 56.0 (4.4 M records/s) | 18.2 | |
| Z3 | 34.5 (4.6 M records/s) | 11.3 | |
| Z4 | 3.3 | 0.4 | 210 MB |

E.31 measured its split (decode plus per-day write) at 3.7 s for the 20.4 M-record 2024-01 Z1 file
(README_measure31.md "Speed and memory").

### 4.3 Already on disk

E.31's per-trade-date split arrays (`/mnt/large-storage/market_data/PropExperiment/derived/e31/`),
816 files per series, byte counts by `du -B1`: Z1 32,842,809,344 (MBO_COMPACT, 47 bytes per record,
10 fields: ts_recv, ts_event, instrument_id, order_id, price, size, flags, action, side, sequence);
Z2 10,176,966,656 and Z3 6,481,924,096 (MBP_COMPACT, 41 bytes, 7 fields: ts_recv, ts_event,
instrument_id, flags, bid_px, ask_px, sequence); 49,501,700,096 bytes in all. The ZS/ZL split keeps
no sizes, counts, action, side or trade fields (section 6.3 item 3). Free space on
/mnt/large-storage on 2026-10-27: 739,511,693,312 bytes.

### 4.4 Projection for rebuilding books and features over the 39 months (816 trade dates)

Measured inputs: section 5 (one-day book rebuild, peak RSS 125-229 MB per process from the split,
338-394 MB from the raw file; book-phase throughput 0.42-0.76 M records/s per process over the 9
split runs and 0.39-0.60 M records/s over the book phase of the 9 raw runs), section 4.2.
Arithmetic, under the assumption that throughput per record is the same on every day:

- Book rebuild, both ZM instruments, all 816 dates: 698,738,911 records / 0.39 M/s = 1,792 s
  (29.9 min) at the slowest measured rate, / 0.76 M/s = 919 s (15.3 min) at the fastest, in one
  process; with 4 processes about 4 to 8 minutes of wall time. ZM.v.0 alone: 414,363,576 records
  (59.3% of the regular-date total), so about 9 to 18 minutes in one process. Loading the day from
  E.31's split adds 0.02-0.10 s a day; decoding from the raw month file instead adds 2.8-4.8 s a
  day when each day re-decodes its month (section 5), avoidable by splitting once (151 s of Z1 decoding in my scan; E.31 estimated about 4 min for
  all four series).
- Memory: 4 processes x 229 MB = 0.92 GB at the busiest measured day from the split; from the raw
  files 4 x 394 MB = 1.58 GB. Holding one busiest day's compact MBO array: 1,748,582 x 47 bytes =
  82 MB. Memory is not the binding limit for the rebuild on the 14 GB machine.
- Disk for a re-split of ZS and ZL keeping all 20 MBP-1 fields (80 bytes): 248,167,909 x 80 =
  19.85 GB and 158,044,028 x 80 = 12.64 GB (fewer if fields are dropped); decode time about 56 s and
  35 s (section 4.2).
- Disk for a feature store, illustrative only (the sampling and the feature count are Part P's
  decisions): rows x features x 4 bytes (float32). Per ZM event (all 584,881,539 F_LAST events of
  both instruments) x 32 features = 74.9 GB; per second over both sessions (765 + 290 = 1,055 minutes
  = 63,300 s a day; x 816 = 51,652,800 rows) x 32 = 6.61 GB; per minute (1,055 x 816 = 860,880
  rows) x 32 = 0.11 GB. Check: 51,652,800 / 860,880 = 60.0.

## 5. Time to rebuild one day of ZM MBO with E.31's book code

Days chosen by message count only (section 3.1 rule, Z1 records of the trade date, both ZM
instruments): median 2022-02-15 (827,199 records), p90 2022-07-27 (1,139,174), max 2021-05-07
(1,748,582). Script `work/F_data_facts/F_book_time.py`: loads the day, then for each instrument runs
E.31's `mbo_book31.time_axis` and feeds every record through `mbo_book31.Book` (top_min 1,
top_max 100 as `kalgo31.ZM_K`; `count_initial` = trade date before 2023-10-02, as E.31) with the
book-changing branches of `measure31_core.InstrumentRun._run_chunk` replicated (valid start at the
first R, bad-book flags, snapshot end, A/C/M/R, F counted against TOP Max, T aggressed lots). E.31's
placements, fill models, markouts and BBO history were not run (they compute market values); a
feature pipeline adds its own extraction cost on top. Each run is a fresh process at nice 19 (nice
10 plus the script's own `os.nice(10)`); load average was about 6 from other jobs (uptime at
00:42 PDT), so the three repeats spread by up to 40%. `free -m` before the runs: 10,186 MB
available, after: 9,279 MB.

Two load routes: "split" = E.31's per-day array `derived/e31/Z1/<date>.npy`; "raw" = decode the
month's DBN file and keep the day (whole-month decode in the load time).

| Day (rule) | Route | Records | Load wall s | Book wall s (3 runs) | Book CPU s (3 runs) | Total wall s (3 runs) | Peak RSS MB (3 runs) |
|---|---|---|---|---|---|---|---|
| 2022-02-15 (median) | split | 827,199 | 0.055 / 0.040 / 0.018 | 1.091 / 1.545 / 1.616 | 1.089 / 1.545 / 1.615 | 1.146 / 1.585 / 1.633 | 125.3 / 125.3 / 125.8 |
| 2022-02-15 (median) | raw | 827,199 | 2.799 / 3.519 / 4.239 | 1.736 / 1.477 / 1.729 | 1.734 / 1.477 / 1.727 | 4.534 / 4.996 / 5.967 | 339.1 / 338.9 / 338.2 |
| 2022-07-27 (p90) | split | 1,139,174 | 0.043 / 0.056 / 0.025 | 2.401 / 2.050 / 2.327 | 2.400 / 2.049 / 2.327 | 2.444 / 2.106 / 2.352 | 208.2 / 208.3 / 208.9 |
| 2022-07-27 (p90) | raw | 1,139,174 | 3.976 / 4.086 / 4.014 | 1.902 / 1.938 / 2.211 | 1.901 / 1.938 / 2.211 | 5.878 / 6.024 / 6.225 | 365.6 / 364.6 / 365.0 |
| 2021-05-07 (max) | split | 1,748,582 | 0.095 / 0.075 / 0.031 | 3.543 / 4.036 / 4.180 | 3.542 / 4.035 / 4.179 | 3.638 / 4.111 / 4.211 | 228.4 / 228.0 / 227.7 |
| 2021-05-07 (max) | raw | 1,748,582 | 4.610 / 4.024 / 4.758 | 3.885 / 3.536 / 4.466 | 3.878 / 3.535 / 4.464 | 8.495 / 7.560 / 9.223 | 393.4 / 393.3 / 394.0 |

Per-instrument counts from the same runs (identical in every repeat): records per instrument
2022-02-15 423,464 (497002 ZMK2) and 403,735 (689369 ZMH2); 2022-07-27 951,663 (697256 ZMZ2) and
187,511 (81763 ZMQ2, ZM.v.1 that day); 2021-05-07 876,595 (156434 ZMN1) and 871,987 (794459 ZMZ1). Records before the
first R (valid start) 33/43, 98/34, 160/34; F_MAYBE_BAD_BOOK/F_TOB/F_MBP records 0 on all three
days; `Book.anomalies` 0 on all three days; ts_event inversions 0. Largest resting-order count
(sampled every 4,096 records) 835-1,456 orders per instrument.

Reading: the book itself runs at 0.39-0.76 M records/s in one pure-Python process (CPU time = wall
time: one core, no I/O wait), below E.31's own 0.97 M records/s for its whole engine on
2024-01-24 (849,507 records; README_measure31.md); the gap is not explained here (the load from
other processes during my runs is one candidate). Peak RSS is set by the day's arrays
plus the Python lists of the replica loop (about 125-230 MB from the split), and by the decode
chunks when reading the raw file (about 340-395 MB).

## 6. E.31 code that can be reused for directional features and labels, and what is missing

Source: module and function docstrings and signatures of reports/stage_e31_briefs/work/pilot/*.py
(read by `ast`, 2026-10-27), reports/stage_e31_pilot_spec.md section headings, and
README_measure31.md. Test counts are `def test_` lines in pilot/tests/. "Reuse" means import as is
or copy with the same semantics; nothing below was run except `mbo_book31.Book` and
`mbo_book31.time_axis` in section 5.

### 6.1 Reusable as is

| Module | Function / class | What it does (docstring) | Directional use | Tests |
|---|---|---|---|---|
| mbo_book31 | `Book` (`add`, `cancel`, `modify`, `clear`, `on_fill`, `end_snapshot`, `mark_bad`, `best`, `level_total`, `queue`, `is_valid`, `top_at`) | "One instrument's displayed outright book with time priority and TOP state." A modify that raises size or changes price loses priority; R clears; T, F, N do not change the book; F_MAYBE_BAD_BOOK marks the book bad until the next R. | The core of every book feature (best levels, level totals, queue lengths, order counts) for ZM.v.0 and ZM.v.1. Only `best` and `level_total` are O(1)/O(levels); there is no depth-k accessor beyond `prices` (sorted price lists per side) and `levels`. | test_book31.py, 19 |
| mbo_book31 | `time_axis(ts_event, ts_recv, flags)` | "ts_event made non-decreasing in file order. Snapshot records carry the snapshot generation time (ts_recv) instead of an event time, so they enter the running maximum with ts_recv; inversions are counted over the other records only." | The event-time axis for any sampler and label horizon. | test_book31.py |
| mbo_book31 | constants `ACT_*`, `SIDE_*`, `F_*`, `UNDEF_PRICE`, `book_side` | Action, side and flag codes matching Databento's. | Shared decoding constants. | |
| measure31.py | `split_file`, `compact`, `day_bounds`, `MBO_COMPACT`, `MBP_COMPACT` | "Stream one Z1/Z2/Z3 file once into per-trade-date compact arrays (resumable per file)." Trade date D = ts_recv in [D-1 16:00 CT, D 16:00 CT); keeps regular grains trade dates of the file's month. | The per-day store already exists for all 39 months (section 4.3, 47 GB at /mnt/large-storage/market_data/PropExperiment/derived/e31/Z1, Z2, Z3; markers checked against the manifest sha256). MBP_COMPACT keeps only ts_recv, ts_event, instrument_id, flags, bid_px, ask_px, sequence: no sizes, counts, action, side or trade price for ZS/ZL. | test_measure31.py, 45 (whole file) |
| measure31.py | `load_manifest`, `guard_request`, `open_store`, `guard_chunk`, `file_sha256` | Manifest hard-check refusal, sha256 re-check, refusal of any record on or after 2024-03-01, refusal of a request touching a sealed window (`data.holdout.request_touches_sealed_window`). | The data guards a directional pipeline needs, plus the soy test-window seal (2017-05-01..2020-11-30) which E.31's guards do not name: they check data.holdout's windows, so the seal must be added. | |
| measure31.py | `definition_rows`, `read_definitions`, `root_tick`, `checked_tick`, `definitions_summary` | "The last definition of every outright future (instrument_class F) of ZM, ZS and ZL"; tick from Z4 `min_price_increment`, checked against tick value in USD. | Tick sizes for tick-normalised labels. Known issue (README_measure31.md): the USD check stops on ZS and ZL because their prices are in cents; the rule for the check is open. | |
| measure31.py | `merge_mappings`, `instrument_on`, `roll_reasons` | Continuous-symbol mapping intervals (UTC dates, end exclusive) to instrument ids; roll day and the trade date after it flagged. | Front and second-month identity per trade date; roll exclusions for labels that would span a roll. | |
| measure31.py | `grains`, `month_trade_dates`, `calendar_reason` | Grains calendar trade dates; holiday, early close and late-open reasons. | Day universe and exclusions. | |
| measure31.py | `load_usda`, `usda_coverage`, `release_trade_date`; measure31_core `usda_minutes` | USDA release instants per trade date (reports/stage_e31_briefs/research/usda_releases*.csv, covered 2020-12-01..2024-02-29); signed minutes to the nearest release. | Event-time conditioning and exclusion windows around releases. | |
| measure31_core | `regular_sessions`, `Session` | OVERNIGHT 19:00 CT (D-1) to 07:45 CT, DAY 08:30-13:20 CT. `Session.grid` is E.31's 5-minute placement grid (DAY 08:35..13:10, 56 times). | Session masks; the grid is a clock-time sampler template. | |
| measure31_core | `instrument_records`, `has_valid_start`, `max_gap_s`, `symbol_prepass` | Per-instrument records with the time axis; a snapshot clear before the first open; largest gap inside a session; day exclusion reasons. | Day-level data-quality filters. | |
| measure31_core | `InstrumentRun.commit` and `History` (`index`, `mid`) | Appends (t, best bid, best ask, valid) whenever the top of book or its validity changes, at F_LAST boundaries only. `History.index(at)` is an as-of lookup. | An as-of top-of-book series for ZM; usable for mid-based labels at fixed horizons. Tied to `InstrumentRun`, which also runs placements and fill models: it must be lifted out to be used alone. | |
| measure31_core | `CondSeries.of`, `mid_at`, `move` | "A ZS or ZL mbp-1 state series of the trade date (time axis, mid, validity, tick)"; `mid_at` = "Last valid mid at or before ``at`` from a record inside the session". Validity: both sides defined, bid < ask, no F_MAYBE_BAD_BOOK. | A minimal as-of aligner for ZS/ZL mid on the ZM clock (top-of-book mid only). | test_measure31.py |
| measure31_core | `markouts` | "markout_h = s x (mid(t_f + h) - mid0) / tick per horizon", headline (dropped at session end or on any invalid state in the window) and no-drop variants. | The template of a fixed-horizon, tick-normalised mid-change label with drop rules; the horizons are E.31's seconds (`HORIZONS_S`), not minutes. | test_measure31.py |
| canary_check31 | `TFPairing`, `TFRuns` | T and F records per instrument paired in file order (each T opens a group the following F records join). | Aggressor-signed trade volume and trade-event grouping for order-flow features. Info-only class today. | test_canary31.py, 15 |
| stats31_core | `bootstrap_weights`, `ratio_stat`, `interval`, `per_day` | Day-block bootstrap ("W[r, d] = how often trade date d is drawn in replicate r (E.28's construction)"), pooled ratios with percentile intervals. | Day-block intervals for any per-day statistic. | test_stats31.py, 29 |
| stats31_core | `imb_bucket`, `usda_bucket`, `move_bucket`, `joint_bucket` | Fixed buckets: side-adjusted imbalance, minutes from USDA release, sign of ZS/ZL move. | Bucket definitions only; directional features need continuous values. | |
| verify31.py | `Scan`, `verify_file`, `snapshot_table`, `tail_check` | File checks that produced the manifests. | Already run; nothing to redo. | |

### 6.2 Not reusable for this purpose

`kalgo31.py` (CME algorithm K fill allocation; only for passive-fill simulation),
`measure31_core.VOrder`, `Loop`, `Placement`, `InstrumentRun.fill`, `through`, `implied_check`,
`close_event`, `_k_allocation`, `touched`, `is_stale` (virtual passive orders and fill models),
`stats31.py` / `stats31_report.py` (the E.31 kill rule and report), `pull31.py`,
`pilot31_common.py` and `vol_pull.py` (purchase and spend-gate code; must not be run),
`vol_measure.py` (daily volume of QM/ZM fronts from ohlcv-1d).

### 6.3 Missing for a directional search (to be written)

1. A standalone book driver: the book-changing branch of `InstrumentRun._run_chunk` without
   placements, fill models and timers (section 5 used a 40-line replica; it should be a tested
   module) that emits book states at chosen sample times.
2. Book feature extractors on the rebuilt book: depth beyond level 1 (sum of the first k levels
   per side from `Book.prices` and `levels`), order counts per level, queue ages, add/cancel/
   trade flow over trailing windows, aggressor-signed volume (from T records; `TFPairing` covers
   only the pairing). Nothing in E.31 computes a trailing-window statistic.
3. A ZS/ZL MBP-1 aligner beyond the mid: E.31's split arrays (MBP_COMPACT) dropped the MBP-1
   sizes, counts, action, side, trade price and size, so trade flow and top-of-book size for ZS
   and ZL need a new split from the raw Z2/Z3 files (about 4 s per month per series, section 4.4).
   Also needed: as-of joins with an explicit latency (ts_recv of the context record < the ZM
   sample time), and the cross-instrument check that ts_recv clocks are comparable (same
   capture, both GLBX).
4. An event-time sampler: samples by trade count, volume, F_LAST event count or a mid-change
   rule, on the `time_axis` clock, with session masks. E.31 has only the 5-minute clock grid.
5. A label builder for minutes-scale directional targets: forward mid change (and sign, and
   triple-barrier style if Part P chooses it) at minute horizons on the ZM.v.0 as-of history, with
   session-end, invalid-book and roll-day drops, and the label end time stored for purging.
6. Purged and embargoed CV folds by trade date with label end times (V43). Nothing in E.31.
7. A feature store writer (per-day parquet with fixed schema and fingerprint) and resumable
   runner; `measure31.py` main/pool/`run_task`/`write_day_tables` are the pattern to copy.
8. The soy test-window seal guard (2017-05-01..2020-11-30) in the data guards, and the 2024-03-01
   cutoff (present).

## 7. What I could not do, and caveats

- Section 5 times only the book rebuild; the BBO history (`InstrumentRun.commit`), feature
  extraction and labels were not timed because they compute market values, which the data rule
  forbids for this worker. A per-event `best()` lookup is O(1) on `Book.prices`, so the BBO
  history should add little, but that is [unverified] by measurement.
- The split of the 2,036 Z1 R records into snapshot clears and channel resets, and the meaning of
  the F records inside the MBP-1 files, were not established.
- Timings were taken under a load average of about 6 from other processes; repeats spread up to
  40%. They are upper-side figures for a quiet machine.
- `ts_event` whole-millisecond values (0.017% of ZM records) are counted but not located.
- No E.31 test was run (the code inventory is from docstrings and signatures).

## Appendix A. ZM.v.1 mapping runs (79)

| Continuous symbol | instrument_id | raw_symbol (Z4) | Mapped from (UTC date) | to (exclusive) | Expiration (Z4, UTC date) |
|---|---|---|---|---|---|
| ZM.v.1 | 413266 | ZMZ0 | 2020-11-30 | 2020-12-02 | 2020-12-14 |
| ZM.v.1 | 282089 | ZMH1 | 2020-12-02 | 2020-12-18 | 2021-03-12 |
| ZM.v.1 | 504886 | ZMF1 | 2020-12-18 | 2021-01-01 | 2021-01-14 |
| ZM.v.1 | 89700 | ZMK1 | 2021-01-01 | 2021-02-22 | 2021-05-14 |
| ZM.v.1 | 282089 | ZMH1 | 2021-02-22 | 2021-02-28 | 2021-03-12 |
| ZM.v.1 | 156434 | ZMN1 | 2021-02-28 | 2021-04-16 | 2021-07-14 |
| ZM.v.1 | 89700 | ZMK1 | 2021-04-16 | 2021-05-02 | 2021-05-14 |
| ZM.v.1 | 794459 | ZMZ1 | 2021-05-02 | 2021-06-17 | 2021-12-14 |
| ZM.v.1 | 727762 | ZMQ1 | 2021-06-17 | 2021-06-18 | 2021-08-13 |
| ZM.v.1 | 794459 | ZMZ1 | 2021-06-18 | 2021-06-24 | 2021-12-14 |
| ZM.v.1 | 156434 | ZMN1 | 2021-06-24 | 2021-06-28 | 2021-07-14 |
| ZM.v.1 | 243619 | ZMF2 | 2021-06-28 | 2021-06-29 | 2022-01-14 |
| ZM.v.1 | 156434 | ZMN1 | 2021-06-29 | 2021-06-30 | 2021-07-14 |
| ZM.v.1 | 727762 | ZMQ1 | 2021-06-30 | 2021-07-30 | 2021-08-13 |
| ZM.v.1 | 535389 | ZMU1 | 2021-07-30 | 2021-09-01 | 2021-09-14 |
| ZM.v.1 | 186868 | ZMV1 | 2021-09-01 | 2021-09-10 | 2021-10-14 |
| ZM.v.1 | 243619 | ZMF2 | 2021-09-10 | 2021-09-12 | 2022-01-14 |
| ZM.v.1 | 186868 | ZMV1 | 2021-09-12 | 2021-10-03 | 2021-10-14 |
| ZM.v.1 | 243619 | ZMF2 | 2021-10-03 | 2021-11-22 | 2022-01-14 |
| ZM.v.1 | 794459 | ZMZ1 | 2021-11-22 | 2021-12-02 | 2021-12-14 |
| ZM.v.1 | 689369 | ZMH2 | 2021-12-02 | 2021-12-22 | 2022-03-14 |
| ZM.v.1 | 243619 | ZMF2 | 2021-12-22 | 2022-01-02 | 2022-01-14 |
| ZM.v.1 | 497002 | ZMK2 | 2022-01-02 | 2022-02-18 | 2022-05-13 |
| ZM.v.1 | 689369 | ZMH2 | 2022-02-18 | 2022-02-28 | 2022-03-14 |
| ZM.v.1 | 120191 | ZMN2 | 2022-02-28 | 2022-04-15 | 2022-07-14 |
| ZM.v.1 | 497002 | ZMK2 | 2022-04-15 | 2022-05-02 | 2022-05-13 |
| ZM.v.1 | 697256 | ZMZ2 | 2022-05-02 | 2022-06-24 | 2022-12-14 |
| ZM.v.1 | 120191 | ZMN2 | 2022-06-24 | 2022-06-27 | 2022-07-14 |
| ZM.v.1 | 697256 | ZMZ2 | 2022-06-27 | 2022-06-29 | 2022-12-14 |
| ZM.v.1 | 81763 | ZMQ2 | 2022-06-29 | 2022-07-28 | 2022-08-12 |
| ZM.v.1 | 274159 | ZMU2 | 2022-07-28 | 2022-08-15 | 2022-09-14 |
| ZM.v.1 | 758259 | ZMV2 | 2022-08-15 | 2022-08-17 | 2022-10-14 |
| ZM.v.1 | 274159 | ZMU2 | 2022-08-17 | 2022-08-24 | 2022-09-14 |
| ZM.v.1 | 758259 | ZMV2 | 2022-08-24 | 2022-08-25 | 2022-10-14 |
| ZM.v.1 | 274159 | ZMU2 | 2022-08-25 | 2022-08-26 | 2022-09-14 |
| ZM.v.1 | 758259 | ZMV2 | 2022-08-26 | 2022-09-11 | 2022-10-14 |
| ZM.v.1 | 8352 | ZMF3 | 2022-09-11 | 2022-09-12 | 2023-01-13 |
| ZM.v.1 | 758259 | ZMV2 | 2022-09-12 | 2022-09-15 | 2022-10-14 |
| ZM.v.1 | 8352 | ZMF3 | 2022-09-15 | 2022-09-16 | 2023-01-13 |
| ZM.v.1 | 758259 | ZMV2 | 2022-09-16 | 2022-09-28 | 2022-10-14 |
| ZM.v.1 | 8352 | ZMF3 | 2022-09-28 | 2022-10-30 | 2023-01-13 |
| ZM.v.1 | 185432 | ZMH3 | 2022-10-30 | 2022-10-31 | 2023-03-14 |
| ZM.v.1 | 8352 | ZMF3 | 2022-10-31 | 2022-11-23 | 2023-01-13 |
| ZM.v.1 | 697256 | ZMZ2 | 2022-11-23 | 2022-12-01 | 2022-12-14 |
| ZM.v.1 | 185432 | ZMH3 | 2022-12-01 | 2022-12-12 | 2023-03-14 |
| ZM.v.1 | 8352 | ZMF3 | 2022-12-12 | 2022-12-14 | 2023-01-13 |
| ZM.v.1 | 185432 | ZMH3 | 2022-12-14 | 2022-12-18 | 2023-03-14 |
| ZM.v.1 | 8352 | ZMF3 | 2022-12-18 | 2023-01-01 | 2023-01-13 |
| ZM.v.1 | 23389 | ZMK3 | 2023-01-01 | 2023-02-20 | 2023-05-12 |
| ZM.v.1 | 185432 | ZMH3 | 2023-02-20 | 2023-03-02 | 2023-03-14 |
| ZM.v.1 | 658865 | ZMN3 | 2023-03-02 | 2023-04-16 | 2023-07-14 |
| ZM.v.1 | 23389 | ZMK3 | 2023-04-16 | 2023-04-30 | 2023-05-12 |
| ZM.v.1 | 51239 | ZMZ3 | 2023-04-30 | 2023-06-22 | 2023-12-14 |
| ZM.v.1 | 658865 | ZMN3 | 2023-06-22 | 2023-06-29 | 2023-07-14 |
| ZM.v.1 | 560547 | ZMQ3 | 2023-06-29 | 2023-07-24 | 2023-08-14 |
| ZM.v.1 | 258176 | ZMU3 | 2023-07-24 | 2023-07-26 | 2023-09-14 |
| ZM.v.1 | 560547 | ZMQ3 | 2023-07-26 | 2023-07-28 | 2023-08-14 |
| ZM.v.1 | 258176 | ZMU3 | 2023-07-28 | 2023-08-18 | 2023-09-14 |
| ZM.v.1 | 466507 | ZMV3 | 2023-08-18 | 2023-08-20 | 2023-10-13 |
| ZM.v.1 | 258176 | ZMU3 | 2023-08-20 | 2023-08-23 | 2023-09-14 |
| ZM.v.1 | 466507 | ZMV3 | 2023-08-23 | 2023-08-24 | 2023-10-13 |
| ZM.v.1 | 258176 | ZMU3 | 2023-08-24 | 2023-08-25 | 2023-09-14 |
| ZM.v.1 | 466507 | ZMV3 | 2023-08-25 | 2023-09-10 | 2023-10-13 |
| ZM.v.1 | 152114 | ZMF4 | 2023-09-10 | 2023-09-11 | 2024-01-12 |
| ZM.v.1 | 466507 | ZMV3 | 2023-09-11 | 2023-09-13 | 2023-10-13 |
| ZM.v.1 | 152114 | ZMF4 | 2023-09-13 | 2023-09-14 | 2024-01-12 |
| ZM.v.1 | 466507 | ZMV3 | 2023-09-14 | 2023-09-17 | 2023-10-13 |
| ZM.v.1 | 152114 | ZMF4 | 2023-09-17 | 2023-09-18 | 2024-01-12 |
| ZM.v.1 | 466507 | ZMV3 | 2023-09-18 | 2023-09-22 | 2023-10-13 |
| ZM.v.1 | 152114 | ZMF4 | 2023-09-22 | 2023-09-24 | 2024-01-12 |
| ZM.v.1 | 466507 | ZMV3 | 2023-09-24 | 2023-10-01 | 2023-10-13 |
| ZM.v.1 | 152114 | ZMF4 | 2023-10-01 | 2023-11-15 | 2024-01-12 |
| ZM.v.1 | 51239 | ZMZ3 | 2023-11-15 | 2023-11-24 | 2023-12-14 |
| ZM.v.1 | 506263 | ZMH4 | 2023-11-24 | 2023-11-27 | 2024-03-14 |
| ZM.v.1 | 51239 | ZMZ3 | 2023-11-27 | 2023-11-30 | 2023-12-14 |
| ZM.v.1 | 506263 | ZMH4 | 2023-11-30 | 2023-12-18 | 2024-03-14 |
| ZM.v.1 | 152114 | ZMF4 | 2023-12-18 | 2023-12-31 | 2024-01-12 |
| ZM.v.1 | 759433 | ZMK4 | 2023-12-31 | 2024-02-16 | 2024-05-14 |
| ZM.v.1 | 506263 | ZMH4 | 2024-02-16 | 2024-03-01 | 2024-03-14 |
