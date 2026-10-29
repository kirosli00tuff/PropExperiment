# Stage E.34 Part F: data facts for the ZL program (DataFacts-SonnetHigh)

Written 2026-10-29 12:23 PDT (America/Vancouver). Counts, schemas, sizes and code references only. No price, return, feature
value, label, markout or model output was computed or looked at; no record was printed. Scripts, logs, per-file
counts and `opens.log` are in `reports/stage_e34_briefs/work/DataFacts-SonnetHigh/` (called "my folder" below).

## 0. Scope, guard and method

- Data touched: the 39 ZL MBP-1 files `Z3_ZL_v_0` and their `manifest.json`; the 39 definition files `Z4_ZM_FUT-ZS_FUT-ZL_FUT`
  (its `manifest.json` is the same discovery manifest and was not opened separately); ohlcv-1m `range=2020-12-01_2021-01-01 ..
  range=2024-02-01_2024-03-01` for ZL_v_0, ZS_v_0, ZM_v_0 (39 each). Nothing else. Every open went through `guard34.check`
  (`guard34.py`, explicit allowlist of 197 real paths, symlinks resolved); `opens.log` holds 281 timestamped opens
  (PDT), including the guard dry-check's one positive-control open and the three measurement runs.
- Fields read from MBP-1: `ts_recv, ts_event, action, side, flags, instrument_id` only (counts, min/max comparisons and
  bit tallies; no `price`, `size`, `bid_px_00` etc. was indexed). From ohlcv-1m: `ts_event, instrument_id, rtype`. From
  definitions: `instrument_id, raw_symbol, asset, instrument_class, expiration, min_price_increment, ts_recv` and the DBN
  header fields. Record-level guard: `ts_recv` must lie in [2020-11-30T22:00Z, 2024-03-01T00:00Z) (`guard34.check_ts`).
- The first MBP-1 file starts at 2020-11-30T22:00Z (the sealed window's exclusive end); its first record has
  `ts_recv` 2020-11-30T22:45:00Z (manifest `ts_recv_min`), inside trade date 2020-12-01 under the rule in section 1.
  No record dated before that instant was seen (guard never fired).
- Per-file decode and counting: `count_zl.py` (MBP-1), `count_bars.py` (bars), `schema_defs.py` (dtypes, definitions),
  `manifest_facts.py` (manifest metadata), `agg_zl.py`, `agg_bars.py`, `facts_misc.py`, `render.py`. Resumable per file;
  results in `counts/`, `bars/`, `agg_zl.json`, `agg_bars.json`, `facts_misc.json`, `schema_defs.json`,
  `manifest_facts.json`. Run under `nice -n 10`, one process at a time; free memory checked first (10.6 GB available).
- Reuse step (brief step 2): E.33's split log `reports/stage_e33_briefs/work/logs/split33_ZL.log` holds only the grand totals
  and the per-month "outside trade dates" counts, no per-date counts (its tail line 41: 158,044,028 records, 816
  dates, `zero_record_dates` empty, `records_read` 158,046,466; E.33_RETURN.md line 136 says the same). The per-date and
  per-action counts were therefore decoded here. My totals reproduce E.33's exactly: 158,046,466 records read,
  158,044,028 stored in the 816 trade dates, 2,438 outside (E.33's per-month outside counts sum to the same 2,438, see
  `counts/` and the log line 41).

Guard dry-check output (`dry_check.out`, run 2026-10-29 12:11:40 PDT):

```
OK    sealed blob under data/sealed: refused
OK    in-window raw ZL ohlcv-1m 2020-11: refused
OK    ZL ohlcv-1m 2024-03: refused
OK    ZS ohlcv-1m 2025: refused
OK    rolls file: refused
OK    FRED csv: refused
OK    E.32 derived tsv: refused
OK    E.12 ML cache: refused
OK    .env: refused
OK    positive control: first ZL MBP-1 file allowed (range=2020-11-30T220000Z_2020-12-31T220000Z.dbn.zst)
allowlist entries: 197
```

## 1. Trade-date rule and calendar

- Calendar: E.33's 816 grains trade dates 2020-12-01..2024-02-29, built by the same rule as
  `cal33._trade_dates` (cal33.py:82-89, via `measure31.month_trade_dates`, measure31.py:319-328): every calendar day in the
  months with `GroupCalendar("grains").covers(D)` and `.is_trade_date(D)` (weekday, not a full closure, not a booked-forward
  day; data/group_session.py:146-148). I rebuilt it directly from `data.group_session.load_group_calendar("grains")` (no
  market data) and got 816 dates, first 2020-12-01, last 2024-02-29 (`trade_dates_e33rule.json`).
- Record-to-date rule: trade date D holds the records with `ts_recv` in [D-1 16:00 CT, D 16:00 CT)
  (`data33.window`, data33.py:84-88; DST-aware America/Chicago). Records whose window date is not one of the 816 (weekends,
  closures) are counted as "outside", not assigned: 2,438 for ZL MBP-1, 0 for every bar file.
- Bars use the same window on `ts_event` (the bar's open minute).
- Segments: "day session" = `ts_recv` Chicago time of day in [08:30, 13:20); "rest" = everything else (evening session
  from 19:00 CT, the 07:45-08:30 pause, post-close, pre-open). The grain complex's session times are the ones
  `feat33.py` documents at lines 55-57 (day (08:30, 13:20], pause 07:45-08:30).
- Hour-of-day histogram of all 158.0M `ts_recv` (Chicago hour, 0..23; `hour_ct.json`): the feed is dense in hours
  19-23 and 0-13 and nearly empty in hours 14-18 (8,578 records in all five hours together; the first record of the first file is at 16:45 CT).
  Trades (`T`) are 0 in hours 14-18 (`hour_ct.json`).

## 2. Schemas, fields, timestamps

DBN metadata (read from every file's header; all 39 MBP-1 files identical in these fields; `counts/zl_*.json` field
`metadata`, `manifest_facts.json`):

| item | ZL MBP-1 | ohlcv-1m (ZL, ZS, ZM) | definition |
|---|---|---|---|
| DBN version | 3 | 3 | 3 |
| dataset | GLBX.MDP3 | GLBX.MDP3 | GLBX.MDP3 |
| schema | mbp-1 | ohlcv-1m | definition |
| stype_in / stype_out | continuous / instrument_id | continuous / instrument_id | parent / instrument_id |
| symbols | ZL.v.0 | ZL.v.0, ZS.v.0, ZM.v.0 (one root per folder) | ZM.FUT, ZS.FUT, ZL.FUT |
| record size | 80 bytes (rtype 1) | 56 bytes (rtype 33) | 520 bytes (rtype 19) |
| file start..end | 2020-11-30T22:00Z..2024-02-29T22:00Z (monthly, ends the 22:00Z or 21:00Z of the month's last day) | 2020-12-01T00:00Z..2024-03-01T00:00Z (calendar months) | same monthly 22:00Z/21:00Z grid as MBP-1 |
| records (39 files) | 158,046,466 | ZL 733,593; ZS 786,583; ZM 679,988 | 1,810,372 |

Request strings are in `manifest_facts.json` (`request`): symbols `['ZL.v.0']`, `stype_in` `continuous`, start/end as the file
names. `.v.0` is Databento's volume-based continuous symbol: the lead month is the one with the highest previous-day volume
(Databento definition; [unverified here], consistent with the roll pattern in section 5, where the front skips ZLU and ZLV).

Record fields (types from the DBN dtype, `schema_defs.json`):

- MBP-1 (80 B): `length u1, rtype u1, publisher_id u2, instrument_id u4, ts_event u8, price i8, size u4, action S1, side S1,
  flags u1, depth u1, ts_recv u8, ts_in_delta i4, sequence u4, bid_px_00 i8, ask_px_00 i8, bid_sz_00 u4, ask_sz_00 u4,
  bid_ct_00 u4, ask_ct_00 u4`. Prices are fixed-point int64 in 1e-9 units. E.33 stores a 79-byte compact version
  (`data33.MBP1_SPLIT`, data33.py:59-65: drops `length`, `action/side` as u1).
- ohlcv-1m (56 B): `length, rtype, publisher_id, instrument_id, ts_event, open, high, low, close, volume` (not read beyond
  `ts_event/instrument_id/rtype`).
- definition (520 B): 75 fields; the ones that matter here are `ts_recv, ts_event, instrument_id, raw_symbol S71, asset S11,
  instrument_class S1, security_update_action S1, expiration u8 (ns UTC), activation u8, min_price_increment i8,
  min_price_increment_amount i8, high_limit_price i8, low_limit_price i8, maturity_year/month/day` (E.33 keeps 26 of them,
  `data33.DEF_FIELDS`, data33.py:68-77; I did not read the limit prices).

Timestamps (MBP-1):

- `ts_event`: the exchange (matching-engine) event time; `ts_recv`: Databento's capture time; `ts_in_delta`: the offset
  between the exchange send time and `ts_recv`, in ns (Databento field definitions; [unverified here, not fetched]). E.33
  ordered and clocked everything on `ts_recv` and never read `ts_event` (lab33.py:20-21: "The clock is ts_recv only (P0.3,
  LT4); ts_event is never read"; cost33.py:36-37: "a record is known at u iff ts_recv <= u").
- Measured on the owned ZL front files (counts, over all 158,046,466 records): `ts_recv` decreases between consecutive
  records within each file: 0 (file order is `ts_recv` order, so the sort in `data33._in_ts_recv_order`,
  data33.py:94-99, did nothing here); `ts_event > ts_recv`: 230,475 records (0.146% of all); `ts_recv - ts_event > 1 s`:
  354 records; `> 1 day`: 7 records (not cross-tabulated against the flags); `ts_event` undefined (max uint64): 0.
- Flag bits (record counts): F_LAST (128) 142,061,153; F_SNAPSHOT (32) 848; F_BAD_TS_RECV (8) 848;
  F_MAYBE_BAD_BOOK (4) 476; F_TOB (64) 0; F_MBP (16) 0. F_SNAPSHOT and F_BAD_TS_RECV have identical counts
  (848); E.33's G6 report excludes records with either flag because their `ts_recv` is the snapshot generation time or
  inaccurate (g6_33.py docstring, READING G6-1).
- `side` counts (A ask / B bid / N none): A 78,392,325, B 77,463,857, N 2,190,284.
- Clock report: E.33's `ts_recv - ts_event` medians per month are in `reports/stage_e33_briefs/work/G6_clock_report.md`
  (not copied here, rule 3).

## 3. Message counts per trade date, ZL MBP-1

Method: all 39 files decoded once (`count_zl.py`, 39.4 s of decode+count in total at nice 10); counts by trade date
(816), action and segment. All 816 dates have records (no zero-record date); 158,044,028 records land in the 816 dates.

Daily record counts, median (5th-95th percentile) over the dates of each group; "other" = actions F, R, N (and any
unlisted code); "day session" and "rest" partition "all":

| group | dates | all | trades T | adds A | cancels C | modifies M | other | day session | rest |
|---|---|---|---|---|---|---|---|---|---|
| all 816 | 816 | 188,782 (129,857-273,153) | 19,206 (12,352-27,993) | 79,789 (51,540-119,854) | 73,184 (46,157-113,305) | 13,040 (7,635-30,049) | 131 (32-645) | 131,302 (86,873-200,348) | 53,878 (32,343-95,750) |
| 2020 (Dec) | 22 | 212,966 (162,479-325,016) | 14,636 (10,377-19,416) | 97,526 (73,587-149,920) | 92,650 (70,075-141,320) | 10,126 (6,910-15,333) | 119 (34-341) | 126,912 (90,642-186,565) | 87,586 (55,716-139,689) |
| 2021 | 252 | 173,748 (115,863-268,582) | 18,476 (12,020-27,010) | 68,874 (47,332-112,793) | 64,208 (42,226-103,849) | 21,832 (10,714-36,269) | 186 (24-1,164) | 115,836 (70,795-172,589) | 56,944 (35,616-101,601) |
| 2022 | 251 | 182,257 (126,388-282,830) | 18,558 (12,254-28,142) | 80,639 (49,932-129,988) | 70,612 (44,210-116,348) | 12,151 (7,865-25,755) | 144 (58-314) | 124,145 (86,898-195,646) | 59,737 (31,232-96,546) |
| 2023 | 250 | 210,162 (137,462-270,760) | 21,883 (14,460-29,034) | 90,086 (58,686-116,843) | 86,602 (54,217-113,723) | 11,064 (7,213-15,169) | 115 (32-347) | 158,332 (104,986-215,706) | 49,010 (32,024-69,939) |
| 2024 (Jan-Feb) | 41 | 185,688 (142,858-220,326) | 18,711 (12,308-24,276) | 82,493 (63,282-96,039) | 74,741 (57,437-88,860) | 10,942 (7,396-18,303) | 103 (25-231) | 139,424 (103,703-165,842) | 47,461 (37,540-57,091) |
| OOF 796 | 796 | 187,297 (129,300-272,784) | 19,298 (12,451-28,070) | 79,421 (51,374-119,150) | 72,581 (46,077-112,681) | 13,072 (7,786-30,240) | 131 (32-660) | 131,676 (86,801-200,998) | 53,601 (32,287-93,810) |

Totals by action and segment over the 816 dates (records):

| action | rest of day | day session 08:30-13:20 CT | total | share of all |
|---|---|---|---|---|
| A add | 19,889,866 | 47,293,153 | 67,183,019 | 42.51% |
| C cancel | 18,431,192 | 43,566,966 | 61,998,158 | 39.23% |
| M modify | 4,810,902 | 7,866,662 | 12,677,564 | 8.02% |
| T trade | 3,812,647 | 12,207,251 | 16,019,898 | 10.14% |
| F fill | 40,587 | 124,801 | 165,388 | 0.10% |
| R clear | 1 | 0 | 1 | 0.00% |
| N none | 0 | 0 | 0 | 0.00% |
| all | 46,985,195 | 111,058,833 | 158,044,028 | 100% |

- Extremes of the daily total (counts, no values): lowest 63,170 (2023-06-21), 71,912 (2021-12-17), 72,083 (2021-12-20),
  78,745 (2021-11-19); highest 486,639 (2021-01-04), 381,067 (2022-09-30), 368,602 (2020-12-30), 354,886 (2022-02-28).
- Per-file table (bytes, records, delivered bytes, records by instrument_id) in `file_table_zl_mbp1.tsv`.
- Action codes seen: A, C, M, T, F, R (R once); N never. `T` records are the trade messages; MBP-1 carries the
  top-of-book fields on every record, and `F_LAST` (Databento: last record of an event packet) is set on 142.1M of the
  158.0M records.

## 4. Bars per trade date (ohlcv-1m, v.0)

Bars are emitted only for minutes in which the root traded (bar counts per date are below the minutes the session
holds: the 19:00-07:45 CT evening session plus 08:30-13:20 CT hold at most 765 + 290 = 1,055 minute starts;
observed maximum 1,055, ZS; the 19:00 CT evening open is from E.31's docstring at measure31.py:356-358). Counts per trade date over the 816 dates; no date is missing for any root; 0 bar
records fall outside the 816 dates; `ts_event` never decreases; no duplicate (`ts_event`, `instrument_id`) pair;
`rtype` 33 for every record.

| root | files | bar records | dates | bars per date median (min-max) | p5-p95 | day-session bars median (min-max) |
|---|---|---|---|---|---|---|
| ZL.v.0 | 39 | 733,593 | 816 | 906 (195-1047) | 790-1012 | 290 (178-290) |
| ZS.v.0 | 39 | 786,583 | 816 | 981 (215-1055) | 876-1034 | 290 (215-290) |
| ZM.v.0 | 39 | 679,988 | 816 | 842 (215-1049) | 731-944 | 290 (215-290) |

By calendar year, median (min-max) of bars per trade date:

| root | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| ZL | 988 (921-1044) | 956 (195-1047) | 889 (215-1005) | 892 (215-1012) | 864 (290-958) |
| ZS | 996 (942-1038) | 990 (215-1052) | 987 (215-1055) | 972 (215-1045) | 928 (290-1002) |
| ZM | 862 (757-948) | 859 (215-1012) | 824 (215-1049) | 841 (215-975) | 816 (290-889) |

- Lowest ZL date: 195 bars on 2021-07-06; lowest ZS and ZM: 215 bars on 2021-11-26, 2022-11-25 and 2023-11-24 (the
  day-after-Thanksgiving half days). Day-session bars at the 290-minute maximum on the median date for all three roots.
- The ohlcv files start at 2020-12-01T00:00Z (18:00 CT on 2020-11-30), before the grain evening open at 19:00 CT, so trade
  date 2020-12-01 is complete in the bar files; the last date 2024-02-29 is complete (file ends 2024-03-01T00:00Z).
- Metadata of every bar file: `ohlcv-1m`, `GLBX.MDP3`, `continuous`, `instrument_id`, symbol `<ROOT>.v.0`, version 3.

## 5. Roll handling

Front-month ids (ZL.v.0), by the three sources, all agreeing:

1. DBN header `mappings` of the MBP-1 files (`manifest_facts.json`): UTC-date intervals [start_date, end_date) per id. Merged over
   the 39 files, 63 distinct intervals (adjacent months repeat the same id), 20 distinct instrument ids, 25 days on which the mapped
   id changes, between 2020-12-22 and 2024-02-22.
2. Record data: on each of the 816 trade dates, the id with the most records equals the mapped id (816 of 816, 0
   differ; `facts_misc.json`). 83 of the 158,044,028 records (0.00005%) carry another id than the mapped front, on 14
   dates (list in `agg_zl.json`, `dates_with_multiple_ids`: e.g. 2021-04-07, 2021-04-08, 2021-04-09, 2021-06-29,
   2021-06-30, 2021-12-16, 2022-02-18, 2022-06-24, 2022-06-30, 2022-07-01, 2023-02-16, 2023-04-14, 2023-06-22,
   2024-02-22; the minority id has 1 to 11 records on each of them).
3. ohlcv-1m `ZL_v_0` bars: the same 25 dominant-id changes on the same dates (`agg_bars.json`), 0 trade dates with two
   ids in the bar files.

Instrument-id changes of ZL.v.0 inside the discovery window (trade date on which the dominant id changes; from -> to; ids
are the definition `raw_symbol`s in section 5a):

| trade date | from id (symbol) | to id (symbol) |
|---|---|---|
| 2020-12-22 | 544759 (ZLF1) | 129522 (ZLH1) |
| 2021-02-22 | 129522 (ZLH1) | 352379 (ZLK1) |
| 2021-04-05 | 352379 (ZLK1) | 571589 (ZLN1) |
| 2021-04-07 | 571589 (ZLN1) | 352379 (ZLK1) |
| 2021-04-08 | 352379 (ZLK1) | 571589 (ZLN1) |
| 2021-04-09 | 571589 (ZLN1) | 352379 (ZLK1) |
| 2021-04-12 | 352379 (ZLK1) | 571589 (ZLN1) |
| 2021-06-21 | 571589 (ZLN1) | 379214 (ZLZ1) |
| 2021-06-29 | 379214 (ZLZ1) | 737124 (ZLQ1) |
| 2021-06-30 | 737124 (ZLQ1) | 379214 (ZLZ1) |
| 2021-11-22 | 379214 (ZLZ1) | 96420 (ZLF2) |
| 2021-12-16 | 96420 (ZLF2) | 704007 (ZLH2) |
| 2022-02-18 | 704007 (ZLH2) | 542130 (ZLK2) |
| 2022-04-18 | 542130 (ZLK2) | 565889 (ZLN2) |
| 2022-06-24 | 565889 (ZLN2) | 150640 (ZLZ2) |
| 2022-06-30 | 150640 (ZLZ2) | 288745 (ZLQ2) |
| 2022-07-01 | 288745 (ZLQ2) | 150640 (ZLZ2) |
| 2022-11-21 | 150640 (ZLZ2) | 276652 (ZLF3) |
| 2022-12-19 | 276652 (ZLF3) | 652024 (ZLH3) |
| 2023-02-16 | 652024 (ZLH3) | 548775 (ZLK3) |
| 2023-04-14 | 548775 (ZLK3) | 673494 (ZLN3) |
| 2023-06-22 | 673494 (ZLN3) | 319302 (ZLZ3) |
| 2023-11-20 | 319302 (ZLZ3) | 391369 (ZLF4) |
| 2023-12-18 | 391369 (ZLF4) | 330370 (ZLH4) |
| 2024-02-22 | 330370 (ZLH4) | 567056 (ZLK4) |

The changes are not a clean one-way calendar. April 2021: the front goes ZLK1 -> ZLN1 on 04-05, back to ZLK1 on 04-07,
to ZLN1 on 04-08, back on 04-09 and to ZLN1 again on 04-12 (5 changes). One-day excursions to the August contract:
ZLQ1 on 2021-06-29 and ZLQ2 on 2022-06-30 (each leaves and returns the next date, 4 changes), after the switches
ZLN1 -> ZLZ1 (2021-06-21) and ZLN2 -> ZLZ2 (2022-06-24). So 9 of the 25 changes belong to these back-and-forth or
one-day patterns, the other 16 are one-way. The September and October contracts (ZLU, ZLV) are never the front. I list
the facts and draw no conclusion on how to treat them.

5a. Definition files (Z4): the 20 front ids resolve to ZL outright futures (`asset` ZL, `instrument_class` F), all with
`min_price_increment` 10,000,000 (= 0.01 in 1e-9 price units, the 0.01 cent/lb tick, `cal33.tick` docstring, cal33.py:408-412).

| instrument_id | raw_symbol | expiration (UTC) | min_price_increment (1e-9 units) | definition records |
|---|---|---|---|---|
| 544759 | ZLF1 | 2021-01-14 18:01Z | 10,000,000 | 40 |
| 129522 | ZLH1 | 2021-03-12 18:01Z | 10,000,000 | 88 |
| 352379 | ZLK1 | 2021-05-14 17:01Z | 10,000,000 | 142 |
| 571589 | ZLN1 | 2021-07-14 17:01Z | 10,000,000 | 196 |
| 737124 | ZLQ1 | 2021-08-13 17:01Z | 10,000,000 | 220 |
| 379214 | ZLZ1 | 2021-12-14 18:01Z | 10,000,000 | 328 |
| 96420 | ZLF2 | 2022-01-14 18:01Z | 10,000,000 | 352 |
| 704007 | ZLH2 | 2022-03-14 17:01Z | 10,000,000 | 406 |
| 542130 | ZLK2 | 2022-05-13 17:01Z | 10,000,000 | 454 |
| 565889 | ZLN2 | 2022-07-14 17:01Z | 10,000,000 | 508 |
| 288745 | ZLQ2 | 2022-08-12 17:01Z | 10,000,000 | 532 |
| 150640 | ZLZ2 | 2022-12-14 18:01Z | 10,000,000 | 640 |
| 276652 | ZLF3 | 2023-01-13 18:01Z | 10,000,000 | 664 |
| 652024 | ZLH3 | 2023-03-14 17:01Z | 10,000,000 | 718 |
| 548775 | ZLK3 | 2023-05-12 17:01Z | 10,000,000 | 766 |
| 673494 | ZLN3 | 2023-07-14 17:01Z | 10,000,000 | 820 |
| 319302 | ZLZ3 | 2023-12-14 18:01Z | 10,000,000 | 952 |
| 391369 | ZLF4 | 2024-01-12 18:01Z | 10,000,000 | 663 |
| 330370 | ZLH4 | 2024-03-14 17:01Z | 10,000,000 | 704 |
| 567056 | ZLK4 | 2024-05-14 17:01Z | 10,000,000 | 704 |

Z4 notes: 39 files, 1,810,372 records in total (3 symbols parents ZM.FUT, ZS.FUT, ZL.FUT; ZM and ZS records are in the same
files; I counted only); the manifest flags `delivered_bytes_equal_quoted_billable` as not passed for 35 of the 39 Z4 files
and `metadata_partial_empty` for some (manifest `checks`, `manifest_facts.json` field `checks_failed`; no other series has a
failed check). I draw no conclusion; E.33 built its definition cache from these files regardless (data33.py:218-256).

How E.33's code handled rolls (file:line):

- Front lookup: `cal33._mappings` (cal33.py:146-152) merges the DBN header mappings of the Z-series; `cal33._front_on`
  (cal33.py:155-158) = `measure31.instrument_on` (measure31.py:355-361), UTC date D inside [start, end); more than one id
  raises `Refused`. `cal33.fronts(D)` (cal33.py:171-174) returns ZM, ZS, ZL ids per trade date.
- Record filter: `feat33.stream_mbp1` keeps only `rec["instrument_id"] == iid` for the day's front (feat33.py:563), so the
  83 non-front records above are dropped (ZL stream called at feat33.py:630).
- Segments: `cal33._segments` / `segment_id` (cal33.py:181-197): a new segment starts when the (ZM, ZS, ZL) front tuple
  differs from the previous trade date's; features that need history stop at a segment boundary
  (`prev_same_seg`, build_features33.py:121; feat33.py:818, 855, 904, 946-960).
- Exclusions: `cal33._exclusions` (cal33.py:207-235) marks the ZM front's roll date and the date after it
  (`REASON_ROLL`, `REASON_AFTER_ROLL`) plus calendar reasons, cross-checked against `measure31.roll_reasons`
  (measure31.py:364-387). It uses the ZM front only; a ZL front change does not exclude a date by itself.
- Chained lookbacks: feat33.py:762 ("pooled across dates (chained across rolls)"); F4.7 uses dates on which the ZM front was
  the same (feat33.py:867-868, 911).

## 6. Disk and memory

On disk (bytes, from the files and the manifest; `ls`, `manifest_facts.json`):

| set | files | bytes | decompressed (delivered) bytes | note |
|---|---|---|---|---|
| ZL MBP-1 Z3 | 39 + manifest | 3,656,692,936 (3.40 GiB) + manifest 7,305,389 | 12,643,717,280 (80 B x 158,046,466; compression 3.46x) | largest month 2023-03: 121,829,001 B, 5,318,297 records, 425,463,760 B; smallest month 2,823,836 records (2023-12) |
| ZS MBP-1 Z2 (E.31, for scale) | 39 | 5,692,759,621 | 19,853,542,560 (248,169,282 records) | 3.49x |
| ZM MBO Z1 (E.31) | 39 | 14,842,362,471 | 39,149,286,512 (699,094,402 records x 56 B) | 2.64x; largest month 2021-05: 24,586,449 records, 526,159,001 B |
| Z4 definitions | 39 | 42,892,820 | 941,393,440 (1,810,372 x 520 B) | 21.9x |
| ohlcv-1m ZL / ZS / ZM (discovery span) | 39 each | 10,229,471 / 10,314,516 / 8,701,901 | 56 B x 733,593 / 786,583 / 679,988 records | tiny |
| E.33 ZL split store (derived/e33/split/ZL) | 816 .npy + 816 .DONE (1,633 entries incl. manifest) | 12 GB (`du -sh`; 158,044,028 x 79 B = 12.49 GB) | uncompressed .npy | ZS split: 19 GB |

Free disk on /mnt/large-storage: 619.5 GiB available of 937 GiB (665,164,488,704 B; 31% used) on 2026-10-29 12:23 PDT.

Memory, measured (`/usr/bin/time -v`, `nice -n 10`, one job, databento 0.82.0 in the project uv environment, files in the OS
page cache; `measure_*.out/.err`, `time_2021-06.*`):

| run | records | in-memory array | peak resident set | wall time |
|---|---|---|---|---|
| whole month in memory (`to_ndarray()`), 2023-03 (largest month) | 5,318,297 | 425,463,760 B | 954,380 kB (about 2.2x the array: compressed input plus the array plus Python) | 0.87 s |
| streaming, 1M-record chunks, 2023-03 | 5,318,297 | 80,000,000 B per chunk | 278,144 kB | 0.73 s |
| streaming + the count script (unique, bincount), 2021-06 | 4,286,776 | 1M chunk | 403,084 kB | 1.26 s |
| all 39 files counted in sequence | 158,046,466 | 1M chunk | not separately timed (one file at a time; the 2021-06 line is representative) | 39.4 s decode+count |

E.33's split of the 39 ZL files shows 68 s between the first and last "done" stamps (split33_ZL.log, 14:57:23 to 14:58:31; includes the .npy writes).
One ZL trade date in the E.33 split averages 188,782 records x 79 B = 14.9 MB (median), peak day 486,639 x 79 B = 38 MB.
The full 12.5 GB split store does not fit in the 14 GB RAM with other work; E.33 read it per date.

ZL MBO estimate for both windows (an estimate, not a measurement; no ZL MBO is owned and none was read):

- Ratio assumed: E.32b's cost census (recs lines 639 and 643) puts ZL MBO at USD 0.4995 a month and ZL MBP-1 at USD 0.5432 a
  month, same price per billable byte, so MBO delivered bytes = 0.4995 / 0.5432 = 0.9196 x MBP-1 delivered bytes; MBO
  records are 56 B, MBP-1 80 B, hence MBO records = 0.9196 x 80 / 56 = 1.314 x MBP-1 records. The census numbers are E.32b's
  (2025 sample months, scaled from MBP-1 there, recs line 639), not re-derived here. On-disk compression: E.31's measured
  ZM MBO ratio, 2.64x (39,149,286,512 / 14,842,362,471), applied to ZL (the measured ZL MBP-1 ratio is 3.46x; I use the
  ZM MBO ratio because the schema is MBO).
- Discovery window (39 months, 2020-12..2024-02): about 207.6M MBO records, 11.63 GB delivered, 4.41 GB on disk
  (3.36 GB at 3.46x).
- Test window (43 months, 2017-05..2020-11, E.32b's month count): the monthly volume of that window is unknown and was
  not looked at; assuming the discovery monthly mean (5.32M MBO records, 298 MB delivered), about 228.8M records,
  12.82 GB delivered, 4.86 GB on disk. If ZL's 2017-2020 months were lighter or heavier the estimate scales linearly.
- Decode memory per month: the largest discovery MBP-1 month implies about 0.92 x 425 MB = 391 MB of MBO array and, at the
  measured 2.2x peak ratio, about 0.9 GB resident for a whole-month decode; streaming in chunks stays near 0.3 GB.
- Cost, not spend: E.32b recs 4.5(c) gives USD 19.48 (discovery MBO), 21.48 (test MBO), 23.36 (test MBP-1); nothing was bought or quoted here.

## 7. What E.33's pipeline can reuse for ZL as the traded leg

E.33 traded ZM (MBO book, 0.10 USD per short ton tick = USD 10, fee 0.528 ticks). ZS and ZL were MBP-1 context legs.
All paths are `reports/stage_e33_briefs/work/pipeline/`.

| module (lines) | what it does | unchanged on ZL as traded leg? | what must change |
|---|---|---|---|
| guard33.py (385) | data guard P1.2: seals, window dates, allowlist of the 156 discovery files, derived stores | partly | the allowlist is exactly the 156 discovery files (`N_DISCOVERY_FILES` guard33.py:55, `_allowed_files` guard33.py:176-186, `discovery_manifest` :159-173); the 117 ohlcv-1m files are not among them and would be new entries (my guard34 `ALLOWED` shows the shape). Date rules (`check_date` guard33.py:269-282, `DISC_FIRST/DISC_LAST` :72) and the seal checks (`check_path` :285-322, `check_records` :325-) stay as they are. A ZL MBO purchase or the test window needs a new guard (E.32b recs 4.5(c), P9) |
| split33.py (202) / data33.py (285) | per-date split of ZS/ZL MBP-1 into compact .npy (MBP1_SPLIT 79 B), definitions cache, `load_mbp1`, `window` | yes for ZL MBP-1 | nothing for ZL: `ROOT_SERIES` already has ZL -> Z3 (data33.py:56) and the 816-date store exists (12 GB). A ZL MBO split would be a new module on the model of E.31's ZM MBO split (`measure31.MBO_COMPACT`) |
| cal33.py (467) | 816 trade dates, burn-in/OOF, fronts, segments, exclusions, USDA releases, ZM limits, tick | mostly | `_exclusions` marks ZM-front roll dates only (cal33.py:207-235): a ZL program needs its own roll rule (decision for the lead). `limits()`/`front_definition` default to ZM (cal33.py:333-362; the ZM limit-proximity rule). `tick("ZL")` already works (cal33.py:408-416: 10_000_000). USDA release table (cal33.py:259-315) is soy-complex-wide; whether it matters for ZL is a design question |
| feat33.py (1148) / build_features33.py (341) | P4 features at the minute marks from ZM MBO plus ZS, ZL MBP-1; sigma per root; 59 S5 features | partly | `stream_mbp1(.., "zl")` (feat33.py:558-617, 630) already builds ZL top-of-book/trade states from MBP-1 and `_day/<D>.json` holds `sigma_zl` (build_features33.py:209). The feature set is ZM-centred (ZM_TICK_USD 0.10, feat33.py:87; sd_e in ZM ticks, feat33.py:820; ZM as target in the crush features). F10 (order-book state at 5 min+) and F09 (lead-lag/relative value into ZL) are new feature definitions on this skeleton (Axis, `_asof`, pass-1/pass-2 split are reusable) |
| lab33.py (859) / build_labels33.py (353) | executable prices (P3.2), FH/TB labels (P3.3-3.4), exclusions, weights, per-minute trade outcomes | no, needs a ZL book | `replay` builds the book from ZM MBO records with `mbo_book31.Book` (lab33.py:215-239; build_labels33.py:165-167 uses `fronts(d)["ZM"]`, `tick=cal33.tick("ZM")` at :102); there is no ZL MBO. A ZL `BookHistory` (t, bid, ask, good; lab33.py:107-130) can be built from MBP-1 `F_LAST` records' `bid_px_00/ask_px_00` the way `feat33.stream_mbp1` does (feat33.py:559-572), with the READING FA-4 bad-book rule. `FEE_TICKS = 0.528` (lab33.py:48, P0.3: USD 5.28 / USD 10) becomes 5.28 / 6.00 = 0.88 ticks for ZL; the executable price model reads the book, so the spread comes from the data; the grid `LAST_GRID_OFFSET` 277 (lab33.py:51) and the horizons are tied to the 08:35-13:15 open-time axis, the same CBOT session for ZL |
| cost33.py (420) | per-firm fees, market round trip, trade-through limit entry, per-fill accounting | partly | `ZM_TICK_USD = 10.0` (cost33.py:39) and the fee conversion `usd / ZM_TICK_USD` (cost33.py:105), the E.28 A2 firm files' `products.ZM` (cost33.py:101) and the P6.4 firm list `PROTOCOL_FEE_TICKS` (cost33.py:55-57, in ZM ticks) all change to ZL (tick USD 6.00; Topstep 5.28 USD = 0.88 ticks). The fill functions (`market_round_trip` 252, `limit_entry_through` 335) take touch/trade arrays in integer ticks and are product-neutral. Trades arrays for ZL would come from MBP-1 `T` records |
| search33.py (997) / run_search33.py (377) / select33.py (468) | folds, LOGIT/LGBM, EV rule, simulation, P6.2 stats, P8 selection | yes in structure | they read features and labels through the INTERFACE.md 4.1/4.2 tables; the volatility terciles use `sigma_zm` from `_day` (search33.py:338-342, select33.py:118, 422-424): switch to `sigma_zl`. Thresholds in select33 are at N = 838 for E.33's T_OOF 796; the ZL program's thresholds are E.32b recs 4.4 (not changed here) |
| synth33.py (757) / run_proofs33.py (388) | synthetic null/planted proofs of the search | partly | price model and labels are written in ZM ticks (synth33.py docstring); needs ZL tick, vol and the new feature set |
| check33.py (175) / g6_33.py (169) | independent raw-count check; clock report | yes | check33.py `split ZL` counts the raw files per date (check33.py docstring) and could be rerun; g6_33 already covers ZL |

Bar inputs: E.33 did not use ohlcv-1m. The 39 ZL/ZS/ZM bar files per root are directly readable (section 4); no module reads
them yet, so F09 bar features need a new loader (guard entries added as in guard34 `ALLOWED`).

## 8. Not done, limits, and items for the lead

- No judgment was made on roll handling, exclusions or fee/tick design; sections 5 and 7 list facts and code locations.
- Databento field meanings (`ts_event`, `ts_recv`, `ts_in_delta`, `.v.0` rule) are stated from general knowledge and the
  E.33 code comments, marked [unverified]; no web page was fetched (no web in this brief).
- E.33's per-date counts were not available in its logs (only totals); the split manifest `derived/e33/split/ZL/split_manifest.json`
  was not opened (it lies outside this brief's allowed data), so per-date totals here come from my own decode and match
  E.33's grand total and outside count exactly.
- Test-window volume per month for ZL MBO is unknown (sealed); the 43-month estimate assumes the discovery monthly mean.
- Peak memory was measured on the two months named above, not on every month.
