# Label builder probe (LabelCoder, Coder-A), 2026-10-27 PDT

Brief deliverable 3: timing and schema on at most 3 real dates; COUNTS only (INTERFACE rule 1: no statistic of
label values, nets or classes was computed or printed). Builder: reports/stage_e33_briefs/work/pipeline/
build_labels33.py, run with `--probe --sigma-override 3.15` (no DERIVED/features/<sha>/_day existed yet, so the
TB tables used a placeholder sigma_ZM of 3.15 ticks, P0.4's standard number, for timing and schema only; these TB
files are not labels). nice 10; free memory 8.5-9.7 GB at start.

Output: /mnt/large-storage/market_data/PropExperiment/derived/e33/probes/lab33_probe/c0271f430413/ (final code,
run 15:05:10-15:05:22 PDT, 3 processes). An earlier probe folder .../lab33_probe/6401f94f5591/ (15:02 PDT, code
before the LT2 self-check and formatting) is superseded; kept, not deleted.

## Per-date seconds

| Date | Run | Procs | Seconds (date) | Replay s | ZM front records (< 13:20 CT) | Book updates |
|---|---|---|---|---|---|---|
| 2021-07-01 | 15:01 single date | 1 | 2.42 | 1.09 | 683,679 | 628,072 |
| 2022-03-14 | 15:02 pair | 2 | 2.30 | 0.73 | - | 279,423 |
| 2023-11-06 | 15:02 pair | 2 | 2.60 | 0.97 | - | 361,421 |
| 2021-07-01 | 15:05 final code | 3 | 5.14 | 3.05 | 683,679 | 628,072 |
| 2022-03-14 | 15:05 final code | 3 | 5.43 | 1.00 | - | 279,423 |
| 2023-11-06 | 15:05 final code | 3 | 7.83 | 2.58 | - | 361,421 |

Seconds per date cover loading (data33.load_zm), the replay and all six labels incl. writing. With 3 processes the
per-date time rises (shared load and memory bandwidth); wall clock for the 3-date final run was 12 s including
start-up. Estimate for the full build (796 OOF dates, 6 labels): about 2.5 s per date single-process, so about
35 min at 1 process and roughly 15-30 min at 3 (guess from 3 dates; the lead launches it).

## Counts (final code, every label)

| Date | Label | Grid | entry_ok | Rows kept | Removed (first rule) |
|---|---|---|---|---|---|
| 2021-07-01 | F05 / F15 / F30 / F60 / T15 / T30 | 273 / 263 / 248 / 218 / 263 / 248 | 0 each | 0 each | r5_limit: all |
| 2022-03-14 | F05 / F15 / F30 / F60 / T15 / T30 | 273 / 263 / 248 / 218 / 263 / 248 | = grid | = grid | none |
| 2023-11-06 | F05 / F15 / F30 / F60 / T15 / T30 | 273 / 263 / 248 / 218 / 263 / 248 | = grid | = grid | none |

On all 18 (label, date) files: LT2 span violations 0; book crossed or locked at a grid minute 0; fallback, not-made
and mark flags 0 on both sides; Book anomalies 0; ts_recv decreases 0; F_MAYBE_BAD_BOOK marks 0; records before the
first R 76 on 2021-07-01. None of the three dates has a P3.6 rule 3 release. Parquet schema = INTERFACE 4.2
(19 columns: i int16, t_ns int64, entry_ok bool, row_ok bool, y int8, n_long/n_short/w float64, span_end_ns int64,
then long_* and short_* made bool, net float64, entry_ns/exit_ns int64, flags int16); rows per file = |G_h(D)|.

2021-07-01: every minute fails the rule 5 limit part because the front traded above the high limit of its 08:30 CT
definition (book states and definitions only; see reports/stage_e33_briefs/work/LabelCoder_readings.md, "Finding").

## Lead follow-up: `mid_move` column (rerun 15:24:23-15:24:34 PDT, same 3 dates, 3 processes)

Code sha12 17934b7b23b1 (output .../lab33_probe/17934b7b23b1/; c0271f430413 is now superseded too, kept). The
table has 20 columns: the 19 above plus `mid_move` (float64) last. Per-date seconds 5.62 (2021-07-01; replay
2.66), 6.33 (2022-03-14; 1.74), 5.56 (2023-11-06; 2.46). Grid, entry_ok and row counts are unchanged; LT2
violations 0. Defined (non-NaN) mid_move: every grid minute of all 18 files (counts only; no value statistic).
The builder now also replays the book on excluded dates (for mid_move only; flags stay false); none of the 3
probe dates is excluded, so that path ran only in the unit tests.
