# B3 agreement (feat_r2_partial): Coder-A (pipeline/) vs Coder-B (implB/)

Written by TestCoder-OpusXHigh, 2026-10-28 03:17 PDT. Script reports/stage_e33_briefs/work/pipeline/tests_b3/compare_b3.py. INTERFACE rule 1: counts and mismatch locations only; the mismatching cells with values are in the parquet named below, never here.

- dates: 10 (given): 2021-01-19, 2021-01-25, 2021-03-11, 2021-03-16, 2021-04-01, 2021-05-04, 2021-07-06, 2021-07-09, 2021-07-29, 2021-08-16
- A features: /mnt/large-storage/market_data/PropExperiment/derived/e33/features/6873427a6150 (code_sha12 6873427a6150)
- B features: /mnt/large-storage/market_data/PropExperiment/derived/e33/implB/features/7d28f22509b4 (code_sha12 7d28f22509b4)
- mismatch cells: 2690 -> /mnt/large-storage/market_data/PropExperiment/derived/e33/b3/mismatches_feat_r2_partial.parquet

Tolerances: labels, classes, flags, made, fill times, n_long, n_short and per-side nets exactly (a == b, NaN == NaN); w within 1e-12 relative (|a-b| <= 1e-12 max(|a|,|b|); a float mean of 1/c_m); features |a-b| <= max(1e-9 max(|a|,|b|), 1e-12) (G7), NaN == NaN; rows joined on i (`__row__` counts rows present on one side only).

## Features: disagreeing cells per column (sum over dates)

Rows joined 2730; rows with any mismatch 2690; NaN cells A 0, B 0.

| column | agree | disagree |
|---|---|---|
| __row__ | 2730 | 0 |
| date | 2730 | 0 |
| t_ns | 2730 | 0 |
| C_1 | 2730 | 0 |
| C_2 | 2730 | 0 |
| C_3 | 2730 | 0 |
| C_4 | 2730 | 0 |
| C_5 | 2730 | 0 |
| C_6 | 2730 | 0 |
| C_7 | 2730 | 0 |
| C_8 | 2730 | 0 |
| C_9 | 2730 | 0 |
| C_10 | 2730 | 0 |
| C_11 | 2730 | 0 |
| C_12 | 2730 | 0 |
| C_13 | 2730 | 0 |
| C_14 | 2730 | 0 |
| C_15 | 2730 | 0 |
| F1_1 | 2730 | 0 |
| F1_2 | 2730 | 0 |
| F1_3 | 2730 | 0 |
| F1_4 | 2730 | 0 |
| F1_5 | 2730 | 0 |
| F1_6 | 2730 | 0 |
| F1_7 | 2730 | 0 |
| F1_8 | 2730 | 0 |
| F2_1 | 2730 | 0 |
| F2_2 | 2730 | 0 |
| F2_3 | 2730 | 0 |
| F2_4 | 2730 | 0 |
| F2_5 | 2730 | 0 |
| F2_6 | 2730 | 0 |
| F2_7 | 2730 | 0 |
| F2_8 | 2730 | 0 |
| F2_9 | 2730 | 0 |
| F2_10 | 2730 | 0 |
| F2_11 | 2730 | 0 |
| F3_1 | 2730 | 0 |
| F3_2 | 2730 | 0 |
| F3_3 | 2730 | 0 |
| F3_4 | 2730 | 0 |
| F3_5 | 2730 | 0 |
| F3_6 | 2730 | 0 |
| F3_7 | 2730 | 0 |
| F3_8 | 2730 | 0 |
| F3_9 | 2730 | 0 |
| F3_10 | 2730 | 0 |
| F3_11 | 40 | 2690 |
| F3_12 | 2730 | 0 |
| F4_1 | 2730 | 0 |
| F4_2 | 2730 | 0 |
| F4_3 | 2730 | 0 |
| F4_4 | 2730 | 0 |
| F4_5 | 2730 | 0 |
| F4_6 | 2730 | 0 |
| F4_7 | 2730 | 0 |
| F4_8 | 2730 | 0 |
| F4_9 | 2730 | 0 |
| F4_10 | 2730 | 0 |
| F4_11 | 2730 | 0 |
| F4_12 | 2730 | 0 |
| F4_13 | 2730 | 0 |

| date | rows joined | rows with any mismatch | disagreeing cells |
|---|---|---|---|
| 2021-01-19 | 273 | 270 | 270 |
| 2021-01-25 | 273 | 267 | 267 |
| 2021-03-11 | 273 | 271 | 271 |
| 2021-03-16 | 273 | 270 | 270 |
| 2021-04-01 | 273 | 263 | 263 |
| 2021-05-04 | 273 | 270 | 270 |
| 2021-07-06 | 273 | 273 | 273 |
| 2021-07-09 | 273 | 270 | 270 |
| 2021-07-29 | 273 | 267 | 267 |
| 2021-08-16 | 273 | 269 | 269 |

## sigma_ZM(D), sigma_ZS(D), sigma_ZL(D) (ticks; feature-layer scales, not outcomes)

| date | A feat zm | B feat zm | B label-builder zm | A vs B feat | A feat vs B lab | B feat vs B lab | zs A/B | zl A/B |
|---|---|---|---|---|---|---|---|---|
| 2021-01-19 | 3.2155289271 | 3.2155289271 | 3.2155289271 | agree | agree | agree | agree | agree |
| 2021-01-25 | 3.29188476166 | 3.29188476166 | 3.29188476166 | agree | agree | agree | agree | agree |
| 2021-03-11 | 2.59320841512 | 2.59320841512 | 2.59320841512 | agree | agree | agree | agree | agree |
| 2021-03-16 | 2.55233061383 | 2.55233061383 | 2.55233061383 | agree | agree | agree | agree | agree |
| 2021-04-01 | 3.16558891915 | 3.16558891915 | 3.16558891915 | agree | agree | agree | agree | agree |
| 2021-05-04 | 2.86422993763 | 2.86422993763 | 2.86422993763 | agree | agree | agree | agree | agree |
| 2021-07-06 | 4.72986249946 | 4.72986249946 | 4.72986249946 | agree | agree | agree | agree | agree |
| 2021-07-09 | 4.8252780258 | 4.8252780258 | 4.8252780258 | agree | agree | agree | agree | agree |
| 2021-07-29 | 4.61664644947 | 4.61664644947 | 4.61664644947 | agree | agree | agree | agree | agree |
| 2021-08-16 | 2.62582782991 | 2.62582782991 | 2.62582782991 | agree | agree | agree | agree | agree |

