### T1. Per trigger-hold statistics (run value / recomputed value / match within 1e-9 relative)


**base case**

| id | n | mean | sd | Sharpe | raw t | raw NW t (lags h) | alpha | alpha HAC t | alpha plain t | p_plain | p_nw | p_alpha | R2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | 1936 / 1936 / ok | 0.000159655 / 0.000159655 / ok | 0.0122672 / 0.0122672 / ok | 0.206604 / 0.206604 / ok | 0.572652 / 0.572652 / ok | 0.616762 / 0.616762 / ok | 0.000138268 / 0.000138268 / ok | 0.551808 / 0.551808 / ok | 0.497376 / 0.497376 / ok | 0.30949 / 0.30949 / ok | 0.29054 / 0.29054 / ok | 0.30949 / 0.30949 / ok | 0.00790181 / 0.00790181 / ok |
| E23-MEZNh5 | 1938 / 1938 / ok | 0.000112023 / 0.000112023 / ok | 0.0129014 / 0.0129014 / ok | 0.137838 / 0.137838 / ok | 0.382248 / 0.382248 / ok | 0.400272 / 0.400272 / ok | 0.000104301 / 0.000104301 / ok | 0.383092 / 0.383092 / ok | 0.357764 / 0.357764 / ok | 0.36028 / 0.36028 / ok | 0.350826 / 0.350826 / ok | 0.36028 / 0.36028 / ok | 0.0116743 / 0.0116743 / ok |
| E23-MEZBh5 | 1938 / 1938 / ok | 1.3346e-05 / 1.3346e-05 / ok | 0.0129933 / 0.0129933 / ok | 0.0163054 / 0.0163054 / ok | 0.0452177 / 0.0452177 / ok | 0.0460419 / 0.0460419 / ok | 2.81538e-05 / 2.81538e-05 / ok | 0.099799 / 0.099799 / ok | 0.0968745 / 0.0968745 / ok | 0.461418 / 0.461418 / ok | 0.460252 / 0.460252 / ok | 0.461418 / 0.461418 / ok | 0.0318475 / 0.0318475 / ok |
| E23-H6NQh5 | 1928 / 1928 / ok | -0.000788222 / -0.000788222 / ok | 0.0248184 / 0.0248184 / ok | -0.504169 / -0.504169 / ok | -1.39453 / -1.39453 / ok | -1.45933 / -1.45933 / ok | -0.000918303 / -0.000918303 / ok | -1.60586 / -1.60586 / ok | -1.632 / -1.632 / ok | 0.948579 / 0.948579 / ok | 0.945848 / 0.945848 / ok | 0.948579 / 0.948579 / ok | 0.0126405 / 0.0126405 / ok |
| E23-H6NQh20 | 1928 / 1928 / ok | -0.000588038 / -0.000588038 / ok | 0.025062 / 0.025062 / ok | -0.372469 / -0.372469 / ok | -1.03025 / -1.03025 / ok | -1.11787 / -1.11787 / ok | -0.000417292 / -0.000417292 / ok | -0.714499 / -0.714499 / ok | -0.745087 / -0.745087 / ok | 0.771845 / 0.771845 / ok | 0.762541 / 0.762541 / ok | 0.771845 / 0.771845 / ok | 0.0407616 / 0.0407616 / ok |

**stress case**

| id | n | mean | sd | Sharpe | raw t | raw NW t (lags h) | alpha | alpha HAC t | alpha plain t | p_plain | p_nw | p_alpha | R2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | 1936 / 1936 / ok | 0.000118853 / 0.000118853 / ok | 0.0122678 / 0.0122678 / ok | 0.153795 / 0.153795 / ok | 0.426281 / 0.426281 / ok | 0.458883 / 0.458883 / ok | 9.76459e-05 / 9.76459e-05 / ok | 0.3894 / 0.3894 / ok | 0.351217 / 0.351217 / ok | 0.362732 / 0.362732 / ok | 0.34849 / 0.34849 / ok | 0.362732 / 0.362732 / ok | 0.00782004 / 0.00782004 / ok |
| E23-MEZNh5 | 1938 / 1938 / ok | 5.85723e-05 / 5.85723e-05 / ok | 0.0129082 / 0.0129082 / ok | 0.0720323 / 0.0720323 / ok | 0.199758 / 0.199758 / ok | 0.209071 / 0.209071 / ok | 5.09932e-05 / 5.09932e-05 / ok | 0.187069 / 0.187069 / ok | 0.174805 / 0.174805 / ok | 0.430625 / 0.430625 / ok | 0.425803 / 0.425803 / ok | 0.430625 / 0.430625 / ok | 0.0114905 / 0.0114905 / ok |
| E23-MEZBh5 | 1938 / 1938 / ok | -3.02743e-05 / -3.02743e-05 / ok | 0.0129952 / 0.0129952 / ok | -0.0369822 / -0.0369822 / ok | -0.102558 / -0.102558 / ok | -0.104358 / -0.104358 / ok | -1.56093e-05 / -1.56093e-05 / ok | -0.0552743 / -0.0552743 / ok | -0.0536987 / -0.0536987 / ok | 0.52141 / 0.52141 / ok | 0.52204 / 0.52204 / ok | 0.52204 / 0.52204 / ok | 0.0317023 / 0.0317023 / ok |
| E23-H6NQh5 | 1928 / 1928 / ok | -0.000838106 / -0.000838106 / ok | 0.0247912 / 0.0247912 / ok | -0.536662 / -0.536662 / ok | -1.48441 / -1.48441 / ok | -1.55486 / -1.55486 / ok | -0.000968319 / -0.000968319 / ok | -1.69661 / -1.69661 / ok | -1.72281 / -1.72281 / ok | 0.957458 / 0.957458 / ok | 0.955115 / 0.955115 / ok | 0.957458 / 0.957458 / ok | 0.0126801 / 0.0126801 / ok |
| E23-H6NQh20 | 1928 / 1928 / ok | -0.000616488 / -0.000616488 / ok | 0.025051 / 0.025051 / ok | -0.390662 / -0.390662 / ok | -1.08057 / -1.08057 / ok | -1.17429 / -1.17429 / ok | -0.000445741 / -0.000445741 / ok | -0.764328 / -0.764328 / ok | -0.796246 / -0.796246 / ok | 0.787007 / 0.787007 / ok | 0.777664 / 0.777664 / ok | 0.787007 / 0.787007 / ok | 0.0407926 / 0.0407926 / ok |

### T2. Screen (Holm one-sided 0.05 over five on base p_alpha; survivor rule)

| id | holm_rejects run/mine | alpha t >= 2.0 run/mine | base Sharpe >= 0.3 run/mine |
|---|---|---|---|
| E23-MEZFh5 | no/no | no/no | no/no |
| E23-MEZNh5 | no/no | no/no | no/no |
| E23-MEZBh5 | no/no | no/no | no/no |
| E23-H6NQh5 | no/no | no/no | no/no |
| E23-H6NQh20 | no/no | no/no | no/no |

Survivors: run [] / mine [] / match yes. Smallest p_alpha: run 0.30949 / mine 0.30949.


### T3. DSR at N 538 and CSCV PBO (descriptive)

| quantity | run | mine | match |
|---|---|---|---|
| dsr/n_trials | 538 | 538 | ok |
| dsr/sharpe_variance | 0.000318927967547 | 0.000318927967547 | ok |
| dsr/expected_max_daily_sharpe_under_null | 0.054905776501 | 0.0549057765217 | ok |
| dsr/E23-MEZFh5 | 0.0331730815614 | 0.0331730814942 | DIFF (see notes) |
| dsr/E23-MEZNh5 | 0.0211025875275 | 0.0211025874814 | DIFF (see notes) |
| dsr/E23-MEZBh5 | 0.00886952458296 | 0.00886952456107 | DIFF (see notes) |
| dsr/E23-H6NQh5 | 6.91017325683e-05 | 6.91017323135e-05 | ok |
| dsr/E23-H6NQh20 | 0.000307992353815 | 0.000307992352789 | DIFF (see notes) |
| pbo/pbo | 0.428571428571 | 0.428571428571 | ok |
| pbo/n_splits | 70 | 70 | ok |
| pbo/n_days | 1940 | 1940 | ok |
| pbo/block_days | 242 | 242 | ok |
| pbo/winner_mean_oos_ticks_per_micro | -0.182318278777 | -0.182318278777 | ok |
| pbo/p_winner_positive_oos | 0.471428571429 | 0.471428571429 | ok |
| pbo/aligned_dates | 1940 | 1940 | ok |
| pbo/first | 2011-07-27 | 2011-07-27 | ok |
| pbo/last | 2019-04-30 | 2019-04-30 | ok |

### T4. Power table and the W_cf confirmation gate

| id | window | E[t] run/mine | power_gate run/mine | power_holm1 (K 5) run/mine | inconclusive run/mine |
|---|---|---|---|---|---|
| E23-MEZFh5 | W_ext | 1.38694/1.38694 | 0.269919/0.269919 | 0.173761/0.173761 | no/no |
| E23-MEZFh5 | W_cf | 1.07736/1.07736 | 0.178099/0.178099 | 0.105836/0.105836 | yes/yes |
| E23-MEZNh5 | W_ext | 1.38694/1.38694 | 0.269919/0.269919 | 0.173761/0.173761 | no/no |
| E23-MEZNh5 | W_cf | 1.07736/1.07736 | 0.178099/0.178099 | 0.105836/0.105836 | yes/yes |
| E23-MEZBh5 | W_ext | 1.38694/1.38694 | 0.269919/0.269919 | 0.173761/0.173761 | no/no |
| E23-MEZBh5 | W_cf | 1.07736/1.07736 | 0.178099/0.178099 | 0.105836/0.105836 | yes/yes |
| E23-H6NQh5 | W_ext | 1.38515/1.38515 | 0.269328/0.269328 | 0.173303/0.173303 | no/no |
| E23-H6NQh5 | W_cf | 1.09291/1.09291 | 0.182179/0.182179 | 0.108706/0.108706 | yes/yes |
| E23-H6NQh20 | W_ext | 1.38515/1.38515 | 0.269328/0.269328 | 0.173303/0.173303 | no/no |
| E23-H6NQh20 | W_cf | 1.09291/1.09291 | 0.182179/0.182179 | 0.108706/0.108706 | yes/yes |

W_cf power at the hurdle b = max(2.0, z(1 - 0.05/S)), recomputed from the power table's W_cf n_dates (1170 rates, 1204 NQ):

| S | b | ZF/ZN/ZB (1170 dates) | NQ (1204 dates) | all < 0.2 |
|---|---|---|---|---|
| 1 | 2 | 0.178099 | 0.182179 | yes |
| 2 | 2 | 0.178099 | 0.182179 | yes |
| 3 | 2.12805 | 0.146703 | 0.150302 | yes |
| 4 | 2.2414 | 0.122204 | 0.125382 | yes |

### T5. Independent re-simulation of the books from the ext2010 stores (spot audit)

| id | units run/mine | unit_counts match | nonoverlap run/mine | n_dates run/mine | in-market run/mine | fills run/mine | base series: dates equal, max abs diff, values differing | stress series: same | alpha3 t_nw run/mine | all exits h marks after entry | all entries on d0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | 131/131 | yes | 71/71 | 1936/1936 | 0.21436/0.21436 | 160/160 | yes, 0, 0 | yes, 0, 0 | 0.119115/0.119115 (ok) | yes | yes |
| E23-MEZNh5 | 137/137 | yes | 77/77 | 1938/1938 | 0.229618/0.229618 | 184/184 | yes, 0, 0 | yes, 0, 0 | -0.34135/-0.34135 (ok) | yes | yes |
| E23-MEZBh5 | 136/136 | yes | 76/76 | 1938/1938 | 0.227038/0.227038 | 180/180 | yes, 0, 0 | yes, 0, 0 | -0.780099/-0.780099 (ok) | yes | yes |
| E23-H6NQh5 | 1729/1729 | yes | 373/373 | 1928/1928 | 0.905602/0.905602 | 429/429 | yes, 0, 0 | yes, 0, 0 | -1.62708/-1.62708 (ok) | yes | yes |
| E23-H6NQh20 | 1713/1713 | yes | 95/95 | 1928/1928 | 0.943465/0.943465 | 289/289 | yes, 0, 0 | yes, 0, 0 | -0.628788/-0.628788 (ok) | yes | yes |

### T6. Spot units


**E23-MEZFh5** (store ohlcv-1m_ZF_v_0_2010-07-01_2019-04-30_ext2010h.parquet, sha256 matches the marker's preflight: yes)

| unit | d0 | tau (CT) | settle minute | tau before S | d_e | d_x | marks between | u | mark price (ticks) | sigma(d_e) | returns before d_e | contracts per $ capital | entry cost c/side base/stress | stress = comm + 2 x slip | value d_e run/mine (base) | entry day is cost only | next mark value run/mine (base) | next value from mark move | value d_x run/mine (base) | splices in hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first | 2011-07-28 | 2011-07-28 07:21 | 14:00 | yes | 2011-07-28 | 2011-08-04 | 5 | 1 | 15448 | 0.0402599 | 260 | 8.23236e-05 (open) | 507/898 | yes | -0.000417381/-0.000417381 | yes | 0.0636722/0.0636722 | yes | 0.0411618/0.0411618 | 0 |
| last | 2019-03-29 | 2019-03-29 07:21 | 14:00 | yes | 2019-03-29 | 2019-04-05 | 5 | 1 | 14826 | 0.0249666 | 2118 | - (no order: net unchanged) | -/- | - | -0.0312502/-0.0312502 | - | -0.0441814/-0.0441814 | - | 0.000378279/0.000378279 | 0 |
| spans_roll | 2011-08-30 | 2011-08-30 07:21 | 14:00 | yes | 2011-08-30 | 2011-09-07 | 5 | 1 | 15822 | 0.0410524 | 283 | 7.88261e-05 (open) | 507/898 | yes | -0.000399649/-0.000399649 | yes | -0.00862161/-0.00862161 | yes | -0.00963709/-0.00963709 | 1 |

Excluded-unit examples (reason: d0, d_e, d_x): exit: early halt: ['2011-09-30', '2011-09-30', '2011-10-07']; exit: no h-th mark date: ['2019-04-29', '2019-04-29', None]

**E23-MEZNh5** (store ohlcv-1m_ZN_v_0_2010-06-07_2019-04-30_ext2010.parquet, sha256 matches the marker's preflight: yes)

| unit | d0 | tau (CT) | settle minute | tau before S | d_e | d_x | marks between | u | mark price (ticks) | sigma(d_e) | returns before d_e | contracts per $ capital | entry cost c/side base/stress | stress = comm + 2 x slip | value d_e run/mine (base) | entry day is cost only | next mark value run/mine (base) | next value from mark move | value d_x run/mine (base) | splices in hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first | 2011-07-28 | 2011-07-28 07:21 | 14:00 | yes | 2011-07-28 | 2011-08-04 | 5 | 1 | 7969 | 0.0605637 | 260 | 5.30424e-05 (open) | 913/1695 | yes | -0.000484277/-0.000484277 | yes | 0.0638167/0.0638167 | yes | 0.0505561/0.0505561 | 0 |
| last | 2019-03-29 | 2019-03-29 07:21 | 14:00 | yes | 2019-03-29 | 2019-04-05 | 5 | 1 | 7949 | 0.0375201 | 2121 | - (no order: net unchanged) | -/- | - | -0.0253527/-0.0253527 | - | -0.0520397/-0.0520397 | - | 0.00455771/0.00455771 | 0 |
| spans_roll | 2011-08-30 | 2011-08-30 07:21 | 14:00 | yes | 2011-08-30 | 2011-09-07 | 5 | 1 | 8346 | 0.0687554 | 283 | 4.46123e-05 (open) | 913/1695 | yes | -0.00040731/-0.00040731 | yes | -0.0174267/-0.0174267 | yes | -0.0150457/-0.0150457 | 1 |

Excluded-unit examples (reason: d0, d_e, d_x): exit: early halt: ['2011-09-30', '2011-09-30', '2011-10-07']; exit: no h-th mark date: ['2019-04-29', '2019-04-29', None]

**E23-MEZBh5** (store ohlcv-1m_ZB_v_0_2010-07-01_2019-04-30_ext2010h.parquet, sha256 matches the marker's preflight: yes)

| unit | d0 | tau (CT) | settle minute | tau before S | d_e | d_x | marks between | u | mark price (ticks) | sigma(d_e) | returns before d_e | contracts per $ capital | entry cost c/side base/stress | stress = comm + 2 x slip | value d_e run/mine (base) | entry day is cost only | next mark value run/mine (base) | next value from mark move | value d_x run/mine (base) | splices in hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first | 2011-07-28 | 2011-07-28 07:21 | 14:00 | yes | 2011-07-28 | 2011-08-04 | 5 | 1 | 4034 | 0.0952188 | 260 | 3.33236e-05 (open) | 1702/3266 | yes | -0.000567167/-0.000567167 | yes | 0.0697712/0.0697712 | yes | 0.0728953/0.0728953 | 0 |
| last | 2019-03-29 | 2019-03-29 07:21 | 14:00 | yes | 2019-03-29 | 2019-04-05 | 5 | 1 | 4789 | 0.0696997 | 2121 | - (no order: net unchanged) | -/- | - | -0.0142311/-0.0142311 | - | -0.0557384/-0.0557384 | - | 0.00884148/0.00884148 | 0 |
| spans_roll | 2011-08-30 | 2011-08-30 07:21 | 14:00 | yes | 2011-08-30 | 2011-09-07 | 5 | 1 | 4434 | 0.128844 | 283 | 2.24052e-05 (open) | 1702/3266 | yes | -0.000381337/-0.000381337 | yes | -0.0280065/-0.0280065 | yes | -0.0297882/-0.0297882 | 1 |

Excluded-unit examples (reason: d0, d_e, d_x): exit: early halt: ['2011-09-30', '2011-09-30', '2011-10-07']; exit: no h-th mark date: ['2019-04-29', '2019-04-29', None]

**E23-H6NQh5** (store ohlcv-1m_NQ_v_0_2010-06-07_2019-04-30_ext2010.parquet, sha256 matches the marker's preflight: yes)

| unit | d0 | tau (CT) | settle minute | tau before S | d_e | d_x | marks between | u | mark price (ticks) | sigma(d_e) | returns before d_e | contracts per $ capital | entry cost c/side base/stress | stress = comm + 2 x slip | value d_e run/mine (base) | entry day is cost only | next mark value run/mine (base) | next value from mark move | value d_x run/mine (base) | splices in hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first | 2011-07-27 | 2011-07-27 14:30 | 15:15 | yes | 2011-07-27 | 2011-08-03 | 5 | 1 | 9440 (close of S-1) | 0.157548 | 261 | 0.000537905 (open) | 105/149 | yes | -0.0005648/-0.0005648 | yes | 0.0107312/0.0107312 | yes | 0.0159078/0.0159078 | 0 |
| last | 2019-04-23 | 2019-04-23 14:30 | 15:15 | yes | 2019-04-23 | 2019-04-30 | 5 | -1 | 31351 (close of S-1) | 0.18614 | 2125 | - (no order: net unchanged) | -/- | - | -0.0266866/-0.0266866 | - | -0.00265571/-0.00265571 | - | 0.0010299/0.0010299 | 0 |
| spans_roll | 2011-09-06 | 2011-09-06 14:30 | 15:15 | yes | 2011-09-06 | 2011-09-13 | 5 | -1 | 8662 (close of S-1) | 0.28428 | 289 | - (no order: net unchanged) | -/- | - | 0.000163895/0.000163895 | - | -0.0386793/-0.0386793 | - | -0.0157339/-0.0157339 | 1 |
| enters_at_first_flip | 2011-08-12 | 2011-08-12 14:30 | 15:15 | yes | 2011-08-12 | 2011-08-19 | 5 | -1 | 8711 (close of S-1) | 0.27284 | 273 | -0.0003366 (flip) | 105/149 | yes | 0.0191208/0.0191208 | no | -0.0173349/-0.0173349 | yes | -0.0302226/-0.0302226 | 0 |

Excluded-unit examples (reason: d0, d_e, d_x): exit: roll blackout: ['2011-08-31', '2011-08-31', '2011-09-08']; exit: no h-th mark date: ['2019-04-24', '2019-04-24', None]

**E23-H6NQh20** (store ohlcv-1m_NQ_v_0_2010-06-07_2019-04-30_ext2010.parquet, sha256 matches the marker's preflight: yes)

| unit | d0 | tau (CT) | settle minute | tau before S | d_e | d_x | marks between | u | mark price (ticks) | sigma(d_e) | returns before d_e | contracts per $ capital | entry cost c/side base/stress | stress = comm + 2 x slip | value d_e run/mine (base) | entry day is cost only | next mark value run/mine (base) | next value from mark move | value d_x run/mine (base) | splices in hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first | 2011-07-27 | 2011-07-27 14:30 | 15:15 | yes | 2011-07-27 | 2011-08-24 | 20 | 1 | 9440 (close of S-1) | 0.157548 | 261 | 0.000537905 (open) | 105/149 | yes | -0.0005648/-0.0005648 | yes | 0.0107312/0.0107312 | yes | 0.0156512/0.0156512 | 0 |
| last | 2019-04-01 | 2019-04-01 14:30 | 15:15 | yes | 2019-04-01 | 2019-04-30 | 20 | -1 | 29991 (close of S-1) | 0.207151 | 2110 | - (no order: net unchanged) | -/- | - | -0.0221996/-0.0221996 | - | -0.00534318/-0.00534318 | - | 0.00101139/0.00101139 | 0 |
| spans_roll | 2011-08-15 | 2011-08-15 14:30 | 15:15 | yes | 2011-08-15 | 2011-09-13 | 20 | -1 | 8814 (close of S-1) | 0.271345 | 274 | - (no order: net unchanged) | -/- | - | 0.0264274/0.0264274 | - | -0.00436181/-0.00436181 | - | -0.0155943/-0.0155943 | 1 |
| enters_at_first_flip | 2011-08-30 | 2011-08-30 14:30 | 15:15 | yes | 2011-08-30 | 2011-09-28 | 20 | -1 | 8906 (close of S-1) | 0.287821 | 285 | -0.000312094 (flip) | 105/149 | yes | 0.00503476/0.00503476 | no | -0.0128269/-0.0128269 | yes | 0.0222544/0.0222544 | 1 |

Excluded-unit examples (reason: d0, d_e, d_x): exit: roll blackout: ['2011-08-10', '2011-08-10', '2011-09-08']; exit: no h-th mark date: ['2019-04-02', '2019-04-02', None]

### T7. Every recomputed row

| name | run | mine | match |
|---|---|---|---|
| E23-H6NQh5/base/raw/n | 1928 | 1928 | ok |
| E23-H6NQh5/base/raw/mean | -0.00078822236651 | -0.00078822236651 | ok |
| E23-H6NQh5/base/raw/sd | 0.0248183575791 | 0.0248183575791 | ok |
| E23-H6NQh5/base/raw/sharpe | -0.504168824136 | -0.504168824136 | ok |
| E23-H6NQh5/base/raw/t | -1.39453439893 | -1.39453439893 | ok |
| E23-H6NQh5/base/raw/t_nw | -1.45932868975 | -1.45932868975 | ok |
| E23-H6NQh5/base/alpha/alpha | -0.00091830258836 | -0.000918302588363 | ok |
| E23-H6NQh5/base/alpha/se_plain | 0.000562684565882 | 0.000562684565882 | ok |
| E23-H6NQh5/base/alpha/se_hac | 0.000571844075647 | 0.000571844075647 | ok |
| E23-H6NQh5/base/alpha/t_plain | -1.63200244691 | -1.63200244692 | ok |
| E23-H6NQh5/base/alpha/t_nw | -1.60586185547 | -1.60586185548 | ok |
| E23-H6NQh5/base/alpha/p_plain | 0.948578734569 | 0.94857873457 | ok |
| E23-H6NQh5/base/alpha/p_nw | 0.945847866903 | 0.945847866904 | ok |
| E23-H6NQh5/base/alpha/p_alpha | 0.948578734569 | 0.94857873457 | ok |
| E23-H6NQh5/base/alpha/r2 | 0.0126404532069 | 0.0126404532069 | ok |
| E23-H6NQh5/base/alpha/beta1 | 0.651420786272 | 0.651420786272 | ok |
| E23-H6NQh5/base/alpha/corr1 | 0.104194530954 | 0.104194530954 | ok |
| E23-H6NQh5/base/alpha/beta2 | 1.20089893591 | 1.20089893591 | ok |
| E23-H6NQh5/base/alpha/corr2 | 0.108180968874 | 0.108180968874 | ok |
| E23-H6NQh5/base/series/n_dates | 1928 | 1928 | ok |
| E23-H6NQh5/base/series/sorted_distinct | yes | yes | ok |
| E23-H6NQh5/base/series/inside_W_ext | yes | yes | ok |
| E23-H6NQh5/stress/raw/n | 1928 | 1928 | ok |
| E23-H6NQh5/stress/raw/mean | -0.000838106242197 | -0.000838106242197 | ok |
| E23-H6NQh5/stress/raw/sd | 0.0247912455507 | 0.0247912455507 | ok |
| E23-H6NQh5/stress/raw/sharpe | -0.536662190184 | -0.536662190184 | ok |
| E23-H6NQh5/stress/raw/t | -1.48441127057 | -1.48441127057 | ok |
| E23-H6NQh5/stress/raw/t_nw | -1.55486414113 | -1.55486414113 | ok |
| E23-H6NQh5/stress/alpha/alpha | -0.00096831861049 | -0.000968318610493 | ok |
| E23-H6NQh5/stress/alpha/se_plain | 0.000562058600428 | 0.000562058600428 | ok |
| E23-H6NQh5/stress/alpha/se_hac | 0.000570737076749 | 0.000570737076749 | ok |
| E23-H6NQh5/stress/alpha/t_plain | -1.72280721219 | -1.72280721219 | ok |
| E23-H6NQh5/stress/alpha/t_nw | -1.69661066354 | -1.69661066355 | ok |
| E23-H6NQh5/stress/alpha/p_plain | 0.957458001174 | 0.957458001174 | ok |
| E23-H6NQh5/stress/alpha/p_nw | 0.955114853783 | 0.955114853783 | ok |
| E23-H6NQh5/stress/alpha/p_alpha | 0.957458001174 | 0.957458001174 | ok |
| E23-H6NQh5/stress/alpha/r2 | 0.0126800776386 | 0.0126800776386 | ok |
| E23-H6NQh5/stress/alpha/beta1 | 0.65431348433 | 0.65431348433 | ok |
| E23-H6NQh5/stress/alpha/corr1 | 0.104405145448 | 0.104405145448 | ok |
| E23-H6NQh5/stress/alpha/beta2 | 1.19813719116 | 1.19813719116 | ok |
| E23-H6NQh5/stress/alpha/corr2 | 0.108315898271 | 0.108315898271 | ok |
| E23-H6NQh5/stress/series/n_dates | 1928 | 1928 | ok |
| E23-H6NQh5/stress/series/sorted_distinct | yes | yes | ok |
| E23-H6NQh5/stress/series/inside_W_ext | yes | yes | ok |
| E23-H6NQh20/base/raw/n | 1928 | 1928 | ok |
| E23-H6NQh20/base/raw/mean | -0.000588037844218 | -0.000588037844218 | ok |
| E23-H6NQh20/base/raw/sd | 0.0250619840367 | 0.0250619840367 | ok |
| E23-H6NQh20/base/raw/sharpe | -0.372468970138 | -0.372468970138 | ok |
| E23-H6NQh20/base/raw/t | -1.03025170642 | -1.03025170642 | ok |
| E23-H6NQh20/base/raw/t_nw | -1.11787470208 | -1.11787470208 | ok |
| E23-H6NQh20/base/alpha/alpha | -0.000417291808521 | -0.000417291808516 | ok |
| E23-H6NQh20/base/alpha/se_plain | 0.000560058027624 | 0.000560058027624 | ok |
| E23-H6NQh20/base/alpha/se_hac | 0.000584034027221 | 0.000584034027221 | ok |
| E23-H6NQh20/base/alpha/t_plain | -0.745086737336 | -0.745086737326 | ok |
| E23-H6NQh20/base/alpha/t_nw | -0.714499137159 | -0.71449913715 | ok |
| E23-H6NQh20/base/alpha/p_plain | 0.771844878539 | 0.771844878536 | ok |
| E23-H6NQh20/base/alpha/p_nw | 0.762540705244 | 0.762540705241 | ok |
| E23-H6NQh20/base/alpha/p_alpha | 0.771844878539 | 0.771844878536 | ok |
| E23-H6NQh20/base/alpha/r2 | 0.0407616040445 | 0.0407616040445 | ok |
| E23-H6NQh20/base/alpha/beta1 | 0.580664322791 | 0.580664322791 | ok |
| E23-H6NQh20/base/alpha/corr1 | -0.141358430388 | -0.141358430388 | ok |
| E23-H6NQh20/base/alpha/beta2 | -4.13879255527 | -4.13879255527 | ok |
| E23-H6NQh20/base/alpha/corr2 | -0.200078101916 | -0.200078101916 | ok |
| E23-H6NQh20/base/series/n_dates | 1928 | 1928 | ok |
| E23-H6NQh20/base/series/sorted_distinct | yes | yes | ok |
| E23-H6NQh20/base/series/inside_W_ext | yes | yes | ok |
| E23-H6NQh20/stress/raw/n | 1928 | 1928 | ok |
| E23-H6NQh20/stress/raw/mean | -0.000616488477854 | -0.000616488477854 | ok |
| E23-H6NQh20/stress/raw/sd | 0.0250509694842 | 0.0250509694842 | ok |
| E23-H6NQh20/stress/raw/sharpe | -0.390661574891 | -0.390661574891 | ok |
| E23-H6NQh20/stress/raw/t | -1.08057257499 | -1.08057257499 | ok |
| E23-H6NQh20/stress/raw/t_nw | -1.17428655274 | -1.17428655274 | ok |
| E23-H6NQh20/stress/alpha/alpha | -0.000445741033745 | -0.00044574103374 | ok |
| E23-H6NQh20/stress/alpha/se_plain | 0.000559802843522 | 0.000559802843522 | ok |
| E23-H6NQh20/stress/alpha/se_hac | 0.000583179969252 | 0.000583179969252 | ok |
| E23-H6NQh20/stress/alpha/t_plain | -0.796246462309 | -0.7962464623 | ok |
| E23-H6NQh20/stress/alpha/t_nw | -0.764328435898 | -0.764328435888 | ok |
| E23-H6NQh20/stress/alpha/p_plain | 0.787006510724 | 0.787006510721 | ok |
| E23-H6NQh20/stress/alpha/p_nw | 0.777664228111 | 0.777664228108 | ok |
| E23-H6NQh20/stress/alpha/p_alpha | 0.787006510724 | 0.787006510721 | ok |
| E23-H6NQh20/stress/alpha/r2 | 0.0407925936018 | 0.0407925936018 | ok |
| E23-H6NQh20/stress/alpha/beta1 | 0.580379318037 | 0.580379318037 | ok |
| E23-H6NQh20/stress/alpha/corr1 | -0.141420554738 | -0.141420554738 | ok |
| E23-H6NQh20/stress/alpha/beta2 | -4.13830947517 | -4.13830947517 | ok |
| E23-H6NQh20/stress/alpha/corr2 | -0.200155717973 | -0.200155717973 | ok |
| E23-H6NQh20/stress/series/n_dates | 1928 | 1928 | ok |
| E23-H6NQh20/stress/series/sorted_distinct | yes | yes | ok |
| E23-H6NQh20/stress/series/inside_W_ext | yes | yes | ok |
| E23-MEZNh5/base/raw/n | 1938 | 1938 | ok |
| E23-MEZNh5/base/raw/mean | 0.000112022591675 | 0.000112022591675 | ok |
| E23-MEZNh5/base/raw/sd | 0.012901421643 | 0.012901421643 | ok |
| E23-MEZNh5/base/raw/sharpe | 0.137837795087 | 0.137837795087 | ok |
| E23-MEZNh5/base/raw/t | 0.382247746099 | 0.382247746099 | ok |
| E23-MEZNh5/base/raw/t_nw | 0.400271733901 | 0.400271733901 | ok |
| E23-MEZNh5/base/alpha/alpha | 0.000104300541949 | 0.000104300541949 | ok |
| E23-MEZNh5/base/alpha/se_plain | 0.000291534759025 | 0.000291534759025 | ok |
| E23-MEZNh5/base/alpha/se_hac | 0.000272259932244 | 0.000272259932244 | ok |
| E23-MEZNh5/base/alpha/t_plain | 0.357763658433 | 0.357763658433 | ok |
| E23-MEZNh5/base/alpha/t_nw | 0.383091779571 | 0.383091779571 | ok |
| E23-MEZNh5/base/alpha/p_plain | 0.360279604172 | 0.360279604172 | ok |
| E23-MEZNh5/base/alpha/p_nw | 0.350825857257 | 0.350825857257 | ok |
| E23-MEZNh5/base/alpha/p_alpha | 0.360279604172 | 0.360279604172 | ok |
| E23-MEZNh5/base/alpha/r2 | 0.0116742670499 | 0.0116742670499 | ok |
| E23-MEZNh5/base/alpha/beta1 | 0.690642787559 | 0.690642787559 | ok |
| E23-MEZNh5/base/alpha/corr1 | 0.107449122659 | 0.107449122659 | ok |
| E23-MEZNh5/base/alpha/beta2 | 0.14499346068 | 0.14499346068 | ok |
| E23-MEZNh5/base/alpha/corr2 | 0.0783005299861 | 0.0783005299861 | ok |
| E23-MEZNh5/base/series/n_dates | 1938 | 1938 | ok |
| E23-MEZNh5/base/series/sorted_distinct | yes | yes | ok |
| E23-MEZNh5/base/series/inside_W_ext | yes | yes | ok |
| E23-MEZNh5/stress/raw/n | 1938 | 1938 | ok |
| E23-MEZNh5/stress/raw/mean | 5.85723175694e-05 | 5.85723175694e-05 | ok |
| E23-MEZNh5/stress/raw/sd | 0.012908183493 | 0.012908183493 | ok |
| E23-MEZNh5/stress/raw/sharpe | 0.0720323441723 | 0.0720323441723 | ok |
| E23-MEZNh5/stress/raw/t | 0.199757992274 | 0.199757992274 | ok |
| E23-MEZNh5/stress/raw/t_nw | 0.209071036299 | 0.209071036299 | ok |
| E23-MEZNh5/stress/alpha/alpha | 5.09932394913e-05 | 5.09932394913e-05 | ok |
| E23-MEZNh5/stress/alpha/se_plain | 0.000291714677372 | 0.000291714677372 | ok |
| E23-MEZNh5/stress/alpha/se_hac | 0.000272590130229 | 0.000272590130229 | ok |
| E23-MEZNh5/stress/alpha/t_plain | 0.174805189614 | 0.174805189614 | ok |
| E23-MEZNh5/stress/alpha/t_nw | 0.187069280346 | 0.187069280346 | ok |
| E23-MEZNh5/stress/alpha/p_plain | 0.4306254991 | 0.4306254991 | ok |
| E23-MEZNh5/stress/alpha/p_nw | 0.425803156841 | 0.425803156841 | ok |
| E23-MEZNh5/stress/alpha/p_alpha | 0.4306254991 | 0.4306254991 | ok |
| E23-MEZNh5/stress/alpha/r2 | 0.0114904761379 | 0.0114904761379 | ok |
| E23-MEZNh5/stress/alpha/beta1 | 0.682546235272 | 0.682546235272 | ok |
| E23-MEZNh5/stress/alpha/corr1 | 0.106552301006 | 0.106552301006 | ok |
| E23-MEZNh5/stress/alpha/beta2 | 0.149572708318 | 0.149572708318 | ok |
| E23-MEZNh5/stress/alpha/corr2 | 0.0779875723763 | 0.0779875723763 | ok |
| E23-MEZNh5/stress/series/n_dates | 1938 | 1938 | ok |
| E23-MEZNh5/stress/series/sorted_distinct | yes | yes | ok |
| E23-MEZNh5/stress/series/inside_W_ext | yes | yes | ok |
| E23-MEZFh5/base/raw/n | 1936 | 1936 | ok |
| E23-MEZFh5/base/raw/mean | 0.000159655268135 | 0.000159655268135 | ok |
| E23-MEZFh5/base/raw/sd | 0.0122671826403 | 0.0122671826403 | ok |
| E23-MEZFh5/base/raw/sharpe | 0.206603984324 | 0.206603984324 | ok |
| E23-MEZFh5/base/raw/t | 0.572652417749 | 0.572652417749 | ok |
| E23-MEZFh5/base/raw/t_nw | 0.616762084415 | 0.616762084415 | ok |
| E23-MEZFh5/base/alpha/alpha | 0.000138268423992 | 0.000138268423992 | ok |
| E23-MEZFh5/base/alpha/se_plain | 0.000277995492385 | 0.000277995492385 | ok |
| E23-MEZFh5/base/alpha/se_hac | 0.000250573548834 | 0.000250573548834 | ok |
| E23-MEZFh5/base/alpha/t_plain | 0.497376496307 | 0.497376496307 | ok |
| E23-MEZFh5/base/alpha/t_nw | 0.551807741219 | 0.551807741219 | ok |
| E23-MEZFh5/base/alpha/p_plain | 0.309490073017 | 0.309490073017 | ok |
| E23-MEZFh5/base/alpha/p_nw | 0.290540041478 | 0.290540041478 | ok |
| E23-MEZFh5/base/alpha/p_alpha | 0.309490073017 | 0.309490073017 | ok |
| E23-MEZFh5/base/alpha/r2 | 0.00790180759522 | 0.00790180759522 | ok |
| E23-MEZFh5/base/alpha/beta1 | 0.682846502287 | 0.682846502287 | ok |
| E23-MEZFh5/base/alpha/corr1 | 0.0868926852939 | 0.0868926852939 | ok |
| E23-MEZFh5/base/alpha/beta2 | -0.224706735932 | -0.224706735932 | ok |
| E23-MEZFh5/base/alpha/corr2 | 0.0411656373194 | 0.0411656373194 | ok |
| E23-MEZFh5/base/series/n_dates | 1936 | 1936 | ok |
| E23-MEZFh5/base/series/sorted_distinct | yes | yes | ok |
| E23-MEZFh5/base/series/inside_W_ext | yes | yes | ok |
| E23-MEZFh5/stress/raw/n | 1936 | 1936 | ok |
| E23-MEZFh5/stress/raw/mean | 0.000118852889225 | 0.000118852889225 | ok |
| E23-MEZFh5/stress/raw/sd | 0.012267805146 | 0.012267805146 | ok |
| E23-MEZFh5/stress/raw/sharpe | 0.153795328708 | 0.153795328708 | ok |
| E23-MEZFh5/stress/raw/t | 0.426280582686 | 0.426280582686 | ok |
| E23-MEZFh5/stress/raw/t_nw | 0.458882747807 | 0.458882747807 | ok |
| E23-MEZFh5/stress/alpha/alpha | 9.76458553237e-05 | 9.76458553236e-05 | ok |
| E23-MEZFh5/stress/alpha/se_plain | 0.000278021055756 | 0.000278021055756 | ok |
| E23-MEZFh5/stress/alpha/se_hac | 0.000250759847863 | 0.000250759847863 | ok |
| E23-MEZFh5/stress/alpha/t_plain | 0.35121748264 | 0.35121748264 | ok |
| E23-MEZFh5/stress/alpha/t_nw | 0.38939988262 | 0.389399882619 | ok |
| E23-MEZFh5/stress/alpha/p_plain | 0.362731735537 | 0.362731735537 | ok |
| E23-MEZFh5/stress/alpha/p_nw | 0.348490179427 | 0.348490179427 | ok |
| E23-MEZFh5/stress/alpha/p_alpha | 0.362731735537 | 0.362731735537 | ok |
| E23-MEZFh5/stress/alpha/r2 | 0.00782004042308 | 0.00782004042308 | ok |
| E23-MEZFh5/stress/alpha/beta1 | 0.678494969306 | 0.678494969306 | ok |
| E23-MEZFh5/stress/alpha/corr1 | 0.0864859293941 | 0.0864859293941 | ok |
| E23-MEZFh5/stress/alpha/beta2 | -0.221094261491 | -0.221094261491 | ok |
| E23-MEZFh5/stress/alpha/corr2 | 0.0411378756277 | 0.0411378756277 | ok |
| E23-MEZFh5/stress/series/n_dates | 1936 | 1936 | ok |
| E23-MEZFh5/stress/series/sorted_distinct | yes | yes | ok |
| E23-MEZFh5/stress/series/inside_W_ext | yes | yes | ok |
| E23-MEZBh5/base/raw/n | 1938 | 1938 | ok |
| E23-MEZBh5/base/raw/mean | 1.33460304648e-05 | 1.33460304648e-05 | ok |
| E23-MEZBh5/base/raw/sd | 0.0129933413477 | 0.0129933413477 | ok |
| E23-MEZBh5/base/raw/sharpe | 0.0163054028928 | 0.0163054028928 | ok |
| E23-MEZBh5/base/raw/t | 0.0452176669037 | 0.0452176669037 | ok |
| E23-MEZBh5/base/raw/t_nw | 0.0460419181201 | 0.0460419181201 | ok |
| E23-MEZBh5/base/alpha/alpha | 2.81537901314e-05 | 2.81537901318e-05 | ok |
| E23-MEZBh5/base/alpha/se_plain | 0.000290621175146 | 0.000290621175146 | ok |
| E23-MEZBh5/base/alpha/se_hac | 0.000282105048834 | 0.000282105048834 | ok |
| E23-MEZBh5/base/alpha/t_plain | 0.0968745313115 | 0.0968745313126 | ok |
| E23-MEZBh5/base/alpha/t_nw | 0.0997989587489 | 0.0997989587501 | ok |
| E23-MEZBh5/base/alpha/p_plain | 0.4614180335 | 0.461418033499 | ok |
| E23-MEZBh5/base/alpha/p_nw | 0.460251967361 | 0.460251967361 | ok |
| E23-MEZBh5/base/alpha/p_alpha | 0.4614180335 | 0.461418033499 | ok |
| E23-MEZBh5/base/alpha/r2 | 0.0318474747238 | 0.0318474747238 | ok |
| E23-MEZBh5/base/alpha/beta1 | 0.852662445573 | 0.852662445573 | ok |
| E23-MEZBh5/base/alpha/corr1 | 0.169601494416 | 0.169601494416 | ok |
| E23-MEZBh5/base/alpha/beta2 | 0.716383908982 | 0.716383908982 | ok |
| E23-MEZBh5/base/alpha/corr2 | 0.152826060983 | 0.152826060983 | ok |
| E23-MEZBh5/base/series/n_dates | 1938 | 1938 | ok |
| E23-MEZBh5/base/series/sorted_distinct | yes | yes | ok |
| E23-MEZBh5/base/series/inside_W_ext | yes | yes | ok |
| E23-MEZBh5/stress/raw/n | 1938 | 1938 | ok |
| E23-MEZBh5/stress/raw/mean | -3.02743362154e-05 | -3.02743362154e-05 | ok |
| E23-MEZBh5/stress/raw/sd | 0.0129951641464 | 0.0129951641464 | ok |
| E23-MEZBh5/stress/raw/sharpe | -0.0369822330051 | -0.0369822330051 | ok |
| E23-MEZBh5/stress/raw/t | -0.102558048052 | -0.102558048052 | ok |
| E23-MEZBh5/stress/raw/t_nw | -0.104357727429 | -0.104357727429 | ok |
| E23-MEZBh5/stress/alpha/alpha | -1.5609345443e-05 | -1.56093454426e-05 | ok |
| E23-MEZBh5/stress/alpha/se_plain | 0.000290683738363 | 0.000290683738363 | ok |
| E23-MEZBh5/stress/alpha/se_hac | 0.000282397675886 | 0.000282397675886 | ok |
| E23-MEZBh5/stress/alpha/t_plain | -0.0536987226422 | -0.053698722641 | ok |
| E23-MEZBh5/stress/alpha/t_nw | -0.0552743410299 | -0.0552743410287 | ok |
| E23-MEZBh5/stress/alpha/p_plain | 0.521409628148 | 0.521409628148 | ok |
| E23-MEZBh5/stress/alpha/p_nw | 0.522040048101 | 0.5220400481 | ok |
| E23-MEZBh5/stress/alpha/p_alpha | 0.522040048101 | 0.5220400481 | ok |
| E23-MEZBh5/stress/alpha/r2 | 0.0317022919726 | 0.0317022919726 | ok |
| E23-MEZBh5/stress/alpha/beta1 | 0.847265949209 | 0.847265949209 | ok |
| E23-MEZBh5/stress/alpha/corr1 | 0.169073881199 | 0.169073881199 | ok |
| E23-MEZBh5/stress/alpha/beta2 | 0.720367598446 | 0.720367598446 | ok |
| E23-MEZBh5/stress/alpha/corr2 | 0.152709271096 | 0.152709271096 | ok |
| E23-MEZBh5/stress/series/n_dates | 1938 | 1938 | ok |
| E23-MEZBh5/stress/series/sorted_distinct | yes | yes | ok |
| E23-MEZBh5/stress/series/inside_W_ext | yes | yes | ok |
| E23-H6NQh5/screen/holm_rejects | no | no | ok |
| E23-H6NQh5/screen/t_nw_at_least_2 | no | no | ok |
| E23-H6NQh5/screen/sharpe_at_least_0.3 | no | no | ok |
| E23-H6NQh20/screen/holm_rejects | no | no | ok |
| E23-H6NQh20/screen/t_nw_at_least_2 | no | no | ok |
| E23-H6NQh20/screen/sharpe_at_least_0.3 | no | no | ok |
| E23-MEZNh5/screen/holm_rejects | no | no | ok |
| E23-MEZNh5/screen/t_nw_at_least_2 | no | no | ok |
| E23-MEZNh5/screen/sharpe_at_least_0.3 | no | no | ok |
| E23-MEZFh5/screen/holm_rejects | no | no | ok |
| E23-MEZFh5/screen/t_nw_at_least_2 | no | no | ok |
| E23-MEZFh5/screen/sharpe_at_least_0.3 | no | no | ok |
| E23-MEZBh5/screen/holm_rejects | no | no | ok |
| E23-MEZBh5/screen/t_nw_at_least_2 | no | no | ok |
| E23-MEZBh5/screen/sharpe_at_least_0.3 | no | no | ok |
| screen/survivors | [] | [] | ok |
| screen/smallest_p_alpha | 0.309490073017 | 0.309490073017 | ok |
| dsr/n_trials | 538 | 538 | ok |
| dsr/sharpe_variance | 0.000318927967547 | 0.000318927967547 | ok |
| dsr/expected_max_daily_sharpe_under_null | 0.054905776501 | 0.0549057765217 | ok |
| dsr/E23-H6NQh5 | 6.91017325683e-05 | 6.91017323135e-05 | ok |
| dsr/E23-H6NQh20 | 0.000307992353815 | 0.000307992352789 | DIFF |
| dsr/E23-MEZNh5 | 0.0211025875275 | 0.0211025874814 | DIFF |
| dsr/E23-MEZFh5 | 0.0331730815614 | 0.0331730814942 | DIFF |
| dsr/E23-MEZBh5 | 0.00886952458296 | 0.00886952456107 | DIFF |
| pbo/pbo | 0.428571428571 | 0.428571428571 | ok |
| pbo/n_splits | 70 | 70 | ok |
| pbo/n_days | 1940 | 1940 | ok |
| pbo/block_days | 242 | 242 | ok |
| pbo/winner_mean_oos_ticks_per_micro | -0.182318278777 | -0.182318278777 | ok |
| pbo/p_winner_positive_oos | 0.471428571429 | 0.471428571429 | ok |
| pbo/aligned_dates | 1940 | 1940 | ok |
| pbo/first | 2011-07-27 | 2011-07-27 | ok |
| pbo/last | 2019-04-30 | 2019-04-30 | ok |
| power/E23-MEZFh5/W_ext/expected_t | 1.38694308142 | 1.38694308142 | ok |
| power/E23-MEZFh5/W_ext/power_gate | 0.269919352474 | 0.269919352474 | ok |
| power/E23-MEZFh5/W_ext/power_holm1 | 0.17376147665 | 0.17376147665 | ok |
| power/E23-MEZFh5/W_ext/inconclusive_by_design | no | no | ok |
| power/E23-MEZFh5/W_cf/expected_t | 1.07736450921 | 1.07736450921 | ok |
| power/E23-MEZFh5/W_cf/power_gate | 0.178098596925 | 0.178098596925 | ok |
| power/E23-MEZFh5/W_cf/power_holm1 | 0.105835579155 | 0.105835579155 | ok |
| power/E23-MEZFh5/W_cf/inconclusive_by_design | yes | yes | ok |
| power/E23-MEZNh5/W_ext/expected_t | 1.38694308142 | 1.38694308142 | ok |
| power/E23-MEZNh5/W_ext/power_gate | 0.269919352474 | 0.269919352474 | ok |
| power/E23-MEZNh5/W_ext/power_holm1 | 0.17376147665 | 0.17376147665 | ok |
| power/E23-MEZNh5/W_ext/inconclusive_by_design | no | no | ok |
| power/E23-MEZNh5/W_cf/expected_t | 1.07736450921 | 1.07736450921 | ok |
| power/E23-MEZNh5/W_cf/power_gate | 0.178098596925 | 0.178098596925 | ok |
| power/E23-MEZNh5/W_cf/power_holm1 | 0.105835579155 | 0.105835579155 | ok |
| power/E23-MEZNh5/W_cf/inconclusive_by_design | yes | yes | ok |
| power/E23-MEZBh5/W_ext/expected_t | 1.38694308142 | 1.38694308142 | ok |
| power/E23-MEZBh5/W_ext/power_gate | 0.269919352474 | 0.269919352474 | ok |
| power/E23-MEZBh5/W_ext/power_holm1 | 0.17376147665 | 0.17376147665 | ok |
| power/E23-MEZBh5/W_ext/inconclusive_by_design | no | no | ok |
| power/E23-MEZBh5/W_cf/expected_t | 1.07736450921 | 1.07736450921 | ok |
| power/E23-MEZBh5/W_cf/power_gate | 0.178098596925 | 0.178098596925 | ok |
| power/E23-MEZBh5/W_cf/power_holm1 | 0.105835579155 | 0.105835579155 | ok |
| power/E23-MEZBh5/W_cf/inconclusive_by_design | yes | yes | ok |
| power/E23-H6NQh5/W_ext/expected_t | 1.38515370759 | 1.38515370759 | ok |
| power/E23-H6NQh5/W_ext/power_gate | 0.269328117148 | 0.269328117148 | ok |
| power/E23-H6NQh5/W_ext/power_holm1 | 0.173302682828 | 0.173302682828 | ok |
| power/E23-H6NQh5/W_ext/inconclusive_by_design | no | no | ok |
| power/E23-H6NQh5/W_cf/expected_t | 1.09290642072 | 1.09290642072 | ok |
| power/E23-H6NQh5/W_cf/power_gate | 0.182178656582 | 0.182178656582 | ok |
| power/E23-H6NQh5/W_cf/power_holm1 | 0.108705553607 | 0.108705553607 | ok |
| power/E23-H6NQh5/W_cf/inconclusive_by_design | yes | yes | ok |
| power/E23-H6NQh20/W_ext/expected_t | 1.38515370759 | 1.38515370759 | ok |
| power/E23-H6NQh20/W_ext/power_gate | 0.269328117148 | 0.269328117148 | ok |
| power/E23-H6NQh20/W_ext/power_holm1 | 0.173302682828 | 0.173302682828 | ok |
| power/E23-H6NQh20/W_ext/inconclusive_by_design | no | no | ok |
| power/E23-H6NQh20/W_cf/expected_t | 1.09290642072 | 1.09290642072 | ok |
| power/E23-H6NQh20/W_cf/power_gate | 0.182178656582 | 0.182178656582 | ok |
| power/E23-H6NQh20/W_cf/power_holm1 | 0.108705553607 | 0.108705553607 | ok |
| power/E23-H6NQh20/W_cf/inconclusive_by_design | yes | yes | ok |
| confirmation/s | 0 | 0 | ok |
| confirmation/survivors_empty | yes | yes | ok |
| confirmation/trigger_holds_empty (nothing read) | yes | yes | ok |
| confirmation/window | yes | yes | ok |
| confirmation/n_trials | 538 | 538 | ok |
| discovery/n_trials | 538 | 538 | ok |
| discovery/k | 5 | 5 | ok |
| discovery/window | yes | yes | ok |
| outputs/max_series_date_<=_2019-04-30 | yes | yes | ok |
| outputs/no_W_cf_series | yes | yes | ok |
| events/E23-MEZFh5/excluded_outside_window | 2 | 2 | ok |
| events/E23-MEZFh5/events | 137 | 137 | ok |
| events/E23-MEZFh5/tau_before_settlement_open (all) | yes | yes | ok |
| events/E23-MEZNh5/excluded_outside_window | 2 | 2 | ok |
| events/E23-MEZNh5/events | 143 | 143 | ok |
| events/E23-MEZNh5/tau_before_settlement_open (all) | yes | yes | ok |
| events/E23-MEZBh5/excluded_outside_window | 2 | 2 | ok |
| events/E23-MEZBh5/events | 142 | 142 | ok |
| events/E23-MEZBh5/tau_before_settlement_open (all) | yes | yes | ok |
| events/E23-H6NQh5/excluded_outside_window | 36 | 36 | ok |
| events/E23-H6NQh5/events | 1860 | 1860 | ok |
| events/E23-H6NQh5/tau_before_settlement_open (all) | yes | yes | ok |
| events/E23-H6NQh20/excluded_outside_window | 36 | 36 | ok |
| events/E23-H6NQh20/events | 1860 | 1860 | ok |
| events/E23-H6NQh20/tau_before_settlement_open (all) | yes | yes | ok |
| trend/T1/max_abs_diff_vs_E21_series | 0 | 2.08166817117e-17 | ok |
| trend/T1/published_sha256_matches | e382770e248b52963818a741ad48498e54cd12bc1f1e43b10f0fc15144f2db46 | e382770e248b52963818a741ad48498e54cd12bc1f1e43b10f0fc15144f2db46 | ok |
| trend/T2/max_abs_diff_vs_E21_series | 0 | 1.04083408559e-17 | ok |
| trend/T2/published_sha256_matches | ab73750ac793ee2142282af38c9ae5a5850599d2a78114f4d72935d3dd93ff82 | ab73750ac793ee2142282af38c9ae5a5850599d2a78114f4d72935d3dd93ff82 | ok |
| order/discovery_marker_before_result | yes | yes | ok |
| order/confirmation_marker_before_result | yes | yes | ok |
| order/registration_after_freeze_commit | yes | yes | ok |
| order/registration_before_discovery_marker | yes | yes | ok |
| order/discovery_result_before_confirmation_marker | yes | yes | ok |
| freeze_sha256/discovery_marker | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | ok |
| freeze_sha256/confirmation_marker | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | ok |
| freeze_sha256/discovery_result | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | ok |
| freeze_sha256/confirmation_result | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | ok |
| freeze_sha256/registry_r008 | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | 24dcf4dd671dbada927f548b3aff7a58a89c8fa92a6d43ae498aa69cbb3df5a5 | ok |
| registry_sha256/discovery_marker | 25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302 | 25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302 | ok |
| registry_sha256/confirmation_marker | 25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302 | 25c04088fed9b1a2bd14a79512bedc8ab9764611aa2abd95e2a29829542aa302 | ok |
| confirmation_marker/discovery_result_sha256 | c3f71384b8537b995f81995c4b798ee04b77e8965c294d737ece7b3ca2b3590d | c3f71384b8537b995f81995c4b798ee04b77e8965c294d737ece7b3ca2b3590d | ok |
| registry/r008/n_before | 533 | 533 | ok |
| registry/r008/n_after | 538 | 538 | ok |
| registry/r008/label | yes | yes | ok |
| registry/r008/ids | yes | yes | ok |
| registry/lines | 9 | 9 | ok |
| registry/r008/harness_sha256 | dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4 | dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4 | ok |
| registry/r007_n_after_equals_r008_n_before | 533 | 533 | ok |
