# B3 agreement (lab_fh_r2): Coder-A (pipeline/) vs Coder-B (implB/)

Written by TestCoder-OpusXHigh, 2026-10-28 02:02 PDT. Script reports/stage_e33_briefs/work/pipeline/tests_b3/compare_b3.py. INTERFACE rule 1: counts and mismatch locations only; the mismatching cells with values are in the parquet named below, never here.

- dates: 20 (B3 rule seed 20261028): 2021-01-19, 2021-01-25, 2021-03-11, 2021-03-16, 2021-04-01, 2021-05-04, 2021-07-06, 2021-07-09, 2021-07-29, 2021-08-16, 2022-06-03, 2022-09-01, 2022-09-29, 2022-12-13, 2022-12-22, 2023-01-11, 2023-02-16, 2023-04-10, 2023-08-11, 2024-02-15
- A labels: /mnt/large-storage/market_data/PropExperiment/derived/e33/labels/17934b7b23b1 (code_sha12 17934b7b23b1)
- B labels: /mnt/large-storage/market_data/PropExperiment/derived/e33/implB/labels (code_sha12 efdde5c74ee1)
- A features: /mnt/large-storage/market_data/PropExperiment/derived/e33/features/45349685744d (code_sha12 45349685744d)
- B features: /mnt/large-storage/market_data/PropExperiment/derived/e33/implB/features/345ba20d4f97 (code_sha12 345ba20d4f97)
- mismatch cells: 0 -> /mnt/large-storage/market_data/PropExperiment/derived/e33/b3/mismatches_lab_fh_r2.parquet

Tolerances: labels, classes, flags, made, fill times, n_long, n_short and per-side nets exactly (a == b, NaN == NaN); w within 1e-12 relative (|a-b| <= 1e-12 max(|a|,|b|); a float mean of 1/c_m); features |a-b| <= max(1e-9 max(|a|,|b|), 1e-12) (G7), NaN == NaN; rows joined on i (`__row__` counts rows present on one side only).

## Labels: disagreeing cells per column (sum over dates; agree / disagree)

| column | F05 | F15 | F30 | F60 |
|---|---|---|---|---|
| __row__ | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| t_ns | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| entry_ok | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| row_ok | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| y | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| n_long | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| n_short | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| w | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| span_end_ns | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| long_made | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| long_net | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| long_entry_ns | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| long_exit_ns | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| long_flags | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| short_made | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| short_net | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| short_entry_ns | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| short_exit_ns | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| short_flags | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |
| rows joined / rows with any mismatch | 5460 / 0 | 5260 / 0 | 4960 / 0 | 4360 / 0 |

## Labels: per date (rows with any mismatch / disagreeing cells; rows joined in brackets)

| date | F05 | F15 | F30 | F60 |
|---|---|---|---|---|
| 2021-01-19 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-01-25 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-03-11 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-03-16 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-04-01 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-05-04 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-07-06 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-07-09 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-07-29 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2021-08-16 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2022-06-03 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2022-09-01 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2022-09-29 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2022-12-13 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2022-12-22 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2023-01-11 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2023-02-16 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2023-04-10 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2023-08-11 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |
| 2024-02-15 | 0 / 0 [273] | 0 / 0 [263] | 0 / 0 [248] | 0 / 0 [218] |

## sigma_ZM(D), sigma_ZS(D), sigma_ZL(D) (ticks; feature-layer scales, not outcomes)

| date | A feat zm | B feat zm | B label-builder zm | A vs B feat | A feat vs B lab | B feat vs B lab | zs A/B | zl A/B |
|---|---|---|---|---|---|---|---|---|
| 2021-01-19 | 3.2155289271 | null | 3.2155289271 | one null | agree | one null | one null | one null |
| 2021-01-25 | 3.29188476166 | null | 3.29188476166 | one null | agree | one null | one null | one null |
| 2021-03-11 | 2.59320841512 | null | 2.59320841512 | one null | agree | one null | one null | one null |
| 2021-03-16 | 2.55233061383 | null | 2.55233061383 | one null | agree | one null | one null | one null |
| 2021-04-01 | 3.16558891915 | null | 3.16558891915 | one null | agree | one null | one null | one null |
| 2021-05-04 | 2.86422993763 | null | 2.86422993763 | one null | agree | one null | one null | one null |
| 2021-07-06 | 4.72986249946 | null | 4.72986249946 | one null | agree | one null | one null | one null |
| 2021-07-09 | 4.8252780258 | null | 4.8252780258 | one null | agree | one null | one null | one null |
| 2021-07-29 | 4.61664644947 | null | 4.61664644947 | one null | agree | one null | one null | one null |
| 2021-08-16 | 2.62582782991 | null | 2.62582782991 | one null | agree | one null | one null | one null |
| 2022-06-03 | 3.34746974179 | null | 3.34746974179 | one null | agree | one null | one null | one null |
| 2022-09-01 | 3.53822320832 | null | 3.53822320832 | one null | agree | one null | one null | one null |
| 2022-09-29 | null | null | 3.46385036838 | both null | one null | one null | both null | both null |
| 2022-12-13 | null | null | 2.88513600167 | both null | one null | one null | both null | both null |
| 2022-12-22 | null | null | 3.03513633158 | both null | one null | one null | both null | both null |
| 2023-01-11 | null | null | 3.10791729116 | both null | one null | one null | both null | both null |
| 2023-02-16 | null | null | 3.53875038072 | both null | one null | one null | both null | both null |
| 2023-04-10 | null | 3.11257974319 | 3.11257974319 | one null | one null | agree | one null | one null |
| 2023-08-11 | null | null | 2.72234717986 | both null | one null | one null | both null | both null |
| 2024-02-15 | null | null | 2.73984106196 | both null | one null | one null | both null | both null |

