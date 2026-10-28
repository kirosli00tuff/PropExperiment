# Feature builder probe (Stage E.33, FeatureCoder; P5 probe bullet)

Code: build_features33.py / feat33.py, code_sha12 c22b0a50f4cd (manifest in
DERIVED/features/c22b0a50f4cd/manifest.json). Times from `date` and the builder's DONE records,
2026-10-28 PDT. Machine shared with other jobs: load average 6.7-8.4 during these runs.

## Probe dates (P5: median, p90 and maximum ZM message-count dates of data facts section 5)

Rule from reports/stage_e32_data_facts.md section 5 (record counts only, both ZM instruments):
median 2022-02-15, p90 2022-07-27, max 2021-05-07. Each date's pass 1 (load + stream, the event
loop) ran in a fresh process at nice 10, written to DERIVED/probes/features_c22b0a50f4cd/
(02:16:36-02:17:09 PDT).

| Date (rule) | ZM / ZS / ZL records | Wall s | Load s | Stream s | Peak RSS MB |
|---|---|---|---|---|---|
| 2022-02-15 (median) | 827,199 / 261,255 / 226,052 | 7.55 | 4.42 | 3.12 | 367.2 |
| 2022-07-27 (p90) | 1,139,174 / 338,500 / 176,407 | 10.90 | 4.04 | 6.85 | 578.2 |
| 2021-05-07 (max) | 1,748,582 / 460,443 / 164,964 | 11.98 | 4.47 | 7.51 | 589.2 |

"Load" in a fresh process includes the first-call guard and manifest checks of guard33/data33;
in a pool process those run once. Pass 2 (features of one date from 22 pass-1 tables) took
0.13-0.26 s per date in the B3 runs.

## Pool throughput (the 20 B3 dates, 3 processes, nice 10)

| Run (PDT) | New pass-1 dates | Pass-1 wall s | Pass-2 dates | Pass-2 wall s |
|---|---|---|---|---|
| A 02:03:17-02:10 | 136 | 398.2 | 10 | 2.6 |
| B 02:10-02:13:10 | 92 | 174.5 | 5 | 0.7 |
| C 02:13:10-02:16:26 | 100 (110 listed, 10 already done) | 189.5 | 5 | 1.3 |
| Total | 328 | 762.2 | 20 | 4.6 |

328 dates in 762 s = 2.3 s of wall per date with 3 processes, about 7.0 s per date per process
(load included).

## Projection for the full build (816 dates; the lead launches it)

- Pass 1: 816 x 2.3 s = about 31 minutes of wall with 3 processes at this machine load (24-40
  minutes over the per-run rates seen, 5.2-8.8 s per date per process); about 1.6 CPU-hours.
- Pass 2: 816 x 0.23 s = about 3 minutes in one process, under 2 with 3.
- Memory: peak RSS at most 590 MB per process (the max date); 3 processes stay under 1.8 GB.
- The protocol's guess (P5 compute estimate: 1-3 CPU-hours for the feature event loop) holds.

## Cutoff mode check (LT1 mechanics, not the LT1 test itself)

`build_features33.py --cutoff-ns` on three times of B3 dates, compared with the production rows at
t <= cutoff (G7 tolerance): 2022-09-29 10:17 (prior pass 1 from production) 103 rows, 6,077 cells,
0 mismatches; 2023-02-16 08:35 (production prior) 1 row, 59 cells, 0; 2021-03-11 12:40 (all 21
prior dates re-streamed from truncated streams) 246 rows, 14,514 cells, 0. Outputs under
DERIVED/features/c22b0a50f4cd/_lt1/<cutoff_ns>/.
