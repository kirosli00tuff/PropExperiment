# Stage D.1e Task 1a — MES null coverage map, recorded figures

Pure extraction from reports/stage_d1d_accounting.json (A), reports/stage_d1d_retests.json (B), reports/stage_d1b_family_f_facts.json (C), reports/stage_d1d_family_g_facts.json (D). No conclusions drawn. Full data: reports/stage_d1e_members_recorded.json.

## Trials (31, source A, B for the 7 RT retest fields)

| label | n_trips | trades/day | p (win_probability) | R (win_loss_ratio) | net ($) | daily sd | t_stat |
|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | 276 | 0.9550 | 0.5072 | 1.0073 | 141.10 | 42.275437 | 0.1963 |
| A-H2 rth close window (buy) | 266 | 0.9204 | 0.4925 | 1.1282 | 587.95 | 64.415517 | 0.5369 |
| A-H2 rth close window (sell) | 266 | 0.9204 | 0.4624 | 0.8598 | -1955.78 | 64.508761 | -1.7834 |
| A-H3 weekend effect | 110 | 0.3806 | 0.4364 | 0.8105 | -4411.16 | 154.063269 | -1.6842 |
| A-H4 eth leg | 277 | 0.9585 | 0.5523 | 0.9431 | 2550.27 | 170.376409 | 0.8805 |
| A-H4 rth leg | 276 | 0.9550 | 0.5290 | 1.1130 | 5509.36 | 279.501907 | 1.1595 |
| B-H1 opening-range breakout (hold 5) | 276 | 0.9550 | 0.4384 | 0.8460 | -1347.18 | 32.948617 | -2.4051 |
| B-H1 opening-range breakout (hold 75) | 276 | 0.9550 | 0.5326 | 0.8568 | -292.95 | 121.35494 | -0.142 |
| B-H2 prior-day stop cascade | 223 | 0.7716 | 0.4484 | 1.3296 | 302.94 | 46.282862 | 0.385 |
| B-H3 breakout leg | 274 | 0.9481 | 0.4927 | 0.8672 | -1186.39 | 72.421634 | -0.9636 |
| B-H3 fade leg | 274 | 0.9481 | 0.4489 | 1.1874 | -231.39 | 72.416005 | -0.188 |
| B-H4 narrow-range breakout | 115 | 0.3979 | 0.4435 | 1.2227 | -59.95 | 34.304737 | -0.1028 |
| C-H1 magnitude-conditioned reversal | 40743 | 140.9792 | 0.3608 | 1.0899 | -107966.84 | 259.62447 | -24.4622 |
| C-H2 post-spike exhaustion fade | 8829 | 30.5502 | 0.3647 | 1.1223 | -20089.79 | 116.423124 | -10.1505 |
| C-H3 close-location-value reversal | 12066 | 41.7509 | 0.3680 | 1.0999 | -29176.33 | 145.83637 | -11.7684 |
| D-H1 trailing-vol regime gate | 106 | 0.3668 | 0.4340 | 0.7992 | -304.16 | 10.36403 | -1.7263 |
| D-H2 inverse-vol sizing | 276 | 0.9550 | 0.4601 | 0.8435 | -2320.19 | 69.528841 | -1.963 |
| D-H3 range-compression gate | 2846 | 9.8478 | 0.3848 | 1.1318 | -8234.14 | 79.872413 | -6.0642 |
| D-H4 overnight gap fade | 134 | 0.4637 | 0.4328 | 0.7033 | -842.60 | 24.173132 | -2.0504 |
| E-H1 scheduled macro drift | 31 | 0.1073 | 0.4839 | 0.6886 | -776.35 | 62.747676 | -0.7278 |
| E-H2 post-release momentum | 25 | 0.0865 | 0.4800 | 1.0408 | -15.96 | 11.763477 | -0.0798 |
| E-H3 quarterly witching short | 4 | 0.0138 | 0.2500 | 1.3555 | -25.60 | 2.326839 | -0.6472 |
| E-H4 turn-of-month long | 55 | 0.1903 | 0.4364 | 1.2557 | -7.44 | 6.692881 | -0.0654 |
| C-H4 passive-fill reversal | 26723 | 92.4671 | 0.4421 | 0.8195 | -78686.96 | 237.766752 | -19.4672 |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | 273 | 0.9446 | 0.4799 | 0.9247 | -477.55 | 30.984895 | -0.9066 |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | 273 | 0.9446 | 0.5385 | 0.7075 | -2001.60 | 120.00123 | -0.9812 |
| RT3 B-H3 breakout leg 5-min bars | 273 | 0.9446 | 0.5348 | 0.7563 | -974.58 | 78.806879 | -0.7275 |
| RT4 B-H3 fade leg 5-min bars | 273 | 0.9446 | 0.4322 | 1.2345 | -437.08 | 78.802846 | -0.3263 |
| RT5 C-H2 spike fade 5-min bars | 2824 | 9.7716 | 0.4111 | 0.9118 | -10474.61 | 84.492485 | -7.2924 |
| RT6 D-H1 daily-vol regime gate | 134 | 0.4637 | 0.3955 | 1.1943 | -217.24 | 13.984327 | -0.9138 |
| RT7 D-H2 daily-vol sizing | 257 | 0.8893 | 0.4553 | 0.9112 | -1070.15 | 42.817076 | -1.4702 |

## Statistics (21, source C = Family F, D = Family G)

| progress name | id | n (n_events for G) | estimate | CI95 | p_boot | implied edge (ticks) | sub-blocks agreeing |
|---|---|---|---|---|---|---|---|
| F3.2 bucket 07→08 | F3_2_bucket07_bucket08 | 134 | -0.075700 | [-0.2184, 0.0621] | 0.265 | -7.5597 | 3/4 |
| F6.1 | F6_1_overnight_range_position | 138 | 0.017004 | [-0.1457, 0.1873] | 0.838 | 6.5797 | 2/4 |
| F3.3(b) | F3_3_opening_30min_to_close_momentum | 134 | -0.109886 | [-0.2764, 0.0703] | 0.223 | -6.3358 | 3/4 |
| F3.2 bucket 08→09 | F3_2_bucket08_bucket09 | 134 | -0.193841 | [-0.4008, 0.0287] | 0.099 | -6.2239 | 3/4 |
| F3.3(a) | F3_3_overnight_to_close_momentum | 134 | -0.055530 | [-0.2483, 0.1238] | 0.534 | -4.9925 | 3/4 |
| F4.4 ×100 | F4_4_round_number_multiples_of_100 | 559 | -4.577350 | [-10.5676, 0.1885] | 0.073 | -3.3631 | 3/4 |
| F3.2 bucket 01→02 | F3_2_bucket01_bucket02 | 138 | 0.085889 | [-0.0998, 0.2713] | 0.371 | 4.1739 | 3/4 |
| F3.2 bucket 10→11 | F3_2_bucket10_bucket11 | 134 | 0.140484 | [-0.0723, 0.3411] | 0.184 | 3.6940 | 2/4 |
| F4.1 | F4_1_rth_open_crossing | 261 | -3.452107 | [-8.6655, 1.8193] | 0.21 | -3.4521 | 3/4 |
| F3.2 bucket 02→03 | F3_2_bucket02_bucket03 | 138 | -0.018486 | [-0.1673, 0.1415] | 0.813 | 3.0580 | 2/4 |
| F3.2 bucket 05→06 | F3_2_bucket05_bucket06 | 138 | 0.090122 | [-0.1158, 0.2381] | 0.359 | 2.9420 | 4/4 |
| F3.2 bucket 04→05 | F3_2_bucket04_bucket05 | 138 | 0.161081 | [-0.1667, 0.4397] | 0.561 | 2.5870 | 2/4 |
| F3.2 bucket 06→07 | F3_2_bucket06_bucket07 | 138 | -0.123129 | [-0.3760, 0.1491] | 0.379 | -2.4855 | 3/4 |
| F3.2 bucket 12→13 | F3_2_bucket12_bucket13 | 134 | 0.108179 | [-0.0903, 0.2746] | 0.262 | 2.3806 | 2/4 |
| G2.RTH.30 | G2.RTH.30 | 319 | 5.191223 | [0.7259, 9.6516] | 0.02 | 5.1912 | 3/4 |
| G1.RTH.5 | G1.RTH.5 | 1789 | 0.879262 | [0.0731, 1.7571] | 0.034 | 0.8793 | 4/4 |
| G2.ETH.30 | G2.ETH.30 | 598 | -1.622074 | [-3.9004, 0.3250] | 0.124 | -1.6221 | 3/4 |
| G2.ETH.5 | G2.ETH.5 | 1328 | -0.491717 | [-1.1619, 0.1497] | 0.137 | -0.4917 | 3/4 |
| G5.RTH.15 | G5.RTH.15 | 129 | -4.015504 | [-11.1568, 2.9138] | 0.239 | -4.0155 | 4/4 |
| G5.RTH.30 | G5.RTH.30 | 124 | 4.516129 | [-4.0464, 12.8806] | 0.283 | 4.5161 | 2/4 |
| G3.RTH.15 | G3.RTH.15 | 138 | -10.079710 | [-38.7846, 14.9462] | 0.452 | -10.0797 | 3/4 |

## Checks

- Trial labels found: 31 (expected 31)
- All 31 trial labels present in A.per_trial: True
- All 21 statistics matched to exactly one id, no duplicates: True
- F ids have n_eda_dates_after_exclusions == 139: True
- G n_events vs progress.md D.1d table (319, 1789, 598, 1328, 129, 124, 138): mismatches = [] (empty list = all match)
- Note on F4.4x100: progress.md's '-4.6 ticks' for F4.4x100 matches the 'estimate' field (-4.577..) of F4_4_round_number_multiples_of_100, not the 'implied_edge_ticks' field (-3.363..) which is the recorded edge in this JSON per the brief's schema. Both are copied verbatim above; flagged here, not resolved, per the extraction brief.

## Unmatched

None. All 31 trials and all 21 named statistics matched uniquely.
