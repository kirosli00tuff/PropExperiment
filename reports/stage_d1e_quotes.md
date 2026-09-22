# Stage D.1e Tasks 4a/4b: MES availability and Databento cost quotes

Generated 2026-09-22T01:12:19.292514+00:00 · session `stage-D.1e-2026-09-21` · **spend this run: $0.00** (quotes only, nothing downloaded).

Gate note: configured external ledger (PosixPath('/mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl'),) absent; used the relocated copy /mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl (read-only). data/config.py NOT modified.

## 1. Availability (4a)

- `metadata.get_dataset_range("GLBX.MDP3")` -> `{'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z', 'schema': {'mbo': {'start': '2017-05-21T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'mbp-1': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'mbp-10': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'tbbo': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'trades': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'bbo-1s': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'bbo-1m': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'ohlcv-1s': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'ohlcv-1m': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'ohlcv-1h': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'ohlcv-1d': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'definition': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'statistics': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'status': {'start': '2010-06-06T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'cmbp-1': {'start': '2017-05-21T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'cbbo-1s': {'start': '2017-05-21T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}, 'cbbo-1m': {'start': '2017-05-21T00:00:00.000000000Z', 'end': '2026-09-21T17:08:30.787880000Z'}}}`
- `metadata.list_schemas("GLBX.MDP3")` -> 17 schemas

| schema | present |
|---|---|
| `ohlcv-1m` | yes |
| `mbo` | yes |
| `mbp-10` | yes |
| `trades` | yes |
| `definition` | yes |
| `statistics` | yes |

### First date MES exists

| symbol | first `d0` | intervals | instrument changes per year |
|---|---|---|---|
| `MES.v.0` | 2019-04-01 | 25 | 2019:3, 2020:4, 2021:4, 2022:4, 2023:4, 2024:4, 2025:1 |
| `MES.c.0` | 2019-04-01 | 25 | 2019:3, 2020:4, 2021:4, 2022:4, 2023:4, 2024:4, 2025:1 |

- `MES.v.0` instrument `7849` (2019-04-01..2019-06-17) -> raw symbol(s) ['DNMH929 C35', 'MESM9']
- `MES.v.0` instrument `7859` (2019-06-17..2019-09-16) -> raw symbol(s) ['MESU9']
- `MES.c.0` instrument `7849` (2019-04-01..2019-06-23) -> raw symbol(s) ['DNMH929 C35', 'MESM9']
- `MES.c.0` instrument `7859` (2019-06-23..2019-09-22) -> raw symbol(s) ['MESU9']

### Dataset condition 2019-04-01 to 2025-04-01

| year | available | degraded |
|---|---|---|
| 2019 | 236 | 0 |
| 2020 | 309 | 5 |
| 2021 | 312 | 1 |
| 2022 | 311 | 1 |
| 2023 | 313 | 0 |
| 2024 | 313 | 1 |
| 2025 | 78 | 0 |

Dates not `available`: **8**

| date | condition | last modified |
|---|---|---|
| 2020-02-27 | degraded | 2026-08-30 |
| 2020-02-28 | degraded | 2026-09-01 |
| 2020-05-05 | degraded | 2026-08-23 |
| 2020-06-30 | degraded | 2026-08-23 |
| 2020-07-01 | degraded | 2026-08-29 |
| 2021-12-05 | degraded | 2026-09-01 |
| 2022-01-02 | degraded | 2026-08-31 |
| 2024-09-18 | degraded | 2026-08-29 |

### Boundary

The current raw data begins at UTC 2025-04-01T00:00 (range=2025-04-01_2025-05-01), so the extension's last chunk must END at 2025-04-01 (exclusive end), i.e. range=2025-03-01_2025-04-01. That gives no overlap and no gap in UTC time.

Trade-date caveat: The 2025-03-31 22:00-24:00 UTC bars inside range=2025-03-01_2025-04-01 belong to CME trade date 2025-04-01 -- the research parquet's first trade date, which currently starts late and is missing its 17:00-19:00 CT open. Extending the raw data would therefore complete an existing research trade date as well as add new ones. How D.1f treats those bars (complete the existing first trade date, or drop it and start the extended series at the first fully covered trade date) is a LEAD decision, not made here.

## 2. ohlcv-1m extension quote (4b.5)

- range: **2019-04-01 .. 2025-04-01** (end exclusive)
- monthly chunks: **72** (72 priced)
- **sum of chunk quotes: $7.5862**, 116,365,984 billable bytes (111.0 MiB)
- single whole-range quote: $7.5862, 116,365,984 billable bytes
- whole minus sum: $0.0000, 0 bytes

<details><summary>Per-chunk quotes</summary>

| chunk | ledger idx | usd | billable bytes |
|---|---|---|---|
| 2019-04-01..2019-05-01 | 72 | $0.0000 | 0 |
| 2019-05-01..2019-06-01 | 73 | $0.0971 | 1,489,488 |
| 2019-06-01..2019-07-01 | 74 | $0.0983 | 1,508,024 |
| 2019-07-01..2019-08-01 | 75 | $0.1091 | 1,673,000 |
| 2019-08-01..2019-09-01 | 76 | $0.1089 | 1,671,152 |
| 2019-09-01..2019-10-01 | 77 | $0.1029 | 1,577,688 |
| 2019-10-01..2019-11-01 | 78 | $0.1132 | 1,735,832 |
| 2019-11-01..2019-12-01 | 79 | $0.1005 | 1,542,016 |
| 2019-12-01..2020-01-01 | 80 | $0.0989 | 1,516,928 |
| 2020-01-01..2020-02-01 | 81 | $0.1075 | 1,649,536 |
| 2020-02-01..2020-03-01 | 82 | $0.0986 | 1,512,728 |
| 2020-03-01..2020-04-01 | 83 | $0.1036 | 1,589,784 |
| 2020-04-01..2020-05-01 | 84 | $0.1047 | 1,605,352 |
| 2020-05-01..2020-06-01 | 85 | $0.1038 | 1,592,640 |
| 2020-06-01..2020-07-01 | 86 | $0.1092 | 1,675,072 |
| 2020-07-01..2020-08-01 | 87 | $0.1134 | 1,738,744 |
| 2020-08-01..2020-09-01 | 88 | $0.1051 | 1,611,680 |
| 2020-09-01..2020-10-01 | 89 | $0.1088 | 1,669,024 |
| 2020-10-01..2020-11-01 | 90 | $0.1092 | 1,674,848 |
| 2020-11-01..2020-12-01 | 91 | $0.1033 | 1,584,128 |
| 2020-12-01..2021-01-01 | 92 | $0.1086 | 1,665,384 |
| 2021-01-01..2021-02-01 | 93 | $0.0991 | 1,519,504 |
| 2021-02-01..2021-03-01 | 94 | $0.0988 | 1,515,976 |
| 2021-03-01..2021-04-01 | 95 | $0.1148 | 1,761,424 |
| 2021-04-01..2021-05-01 | 96 | $0.1074 | 1,646,904 |
| 2021-05-01..2021-06-01 | 97 | $0.1042 | 1,598,912 |
| 2021-06-01..2021-07-01 | 98 | $0.1096 | 1,680,784 |
| 2021-07-01..2021-08-01 | 99 | $0.1094 | 1,678,544 |
| 2021-08-01..2021-09-01 | 100 | $0.1111 | 1,704,416 |
| 2021-09-01..2021-10-01 | 101 | $0.1099 | 1,685,656 |
| 2021-10-01..2021-11-01 | 102 | $0.1058 | 1,622,824 |
| 2021-11-01..2021-12-01 | 103 | $0.1089 | 1,669,864 |
| 2021-12-01..2022-01-01 | 104 | $0.1106 | 1,696,072 |
| 2022-01-01..2022-02-01 | 105 | $0.1051 | 1,612,576 |
| 2022-02-01..2022-03-01 | 106 | $0.0999 | 1,532,160 |
| 2022-03-01..2022-04-01 | 107 | $0.1161 | 1,780,800 |
| 2022-04-01..2022-05-01 | 108 | $0.1003 | 1,538,880 |
| 2022-05-01..2022-06-01 | 109 | $0.1104 | 1,693,440 |
| 2022-06-01..2022-07-01 | 110 | $0.1100 | 1,686,720 |
| 2022-07-01..2022-08-01 | 111 | $0.1049 | 1,609,440 |
| 2022-08-01..2022-09-01 | 112 | $0.1159 | 1,777,440 |
| 2022-09-01..2022-10-01 | 113 | $0.1095 | 1,679,888 |
| 2022-10-01..2022-11-01 | 114 | $0.1062 | 1,629,600 |
| 2022-11-01..2022-12-01 | 115 | $0.1089 | 1,670,536 |
| 2022-12-01..2023-01-01 | 116 | $0.1056 | 1,619,408 |
| 2023-01-01..2023-02-01 | 117 | $0.1051 | 1,612,800 |
| 2023-02-01..2023-03-01 | 118 | $0.0999 | 1,532,104 |
| 2023-03-01..2023-04-01 | 119 | $0.1156 | 1,773,968 |
| 2023-04-01..2023-05-01 | 120 | $0.0994 | 1,524,880 |
| 2023-05-01..2023-06-01 | 121 | $0.1150 | 1,763,384 |
| 2023-06-01..2023-07-01 | 122 | $0.1094 | 1,678,768 |
| 2023-07-01..2023-08-01 | 123 | $0.1044 | 1,600,816 |
| 2023-08-01..2023-09-01 | 124 | $0.1158 | 1,776,936 |
| 2023-09-01..2023-10-01 | 125 | $0.1043 | 1,600,536 |
| 2023-10-01..2023-11-01 | 126 | $0.1113 | 1,706,712 |
| 2023-11-01..2023-12-01 | 127 | $0.1088 | 1,668,240 |
| 2023-12-01..2024-01-01 | 128 | $0.1003 | 1,538,768 |
| 2024-01-01..2024-02-01 | 129 | $0.1101 | 1,689,016 |
| 2024-02-01..2024-03-01 | 130 | $0.1048 | 1,607,648 |
| 2024-03-01..2024-04-01 | 131 | $0.1009 | 1,548,288 |
| 2024-04-01..2024-05-01 | 132 | $0.1108 | 1,699,712 |
| 2024-05-01..2024-06-01 | 133 | $0.1144 | 1,755,432 |
| 2024-06-01..2024-07-01 | 134 | $0.1001 | 1,535,800 |
| 2024-07-01..2024-08-01 | 135 | $0.1140 | 1,749,328 |
| 2024-08-01..2024-09-01 | 136 | $0.1104 | 1,693,440 |
| 2024-09-01..2024-10-01 | 137 | $0.1053 | 1,615,544 |
| 2024-10-01..2024-11-01 | 138 | $0.1159 | 1,777,328 |
| 2024-11-01..2024-12-01 | 139 | $0.1036 | 1,589,616 |
| 2024-12-01..2025-01-01 | 140 | $0.1049 | 1,608,936 |
| 2025-01-01..2025-02-01 | 141 | $0.1083 | 1,661,520 |
| 2025-02-01..2025-03-01 | 142 | $0.0999 | 1,532,104 |
| 2025-03-01..2025-04-01 | 143 | $0.1062 | 1,629,544 |

</details>

## 3. Auxiliary schemas (4b.6)

The pipeline needs only the paid schema ohlcv-1m, plus free metadata and symbology. No auxiliary paid schema was quoted because none is used.

- `data/adapter.py:43` — `OHLCV_1M = "ohlcv-1m"` — the only schema constant in the data package
- `data/pull_mes.py:83, 95` — `RequestParams(DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS, ...)` — the only two RequestParams construction sites outside tests; both pass OHLCV_1M
- `data/adapter.py:85` — `def fetch_range(gate, client, params, root=VENDOR_ROOT, note='')` — the only download path; its sole non-test caller is data/pull_mes.py:104, which passes an ohlcv-1m params
- `data/build_mes_bars.py:41-53` — `client.metadata.get_dataset_condition(dataset=DATASET, ...)` — the vendor_degraded_day source; free metadata, cached to data/vendor/databento/condition/ and never rewritten
- `data/adapter.py:162-180` — `client.symbology.resolve(... stype_out='instrument_id' / 'raw_symbol')` — roll boundaries; the module docstring states symbology is metadata-only and free, so it never touches the spend gate
- `data/pull_mes.py:58` — `client.metadata.get_dataset_range(dataset=DATASET)` — free metadata, printed at startup
- `data/bars.py:17, 127` — `vendor_degraded_day flag column` — consumes the cached condition list; buys nothing
- `data/tick_crosscheck.py:1-10, 40, 107` — `MLCE_VENDOR / f'date={day}' / 'MES_c_0.trades.dbn.zst'` — the only use of the trades schema anywhere; it reads MLCryptoEngine's already-paid-for files IN PLACE, read-only, and never buys trades on this account
- `data/validate.py:7-9` — `ts_recv ordering check applies to the tick data (trades / mbp-10)` — a comment about borrowed tick data, not a purchase by this pipeline

Extending ohlcv-1m back before 2025-04-01 needs exactly one paid schema. get_dataset_condition and symbology.resolve must be re-run over the extended range so vendor_degraded_day and the roll boundaries cover it, but both are free.

## 4. Order book (4b.7 to 4b.9)

RTH = 08:30 to 15:10 America/Chicago; full trade date = 17:00 CT previous calendar day to 16:00 CT. Offsets computed with `zoneinfo` (CDT/CST differ).

| day | CT offset | RTH UTC | front month | mbo RTH | mbo full | mbp-10 RTH | mbp-10 full |
|---|---|---|---|---|---|---|---|
| 2025-05-14 | UTC-5 | 13:30–20:10Z | None | $0.7532 | $0.9539 | $1.1464 | $1.4333 |
| 2025-08-13 | UTC-5 | 13:30–20:10Z | None | $0.4710 | $0.5932 | $0.7060 | $0.8741 |
| 2025-11-12 | UTC-6 | 14:30–21:10Z | None | $0.8302 | $1.0480 | $1.3091 | $1.6405 |
| 2026-02-11 | UTC-6 | 14:30–21:10Z | None | $1.2413 | $1.5307 | $1.9572 | $2.3963 |
| 2026-04-15 | UTC-5 | 13:30–20:10Z | None | $0.6222 | $0.8740 | $0.9254 | $1.2988 |

Billable bytes per day:

| day | mbo RTH | mbo full | mbp-10 RTH | mbp-10 full |
|---|---|---|---|---|
| 2025-05-14 | 428.5 MiB | 542.7 MiB | 2.29 GiB | 2.87 GiB |
| 2025-08-13 | 267.9 MiB | 337.4 MiB | 1.41 GiB | 1.75 GiB |
| 2025-11-12 | 472.3 MiB | 596.2 MiB | 2.62 GiB | 3.28 GiB |
| 2026-02-11 | 706.2 MiB | 870.8 MiB | 3.91 GiB | 4.79 GiB |
| 2026-04-15 | 354.0 MiB | 497.2 MiB | 1.85 GiB | 2.60 GiB |

Symbol form used (fallback chain continuous -> raw front month -> parent):

- mbo/rth: continuous MES.v.0 x5
- mbo/full: continuous MES.v.0 x5
- mbp-10/rth: continuous MES.v.0 x5
- mbp-10/full: continuous MES.v.0 x5

### Means and linear scalings

| series | days sampled | mean $/day | mean bytes/day | 20 d | 40 d | 60 d | 120 d |
|---|---|---|---|---|---|---|---|
| mbo/rth | 5 | $0.7836 | 445.8 MiB | $15.6713 | $31.3427 | $47.0140 | $94.0280 |
| mbo/full | 5 | $1.0000 | 568.9 MiB | $19.9993 | $39.9987 | $59.9980 | $119.9960 |
| mbp-10/rth | 5 | $1.2088 | 2.42 GiB | $24.1766 | $48.3532 | $72.5299 | $145.0597 |
| mbp-10/full | 5 | $1.5286 | 3.06 GiB | $30.5722 | $61.1443 | $91.7165 | $183.4330 |

Every 20/40/60/120-day figure is a LINEAR SCALING of the five-day mean, not a quote. See total_for_days() in strategy/research/_d1e_quotes.py.

### 20-day contiguous block quotes (linearity check)

Range 2025-10-01T00:00:00Z .. 2025-10-29T00:00:00Z.

| schema | block quote | scaled 20 x full-day mean | ratio |
|---|---|---|---|
| mbo | $22.0305 | $19.9993 | 1.102 |
| mbp-10 | $33.4886 | $30.5722 | 1.095 |

## 5. Disk footprint (4b.10)

Measured zstd ratio: 530,123 bytes on disk / 1,622,824 billable = **0.3267** (`data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0/range=2025-04-01_2025-05-01.dbn.zst`).

Measured on one month of MES ohlcv-1m. Book schemas compress differently, so every mbo / mbp-10 disk figure below is an estimate, not a measurement.

Free space: main drive ~368 GB, `/mnt/large-storage` ~770 GB.

| dataset | billable | est. on disk | quality | drive |
|---|---|---|---|---|
| ohlcv-1m extension 2019-04-01..2025-04-01 | 111.0 MiB | 36.3 MiB | measured ratio | main drive, beside the existing raw files |
| mbo rth x20 days | 8.71 GiB | 2.84 GiB | ESTIMATE | /mnt/large-storage |
| mbo rth x40 days | 17.41 GiB | 5.69 GiB | ESTIMATE | /mnt/large-storage |
| mbo rth x60 days | 26.12 GiB | 8.53 GiB | ESTIMATE | /mnt/large-storage |
| mbo rth x120 days | 52.24 GiB | 17.06 GiB | ESTIMATE | /mnt/large-storage |
| mbo full x20 days | 11.11 GiB | 3.63 GiB | ESTIMATE | /mnt/large-storage |
| mbo full x40 days | 22.22 GiB | 7.26 GiB | ESTIMATE | /mnt/large-storage |
| mbo full x60 days | 33.33 GiB | 10.89 GiB | ESTIMATE | /mnt/large-storage |
| mbo full x120 days | 66.66 GiB | 21.78 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 rth x20 days | 48.35 GiB | 15.80 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 rth x40 days | 96.71 GiB | 31.59 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 rth x60 days | 145.06 GiB | 47.39 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 rth x120 days | 290.12 GiB | 94.77 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 full x20 days | 61.14 GiB | 19.97 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 full x40 days | 122.29 GiB | 39.95 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 full x60 days | 183.43 GiB | 59.92 GiB | ESTIMATE | /mnt/large-storage |
| mbp-10 full x120 days | 366.87 GiB | 119.84 GiB | ESTIMATE | /mnt/large-storage |

**Recommendation**

- ohlcv-1m extension: main drive, data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0/, beside the existing monthly chunks -- it is small and the bar pipeline reads it by path
- mbo / mbp-10: /mnt/large-storage -- bulk order-book data only; nothing secret is ever written there, and the sealed holdout stays on the main drive

## 6. Ledger accounting (4b.11)

- `ledger/databento_spend.jsonl`: **72 lines before, 167 after** (95 added)
- new line indices (0-based): 72..166
- events on new lines: {'quote': 95}
- sum of `usd` on new lines: $0.0000
- `shared_cumulative_usd`: 84.006048 (expected 84.006048)
- files under `data/vendor`: 17 before, 17 after; added []

| check | result |
|---|---|
| every_new_line_is_a_quote | PASS |
| every_new_line_usd_is_zero | PASS |
| no_commit_settle_or_refused_added | PASS |
| no_new_vendor_file | PASS |
| new_line_count_matches_quote_records | PASS |
| shared_cumulative_unchanged | PASS |
| session_cumulative_is_zero | PASS |

## 7. Endpoints

Called (all free): `metadata.get_dataset_range`, `metadata.list_schemas`, `metadata.list_datasets`, `metadata.get_dataset_condition`, `metadata.get_cost`, `metadata.get_billable_size`, `symbology.resolve`

Not called:
- metadata.get_record_count (optional, not needed)
- every method under the two guarded billable namespaces (replaced by a raising guard)
- data.adapter.fetch_range, SpendGate.authorize, SpendGate.commit, SpendGate.settle

