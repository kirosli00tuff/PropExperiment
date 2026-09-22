# Stage D.1e Task 3: power and sample size for the class null

Generated 2026-09-22T07:04:19.236726+00:00 - eps_day = 34 net ticks per micro per day, Holm family m = 58, alpha_holm = 8.621e-04, z_a = 3.134046, z_b = 0.841621, z_95 = 1.644854.
Bootstrap: mean block 5, K = 20, 2,000 replications per length, seed base 20260922. Runtime 43.1 s. VIF floor hits: 0.

n_a = days to DETECT a true edge of eps_day with 80% power at the Holm-corrected one-sided level. n_b = days for the one-sided 95% UCB to fall below eps_day with 80% probability when the true edge is zero. Holm's most stringent step (0.05/58) is used for every member, so every n_a is conservative.

Units: net ticks PER MICRO per day. Trial members are read as daily_net_ticks_per_micro, which divides each round trip by its own contract quantity (trip net / ($1.25 x trip_micros)). This corrects finding R-1 of reports/stage_d1e_adjudication.md: the earlier run divided daily dollars by $2.50, assuming 2 micros for every trial, which put every trial series at half scale and every trial sample size at a quarter of the right one. The Family H per-trade SD proxies were read off the same half-scale table and are corrected with it (200 ticks for H1-H5, 230 for H6). Statistic members are built from tick sums and were never affected.

Chosen figure: where the simulated and analytic sizes differ by more than 15%, the chosen figure is max(analytic, simulated). A simulated size BELOW the analytic one is not evidence that fewer days suffice - for a heavy-tailed member at short lengths the replicate's variance estimate is right-skewed, so the closed-form UCB under-covers there, and adopting the smaller figure would plan on an anti-conservative test. Where the simulation asks for MORE days it is used (sim_used_larger_*); where it asks for fewer it is recorded and ignored (sim_smaller_ignored_*). Both figures and the difference stay in every row.

Simulation SE: SE_hat = sqrt(gamma_0_hat(x) * VIF_boot(source) / n), with gamma_0_hat(x) the replicate's own sample variance (ddof = 1). A replicate's own lag-k autocovariance is already about (1-p)^k times the source's, so computing V_B from the replicate would attenuate the dependence term twice; the dependence factor therefore comes from the source, exactly as the analytic formula uses it.

## 1. Supplied confirmation days (estimate, +/-3%)

| start S | weekday open dates | roll blackout | vendor degraded | days |
|---|---|---|---|---|
| 2019-05-06 | 1,216 | 58 | 7 | **1,151** |
| 2019-07-01 | 1,177 | 56 | 7 | **1,114** |
| 2020-01-02 | 1,049 | 50 | 7 | **992** |
| 2021-01-04 | 795 | 38 | 2 | **755** |
| 2022-01-03 | 542 | 26 | 0 | **516** |
| 2023-01-03 | 291 | 14 | 0 | **277** |

All ranges end 2024-02-29. Holdout-2 (2024-04-01..2025-03-31) supplies **239** trade dates by the same method.

## 2. Per class: binding members, eps per trade, days supplied

| class | typical r (trades/day) | eps/trade | gross-equiv/trade | market cost | passive cost | binding n_a (member) | binding n_b (member) |
|---|---|---|---|---|---|---|---|
| C1 | 0.938 | 36.26 | 38.37 | 2.11 | 0.98 | 379 (A-H4 rth leg) | 149 (A-H4 rth leg) |
| C2 | 0.945 | 35.99 | 38.10 | 2.11 | 0.98 | 492 (G3.RTH.5) | 193 (G3.RTH.5) |
| C3 | 36.151 | 0.94 | 3.05 | 2.11 | 0.98 | 1,447 (F1_1_h1_RTH) | 566 (F1_1_h1_RTH) |
| C4 | 0.676 | 50.26 | 52.37 | 2.11 | 0.98 | 436 (F2_4_15min_vol_tercile_top) | 171 (F2_4_15min_vol_tercile_top) |
| C5 | 0.097 | 350.93 | 353.04 | 2.11 | 0.98 | 41 (E-H1 scheduled macro drift) | 16 (E-H1 scheduled macro drift) |
| C6 | 92.467 | 0.37 | 2.48 | 2.11 | 0.98 | 461 (C-H4 passive-fill reversal) | 181 (C-H4 passive-fill reversal) |
| C7 | 0.263 | 129.52 | 131.63 | 2.11 | 0.98 | 290 (H6 prior-close location follow-through) | 114 (H6 prior-close location follow-through) |

### 2b. Days supplied at each start S against the binding n_b

| class | binding n_b | 2019-05-06 | 2019-07-01 | 2020-01-02 | 2021-01-04 | 2022-01-03 | 2023-01-03 |
|---|---|---|---|---|---|---|---|
| C1 | 149 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 ok | 277 ok |
| C2 | 193 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 ok | 277 ok |
| C3 | 566 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 short | 277 short |
| C4 | 171 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 ok | 277 ok |
| C5 | 16 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 ok | 277 ok |
| C6 | 181 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 ok | 277 ok |
| C7 | 114 | 1,151 ok | 1,114 ok | 992 ok | 755 ok | 516 ok | 277 ok |

## 3. Per member

| class | tier | member | kind | r | SD/day | lag1 | VIF_boot | eps/trade | n_a | n_b | n_a sim | n_b sim | diff a % | diff b % | chosen a | chosen b | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | A | A-H1 european-open overnight drift | trial | 0.955 | 33.88 | 0.004 | 0.890 | 35.60 | 14 | 6 | 11.9 | 6.0 | -15.3 | 0.0 | 14 | 6 | sim_smaller_ignored_a,sim_censored_below_grid_b |
| C1 | A | A-H2 rth close window (buy) | trial | 0.920 | 51.62 | -0.086 | 0.973 | 36.94 | 36 | 14 | 36.3 | 13.8 | 0.8 | -1.1 | 36 | 14 | - |
| C1 | A | A-H2 rth close window (sell) | trial | 0.920 | 51.70 | -0.086 | 0.975 | 36.94 | 36 | 14 | 37.9 | 14.0 | 5.4 | -0.2 | 36 | 14 | - |
| C1 | A | A-H3 weekend effect | trial | 0.381 | 123.46 | 0.122 | 0.987 | 89.33 | 206 | 81 | 227.7 | 66.6 | 10.5 | -17.8 | 206 | 81 | sim_smaller_ignored_b |
| C1 | A | A-H4 eth leg | trial | 0.958 | 136.54 | -0.013 | 0.878 | 35.47 | 224 | 88 | 224.8 | 84.4 | 0.4 | -4.1 | 224 | 88 | - |
| C1 | A | A-H4 rth leg | trial | 0.955 | 223.99 | -0.301 | 0.552 | 35.60 | 379 | 149 | 374.5 | 161.0 | -1.2 | 8.1 | 379 | 149 | - |
| C2 | A | B-H1 opening-range breakout (hold 5) | trial | 0.955 | 26.40 | 0.109 | 0.970 | 35.60 | 10 | 4 | 8.7 | 4.0 | -13.4 | 0.0 | 10 | 4 | zero_variance_draws,sim_censored_below_grid_b |
| C2 | A | B-H1 opening-range breakout (hold 75) | trial | 0.955 | 97.25 | -0.086 | 0.922 | 35.60 | 120 | 47 | 119.6 | 43.8 | -0.3 | -6.8 | 120 | 47 | - |
| C2 | A | B-H2 prior-day stop cascade | trial | 0.772 | 37.09 | 0.087 | 1.212 | 44.06 | 23 | 9 | 21.9 | 9.0 | -4.9 | 0.0 | 23 | 9 | sim_censored_below_grid_b |
| C2 | A | B-H3 breakout leg | trial | 0.948 | 58.04 | -0.053 | 0.817 | 35.86 | 38 | 15 | 40.0 | 13.3 | 5.3 | -11.3 | 38 | 15 | - |
| C2 | A | B-H3 fade leg | trial | 0.948 | 58.03 | -0.055 | 0.818 | 35.86 | 38 | 15 | 39.8 | 13.8 | 4.8 | -7.8 | 38 | 15 | - |
| C2 | A | B-H4 narrow-range breakout | trial | 0.398 | 27.49 | -0.035 | 0.735 | 85.44 | 8 | 3 | 7.9 | 3.0 | -1.1 | 0.0 | 8 | 3 | zero_variance_draws,sim_censored_below_grid_b |
| C3 | A | C-H1 magnitude-conditioned reversal | trial | 140.979 | 208.06 | -0.091 | 0.799 | 0.24 | 473 | 185 | 472.6 | 181.6 | -0.1 | -1.8 | 473 | 185 | - |
| C3 | A | C-H2 post-spike exhaustion fade | trial | 30.550 | 93.30 | 0.177 | 1.167 | 1.11 | 139 | 55 | 126.1 | 45.2 | -9.3 | -17.8 | 139 | 55 | sim_smaller_ignored_b |
| C3 | A | C-H3 close-location-value reversal | trial | 41.751 | 116.87 | 0.088 | 0.788 | 0.81 | 148 | 58 | 184.1 | 41.8 | 24.4 | -28.0 | 185 | 58 | sim_used_larger_a,sim_smaller_ignored_b |
| C4 | A | D-H1 trailing-vol regime gate | trial | 0.367 | 8.31 | -0.019 | 0.913 | 92.70 | 1 | 1 | 2.0 | 2.0 | 100.0 | 100.0 | 1 | 1 | zero_variance_draws,sim_censored_below_grid_a,sim_censored_below_grid_b |
| C4 | A | D-H2 inverse-vol sizing | trial | 0.955 | 22.99 | 0.036 | 0.859 | 35.60 | 7 | 3 | 6.4 | 3.0 | -8.2 | 0.0 | 7 | 3 | zero_variance_draws,sim_censored_below_grid_b |
| C4 | A | D-H3 range-compression gate | trial | 9.848 | 64.01 | 0.007 | 0.945 | 3.45 | 53 | 21 | 51.2 | 14.2 | -3.4 | -32.6 | 53 | 21 | sim_smaller_ignored_b |
| C4 | A | D-H4 overnight gap fade | trial | 0.464 | 19.37 | 0.023 | 1.139 | 73.33 | 6 | 3 | 3.0 | 3.0 | -50.0 | 0.0 | 6 | 3 | zero_variance_draws,sim_censored_below_grid_a,sim_censored_below_grid_b |
| C5 | A | E-H1 scheduled macro drift | trial | 0.107 | 50.29 | -0.002 | 1.176 | 316.97 | 41 | 16 | 13.7 | 10.0 | -66.5 | -37.5 | 41 | 16 | zero_variance_draws,sim_smaller_ignored_a,sim_censored_below_grid_b |
| C5 | A | E-H2 post-release momentum | trial | 0.087 | 9.43 | -0.000 | 0.948 | 393.04 | 2 | 1 | 2.0 | 2.0 | 0.0 | 100.0 | 2 | 1 | zero_variance_draws,sim_censored_below_grid_a,sim_censored_below_grid_b |
| C5 | A | E-H3 quarterly witching short | trial | 0.014 | 1.86 | -0.001 | 0.988 | 2,456.50 | 1 | 1 | 2.0 | 2.0 | 100.0 | 100.0 | 1 | 1 | zero_variance_draws,sim_censored_below_grid_a,sim_censored_below_grid_b |
| C5 | A | E-H4 turn-of-month long | trial | 0.190 | 5.36 | 0.074 | 0.900 | 178.65 | 1 | 1 | 2.0 | 2.0 | 100.0 | 100.0 | 1 | 1 | zero_variance_draws,sim_censored_below_grid_a,sim_censored_below_grid_b |
| C6 | A | C-H4 passive-fill reversal | trial | 92.467 | 190.54 | 0.013 | 0.927 | 0.37 | 461 | 181 | 474.8 | 173.6 | 3.0 | -4.1 | 461 | 181 | - |
| C2 | A | RT1 B-H1 ORB 5-min bars (hold 1 bar) | trial | 0.945 | 24.83 | 0.052 | 0.964 | 35.99 | 9 | 4 | 8.9 | 4.0 | -1.6 | 0.0 | 9 | 4 | zero_variance_draws,sim_censored_below_grid_b |
| C2 | A | RT2 B-H1 ORB 5-min bars (hold 15 bars) | trial | 0.945 | 96.17 | 0.173 | 1.363 | 35.99 | 173 | 68 | 199.6 | 47.3 | 15.4 | -30.5 | 200 | 68 | sim_used_larger_a,sim_smaller_ignored_b |
| C2 | A | RT3 B-H3 breakout leg 5-min bars | trial | 0.945 | 63.15 | -0.052 | 0.907 | 35.99 | 50 | 20 | 53.8 | 13.7 | 7.7 | -31.7 | 50 | 20 | sim_smaller_ignored_b |
| C2 | A | RT4 B-H3 fade leg 5-min bars | trial | 0.945 | 63.15 | -0.053 | 0.906 | 35.99 | 50 | 20 | 44.4 | 14.9 | -11.2 | -25.6 | 50 | 20 | sim_smaller_ignored_b |
| C3 | A | RT5 C-H2 spike fade 5-min bars | trial | 9.772 | 67.71 | 0.070 | 0.972 | 3.48 | 61 | 24 | 65.7 | 21.2 | 7.8 | -11.5 | 61 | 24 | - |
| C4 | A | RT6 D-H1 daily-vol regime gate | trial | 0.464 | 11.21 | 0.076 | 0.944 | 73.33 | 2 | 1 | 2.0 | 2.0 | 0.0 | 100.0 | 2 | 1 | zero_variance_draws,sim_censored_below_grid_a,sim_censored_below_grid_b |
| C4 | A | RT7 D-H2 daily-vol sizing | trial | 0.889 | 19.40 | 0.040 | 0.859 | 38.23 | 5 | 2 | 4.0 | 2.0 | -20.7 | 0.0 | 5 | 2 | zero_variance_draws,sim_smaller_ignored_a,sim_censored_below_grid_b |
| C3 | A | F3_2_bucket07_bucket08 | statistic | 0.964 | 39.48 | -0.018 | 1.174 | 35.27 | 26 | 10 | 23.3 | 10.0 | -10.2 | 0.0 | 26 | 10 | sim_censored_below_grid_b |
| C2 | A | F6_1_overnight_range_position | statistic | 0.993 | 103.10 | 0.091 | 0.959 | 34.25 | 140 | 55 | 147.7 | 51.5 | 5.5 | -6.4 | 140 | 55 | - |
| C3 | A | F3_3_opening_30min_to_close_momentum | statistic | 0.964 | 46.10 | 0.017 | 0.932 | 35.27 | 28 | 11 | 28.4 | 10.7 | 1.5 | -2.9 | 28 | 11 | - |
| C3 | A | F3_2_bucket08_bucket09 | statistic | 0.964 | 38.90 | 0.243 | 1.030 | 35.27 | 22 | 9 | 19.7 | 9.0 | -10.5 | 0.0 | 22 | 9 | sim_censored_below_grid_b |
| C3 | A | F3_3_overnight_to_close_momentum | statistic | 0.964 | 46.25 | 0.035 | 0.924 | 35.27 | 28 | 11 | 29.9 | 10.2 | 6.9 | -6.9 | 28 | 11 | - |
| C2 | A | F4_4_round_number_multiples_of_100 | statistic | 4.022 | 87.88 | 0.114 | 1.100 | 8.45 | 117 | 46 | 98.5 | 54.5 | -15.8 | 18.5 | 117 | 55 | sim_smaller_ignored_a,sim_used_larger_b |
| C3 | A | F3_2_bucket01_bucket02 | statistic | 0.993 | 59.60 | 0.014 | 1.212 | 34.25 | 59 | 24 | 62.2 | 22.6 | 5.5 | -5.9 | 59 | 24 | - |
| C3 | A | F3_2_bucket10_bucket11 | statistic | 0.964 | 41.60 | -0.123 | 0.773 | 35.27 | 19 | 8 | 18.7 | 9.0 | -1.7 | 12.5 | 19 | 8 | - |
| C2 | A | F4_1_rth_open_crossing | statistic | 1.878 | 53.95 | 0.079 | 1.258 | 18.11 | 51 | 20 | 55.2 | 16.7 | 8.3 | -16.7 | 51 | 20 | sim_smaller_ignored_b |
| C3 | A | F3_2_bucket02_bucket03 | statistic | 0.993 | 61.31 | 0.005 | 1.146 | 34.25 | 59 | 24 | 56.8 | 22.5 | -3.8 | -6.4 | 59 | 24 | - |
| C3 | A | F3_2_bucket05_bucket06 | statistic | 0.993 | 42.77 | -0.053 | 0.883 | 34.25 | 23 | 9 | 22.9 | 9.0 | -0.5 | 0.0 | 23 | 9 | sim_censored_below_grid_b |
| C3 | A | F3_2_bucket04_bucket05 | statistic | 0.993 | 54.30 | 0.054 | 1.030 | 34.25 | 42 | 17 | 36.8 | 14.7 | -12.4 | -13.7 | 42 | 17 | - |
| C3 | A | F3_2_bucket06_bucket07 | statistic | 0.993 | 43.85 | -0.122 | 0.777 | 34.25 | 21 | 8 | 22.5 | 8.5 | 7.1 | 5.9 | 21 | 8 | - |
| C3 | A | F3_2_bucket12_bucket13 | statistic | 0.964 | 46.42 | -0.051 | 0.868 | 35.27 | 26 | 11 | 25.2 | 11.4 | -3.1 | 3.8 | 26 | 11 | - |
| C2 | A | G2.RTH.30 | statistic | 2.295 | 62.92 | -0.057 | 0.984 | 14.82 | 54 | 21 | 47.9 | 22.7 | -11.3 | 8.3 | 54 | 21 | - |
| C3 | A | G1.RTH.5 | statistic | 12.871 | 106.33 | -0.279 | 0.440 | 2.64 | 68 | 27 | 73.8 | 25.5 | 8.5 | -5.6 | 68 | 27 | - |
| C2 | A | G2.ETH.30 | statistic | 4.302 | 54.12 | 0.049 | 1.078 | 7.90 | 44 | 17 | 40.3 | 17.2 | -8.4 | 1.3 | 44 | 17 | - |
| C2 | A | G2.ETH.5 | statistic | 9.554 | 39.59 | 0.033 | 0.974 | 3.56 | 21 | 9 | 22.4 | 9.0 | 6.6 | 0.0 | 21 | 9 | sim_censored_below_grid_b |
| C2 | A | G5.RTH.15 | statistic | 0.928 | 40.62 | 0.173 | 0.931 | 36.64 | 22 | 9 | 20.6 | 9.0 | -6.5 | 0.0 | 22 | 9 | sim_censored_below_grid_b |
| C2 | A | G5.RTH.30 | statistic | 0.892 | 48.54 | -0.016 | 0.885 | 38.11 | 29 | 12 | 29.2 | 12.7 | 0.6 | 5.7 | 29 | 12 | - |
| C2 | A | G3.RTH.15 | statistic | 0.993 | 163.04 | 0.065 | 0.947 | 34.25 | 345 | 135 | 323.3 | 141.6 | -6.3 | 4.9 | 345 | 135 | - |
| C3 | B | F1_1_h1_RTH | statistic | 381.129 | 263.27 | 0.097 | 1.527 | 0.09 | 1,447 | 566 | 1,469.7 | 570.6 | 1.6 | 0.8 | 1,447 | 566 | - |
| C3 | B | F1_1_h5_RTH | statistic | 75.432 | 182.52 | -0.162 | 0.667 | 0.45 | 304 | 119 | 316.3 | 118.2 | 4.0 | -0.7 | 304 | 119 | - |
| C3 | B | F1_1_h15_RTH | statistic | 24.482 | 191.78 | 0.113 | 1.152 | 1.39 | 580 | 227 | 603.5 | 219.3 | 4.1 | -3.4 | 580 | 227 | - |
| C3 | B | F1_1_h30_RTH | statistic | 11.741 | 168.27 | 0.074 | 1.053 | 2.90 | 408 | 160 | 400.0 | 158.4 | -2.0 | -1.0 | 408 | 160 | - |
| C3 | B | F1_1_h60_RTH | statistic | 4.878 | 141.64 | 0.052 | 1.031 | 6.97 | 283 | 111 | 273.9 | 106.8 | -3.2 | -3.8 | 283 | 111 | - |
| C3 | B | F1_1_h1_ETH | statistic | 927.827 | 177.32 | 0.134 | 1.334 | 0.04 | 574 | 225 | 589.2 | 213.4 | 2.7 | -5.1 | 574 | 225 | - |
| C3 | B | F1_1_h5_ETH | statistic | 183.942 | 153.00 | 0.015 | 1.031 | 0.18 | 330 | 130 | 329.1 | 128.7 | -0.3 | -1.0 | 330 | 130 | - |
| C3 | B | F1_1_h15_ETH | statistic | 59.964 | 149.20 | -0.117 | 0.792 | 0.57 | 242 | 95 | 264.2 | 84.4 | 9.2 | -11.2 | 242 | 95 | - |
| C3 | B | F1_1_h30_ETH | statistic | 28.964 | 145.37 | 0.112 | 0.949 | 1.17 | 275 | 108 | 268.3 | 112.8 | -2.4 | 4.4 | 275 | 108 | - |
| C3 | B | F1_1_h60_ETH | statistic | 12.971 | 142.75 | 0.061 | 1.206 | 2.62 | 337 | 132 | 329.3 | 134.3 | -2.3 | 1.8 | 337 | 132 | - |
| C4 | B | F2_4_15min_vol_tercile_bottom | statistic | 8.165 | 55.26 | -0.024 | 1.042 | 4.16 | 44 | 18 | 46.3 | 15.8 | 5.2 | -12.3 | 44 | 18 | - |
| C4 | B | F2_4_15min_vol_tercile_top | statistic | 8.158 | 150.54 | 0.184 | 1.405 | 4.17 | 436 | 171 | 458.5 | 152.3 | 5.2 | -10.9 | 436 | 171 | - |
| C3 | B | F3_2_bucket03_bucket04 | statistic | 0.993 | 53.40 | -0.102 | 0.594 | 34.25 | 24 | 10 | 27.0 | 10.0 | 12.5 | 0.0 | 24 | 10 | sim_censored_below_grid_b |
| C3 | B | F3_2_bucket09_bucket10 | statistic | 0.964 | 41.23 | 0.026 | 0.774 | 35.27 | 18 | 8 | 18.5 | 8.2 | 2.6 | 2.9 | 18 | 8 | - |
| C3 | B | F3_2_bucket11_bucket12 | statistic | 0.964 | 47.76 | -0.205 | 0.685 | 35.27 | 22 | 9 | 20.5 | 9.0 | -6.8 | 0.0 | 22 | 9 | sim_censored_below_grid_b |
| C2 | B | F4_2_prior_rth_close_crossing | statistic | 1.705 | 49.45 | 0.077 | 0.956 | 19.94 | 32 | 13 | 33.4 | 12.6 | 4.3 | -2.8 | 32 | 13 | - |
| C2 | B | F4_4_round_number_multiples_of_50 | statistic | 8.986 | 118.14 | 0.064 | 0.724 | 3.78 | 139 | 55 | 140.7 | 53.3 | 1.3 | -3.1 | 139 | 55 | - |
| C4 | B | F5_1_relvol_tercile_bottom | statistic | 3.338 | 73.23 | -0.170 | 0.822 | 10.19 | 61 | 24 | 60.5 | 24.6 | -0.8 | 2.5 | 61 | 24 | zero_variance_draws |
| C4 | B | F5_1_relvol_tercile_top | statistic | 3.338 | 117.07 | 0.094 | 0.717 | 10.19 | 135 | 53 | 141.1 | 48.3 | 4.5 | -8.9 | 135 | 53 | - |
| C4 | B | F5_2_efficiency_tercile_bottom | statistic | 3.914 | 93.31 | -0.076 | 0.966 | 8.69 | 116 | 45 | 110.9 | 47.0 | -4.4 | 4.5 | 116 | 45 | - |
| C4 | B | F5_2_efficiency_tercile_top | statistic | 3.914 | 112.12 | 0.105 | 0.725 | 8.69 | 125 | 49 | 138.0 | 44.3 | 10.4 | -9.7 | 125 | 49 | - |
| C4 | B | F5_3_range_volume_residual | statistic | 11.741 | 162.95 | 0.016 | 0.701 | 2.90 | 255 | 100 | 258.1 | 99.3 | 1.2 | -0.7 | 255 | 100 | - |
| C3 | B | G1.ETH.5 | statistic | 31.691 | 97.11 | 0.323 | 2.363 | 1.07 | 305 | 120 | 328.9 | 105.2 | 7.8 | -12.4 | 305 | 120 | zero_variance_draws |
| C2 | B | G2.RTH.5 | statistic | 7.288 | 66.23 | 0.031 | 0.775 | 4.67 | 47 | 19 | 43.6 | 20.8 | -7.3 | 9.6 | 47 | 19 | - |
| C2 | B | G3.RTH.5 | statistic | 0.993 | 175.50 | 0.088 | 1.167 | 34.25 | 492 | 193 | 517.9 | 181.7 | 5.3 | -5.9 | 492 | 193 | - |
| C3 | B | G4.RTH.5 | statistic | 12.835 | 89.38 | 0.066 | 1.062 | 2.65 | 116 | 46 | 104.2 | 54.0 | -10.2 | 17.4 | 116 | 55 | zero_variance_draws,sim_used_larger_b |
| C2 | B | G5.RTH.5 | statistic | 1.014 | 27.37 | 0.107 | 0.928 | 33.52 | 10 | 4 | 10.0 | 4.0 | -0.3 | 0.0 | 10 | 4 | sim_censored_below_grid_b |
| C3 | B | G1.ETH.15 | statistic | 10.475 | 96.68 | -0.104 | 0.995 | 3.25 | 128 | 50 | 115.6 | 58.5 | -9.7 | 17.0 | 128 | 59 | zero_variance_draws,sim_used_larger_b |
| C2 | B | G2.ETH.15 | statistic | 5.993 | 62.90 | -0.027 | 0.839 | 5.67 | 46 | 18 | 43.7 | 14.2 | -5.0 | -21.4 | 46 | 18 | sim_smaller_ignored_b |
| C3 | B | G1.RTH.15 | statistic | 4.151 | 106.08 | 0.222 | 1.453 | 8.19 | 224 | 88 | 266.6 | 62.3 | 19.0 | -29.2 | 267 | 88 | zero_variance_draws,sim_used_larger_a,sim_smaller_ignored_b |
| C2 | B | G2.RTH.15 | statistic | 3.806 | 68.93 | 0.077 | 1.130 | 8.93 | 74 | 29 | 80.6 | 26.9 | 9.0 | -7.3 | 74 | 29 | - |
| C3 | B | G4.RTH.15 | statistic | 4.151 | 100.09 | -0.036 | 0.727 | 8.19 | 100 | 39 | 121.1 | 27.9 | 21.1 | -28.6 | 122 | 39 | sim_used_larger_a,sim_smaller_ignored_b |
| C3 | B | G1.ETH.30 | statistic | 5.144 | 76.16 | -0.067 | 0.727 | 6.61 | 58 | 23 | 66.4 | 18.7 | 14.5 | -18.6 | 58 | 23 | zero_variance_draws,sim_smaller_ignored_b |
| C3 | B | G1.RTH.30 | statistic | 2.007 | 76.18 | 0.086 | 0.812 | 16.94 | 65 | 26 | 66.7 | 23.4 | 2.5 | -10.0 | 65 | 26 | zero_variance_draws |
| C2 | B | G3.RTH.30 | statistic | 0.964 | 129.81 | -0.122 | 0.668 | 35.27 | 154 | 61 | 151.1 | 61.2 | -1.9 | 0.4 | 154 | 61 | - |
| C3 | B | G4.RTH.30 | statistic | 1.993 | 83.21 | -0.225 | 0.400 | 17.06 | 38 | 15 | 53.8 | 12.1 | 41.5 | -19.1 | 54 | 15 | sim_used_larger_a,sim_smaller_ignored_b |
| C3 | B | G1.ETH.60 | statistic | 2.403 | 66.75 | 0.010 | 0.734 | 14.15 | 45 | 18 | 52.6 | 15.2 | 16.9 | -15.7 | 53 | 18 | zero_variance_draws,sim_used_larger_a,sim_smaller_ignored_b |
| C2 | B | G2.ETH.60 | statistic | 2.885 | 63.38 | 0.010 | 0.662 | 11.79 | 37 | 15 | 40.0 | 12.1 | 8.1 | -19.4 | 37 | 15 | sim_smaller_ignored_b |
| C3 | B | G1.RTH.60 | statistic | 0.842 | 72.29 | -0.177 | 0.600 | 40.39 | 43 | 17 | 48.8 | 16.7 | 13.5 | -1.9 | 43 | 17 | zero_variance_draws |
| C2 | B | G2.RTH.60 | statistic | 1.209 | 68.42 | -0.174 | 0.604 | 28.13 | 39 | 16 | 38.6 | 17.6 | -0.9 | 10.3 | 39 | 16 | - |
| C2 | B | G3.RTH.60 | statistic | 0.806 | 102.19 | -0.080 | 0.818 | 42.20 | 117 | 46 | 109.4 | 52.6 | -6.5 | 14.3 | 117 | 46 | - |
| C3 | B | G4.RTH.60 | statistic | 0.827 | 75.72 | -0.303 | 0.605 | 41.10 | 48 | 19 | 56.0 | 19.5 | 16.7 | 2.6 | 57 | 19 | zero_variance_draws,sim_used_larger_a |
| C2 | B | G5.RTH.60 | statistic | 0.806 | 68.26 | 0.176 | 1.055 | 42.20 | 68 | 27 | 64.4 | 28.6 | -5.2 | 6.0 | 68 | 27 | - |
| C7 | H | H1 NR4 opening-range breakout | projected | 0.225 | 94.87 | 0.000 | 1.000 | 151.11 | 124 | 49 | - | - | - | - | 124 | 49 | projected |
| C7 | H | H2 NR7 opening-range breakout | projected | 0.129 | 71.71 | 0.000 | 1.000 | 264.44 | 71 | 28 | - | - | - | - | 71 | 28 | projected |
| C7 | H | H3 inside-day opening-range breakout | projected | 0.225 | 94.87 | 0.000 | 1.000 | 151.11 | 124 | 49 | - | - | - | - | 124 | 49 | projected |
| C7 | H | H4 bottom-tercile prior range, breakout | projected | 0.300 | 109.54 | 0.000 | 1.000 | 113.33 | 165 | 65 | - | - | - | - | 165 | 65 | projected |
| C7 | H | H5 top-tercile prior range, opening-range fade | projected | 0.300 | 109.54 | 0.000 | 1.000 | 113.33 | 165 | 65 | - | - | - | - | 165 | 65 | projected |
| C7 | H | H6 prior-close location follow-through | projected | 0.400 | 145.46 | 0.000 | 1.000 | 85.00 | 290 | 114 | - | - | - | - | 290 | 114 | projected |

## 4. Spot check: percentile bootstrap vs the closed-form SE

At each class's binding n_b, the same draws scored with a percentile UCB (95th percentile of an inner stationary bootstrap of the mean, B = 1,000, 200 replicates) instead of mean + 1.645 x SE. This is a check of the closed form against the percentile construction INSIDE THE BOOTSTRAP WORLD. The inner bootstrap resamples a replicate that has already been block-resampled once, so its dependence term is attenuated twice and the percentile column is biased UPWARD for an autocorrelated member. It is not a check of the absolute level of power_b, and it changes no figure.

| class | member | n | closed-form power_b | percentile success |
|---|---|---|---|---|
| C1 | A-H4 rth leg | 149 | 0.780 | 0.795 |
| C2 | G3.RTH.5 | 193 | 0.833 | 0.845 |
| C3 | F1_1_h1_RTH | 566 | 0.800 | 0.905 |
| C4 | F2_4_15min_vol_tercile_top | 171 | 0.817 | 0.870 |
| C5 | E-H1 scheduled macro drift | 16 | 0.919 | 0.990 |
| C6 | C-H4 passive-fill reversal | 181 | 0.814 | 0.810 |
| C7 | H6 prior-close location follow-through | - | - | - (projected, not simulated) |

## 5. Descriptive extras (descriptive, not a criterion)

### 5a. eps_min at each supplied-days count, for each class's binding n_b member

| class | member | 2019-05-06 per day / per trade | 2019-07-01 per day / per trade | 2020-01-02 per day / per trade | 2021-01-04 per day / per trade | 2022-01-03 per day / per trade | 2023-01-03 per day / per trade |
|---|---|---|---|---|---|---|---|
| C1 | A-H4 rth leg | 12.20 / 12.77 | 12.40 / 12.98 | 13.14 / 13.76 | 15.06 / 15.77 | 18.22 / 19.07 | 24.86 / 26.03 |
| C2 | G3.RTH.5 | 13.89 / 14.00 | 14.12 / 14.23 | 14.97 / 15.08 | 17.16 / 17.28 | 20.75 / 20.90 | 28.32 / 28.53 |
| C3 | F1_1_h1_RTH | 23.84 / 0.06 | 24.24 / 0.06 | 25.68 / 0.07 | 29.44 / 0.08 | 35.61 / 0.09 | 48.60 / 0.13 |
| C4 | F2_4_15min_vol_tercile_top | 13.08 / 1.60 | 13.29 / 1.63 | 14.09 / 1.73 | 16.15 / 1.98 | 19.53 / 2.39 | 26.66 / 3.27 |
| C5 | E-H1 scheduled macro drift | 4.00 / 37.26 | 4.06 / 37.88 | 4.31 / 40.14 | 4.94 / 46.01 | 5.97 / 55.65 | 8.15 / 75.96 |
| C6 | C-H4 passive-fill reversal | 13.45 / 0.15 | 13.67 / 0.15 | 14.48 / 0.16 | 16.60 / 0.18 | 20.08 / 0.22 | 27.41 / 0.30 |
| C7 | H6 prior-close location follow-through | 10.66 / 26.65 | 10.84 / 27.09 | 11.48 / 28.71 | 13.16 / 32.91 | 15.92 / 39.81 | 21.73 / 54.33 |

### 5a-bis. eps_min per trade ACROSS each class, not only its binding member

Smallest and largest per-trade eps_min over the class's measured members (C7: over its projected Family H rows - see the basis column).

| class | basis | members | 2019-05-06 min (member) | 2019-05-06 max (member) | 2021-01-04 min (member) | 2021-01-04 max (member) |
|---|---|---|---|---|---|---|
| C1 | measured | 6 | 2.45 (A-H1 european-open overnight drift) | 23.62 (A-H3 weekend effect) | 3.03 (A-H1 european-open overnight drift) | 29.16 (A-H3 weekend effect) |
| C2 | measured | 31 | 0.30 (G2.ETH.5) | 14.00 (G3.RTH.5) | 0.37 (G2.ETH.5) | 17.28 (G3.RTH.5) |
| C3 | measured | 40 | 0.02 (F1_1_h1_ETH) | 5.22 (G4.RTH.60) | 0.02 (F1_1_h1_ETH) | 6.44 (G4.RTH.60) |
| C4 | measured | 13 | 0.46 (D-H3 range-compression gate) | 3.27 (D-H4 overnight gap fade) | 0.57 (D-H3 range-compression gate) | 4.04 (D-H4 overnight gap fade) |
| C5 | measured | 4 | 1.96 (E-H4 turn-of-month long) | 37.26 (E-H1 scheduled macro drift) | 2.42 (E-H4 turn-of-month long) | 46.01 (E-H1 scheduled macro drift) |
| C6 | measured | 1 | 0.15 (C-H4 passive-fill reversal) | 0.15 (C-H4 passive-fill reversal) | 0.18 (C-H4 passive-fill reversal) | 0.18 (C-H4 passive-fill reversal) |
| C7 | projected | 6 | 26.65 (H6 prior-close location follow-through) | 40.88 (H2 NR7 opening-range breakout) | 32.91 (H6 prior-close location follow-through) | 50.47 (H2 NR7 opening-range breakout) |

### 5b. Days for a reference threshold of 1 net tick per trade

| class | member | eps_day_ref | n_a_ref | n_b_ref |
|---|---|---|---|---|
| C1 | A-H4 rth leg | 0.955 | 479,958 | 187,738 |
| C2 | G3.RTH.5 | 0.993 | 576,359 | 225,446 |
| C3 | F1_1_h1_RTH | 381.129 | 12 | 5 |
| C4 | F2_4_15min_vol_tercile_top | 8.158 | 7,563 | 2,959 |
| C5 | E-H1 scheduled macro drift | 0.107 | 4,085,609 | 1,598,104 |
| C6 | C-H4 passive-fill reversal | 92.467 | 63 | 25 |
| C7 | H6 prior-close location follow-through | 0.400 | 2,090,335 | 817,644 |

### 5c. n_b analytic sensitivity to eps_day, class binding members

| class | member | 30 | 32 | 34 | 36 | 38 | 40 |
|---|---|---|---|---|---|---|---|
| C1 | A-H4 rth leg | 191 | 168 | 149 | 133 | 119 | 108 |
| C2 | G3.RTH.5 | 247 | 218 | 193 | 172 | 154 | 139 |
| C3 | F1_1_h1_RTH | 727 | 639 | 566 | 505 | 454 | 409 |
| C4 | F2_4_15min_vol_tercile_top | 219 | 193 | 171 | 152 | 137 | 124 |
| C5 | E-H1 scheduled macro drift | 21 | 18 | 16 | 15 | 13 | 12 |
| C6 | C-H4 passive-fill reversal | 232 | 204 | 181 | 161 | 145 | 131 |
| C7 | H6 prior-close location follow-through | 146 | 128 | 114 | 101 | 91 | 82 |

## 6. Notes

- descriptive, not a criterion: sections 5a, 5b and 5c, and every eps_min / eps_ref field.
- Holm's most stringent step (alpha/58 = Bonferroni) is applied to every member, so every n_a is an upper bound on what Holm requires.
- VIF_boot is the inflation the program's own block-5 stationary bootstrap sees (Politis-Romano, p = 1/5), not the true long-run variance ratio; for a persistent series it is the smaller of the two, so the bootstrap under-corrects by design.
- V_B floored at 0.2 x gamma_0 for 0 of 101 members.
- Family H (C7) rows are projected from the coverage map's proxy rule, analytic only, never simulated; their achieved null power is measured in D.1f on the H series.
- Phi^-1 comes from statistics.NormalDist().inv_cdf (standard library); scipy is not a project dependency. The values agree with scipy.stats.norm.ppf to ~1e-15.
- Supplied days are an estimate, +/-3%; no exchange calendar file was read.
- sim_censored_below_grid_*: the shortest simulated length already reached 80% power, so the crossing was never bracketed; the figure is reported as an upper bound and the analytic sample size is kept.
- Simulation SE: SE_hat = sqrt(gamma_0_hat(x) * VIF_boot(source) / n), gamma_0_hat(x) the replicate's own sample variance (ddof = 1). A block-bootstrap replicate's lag-k autocovariance is already about (1-p)^k times the source's, so a V_B computed from the replicate attenuates the dependence term twice and understates the SE; measured on an AR(1) with phi = 0.3 that put simulated power_b at 0.848 instead of 0.80. The replicate supplies the finite-sample variance noise and the heavy tails; the dependence factor comes from the source, exactly as the analytic formula uses it (lead ruling, Stage D.1e Task 3).
- UNIT CORRECTION (reports/stage_d1e_adjudication.md, finding R-1): trial series are read from members_trials.json as daily_net_ticks_per_micro, which divides each round trip by its OWN contract quantity (trip net / ($1.25 x trip_micros)). The earlier run divided daily dollars by $2.50, assuming 2 micros for every trial; 29 trials and C-H4 code 1 micro and D-H2 and RT7 size 1 to 5 by rule, so every trial series was at half scale, every trial SD was halved and every trial sample size was a quarter of the right one. Family H per-trade SD proxies were read off the same half-scale table and are corrected with it: 200 ticks for H1-H5, 230 for H6. Statistic members are built from tick sums and were never affected.
- Chosen figure: where the simulated and analytic sizes differ by more than 15% the chosen figure is max(analytic, simulated). A simulated size below the analytic one is not evidence that fewer days suffice: for a heavy-tailed member at short lengths the replicate's variance estimate is right-skewed, so the closed-form UCB under-covers there and adopting the smaller figure would plan on an anti-conservative test. Where the simulation asks for MORE days the simulated figure is used (sim_used_larger_*); where it asks for fewer it is recorded and ignored (sim_smaller_ignored_*). Both figures and the difference stay in every row (lead ruling, Stage D.1e Task 3).
- classes[c].resolution_range is descriptive: the spread of eps_min ACROSS a class's measured members at each supplied-days start, not only at its binding member. C7 has no measured member, so its range is over the projected Family H rows (basis field).
- spot_check.percentile_success is a check of the closed form against the percentile construction inside the bootstrap world, biased upward for autocorrelated members by the same double attenuation; it is not a check of the absolute level.
