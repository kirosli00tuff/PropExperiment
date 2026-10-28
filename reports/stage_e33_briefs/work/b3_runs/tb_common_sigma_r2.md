# B3 agreement (tb_common_sigma_r2): Coder-A (pipeline/) vs Coder-B (implB/)

Written by TestCoder-OpusXHigh, 2026-10-28 02:02 PDT. Script reports/stage_e33_briefs/work/pipeline/tests_b3/compare_b3.py. INTERFACE rule 1: counts and mismatch locations only; the mismatching cells with values are in the parquet named below, never here.

- dates: 20 (B3 rule seed 20261028): 2021-01-19, 2021-01-25, 2021-03-11, 2021-03-16, 2021-04-01, 2021-05-04, 2021-07-06, 2021-07-09, 2021-07-29, 2021-08-16, 2022-06-03, 2022-09-01, 2022-09-29, 2022-12-13, 2022-12-22, 2023-01-11, 2023-02-16, 2023-04-10, 2023-08-11, 2024-02-15
- A labels: /mnt/large-storage/market_data/PropExperiment/derived/e33/b3/tb_common_sigma/17934b7b23b1 (code_sha12 17934b7b23b1)
- B labels: /mnt/large-storage/market_data/PropExperiment/derived/e33/implB/labels (code_sha12 efdde5c74ee1)
- mismatch cells: 0 -> /mnt/large-storage/market_data/PropExperiment/derived/e33/b3/mismatches_tb_common_sigma_r2.parquet

Tolerances: labels, classes, flags, made, fill times, n_long, n_short and per-side nets exactly (a == b, NaN == NaN); w within 1e-12 relative (|a-b| <= 1e-12 max(|a|,|b|); a float mean of 1/c_m); features |a-b| <= max(1e-9 max(|a|,|b|), 1e-12) (G7), NaN == NaN; rows joined on i (`__row__` counts rows present on one side only).

## Labels: disagreeing cells per column (sum over dates; agree / disagree)

| column | T15 | T30 |
|---|---|---|
| __row__ | 5260 / 0 | 4960 / 0 |
| t_ns | 5260 / 0 | 4960 / 0 |
| entry_ok | 5260 / 0 | 4960 / 0 |
| row_ok | 5260 / 0 | 4960 / 0 |
| y | 5260 / 0 | 4960 / 0 |
| n_long | 5260 / 0 | 4960 / 0 |
| n_short | 5260 / 0 | 4960 / 0 |
| w | 5260 / 0 | 4960 / 0 |
| span_end_ns | 5260 / 0 | 4960 / 0 |
| long_made | 5260 / 0 | 4960 / 0 |
| long_net | 5260 / 0 | 4960 / 0 |
| long_entry_ns | 5260 / 0 | 4960 / 0 |
| long_exit_ns | 5260 / 0 | 4960 / 0 |
| long_flags | 5260 / 0 | 4960 / 0 |
| short_made | 5260 / 0 | 4960 / 0 |
| short_net | 5260 / 0 | 4960 / 0 |
| short_entry_ns | 5260 / 0 | 4960 / 0 |
| short_exit_ns | 5260 / 0 | 4960 / 0 |
| short_flags | 5260 / 0 | 4960 / 0 |
| rows joined / rows with any mismatch | 5260 / 0 | 4960 / 0 |

## Labels: per date (rows with any mismatch / disagreeing cells; rows joined in brackets)

| date | T15 | T30 |
|---|---|---|
| 2021-01-19 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-01-25 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-03-11 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-03-16 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-04-01 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-05-04 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-07-06 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-07-09 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-07-29 | 0 / 0 [263] | 0 / 0 [248] |
| 2021-08-16 | 0 / 0 [263] | 0 / 0 [248] |
| 2022-06-03 | 0 / 0 [263] | 0 / 0 [248] |
| 2022-09-01 | 0 / 0 [263] | 0 / 0 [248] |
| 2022-09-29 | 0 / 0 [263] | 0 / 0 [248] |
| 2022-12-13 | 0 / 0 [263] | 0 / 0 [248] |
| 2022-12-22 | 0 / 0 [263] | 0 / 0 [248] |
| 2023-01-11 | 0 / 0 [263] | 0 / 0 [248] |
| 2023-02-16 | 0 / 0 [263] | 0 / 0 [248] |
| 2023-04-10 | 0 / 0 [263] | 0 / 0 [248] |
| 2023-08-11 | 0 / 0 [263] | 0 / 0 [248] |
| 2024-02-15 | 0 / 0 [263] | 0 / 0 [248] |

