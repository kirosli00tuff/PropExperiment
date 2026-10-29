# Stage E.33c Part D statistics (branch N: Tier A empty)

Written 2026-10-28 20:57:28 PDT by StatsCoder-OpusXHigh (reports/stage_e33c_briefs/work/stats/run_dstats.py, make_md.py; figure plot_dstats.py). Every number below is in work/D_stats.json (sha256 in the return); the full per-configuration table is /mnt/large-storage/market_data/PropExperiment/derived/e33/stats_c/per_config_full.json (sha256 11baf24ae32e219d...).

- Protocol 0.3 sha256 a2a2856f49723f97... (checked equal to a2a2856f...; refuse otherwise).
- Selection: reports/stage_e33c_briefs/select/P8_select33.json sha256 ee506884263d712e... (frozen select33.py, N 838, b_test 0.164882, Tier B reading continue). Reported, never re-selected.
- Search root /mnt/large-storage/market_data/PropExperiment/derived/e33/search/<cid>/ (stats.json, daily.parquet, trades.parquet), 300/300 DONE; feature store 2b30cb0e953b (_day sigma_zm), label store b15c4ca10d68 (not read: no item here needs it).
- OOF dates: 796, 2020-12-30 .. 2024-02-29; asserted inside 2020-12-01..2024-02-29, none in the test window 2017-05-01..2020-11-30, none on or after 2024-03-01.
- Thresholds recomputed with p7_final.py's functions at N 838 (T_disc 796, T_test 870): SR0 0.1137, G3 0.1724 (skew -0.5, kurtosis 6: 0.1756), b_test 0.164882, G4 0.2007, binding 0.2007. N is 838, so P7.2's lines stand.
- Scope (branch N): D1, D3, P10 (i)-(vi). D2 does not apply (no configuration passes D1). No P6.4 or P6.5 item is computed (they run only after a hashed test list; there is none). Item (vii) is the lead's.

## 0. Independent recomputation against select33 and the search's stats.json

My gate code (dstats_lib.evaluate, written from the P8 text and readings P01-P08) and select33 agree on every number; no disagreement to report. Source: D_stats.json agreement_with_select33.

| check | result |
|---|---|
| funnel (alone and in order) | yes |
| P8 total order of all 300 | yes |
| BH / Holm rejection counts | yes |
| one-sided p, max abs diff | 0.0e+00 |
| PBO report (all fields) | yes |
| b_test, abs diff | 0.0e+00 |
| configurations with any gate flag different | 0 |
| configurations with any G5 part different | 0 |
| max abs diff vs select33 over SR_d, t, DSR, se, SR - se, counts, mean net, G5 values | 0.0e+00 |
| max abs diff vs stats.json over moments, t, counts, hit rate, fold/quarter/month sums, terciles | 1.8e-15 |

## D1 and P10 (i): the gate funnel (P8; Topstep, market, L = 1 s)

Source: my recomputation from daily.parquet (D_stats.json funnel, configs.*.gates) beside select33's P8_select33.json funnel. Failed configurations: 0.

| gate | alone (mine) | alone (select33) | in order G1.. (mine) | in order (select33) |
|---|---|---|---|---|
| G1 | 61 | 61 | 61 | 61 |
| G2 | 8 | 8 | 0 | 0 |
| G3 | 0 | 0 | 0 | 0 |
| G4 | 0 | 0 | 0 | 0 |
| G5 | 0 | 0 | 0 | 0 |

- G1 (>= 796 trades and a trade on >= 398 dates): 61 pass; by set {'S1': 0, 'S2': 10, 'S3': 12, 'S4': 16, 'S5': 23}; by label {'F05': 0, 'F15': 0, 'F30': 2, 'F60': 20, 'T15': 5, 'T30': 34}. The best G1 passer by SR_d is E33-S3F60L001A at -0.0522; the largest mean net per trade among G1 passers is -1.098 ticks (all 61 are negative).
- G2 (mean net per trade >= 0.50): 8 pass alone, none of them with G1 (largest trade count 55; table below).
- G3 (DSR > 0.95 at N 838): 0; largest DSR 0.0248 (E33-S2F30G2200).
- G4 (SR_d - se >= b_test 0.164882): 0; largest SR_d - se 0.0305 (E33-S1F15G3200).
- G5 parts over the 300: (a) >= 9 of 13 quarters positive: 0 (most quarters positive in any configuration: 6); (b) total > 0 and no month above 25%: 0 (total > 0: 10); (c) every leave-one-month-out t >= 2.5: 0; (d) all three sigma_ZM terciles positive: 1; all four: 0.
- Tier A: [] (empty). Tier B as select33 wrote it (reading continue): ['E33-S2F30G2200', 'E33-S1F15G3200']; with Tier A empty P8 writes no test list, so Tier B has no use; it is reported, not recomputed here.

## D1: mean net per trade by firm (market entry and exit, L = 1 s)

The fills are the selection variant's; only the round-trip fee differs, so net_firm = net_Topstep + 0.528 - fee (dstats_lib.firm_net). This is a fee shift on the P8 series for all 300, not P6.4's execution variants (limit routes, L = 0.300 s), which are not computed. Lucid at 0.560 and, if the 5.60 USD is not all-in, 0.920 (reading K01). Over the 222 configurations with trades. Source: D_stats.json firm_summary, configs.*.firm_mean_net_per_trade.

| firm | fee (ticks/RT) | configs with trades | mean net >= 0.50 | mean net > 0 | median | max | max at |
|---|---|---|---|---|---|---|---|
| Bulenox | 0.572 | 222 | 8 | 10 | -2.251 | 8.428 | E33-S1F15G3200 |
| Lucid | 0.560 | 222 | 8 | 10 | -2.239 | 8.440 | E33-S1F15G3200 |
| Lucid_not_all_in | 0.920 | 222 | 6 | 8 | -2.599 | 8.080 | E33-S1F15G3200 |
| MFFU | 0.612 | 222 | 8 | 10 | -2.291 | 8.388 | E33-S1F15G3200 |
| Topstep | 0.528 | 222 | 8 | 10 | -2.207 | 8.472 | E33-S1F15G3200 |
| Tradeify | 0.920 | 222 | 6 | 8 | -2.599 | 8.080 | E33-S1F15G3200 |

The 8 G2 passers (all fail G1):

| config | trades | dates with a trade | SR_d | Bulenox | Lucid | Lucid_not_all_in | MFFU | Topstep | Tradeify |
|---|---|---|---|---|---|---|---|---|---|
| E33-S2F30G2200 | 55 | 47 | 0.0478 | 4.355 | 4.367 | 4.007 | 4.315 | 4.399 | 4.007 |
| E33-S1F15G3200 | 8 | 2 | 0.0473 | 8.428 | 8.440 | 8.080 | 8.388 | 8.472 | 8.080 |
| E33-S2F30L001A | 13 | 10 | 0.0452 | 7.428 | 7.440 | 7.080 | 7.388 | 7.472 | 7.080 |
| E33-S5F15G2050 | 39 | 4 | 0.0426 | 2.018 | 2.030 | 1.670 | 1.978 | 2.062 | 1.670 |
| E33-S5F15G3050 | 36 | 7 | 0.0225 | 0.567 | 0.579 | 0.219 | 0.527 | 0.611 | 0.219 |
| E33-S3F30L001A | 14 | 12 | 0.0140 | 1.357 | 1.369 | 1.009 | 1.317 | 1.401 | 1.009 |
| E33-S2F30L100A | 30 | 22 | 0.0084 | 0.895 | 0.907 | 0.547 | 0.855 | 0.939 | 0.547 |
| E33-S2F30L100E | 26 | 18 | 0.0067 | 0.774 | 0.786 | 0.426 | 0.734 | 0.818 | 0.426 |

## D1: trade counts and trades per date

Total trades over the 300: 162,189; configurations with no trade: 78 (constant series, SR_d 0 by moments()); largest count 3,905; largest trades per date 4.906. P3.2 counts summed over the 300 (stats.json counts): {'entries_not_made': 0, 'entry_fallback_fills': 0, 'exit_fallback_fills': 0, 'exit_last_touch_marks': 0, 'exit_limit_marks': 0, 'not_made_flag16': 0, 'not_made_flag32': 0}. By label (D_stats.json mde.horizons):

| label | configs | with trades | trades (pooled) | median trades/date (traded) | max trades/date | G1 passers |
|---|---|---|---|---|---|---|
| F05 | 50 | 5 | 16 | 0.004 | 0.005 | 0 |
| F15 | 50 | 28 | 876 | 0.009 | 0.207 | 0 |
| F30 | 50 | 44 | 9,695 | 0.181 | 1.099 | 2 |
| F60 | 50 | 45 | 40,685 | 0.969 | 2.436 | 20 |
| T15 | 50 | 50 | 24,957 | 0.455 | 2.770 | 5 |
| T30 | 50 | 50 | 85,960 | 2.231 | 4.906 | 34 |

Per-configuration trade counts, trades per date and dates with a trade: D_stats.json configs.*.

## D1: DSR at N, BH and Holm (reports, never gates)

- DSR (funnel.multiple_comparisons.deflated_sharpe_ratio, N 838, V = 1/795, T 796, own skewness and raw kurtosis): largest 0.0248; above 0.95: 0; undefined (constant series): 78. Per configuration: D_stats.json configs.*.dsr.
- BH (q 0.05) and Holm (0.05) over m = 300 one-sided p = 1 - Phi(daily t) (reading P07; no t -> p = 1): BH rejects 0, Holm rejects 0; smallest p 0.0888 (E33-S2F30G2200, t 1.348).
- Reference z (P7.2, select33): Bonferroni/Holm step 1 at m 300 3.588; BY rank 1 4.042; Bonferroni at N 838 3.847; HLZ t 3.0. The largest daily t of the 300 is 1.348.

## D1 and P10 (iv): discovery PBO (CSCV; reported, not a gate)

screening.stage_e_verdict.pbo over 300 series (reading P08: every configuration with a series, the 78 constant ones included; 0 failed), 8 blocks of 99 dates, 70 splits: PBO = 0.1429 (10 of 70), against M5a e's null band 0.13-0.83 (P6.3). The in-sample winner's out-of-sample net (4 blocks, ticks) averages -57.18, positive in 0.614 of the splits. Mechanical note: the median SR_d of the 300 is -0.0706, so an in-sample winner can rank above the out-of-sample median with a negative out-of-sample net, as the mean above shows. Source: D_stats.json pbo (equal to select33's reports.pbo).

## D1: G5 parts and the largest month's share of the total net

The share is defined only when the total net is positive (10 configurations); all of them fail G5 (b). Every configuration's G5 values: D_stats.json configs.*.g5.

| config | total net (ticks) | largest month | its net | share of total | quarters > 0 (of 13) | min leave-one-month-out t | tercile means (low/mid/high sigma) |
|---|---|---|---|---|---|---|---|
| E33-S2F30G2200 | 241.96 | 2023-03 | 107.36 | 0.444 | 5 | 0.86 | 0.271 / 0.541 / 0.101 |
| E33-S1F15G3200 | 67.78 | 2022-02 | 45.89 | 0.677 | 2 | 1.00 | 0.000 / 0.000 / 0.255 |
| E33-S2F30L001A | 97.14 | 2021-11 | 71.94 | 0.741 | 2 | 0.51 | 0.424 / -0.028 / -0.029 |
| E33-S5F15G2050 | 80.41 | 2024-01 | 64.78 | 0.806 | 2 | 0.91 | 0.262 / 0.059 / -0.018 |
| E33-S5F15G3050 | 21.99 | 2024-01 | 30.72 | 1.397 | 2 | -0.53 | 0.159 / -0.058 / -0.018 |
| E33-S3F30L001A | 19.61 | 2023-11 | 32.42 | 1.653 | 3 | -0.34 | -0.031 / 0.009 / 0.095 |
| E33-S2F30L100A | 28.16 | 2021-11 | 88.42 | 3.140 | 4 | -0.65 | 0.270 / -0.164 / 0.001 |
| E33-S2F30L100E | 21.27 | 2021-11 | 88.42 | 4.156 | 3 | -0.79 | 0.336 / -0.164 / -0.091 |
| E33-S1T15G2200 | 14.15 | 2023-11 | 38.50 | 2.720 | 2 | -0.32 | -0.000 / -0.025 / 0.079 |
| E33-S2F30L010A | 5.69 | 2021-11 | 88.42 | 15.544 | 4 | -0.91 | 0.211 / -0.164 / -0.025 |

## P10 (ii): the 10 best configurations by SR_d with every P6.2 statistic

Order: P8's total order over all 300, gates ignored (round(SR_d, 4) descending, then the tie-breaks), identical to select33's ranking_all. Recomputed from daily.parquet and trades.parquet and equal to each stats.json to 1.8e-15; the three reported-only statistics (rho, mid-sign hit rate, top decile) are stats.json's reported_only fields (computed by the search from the fold predictions; not recomputed). Source: D_stats.json top10.

| # | config | SR_d | t | mean/day | SD/day | skew | raw kurt | trades | trades/date | mean net/trade | hit rate | share dates traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | E33-S2F30G2200 | 0.0478 | 1.35 | 0.304 | 6.361 | 2.94 | 61.9 | 55 | 0.069 | 4.399 | 0.564 | 0.059 |
| 2 | E33-S1F15G3200 | 0.0473 | 1.33 | 0.085 | 1.800 | 22.93 | 553.8 | 8 | 0.010 | 8.472 | 0.875 | 0.003 |
| 3 | E33-S2F30L001A | 0.0452 | 1.27 | 0.122 | 2.702 | 12.41 | 260.6 | 13 | 0.016 | 7.472 | 0.615 | 0.013 |
| 4 | E33-S5F15G2050 | 0.0426 | 1.20 | 0.101 | 2.372 | 25.81 | 696.2 | 39 | 0.049 | 2.062 | 0.513 | 0.005 |
| 5 | E33-S5F15G3050 | 0.0225 | 0.64 | 0.028 | 1.225 | 11.62 | 230.1 | 36 | 0.045 | 0.611 | 0.500 | 0.009 |
| 6 | E33-S3F30L001A | 0.0140 | 0.39 | 0.025 | 1.762 | 8.20 | 199.6 | 14 | 0.018 | 1.401 | 0.429 | 0.015 |
| 7 | E33-S2F30L100A | 0.0084 | 0.24 | 0.035 | 4.226 | 8.10 | 161.8 | 30 | 0.038 | 0.939 | 0.533 | 0.028 |
| 8 | E33-S2F30L100E | 0.0067 | 0.19 | 0.027 | 4.014 | 9.76 | 195.0 | 26 | 0.033 | 0.818 | 0.500 | 0.023 |
| 9 | E33-S1T15G2200 | 0.0053 | 0.15 | 0.018 | 3.341 | -2.06 | 46.9 | 66 | 0.083 | 0.214 | 0.576 | 0.057 |
| 10 | E33-S2F30L010A | 0.0017 | 0.05 | 0.007 | 4.166 | 8.36 | 171.1 | 29 | 0.036 | 0.196 | 0.517 | 0.026 |

Gates, DSR, power and reported-only statistics:

| config | gates passed | DSR | se | SR_d - se | p (one-sided) | tercile means | rho EV-net (rows) | rho (trades) | mid-sign hit | top-decile mean net |
|---|---|---|---|---|---|---|---|---|---|---|
| E33-S2F30G2200 | G2 | 0.0248 | 0.0335 | 0.0142 | 0.0888 | 0.271 / 0.541 / 0.101 | -0.011 | -0.013 | 0.600 (n 55) | -2.381 (n 16693) |
| E33-S1F15G3200 | G2 | 0.0000 | 0.0168 | 0.0305 | 0.0910 | 0.000 / 0.000 / 0.255 | -0.022 | 0.277 | 0.875 (n 8) | -2.663 (n 17827) |
| E33-S2F30L001A | G2 | 0.0053 | 0.0268 | 0.0183 | 0.1013 | 0.424 / -0.028 / -0.029 | -0.011 | 0.566 | 0.692 (n 13) | -2.278 (n 16693) |
| E33-S5F15G2050 | G2 | 0.0000 | 0.0165 | 0.0261 | 0.1148 | 0.262 / 0.059 / -0.018 | -0.001 | -0.251 | 0.605 (n 38) | -2.131 (n 17827) |
| E33-S5F15G3050 | G2 | 0.0017 | 0.0311 | -0.0085 | 0.2623 | 0.159 / -0.058 / -0.018 | -0.003 | -0.233 | 0.588 (n 34) | -2.075 (n 17827) |
| E33-S3F30L001A | G2 | 0.0015 | 0.0336 | -0.0196 | 0.3466 | -0.031 / 0.009 / 0.095 | -0.016 | 0.534 | 0.500 (n 14) | -2.266 (n 16693) |
| E33-S2F30L100A | G2 | 0.0011 | 0.0343 | -0.0259 | 0.4066 | 0.270 / -0.164 / 0.001 | -0.009 | 0.097 | 0.586 (n 29) | -2.143 (n 16693) |
| E33-S2F30L100E | G2 | 0.0009 | 0.0343 | -0.0277 | 0.4255 | 0.336 / -0.164 / -0.091 | -0.008 | 0.214 | 0.560 (n 25) | -2.207 (n 16693) |
| E33-S1T15G2200 | none | 0.0012 | 0.0357 | -0.0303 | 0.4403 | -0.000 / -0.025 / 0.079 | -0.006 | -0.014 | 0.462 (n 65) | -2.107 (n 17827) |
| E33-S2F30L010A | none | 0.0007 | 0.0352 | -0.0335 | 0.4807 | 0.211 / -0.164 / -0.025 | -0.009 | 0.210 | 0.571 (n 28) | -2.200 (n 16693) |

Per-fold sums (P6.1 blocks 1-6, ticks):

| config | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| E33-S2F30G2200 | 0.00 | 75.16 | 0.00 | 0.00 | 166.80 | 0.00 |
| E33-S1F15G3200 | 0.00 | 0.00 | 67.78 | 0.00 | 0.00 | 0.00 |
| E33-S2F30L001A | 0.00 | 67.83 | 0.00 | 0.00 | 0.00 | 29.30 |
| E33-S5F15G2050 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 80.41 |
| E33-S5F15G3050 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 21.99 |
| E33-S3F30L001A | -1.53 | -5.53 | 0.00 | 22.47 | 0.00 | 4.19 |
| E33-S2F30L100A | 0.00 | 28.61 | 9.47 | -49.06 | 0.47 | 38.66 |
| E33-S2F30L100E | 0.00 | 33.14 | 0.00 | -49.06 | 0.47 | 36.72 |
| E33-S1T15G2200 | 0.00 | 0.00 | 0.00 | 1.50 | 0.00 | 12.66 |
| E33-S2F30L010A | 0.00 | 28.61 | 9.47 | -49.06 | 0.47 | 16.19 |

Per-quarter sums (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov, named by the first month; ticks):

| quarter | S2F30G2200 | S1F15G3200 | S2F30L001A | S5F15G2050 | S5F15G3050 | S3F30L001A | S2F30L100A | S2F30L100E | S1T15G2200 | S2F30L010A |
|---|---|---|---|---|---|---|---|---|---|---|
| 2020-12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-06 | 3.38 | 0.00 | 0.00 | 0.00 | 0.00 | -7.06 | -18.53 | -18.53 | 0.00 | -18.53 |
| 2021-09 | 54.36 | 0.00 | 71.94 | 0.00 | 0.00 | 0.00 | 83.89 | 88.42 | 0.00 | 83.89 |
| 2021-12 | 17.42 | 45.89 | -4.11 | 0.00 | 0.00 | 0.00 | -36.75 | -36.75 | 0.00 | -36.75 |
| 2022-03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-06 | 0.00 | 21.89 | 0.00 | 0.00 | 0.00 | 0.00 | 9.47 | 0.00 | -2.86 | 9.47 |
| 2022-09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -18.53 | -18.53 | 4.36 | -18.53 |
| 2022-12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 22.47 | -30.53 | -30.53 | 0.00 | -30.53 |
| 2023-03 | 108.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-06 | 58.19 | 0.00 | 0.00 | 0.00 | 0.00 | 4.47 | 0.47 | 0.47 | 0.00 | 0.47 |
| 2023-09 | 0.00 | 0.00 | -2.11 | 20.44 | 5.08 | 8.83 | 52.83 | 37.36 | 38.80 | 37.36 |
| 2023-12 | 0.00 | 0.00 | 31.42 | 59.97 | 16.91 | -9.11 | -14.17 | -0.64 | -26.14 | -21.17 |

Per-month sums (ticks):

| month | S2F30G2200 | S1F15G3200 | S2F30L001A | S5F15G2050 | S5F15G3050 | S3F30L001A | S2F30L100A | S2F30L100E | S1T15G2200 | S2F30L010A |
|---|---|---|---|---|---|---|---|---|---|---|
| 2020-12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -1.53 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-07 | 26.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-08 | -23.53 | 0.00 | 0.00 | 0.00 | 0.00 | -5.53 | -18.53 | -18.53 | 0.00 | -18.53 |
| 2021-09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2021-10 | -10.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -4.53 | 0.00 | 0.00 | -4.53 |
| 2021-11 | 64.42 | 0.00 | 71.94 | 0.00 | 0.00 | 0.00 | 88.42 | 88.42 | 0.00 | 88.42 |
| 2021-12 | 17.42 | 0.00 | -19.53 | 0.00 | 0.00 | 0.00 | -41.64 | -41.64 | 0.00 | -41.64 |
| 2022-01 | 0.00 | 0.00 | 15.42 | 0.00 | 0.00 | 0.00 | 4.89 | 4.89 | 0.00 | 4.89 |
| 2022-02 | 0.00 | 45.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-06 | 0.00 | 21.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.47 | 0.00 | 0.00 | 9.47 |
| 2022-08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -2.86 | 0.00 |
| 2022-09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -18.53 | -18.53 | 0.00 | -18.53 |
| 2022-10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.36 | 0.00 |
| 2022-11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2022-12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -30.53 | -30.53 | 0.00 | -30.53 |
| 2023-01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 22.47 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-03 | 107.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-04 | 1.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-06 | 38.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-08 | 19.36 | 0.00 | 0.00 | 0.00 | 0.00 | 4.47 | 0.47 | 0.47 | 0.00 | 0.47 |
| 2023-09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -11.53 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2023-10 | 0.00 | 0.00 | 18.47 | 20.44 | 5.08 | -12.06 | 71.42 | 55.94 | 0.30 | 55.94 |
| 2023-11 | 0.00 | 0.00 | -20.58 | 0.00 | 0.00 | 32.42 | -18.58 | -18.58 | 38.50 | -18.58 |
| 2023-12 | 0.00 | 0.00 | 12.94 | -4.81 | -4.75 | -7.06 | 27.89 | 12.89 | -30.17 | 20.89 |
| 2024-01 | 0.00 | 0.00 | 18.47 | 64.78 | 30.72 | -2.06 | -13.53 | -13.53 | 9.78 | -13.53 |
| 2024-02 | 0.00 | 0.00 | 0.00 | 0.00 | -9.06 | 0.00 | -28.53 | 0.00 | -5.75 | -28.53 |

## D3 and P10 (iii): the 300 OOF daily Sharpes beside the null

Figure: reports/stage_e33c_briefs/work/stats/fig/D3_sharpe_hist.png. Top: the 300 real SR_d and the 400 null per-configuration SR_d (B5: 20 null seeds x S5 x {F15, T30} x 10 grid points; same statistic, same 796 dates; derived/e33/proofs/seed1..20/search/<cid>/daily.parquet, recomputed and equal to each stats.json), as shares of each group per 0.01 bin; no-trade series sit at 0 (moments() convention). Bottom: the 20 null per-seed maxima, each a maximum over 20 configurations, not the null of the maximum over 300. Lines: SR0 0.1137, G3 0.1724, binding 0.2007 (p7_final at N 838).

| series | n | mean | SD | q05 | median | q95 | max |
|---|---|---|---|---|---|---|---|
| real E.33 (all 300) | 300 | -0.0840 | 0.0839 | -0.2603 | -0.0706 | 0.0000 | 0.0478 |
| real, with trades | 222 | -0.1135 | 0.0786 | -0.2651 | -0.0977 | -0.0093 | 0.0478 |
| null per-configuration (all 400) | 400 | -0.1194 | 0.0937 | -0.2809 | -0.0988 | 0.0000 | 0.0602 |
| null, with trades | 369 | -0.1295 | 0.0906 | -0.2820 | -0.1091 | 0.0014 | 0.0602 |
| null per-seed max over 20 configs | 20 | -0.0014 |  | -0.0586 | 0.0058 | 0.0514 | 0.0602 |

- Real configurations at or above SR0: 0; G3: 0; binding: 0; SR_d > 0: 10; above the null 400's q95 (3.5e-05): 10; above the null 400's max (0.0602): 0. The real max 0.0478 lies inside the range of the null per-seed maxima over only 20 configurations (-0.0757 to 0.0602).
- The per-seed maxima agree with B5_proofs.md's table in 20 of 20 seeds (same configuration, same SR_d to 4 decimals). Null constants: 31 of 400; with trades 369 (B5's line 41 says 368: that is the count in configurations with at least 2 non-constant seeds, 368; its 0.0434 reproduces either way). Centred SD of the 400 (P4.2): 0.0425 (B5: 0.0425).
- Real 300: mean pairwise correlation of the 222 non-constant daily series 0.064; share of pairs above 0.70 0.0095.

Expected null maximum over 300 (brief addendum). Method: REPORT, not a gate. The null's per-configuration spread is P4.2's statistic: the SD of the 400 null daily Sharpes, each centred on its configuration's mean over the 20 seeds (sigma_c, population; df-corrected x sqrt(20/19)). Zero-edge null for the 300: every configuration's true daily Sharpe 0, independent sampling errors with SD sigma_c; E[max over n] = expected_max_sharpe(n, sigma_c^2) (Bailey and Lopez de Prado 2014 eq. 3, the program's function; the same construction as SR0, which uses 1/sqrt(T_disc - 1) in place of sigma_c). Check of the construction at n = 20 in B5's own setting: E[max_c (mu_c + sigma_c,df eps_c)] by Monte Carlo (100,000 draws, seed 20261028; mu_c = each null configuration's mean over the seeds) against the mean of the 20 observed per-seed maxima. Caveats: independence overstates the max for correlated configurations; true Sharpes of a real null search are below 0 by costs (the B5 null mean is negative), which lowers the max; the null covers S5 x {F15, T30} only.

- sigma_c 0.0425 (df-corrected 0.0436); E[max over 300] = 0.1230 (0.1262 df-corrected); over 838: 0.1397.
- Check at n = 20: the construction gives 0.0297 against the observed mean of the 20 per-seed maxima -0.0014 (SE 0.0082): it overstates by 0.0311. The null's Sharpe errors are positively correlated across one seed's configurations (mean pairwise 0.203), so the independent figure is an upper-side value.
- Not used: pooling the 400 values as iid (mean -0.1194, SD 0.0937) predicts 0.0586 at n = 20 against the observed -0.0014; it mixes the configurations' different null means into the spread.

## P10 (v): minimum detectable net edge per trade at 80% power on the OOF dates

Formula: e80 = s80 x sigma_h / sqrt(n): P7.2 'Per trade (random-walk sigma_h; independent trades every date): 0.71 ticks net at 5-minute holds and 4 trades a date ...' (p7_final 'mu at selection threshold' = threshold x sigma_h / sqrt(n), sigma_h = 3.15 sqrt(h)), with the threshold replaced by s80 = bar + z_0.80 se(bar), se = sqrt((1 + bar^2/2)/(T_disc - 1)) (p7_final's s80 convention, its test line '80% power needs a true daily Sharpe of 0.1936'), T_disc = 796. Source line in P7.2: "Per trade (random-walk sigma_h; independent trades every date): 0.71 ticks net at 5-minute holds and 4 trades a date (0.50 at 8); 1.22 at 15 minutes and 4 a date (0.87 at 8); 1.73 at 30 minutes and 4 a date; 3.46 at 60 minutes and 2 a date." That line is the edge at the selection threshold itself (about 50% power); the tests reproduce it to the printed digits.
- 80%-power true daily Sharpe on T_disc 796: at the binding threshold 0.2007, s80 = 0.2309 (se at the true value instead: 0.2309); at G3 alone 0.1724, s80 = 0.2025.
- Selection also needs G2 (>= 0.50 net per trade) and G1 (>= 1 trade a date), so an e80 below 0.50 is not enough by itself. TB labels use the vertical h (an upper bound on the hold). Measured sigma is the population SD of the realised per-trade nets pooled over the label's 50 configurations (stated beside the 3.15 sqrt(h) standard number; P0.4: standard numbers are for power only).

| label | trades/date n | sigma_h (3.15 sqrt h) | sigma measured | trades pooled | edge at binding (P7.2 line) | e80 at G3 | e80 at binding | e80 at binding, measured sigma |
|---|---|---|---|---|---|---|---|---|
| F05 | 1 | 7.04 | 2.77 | 16 | 1.41 | 1.43 | 1.63 | 0.64 |
| F05 | 2 | 7.04 | 2.77 | 16 | 1.00 | 1.01 | 1.15 | 0.45 |
| F05 | 4 | 7.04 | 2.77 | 16 | 0.71 | 0.71 | 0.81 | 0.32 |
| F05 | 8 | 7.04 | 2.77 | 16 | 0.50 | 0.50 | 0.57 | 0.23 |
| F05 | 12 | 7.04 | 2.77 | 16 | 0.41 | 0.41 | 0.47 | 0.18 |
| F15 | 1 | 12.20 | 15.37 | 876 | 2.45 | 2.47 | 2.82 | 3.55 |
| F15 | 2 | 12.20 | 15.37 | 876 | 1.73 | 1.75 | 1.99 | 2.51 |
| F15 | 4 | 12.20 | 15.37 | 876 | 1.22 | 1.24 | 1.41 | 1.77 |
| F15 | 8 | 12.20 | 15.37 | 876 | 0.87 | 0.87 | 1.00 | 1.25 |
| F15 | 12 | 12.20 | 15.37 | 876 | 0.71 | 0.71 | 0.81 | 1.02 |
| F30 | 1 | 17.25 | 19.50 | 9695 | 3.46 | 3.49 | 3.98 | 4.50 |
| F30 | 2 | 17.25 | 19.50 | 9695 | 2.45 | 2.47 | 2.82 | 3.18 |
| F30 | 4 | 17.25 | 19.50 | 9695 | 1.73 | 1.75 | 1.99 | 2.25 |
| F30 | 8 | 17.25 | 19.50 | 9695 | 1.22 | 1.24 | 1.41 | 1.59 |
| F60 | 1 | 24.40 | 23.38 | 40685 | 4.90 | 4.94 | 5.63 | 5.40 |
| F60 | 2 | 24.40 | 23.38 | 40685 | 3.46 | 3.49 | 3.98 | 3.82 |
| T15 | 1 | 12.20 | 10.51 | 24957 | 2.45 | 2.47 | 2.82 | 2.43 |
| T15 | 2 | 12.20 | 10.51 | 24957 | 1.73 | 1.75 | 1.99 | 1.72 |
| T15 | 4 | 12.20 | 10.51 | 24957 | 1.22 | 1.24 | 1.41 | 1.21 |
| T15 | 8 | 12.20 | 10.51 | 24957 | 0.87 | 0.87 | 1.00 | 0.86 |
| T15 | 12 | 12.20 | 10.51 | 24957 | 0.71 | 0.71 | 0.81 | 0.70 |
| T30 | 1 | 17.25 | 14.34 | 85960 | 3.46 | 3.49 | 3.98 | 3.31 |
| T30 | 2 | 17.25 | 14.34 | 85960 | 2.45 | 2.47 | 2.82 | 2.34 |
| T30 | 4 | 17.25 | 14.34 | 85960 | 1.73 | 1.75 | 1.99 | 1.66 |
| T30 | 8 | 17.25 | 14.34 | 85960 | 1.22 | 1.24 | 1.41 | 1.17 |

Measured, per configuration (no random-walk or independence assumption): e80 = s80 x SD(X_D) / (trades per date), the per-trade shift that gives the configuration's own daily series a true daily Sharpe of s80 (binding) from a zero mean:

| label | configs with trades | min | q25 | median | G1 passers | G1 min | G1 median |
|---|---|---|---|---|---|---|---|
| F05 | 5 | 20.97 | 20.97 | 23.24 | 0 | n/a | n/a |
| F15 | 28 | 6.25 | 12.07 | 24.39 | 0 | n/a | n/a |
| F30 | 44 | 4.23 | 7.05 | 12.55 | 2 | 4.23 | 4.37 |
| F60 | 45 | 3.28 | 4.38 | 5.58 | 20 | 3.28 | 4.33 |
| T15 | 50 | 1.56 | 2.79 | 3.99 | 5 | 1.56 | 1.57 |
| T30 | 50 | 1.47 | 1.82 | 2.16 | 34 | 1.47 | 1.95 |

F05 and F15 configurations traded rarely (pooled 16 and 876 trades), so their measured sigma and per-configuration values rest on few trades. Source: D_stats.json mde.

## P10 (vi): a null statement per family in the sense of docs/NULL_CRITERIA_E.md

Criteria file docs/NULL_CRITERIA_E.md sha256 b27ca69cf8f3ec41.... Family = feature set (P10: the cut unit, "a whole feature set ... which is the 'family' of the prompt's C3"), with its P2 idea family. The criterion, quoted (each string checked verbatim against the file, block-quote markers removed):

- section 1: "tested on the pre-registered confirmation windows (trade dates S_X to 2024-02-29 for each exposure X" (found: yes)
- section 1: "Members and their definitions: {reports/stage_e1_confirmation_list_K#.md, sha256}" (found: yes)
- section 3: "Null for a cluster: every member (Tier A and Tier B, D5) has UCB95 < eps_X and achieved null power" (found: yes)
- section 3: "Rules found by the Stage E ML route are pre-registered and tested as ordinary members" (found: yes)
- section 6: "signals needing order-book data; constructions not on the frozen lists" (found: yes)
- section 1: "The statement is made per cluster, never for" (found: yes)

ZM belongs to cluster K6, whose hashed list reports/stage_e22_k6_confirmation_list.json (sha256 ebb3d034ed001498...) has 27 members, ZM window 2019-05-06..2024-02-29, eps_ZM 5 ticks a day (50.0 USD at q 1); its ZM members are K6-cp1-01 ZM, K6-cp2-01 ZM, K6-cp3-01 ZM. No E.33 configuration is a member.

| set | idea family | configs | with trades | G1 | SR_d > 0 | best with trades | statement |
|---|---|---|---|---|---|---|---|
| S1 | F1 crush-residual reversion (+C) | 60 | 47 | 0 | 2 | S1F15G3200 0.0473 (8 trades) | no statement |
| S2 | F2 cross-asset propagation (+C) | 60 | 37 | 10 | 5 | S2F30G2200 0.0478 (55 trades) | no statement |
| S3 | F3 ZM order flow and book state (+C) | 60 | 43 | 12 | 1 | S3F30L001A 0.0140 (14 trades) | no statement |
| S4 | F4 ZM own price path (+C) | 60 | 45 | 16 | 0 | S4F15G3050 -0.0177 (46 trades) | no statement |
| S5 | pooled F1-F4 (+C) | 60 | 50 | 23 | 2 | S5F15G2050 0.0426 (39 trades) | no statement |

Reasons, the same for every family:
- not members of a hashed confirmation list (section 1; section 6 'constructions not on the frozen lists'); ZM's cluster K6 list holds 27 members, none an E.33 configuration
- the 796 OOF dates are discovery (search) dates, not a pre-registered confirmation read; an ML-route rule becomes a member only after pre-registration and a test (section 3, U6)
- every set includes C.3 (ZM spread) and C.4 (ZM touch depth) from the MBO book and trades at book prices: 'signals needing order-book data' are out of scope (section 6)
- no UCB95 or SE_boot (section 3) is computed for these series: the comparable day-block bootstrap is a P6.5 item, run only after a hashed test list; with it, reasons 1-3 would still stand

Not a null statement, and not a reason above:
- What the data do show is not a null statement: no configuration of any family passes G3 or G4 on the discovery dates, and the minimum detectable edges above say what size of edge this search could have selected.

## Not done, and limits

- P6.4 (per-firm execution variants beyond the market fee shift, L = 0.300 s, limit routes) and P6.5 (reversed walk-forward, splits by year, release day and roll phase, MDA, SFI, VECM, block-bootstrap intervals, decay, robustness, calibration): not computed; they run only after a hashed test list (P8, last bullet) and Tier A is empty.
- D2: not applicable (no configuration passes D1). P10 (vii): the lead's.
- The reported-only P6.2 statistics (rho, mid-sign hit rate, top-decile net) are quoted from stats.json, not recomputed (they need the fold predictions and the label store).
- Tier B: reported as select33 wrote it; the walk is not recomputed (with Tier A empty it has no use).
- The expected null maximum over 300 is a report with an upward bias shown by its own n = 20 check.

