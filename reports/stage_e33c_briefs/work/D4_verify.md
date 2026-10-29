# Stage E.33c Part D4: independent recomputation of the selection (VerifyWorker-FableXHigh)

Worker: VerifyWorker-FableXHigh (Fable 5.1, xhigh, fresh context). Brief: reports/stage_e33c_briefs/brief_VerifyWorker_c.md
with its E.33c addendum. Branch N (the pipeline reports Tier A empty). Started 2026-10-28 20:40 PDT; finished 20:57 PDT.

## Verdict

**The selection decision is CONFIRMED: no configuration passes G1-G5, Tier A is empty, no test list and no purchase (P8;
P10's null report).** Recomputed from the raw out-of-fold predictions (search/<cid>/fold<k>.npz, fold<k>.model.json) and
the label store alone, with code written for this check, the funnel is G1 61, G2 8, G3 0, G4 0, G5 0 alone and
G1 61, G1..G2 0, G1..G3 0, G1..G4 0, G1..G5 0 in order, for all 300 configurations, the same as P8_select33.json and the
StatsCoder's D_stats.json. No gate result, funnel count, ranking position, Tier A or Tier B membership differs between the
three. Every difference found is in a reported value that no gate uses (listed in section 6: a None-versus-value
representation on the 78 no-trade series, an inverse-normal implementation difference of at most 8.9e-9 relative in my
own-formula DSR on 14 configurations, and a None-versus-min convention on the leave-one-month-out t of 8 configurations).

## 1. Inputs and their hashes (verified at the start)

- Protocol 0.3: reports/stage_e32_discovery_protocol_v0.3.md, sha256
  a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 (matches the addendum). Sections read: 0.3, P3.2-P3.8,
  P6.1-P6.3, P7.1-P7.2, P8. Readings file reports/stage_e33_protocol_readings.md: Lead readings R-L1..R-L12, the B3 rulings,
  and Appendix S01-S21 and P01-P14 (S03, S04, S06, S07, S08, S20, P01, P02, P04, P05, P06, P11, P13 and R-L8 were applied).
- Search root /mnt/large-storage/market_data/PropExperiment/derived/e33/search: 300 configuration folders, every DONE status
  "ok", pipeline_sha 323a82ff96cabbd509ba2c8dc358dcf50c3aa09cee8a22fbc2e57285739e7b64, tables_fingerprint
  be68541d487d46dfafa294171a58d73449affecfe02efb6374175d00b62f61fd, feat_sha 2b30cb0e953b, label_sha b15c4ca10d68.
  The sha256 recorded in every DONE marker (daily, trades, not_made, stats) and every fold<k>.DONE (npz, model.json) was
  recomputed and matches for all 300 configurations (1,800 folds).
- Label store labels/b15c4ca10d68 (manifest: L 1.000 s, fee 0.528, kappa 1.0, protocol c4ffb9d7 = v1.0, as the addendum
  states); feature store _day files features/2b30cb0e953b/_day (sigma_zm, 816 dates; the 796 OOF dates read).
- Calendar: pipeline/cal33.oof_dates() (796 dates 2020-12-30..2024-02-29, 49 excluded by P1.4). Every date read was asserted
  inside 2020-12-01..2024-02-29; no test-window file and nothing dated 2024-03-01 or later was opened.
- Compared against, only after my numbers were written: reports/stage_e33c_briefs/select/P8_select33.json (sha256
  ee506884263d712e92d8251f2796a1ecdc8f9de30f94caf077b07717c896ad19; select33 9b992806..., N 838, Tier B reading
  "continue"), the engine's search/<cid>/stats.json (300 files), and the StatsCoder's
  reports/stage_e33c_briefs/work/D_stats.json (sha256 fac9aea96b8d043b907a49ff82108c3d95374ff01d25bf6f00356dd8d50612ac,
  mtime 20:50 PDT; it existed when my numbers were written at 20:50, so the comparison is done, not pending).
- Disclosure: during orientation I read reports/stage_e33c_briefs/select/P8_select33.out (the stdout the addendum names
  beside the JSON), so I knew the pipeline's headline funnel and Tier B before computing. The computation below runs from the
  raw files with code that imports nothing from search33.py, select33.py or work/stats/; the JSON fields were read only
  after derived/e33/verify_c/gates_own.json and gates_parquet.json were on disk (20:50:22 PDT; compare run 20:53:20).

## 2. What was recomputed, and how (code under reports/stage_e33c_briefs/work/verify/)

- verify_common.py: constants (N 838, T_disc 796, T_test 870, V = 1/(T-1), gates' thresholds), loaders, own
  implementations of moments() and t_stat() (population SD; skew and raw kurtosis from the centred third and fourth
  moments; Sharpe = mean/SD; SD 0 gives sharpe 0, skew 0, kurtosis 3), the DSR from its formula with Python's
  statistics.NormalDist (AS241 inverse CDF) and a wrapper on the program's funnel.multiple_comparisons.deflated_sharpe_ratio,
  se(SR_d) of G4, the quarter key (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov keyed by the start month), the sigma_ZM terciles
  (ascending, ties by date, ranks 1-265, 266-530, 531-796).
- resim_all.py (run 20:48:58-20:49:31 PDT, one process, 31 s): for each of the 300 configurations, the 6 npz files are
  loaded, the classes checked to be (-1, 0, +1), mu_k checked equal between npz and model.json, EV_long = sum_k p_k mu_long_k
  and EV_short likewise per fold; the 6 folds' dates checked to partition the 796 OOF dates with the grid (i, t_ns) of every
  date equal to the label table's; then P3.8 per date: walk the grid minutes with entry_ok and a P3.5 decision (long if
  EV_long > max(EV_short, 0), short if EV_short > max(EV_long, 0), an exact tie is no trade), skip minutes before the last
  exit fill time (S04: next decision at the first grid minute with t_ns >= s_exit_ns), take s_net, s_entry_ns, s_exit_ns,
  s_flags of the chosen side from the label table when s_made, otherwise record a not-made entry and let the next minute
  decide without counting it (S03 a), stop after 20 made entries (P3.8). X_D = fsum of the nets of the trades entered on D
  (S20), 0 on dates without a trade. Output per configuration: derived/e33/verify_c/resim/<cid>.json (own daily series,
  counts, reported-only statistics, the comparison) and <cid>.trades.parquet.
- gates_all.py (20:50:09-20:50:22): P6.2 statistics, G1-G5, the funnel, the ranking key (SR_d rounded to 4 dp with
  round(), fewer trades per date, LOGIT before LGBM, lower set, shorter h with FH before TB, earlier grid), the Tier A walk
  over passers with Pearson <= 0.70, the Tier B walk continuing from the position reached (R-L8), and the near-threshold
  list; run twice, from the own re-simulated series (--source own) and from the pipeline's daily.parquet and trades.parquet
  (--source parquet). G3 is computed both with the program's function and with the own formula; G4 uses b_test solved
  independently (section 4).
- compare_select.py (20:53:20-20:53:22): field-by-field comparison with P8_select33.json, stats.json and D_stats.json at
  1e-9 relative, 1e-12 absolute for floats and exact for integers, flags and memberships; writes
  derived/e33/verify_c/compare.json and three_dates.json. report_tables.py writes report_tables.md and gates_table.csv
  (one row per configuration with the own values and the equality flags).
- Compute: nice 10, one process at a time, peak well under 1 GB; free memory never below 4.4 GB.

## 3. Re-simulation from the predictions and labels: 300 of 300 configurations equal the pipeline

| check | result |
|---|---|
| configurations re-simulated | 300 (all; the brief's minimum was the rows of sections 4-5, the rest by daily/trades) |
| daily.parquet: dates equal the 796 OOF dates; X_D equal (1e-9 rel) on every date; n_trades equal on every date | 300 / 300 |
| trades.parquet: the set of (date, i, side) equal; net, entry_ns, exit_ns, flags exact; ev_long, ev_short within 1e-9 | 300 / 300 (162,189 trades in all; 0 only-own, 0 only-pipeline, 0 field mismatches) |
| not_made.parquet | 0 rows in all 300, own and pipeline |
| entries not made, entry or exit fallback fills, limit marks, last-touch marks (P3.2 counts) | 0 of each over all 300 (so every s_net equals the label's n_s exactly) |
| DONE and fold<k>.DONE sha256 of daily, trades, not_made, stats, npz, model.json | all match, 300 configurations, 1,800 folds |
| configurations with trades / constant (no-trade) series | 222 / 78 |
| "3 dates per configuration" listing (the 3 dates with the most trades, ties by date, filled by the first OOF dates when fewer than 3 dates traded): own trade rows = pipeline trade rows on every listed date | 900 dates, all equal (derived/e33/verify_c/three_dates.json) |
| P6.2 statistics from the own series versus from the pipeline's parquet files (gates_own.json vs gates_parquet.json) | 5,105 fields compared, 0 differ |

## 4. Thresholds (own, from the protocol's definitions)

b_test = max(3/sqrt(T_test), the SR whose DSR reaches 0.95 at N 838, V = 1/(T_test - 1), normal moments), solved by
200-step bisection on [0, 1]; the G3 SR threshold at normal moments and SR0 at the discovery V for information.

| quantity | own (program function) | own (own formula, NormalDist) | P8_select33 | D_stats |
|---|---|---|---|---|
| b_test | 0.16488165417252623 | 0.16488165425270523 | 0.16488165417252623 | 0.16488165417252623 |
| 3/sqrt(870) | 0.10170952554312156 | - | - | - |
| G3 SR threshold at normal moments (P7.2 prints 0.1724) | 0.17242150688451255 | 0.1724215069683758 | - | 0.17242150688451255 |
| SR0 = E[max SR] at N 838, V 1/795 (P7.2 prints 0.1137) | 0.11365258253614735 | 0.11365258261959192 | - | 0.11365258253614735 |
| N, T_disc, T_test | 838, 796, 870 | - | 838, 796 | 838, 796, 870 |

The pipeline's b_test equals my program-function value to all printed digits (agree at 1e-9). The own-formula value differs
from it by 8.0e-11 absolute (4.9e-10 relative): funnel._norm_ppf is Acklam's rational approximation (about 1e-9 relative),
NormalDist.inv_cdf is AS241. Since P7.2 pins b_test at p7_final.py's value, which uses the program's function, G4 was
evaluated against 0.16488165417252623; with the own-formula value every G4 result is the same.

## 5. Funnel, the 10 best configurations, near-threshold configurations, passers, Tier walks

### T1. Funnel (count passing each gate alone and in order)
| gate | own | P8_select33 | D_stats |
|---|---|---|---|
| G1 alone | 61 | 61 | 61 |
| G2 alone | 8 | 8 | 8 |
| G3 alone | 0 | 0 | 0 |
| G4 alone | 0 | 0 | 0 |
| G5 alone | 0 | 0 | 0 |
| G1 in order | 61 | 61 | 61 |
| G1..G2 in order | 0 | 0 | 0 |
| G1..G3 in order | 0 | 0 | 0 |
| G1..G4 in order | 0 | 0 | 0 |
| G1..G5 in order | 0 | 0 | 0 |
| G3 alone, own DSR formula | 0 | - | - |
| failed configurations | 0 | 0 | - |

Per-configuration gate flags G1..G5: own = P8_select33 = D_stats on all 300 (compare.json: 0 differences in gates.*,
passes_all, g5.a-d, g5.pass). The highest DSR of any configuration is 0.0248 (E33-S2F30G2200), against the gate's 0.95; the
highest SR_d - se is 0.0305 (E33-S1F15G3200), against b_test 0.1649. No configuration is within 10% of the G3 or G4
threshold.

### T3. The 10 best configurations by the P8 ranking key (SR_d rounded to 4 dp, then tiebreaks): own values, with agreement flags against P8_select33 (P) and D_stats (D)
| rank | config | trades | dates w/ trade | mean net/trade | hit rate | mean X_D | pop SD | SR_d | skew | kurtosis | t | DSR program | DSR own formula | se | SR_d - se | G5 quarters>0 | max month share | min LOMO t | tercile means | gates G1..G5 | P | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | E33-S2F30G2200 | 55 | 47 | 4.39927 | 0.563636 | 0.30397 | 6.36119 | 0.04778504756 | 2.93958 | 61.8586 | 1.34818 | 0.0247707209 | 0.02477072076 | 0.0335391 | 0.0142459 | 5/13 | 0.44371 | 0.856286 | 0.2709, 0.5406, 0.1012 | FTFFF | agree | agree |
| 2 | E33-S1F15G3200 | 8 | 2 | 8.472 | 0.875 | 0.0851457 | 1.79999 | 0.04730334535 | 22.9316 | 553.755 | 1.33459 | 3.93089272e-05 | 3.930892638e-05 | 0.0168033 | 0.0305 | 2/13 | 0.677054 | 1.00064 | 0, 0, 0.2548 | FTFFF | agree | agree |
| 3 | E33-S2F30L001A | 13 | 10 | 7.472 | 0.615385 | 0.12203 | 2.70235 | 0.04515698932 | 12.4134 | 260.625 | 1.27404 | 0.005324404503 | 0.005324404456 | 0.0268188 | 0.0183382 | 2/13 | 0.740652 | 0.51471 | 0.4238, -0.02841, -0.02872 | FTFFF | agree | agree |
| 4 | E33-S5F15G2050 | 39 | 4 | 2.06174 | 0.512821 | 0.101015 | 2.37246 | 0.04257828262 | 25.8074 | 696.21 | 1.20128 | 8.186507761e-06 | 8.186507573e-06 | 0.016493 | 0.0260853 | 2/13 | 0.805591 | 0.914483 | 0.2622, 0.05932, -0.01808 | FTFFF | agree | agree |
| 5 | E33-S5F15G3050 | 36 | 7 | 0.610889 | 0.5 | 0.0276281 | 1.2252 | 0.02254996364 | 11.6207 | 230.097 | 0.636213 | 0.001679152399 | 0.001679152384 | 0.0310625 | -0.00851252 | 2/13 | 1.39687 | -0.52826 | 0.1588, -0.05787, -0.01786 | FTFFF | agree | agree |
| 6 | E33-S3F30L001A | 14 | 12 | 1.40057 | 0.428571 | 0.0246332 | 1.76217 | 0.013978884 | 8.19997 | 199.65 | 0.394393 | 0.001486440706 | 0.001486440694 | 0.0335542 | -0.0195753 | 3/13 | 1.6532 | -0.33974 | -0.03082, 0.009117, 0.09534 | FTFFF | agree | agree |
| 7 | E33-S2F30L100A | 30 | 22 | 0.938667 | 0.533333 | 0.0353769 | 4.22561 | 0.008372022865 | 8.09845 | 161.803 | 0.236204 | 0.001070710638 | 0.00107071063 | 0.0342946 | -0.0259226 | 4/13 | 3.13977 | -0.647903 | 0.2698, -0.1645, 0.0009323 | FTFFF | agree | agree |
| 8 | E33-S2F30L100E | 26 | 18 | 0.818154 | 0.5 | 0.0267236 | 4.01424 | 0.006657204795 | 9.75504 | 194.978 | 0.187823 | 0.0009158721918 | 0.0009158721843 | 0.0343348 | -0.0276776 | 3/13 | 4.15645 | -0.787948 | 0.3362, -0.1645, -0.09107 | FTFFF | agree | agree |
| 9 | E33-S1T15G2200 | 66 | 45 | 0.214424 | 0.575758 | 0.0177789 | 3.34115 | 0.005321183879 | -2.06413 | 46.8811 | 0.150129 | 0.001193305572 | 0.001193305562 | 0.0356663 | -0.0303451 | 2/13 | 2.72018 | -0.319642 | -0.0001208, -0.02548, 0.07871 | FFFFF | agree | agree |
| 10 | E33-S2F30L010A | 29 | 21 | 0.196138 | 0.517241 | 0.00714573 | 4.16593 | 0.001715279136 | 8.35894 | 171.076 | 0.048394 | 0.0007393629487 | 0.0007393629427 | 0.0352134 | -0.0334981 | 4/13 | 15.5443 | -0.911051 | 0.2114, -0.1645, -0.02538 | FFFFF | agree | agree |

"agree" in P and D means every listed number (SR_d, DSR with the program's function, se, trade count, mean net, t, the five
gates, quarters positive, max month share, min LOMO t, tercile means, and for D also the hit rate and the rank 1-10) agrees
at the tolerance. The 10 configurations and their order equal P8's ranking_all[:10] and D_stats' ranking_top10. The per-fold,
per-month and per-quarter sums of all 300 agree with stats.json (compare.json: own_vs_stats_json 80,700 fields, 0 differ)
and the top 10's with D_stats' p62 block.

### T4. Reported-only P6.2 statistics of the 10 best (own; agreement with stats.json (E) and D_stats top10 (D))
| config | rows (row_ok) | rho(EV chosen, net) rows | rho trades | top-decile n | top-decile mean net | mid-sign hit rate | n_used/n_nan/n_zero | E | D |
|---|---|---|---|---|---|---|---|---|---|
| E33-S2F30G2200 | 166924 | -0.0106329 | -0.013203 | 16693 | -2.38051 | 0.6 | 55/0/0 | agree | agree |
| E33-S1F15G3200 | 178269 | -0.0223642 | 0.27687 | 17827 | -2.66302 | 0.875 | 8/0/0 | agree | agree |
| E33-S2F30L001A | 166924 | -0.0105312 | 0.565736 | 16693 | -2.27778 | 0.692308 | 13/0/0 | agree | agree |
| E33-S5F15G2050 | 178269 | -0.000611134 | -0.250717 | 17827 | -2.13135 | 0.605263 | 38/0/1 | agree | agree |
| E33-S5F15G3050 | 178269 | -0.00282295 | -0.233364 | 17827 | -2.07492 | 0.588235 | 34/0/2 | agree | agree |
| E33-S3F30L001A | 166924 | -0.0163673 | 0.534111 | 16693 | -2.26573 | 0.5 | 14/0/0 | agree | agree |
| E33-S2F30L100A | 166924 | -0.00898443 | 0.0973974 | 16693 | -2.14341 | 0.586207 | 29/0/1 | agree | agree |
| E33-S2F30L100E | 166924 | -0.0084039 | 0.21444 | 16693 | -2.20697 | 0.56 | 25/0/1 | agree | agree |
| E33-S1T15G2200 | 178269 | -0.00633256 | -0.013804 | 17827 | -2.1065 | 0.461538 | 65/0/1 | agree | agree |
| E33-S2F30L010A | 166924 | -0.00908255 | 0.210143 | 16693 | -2.20026 | 0.571429 | 28/0/1 | agree | agree |

Reading used (S07, S08): rows = row_ok rows with the fold's prediction; side = the larger EV ignoring the 0 threshold, exact
ties dropped (0 ties occurred); net = n_long or n_short of that side; top decile = ceil(n/10) rows by max(EV_long, EV_short)
descending, ties by (date, i); mid-sign over trades taken, NaN and exact-0 moves left out. The reported-only statistics of
all 300 agree with stats.json (part of the 80,700 fields).

### T5. Configurations within 10% of a non-zero gate threshold (own values; every one was fully re-simulated)
Rule: |value - threshold| <= 0.10 x |threshold|. No configuration is within 10% of G2 (0.50 tick: nearest 0.6109 above and
0.214 below), G3 (0.95), G4 (b_test), G5 (a) (exactly 9 quarters), G5 (b) (0.25) or G5 (c) (2.5). The G1 list:

| config | gate | value | threshold | gate result (own / P8 / D) |
|---|---|---|---|---|
| E33-S1F60L010A | G1 trade_count | 748 | 796 | F / F / F |
| E33-S1F60L010A | G1 dates_with_trade | 416 | 398 | F / F / F |
| E33-S1F60L100A | G1 trade_count | 794 | 796 | F / F / F |
| E33-S1F60L100E | G1 trade_count | 722 | 796 | F / F / F |
| E33-S1F60L100E | G1 dates_with_trade | 408 | 398 | F / F / F |
| E33-S1T30G3050 | G1 trade_count | 847 | 796 | F / F / F |
| E33-S2F60G3200 | G1 trade_count | 745 | 796 | F / F / F |
| E33-S2F60G3200 | G1 dates_with_trade | 372 | 398 | F / F / F |
| E33-S2F60L010A | G1 trade_count | 797 | 796 | T / T / T |
| E33-S2F60L100A | G1 trade_count | 828 | 796 | T / T / T |
| E33-S2F60L100E | G1 trade_count | 765 | 796 | F / F / F |
| E33-S2F60L100E | G1 dates_with_trade | 429 | 398 | F / F / F |
| E33-S2T30G2050 | G1 dates_with_trade | 420 | 398 | T / T / T |
| E33-S2T30G2200 | G1 trade_count | 854 | 796 | F / F / F |
| E33-S3F60G3200 | G1 dates_with_trade | 364 | 398 | F / F / F |
| E33-S3F60L010E | G1 dates_with_trade | 393 | 398 | F / F / F |
| E33-S3T15L010A | G1 trade_count | 790 | 796 | F / F / F |
| E33-S3T15L010A | G1 dates_with_trade | 368 | 398 | F / F / F |
| E33-S3T15L100A | G1 trade_count | 805 | 796 | F / F / F |
| E33-S3T15L100A | G1 dates_with_trade | 374 | 398 | F / F / F |
| E33-S3T15L100E | G1 trade_count | 794 | 796 | F / F / F |
| E33-S3T15L100E | G1 dates_with_trade | 372 | 398 | F / F / F |
| E33-S4F30G3050 | G1 trade_count | 752 | 796 | F / F / F |
| E33-S4F60G2200 | G1 dates_with_trade | 389 | 398 | F / F / F |
| E33-S4F60G3200 | G1 dates_with_trade | 435 | 398 | T / T / T |
| E33-S4F60L010E | G1 trade_count | 756 | 796 | F / F / F |
| E33-S4F60L010E | G1 dates_with_trade | 406 | 398 | F / F / F |
| E33-S4T15G3200 | G1 trade_count | 804 | 796 | F / F / F |
| E33-S5F30L010A | G1 trade_count | 819 | 796 | T / T / T |
| E33-S5F30L010A | G1 dates_with_trade | 416 | 398 | T / T / T |
| E33-S5F30L100A | G1 trade_count | 875 | 796 | T / T / T |
| E33-S5F30L100A | G1 dates_with_trade | 430 | 398 | T / T / T |
| E33-S5F30L100E | G1 trade_count | 785 | 796 | F / F / F |
| E33-S5F30L100E | G1 dates_with_trade | 402 | 398 | F / F / F |
| E33-S5F60G3200 | G1 trade_count | 771 | 796 | F / F / F |
| E33-S5F60G3200 | G1 dates_with_trade | 376 | 398 | F / F / F |

E33-S2F60L010A passes G1 by one trade (797 >= 796); its re-simulated trade list equals the pipeline's row for row, so the
count is not in doubt, and it fails G2 (mean net per trade below 0.50) in all three sources. The G1 trade count and the G1
dates-with-trade count are integers, so the 10% band is the one place a simulation difference could have moved a gate; none
did (300 of 300 trade lists equal).

For the two zero thresholds (G5 (b) total > 0, G5 (d) tercile means > 0) "within 10%" has no literal meaning; I read it as
within 0.1 standard errors of 0 (SE = SD x sqrt(n) for the total, SD/sqrt(n_tercile) for a tercile mean). That flags 361
items on 115 configurations: the 78 no-trade series, which sit exactly on 0, and 37 trading ones (E33-S1F15G2050,
E33-S1F15G2200, E33-S1F15G3050, E33-S1F15G3200, E33-S1F30G2050, E33-S1F60G3050, E33-S1F60G3200, E33-S1T15G2200, E33-S2F30G2050,
E33-S2F30G3050, E33-S2F30G3200, E33-S2F30L010A, E33-S2F30L100A, E33-S3F15L001A, E33-S3F15L010A, E33-S3F15L010E, E33-S3F15L100A,
E33-S3F15L100E, E33-S3F30G2050, E33-S3F30G3050, E33-S3F30G3200, E33-S3F30L001A, E33-S3F30L010E, E33-S3F30L100E, E33-S3F60L100A,
E33-S4F15L001A, E33-S4F15L010A, E33-S4F15L010E, E33-S4F15L100A, E33-S4F15L100E, E33-S4F30L001A, E33-S5F05L001A, E33-S5F05L010A,
E33-S5F05L010E, E33-S5F05L100A, E33-S5F05L100E, E33-S5F30G2200). Since all 300 configurations were re-simulated in full, this
reading does not limit the check; it is stated so the lead can apply another one to gates_table.csv.

### T6. Gate passers alone
G1 alone (61): E33-S2F60L010A, E33-S2F60L100A, E33-S2T30L001A, E33-S2T30L010A, E33-S2T30L010E, E33-S2T30L100A, E33-S2T30L100E,
E33-S2T30G2050, E33-S2T30G3050, E33-S2T30G3200, E33-S3F60L001A, E33-S3F60L010A, E33-S3F60L100A, E33-S3F60L100E, E33-S3T30L001A,
E33-S3T30L010A, E33-S3T30L010E, E33-S3T30L100A, E33-S3T30L100E, E33-S3T30G2050, E33-S3T30G3050, E33-S3T30G3200, E33-S4F60L001A,
E33-S4F60L010A, E33-S4F60L100A, E33-S4F60L100E, E33-S4F60G2050, E33-S4F60G3050, E33-S4F60G3200, E33-S4T30L001A, E33-S4T30L010A,
E33-S4T30L010E, E33-S4T30L100A, E33-S4T30L100E, E33-S4T30G2050, E33-S4T30G2200, E33-S4T30G3050, E33-S4T30G3200, E33-S5F30L010A,
E33-S5F30L100A, E33-S5F60L001A, E33-S5F60L010A, E33-S5F60L010E, E33-S5F60L100A, E33-S5F60L100E, E33-S5F60G2050, E33-S5F60G3050,
E33-S5T15L001A, E33-S5T15L010A, E33-S5T15L010E, E33-S5T15L100A, E33-S5T15L100E, E33-S5T30L001A, E33-S5T30L010A, E33-S5T30L010E,
E33-S5T30L100A, E33-S5T30L100E, E33-S5T30G2050, E33-S5T30G2200, E33-S5T30G3050, E33-S5T30G3200.

G2 alone (8), each with fewer than 60 trades and failing G1: E33-S1F15G3200 (8 trades, mean net 8.4720), E33-S2F30L001A
(13, 7.4720), E33-S2F30L100A (30, 0.9387), E33-S2F30L100E (26, 0.8182), E33-S2F30G2200 (55, 4.3993), E33-S3F30L001A (14,
1.4006), E33-S5F15G2050 (39, 2.0617), E33-S5F15G3050 (36, 0.6109). G1 and G2 both: none. Hence G1..G2 in order = 0 and the
later gates are never reached in order; alone, G3, G4 and G5 pass 0 each (G5's four parts: no configuration has 9 positive
quarters, every trading configuration has a month above 25% of its total or a total <= 0, and no leave-one-month-out t
reaches 2.5).

### T7. Tier walks
Passers of G1-G5: none, so Tier A = [] (own, P8, D_stats). Tier B under R-L8 "continue" from position 0 (gates ignored,
constant series skipped): E33-S2F30G2200 then E33-S1F15G3200 (correlation -0.00226 between them); P8_select33.json
tier_b = ['E33-S2F30G2200', 'E33-S1F15G3200'], tier_b_detail.continue.start_position 0: agree. Best configuration
E33-S2F30G2200, SR_d 0.04778504755788138: agree with P8 best_config and best_sharpe. ranking_all (300) equal; ranking_pass
[] equal.

## 6. Every difference found (none touches a gate, a funnel count, a ranking position or a tier)

compare.json totals: own vs P8_select33 17,689 fields agree, 334 differ; own vs stats.json 80,700 agree, 0 differ; own vs
D_stats 14,038 agree, 242 differ; own (re-simulated) vs own (pipeline parquet) 5,105 agree, 0 differ.

1. DSR, se and sr_lower on the 78 constant (no-trade) series: file P8_select33.json configs[].dsr/se/sr_lower and
   D_stats.json configs[cid].dsr/se/sr_lower = None; own = 0.000676441420536189 (program function; 0.000676441415007556 by
   the own formula), se 0.03546634510659543, sr_lower -0.03546634510659543, from moments()'s SD-0 defaults (sharpe 0, skew
   0, kurtosis 3), for which the program's function returns a value. Gate effect: none (G3 false and G4 false either way;
   P8 G3 "a DSR that cannot be computed fails G3" and the computed 0.00068 both fail). Configurations (78, all with
   trade_count 0): E33-S1F05L001A, E33-S1F05L001E, E33-S1F05L010A, E33-S1F05L010E, E33-S1F05L100A, E33-S1F05L100E,
   E33-S1F15L001E, E33-S1F30L001E, E33-S1F60L001E, E33-S2F05L001A, E33-S2F05L001E, E33-S2F05L010A, E33-S2F05L010E,
   E33-S2F05L100A, E33-S2F05L100E, E33-S2F15L001A, E33-S2F15L001E, E33-S2F15L010A, E33-S2F15L010E, E33-S2F15L100A,
   E33-S2F15L100E, E33-S2F30L001E, E33-S2F30L010E, E33-S2F60L001E, E33-S3F05L001A, E33-S3F05L001E, E33-S3F05L010A,
   E33-S3F05L010E, E33-S3F05L100A, E33-S3F05L100E, E33-S3F15L001E, E33-S3F30L001E, E33-S3F60L001E, E33-S4F05L001A,
   E33-S4F05L001E, E33-S4F05L010A, E33-S4F05L010E, E33-S4F05L100A, E33-S4F05L100E, E33-S4F15L001E, E33-S4F30L001E,
   E33-S4F60L001E, E33-S5F05L001E, E33-S5F15L001E, E33-S5F30L001E, E33-S5F60L001E, E33-S1F05G2050, E33-S1F05G2200,
   E33-S1F05G3050, E33-S1F05G3200, E33-S2F05G2050, E33-S2F05G2200, E33-S2F05G3050, E33-S2F05G3200, E33-S2F15G2050,
   E33-S2F15G2200, E33-S2F15G3050, E33-S2F15G3200, E33-S3F05G2050, E33-S3F05G2200, E33-S3F05G3050, E33-S3F05G3200,
   E33-S3F15G2050, E33-S3F15G2200, E33-S3F15G3050, E33-S3F15G3200, E33-S4F05G2050, E33-S4F05G2200, E33-S4F05G3050,
   E33-S4F05G3200, E33-S4F15G2200, E33-S4F15G3200, E33-S5F05G2050, E33-S5F05G2200, E33-S5F05G3050, E33-S5F05G3200,
   E33-S5F15G2200, E33-S5F15G3200 (45 F05, 22 F15, 6 F30, 5 F60; 46 LOGIT, 32 LGBM). This is a representation choice
   (None for a constant series), not a numerical disagreement.
2. DSR by the own formula versus P8_select33.json configs[].dsr on 14 trading configurations: relative differences
   5.8e-9 to 8.9e-9 (tolerance 1e-9), e.g. E33-S2F30G2200 own-formula 0.02477072075600073 vs P8 0.024770720900291587;
   also E33-S1F15G2200, E33-S1F15G3050, E33-S1F30G2050, E33-S1T15G2200, E33-S1T15L001E, E33-S1T30L001E, E33-S2F30L001A,
   E33-S2F30L010A, E33-S2F30L100A, E33-S2F30L100E, E33-S3F30L001A, E33-S4F15G3050, E33-S5F15G3050. Cause: SR0 differs by
   8.3e-11 between funnel._norm_ppf (Acklam) and NormalDist.inv_cdf (AS241); multiplied by sqrt(795) in z and by the normal
   density at z of about -3, the DSR (about 1e-3) moves by about 5e-12 absolute, which is 8e-9 relative. The DSR with the
   program's function, which G3 names, agrees with P8 and D_stats on all 222 trading configurations at 1e-9. Gate effect:
   none (all these DSRs are below 0.025).
3. g5.min_lomo_t on 8 trading configurations with one undefined leave-one-month-out t (the month removed holds all the
   configuration's trades, so the remaining series has SD 0): own None (I report the minimum only when all 39 are defined);
   P8_select33.json configs[].g5.min_lomo_t and D_stats.json configs[cid].g5.min_lomo_t report the minimum over the 38
   defined months, -1.0006474587923384 (or ...386). lomo_undefined = 1 agrees in all three, and G5 (c) is false in all
   three (P05: an undefined t fails (c)). Configurations: E33-S1F15G2050 (5 trades), E33-S3F15L001A, E33-S3F15L010A,
   E33-S3F15L010E, E33-S3F15L100A, E33-S3F15L100E, E33-S3F30L010E, E33-S4F15L010E (1 trade each). My minimum over the
   defined months equals theirs. A convention difference, no numerical disagreement.

No difference was found in: any trade, daily value or not-made record (300 configurations, 796 dates each); any
moment, t, trade count, trades per date, dates with trade, mean net per trade, hit rate, total; any per-fold, per-month,
per-quarter sum or vol-tercile mean; any gate flag or G5 part; any reported-only statistic; the funnel; the ranking; Tier A;
Tier B; b_test; N; T.

## 7. StatsCoder comparison

Done (not pending): reports/stage_e33c_briefs/work/D_stats.json, sha256 fac9aea9..., read after my numbers were written.
Funnel, branch "N (Tier A empty)", ranking_top10, thresholds (b_test, G3, SR0, N, T_disc, T_test), selection_as_written
tier_a and tier_b, all 300 configurations' moments, t, DSR (program function), se, sr_lower, gates, G5 parts and P3.2 counts,
and the top 10's p62 and reported_only blocks agree, apart from items 1 and 3 of section 6 (the same None conventions as
P8). Its own agreement_with_select33 block (not verified by me) reports no gate or ranking mismatch, consistent with this.

## 8. Not done, and caveats

- P6.3 discovery PBO, the BH/Holm report, the reference thresholds and the per-firm nets in P8_select33.json "reports" and
  in D_stats.json were not recomputed: they are reports, never gates (P8; ProtocolReview DO-20), and outside the brief's
  branch-N scope.
- "Within 10%" of the zero thresholds G5 (b) total > 0 and G5 (d) tercile mean > 0 has no literal reading; the rule I used
  is stated in T5. Every configuration was re-simulated regardless.
- The pipeline's headline (P8_select33.out) was seen before computing (section 1, disclosure); the computation did not use
  it, and the JSON fields were compared only afterwards.
- Holdout: `uv run python -m data.holdout status` at the end: unlocks_logged 0, all_ok true. Nothing under live/, ops/,
  the search root, the stores, the frozen pipeline, the protocol, the ledger or reports/stage_e33_STATE.md was written. No
  Databento call. Timestamps from `date` (PDT): start 20:40:03; re-simulation 20:48:58-20:49:31; gates 20:50:09-20:50:22;
  comparison 20:53:20-20:53:22; tables 20:55; report written 20:57.

## 9. Files

- This report: reports/stage_e33c_briefs/work/D4_verify.md.
- Code: reports/stage_e33c_briefs/work/verify/{verify_common.py, resim_all.py, gates_all.py, compare_select.py,
  report_tables.py} (sha256 prefixes 282cd4231d2f, ce318277716e, a8f9c958eb6b, 56ab11958263, 59016ef43ac5).
- Results: /mnt/large-storage/market_data/PropExperiment/derived/e33/verify_c/{resim/<cid>.json, resim/<cid>.trades.parquet
  (300 each, 18 MB), resim_all.log, gates_own.json, gates_parquet.json, gates_own.log, gates_parquet.log, compare.json,
  three_dates.json, report_tables.md, gates_table.csv (one row per configuration: own values and equality flags against
  P8 and D_stats)}.
