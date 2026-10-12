# Stage E.20 Step 6 sentinel dry check (synthetic sentinel frames, no store)

Written 2026-10-11T17:10:42-07:00 (PDT) by pattern_search.dry_check (seed 20261012, wall 27.9 s). Plan sections 10.1 and 13; review PR-1, PR-15; recheck PR-16, PR-18.

## Verdicts

- features: PASS
- legs: PASS
- row_losses: PASS
- ruling2_only_le_t1: PASS

Features failing: none

Derived tables equal the frozen ones on the overlap: {'equity_full': True, 'auctions': True, 'month_end': True, 'wpsr': True, 'ngs': True, 'energy_full': True, 'metals_full': True}

## 1. Every KEPT feature and both rod features under the swaps

| Feature | W1 app rows / finite / event dates | W2 app rows / finite / event dates | W3 app rows / finite / event dates | Passes |
|---|---|---|---|---|
| cp1_ret | 29008 / 17124 | 16469 / 16283 | 20948 / 20948 | yes  |
| cp2_range | 29008 / 23320 | 16469 / 16283 | 20948 / 20948 | yes  |
| cp2_brk | 29008 / 23320 | 16469 / 16283 | 20948 / 20948 | yes  |
| cp3_clv | 29008 / 23268 | 16469 / 16224 | 20948 / 20880 | yes  |
| k1_vwap_dist | 2260 / 2260 / 565 | 1196 / 1196 / 299 | 1232 / 1232 / 308 | yes  |
| k2_auction_mto | 270 / 270 / 108 | 148 / 148 / 58 | 176 / 176 / 57 | yes  |
| k2_auction_msince | 270 / 270 / 108 | 148 / 148 / 58 | 176 / 176 / 57 | yes  |
| k2_monthend_msince | 1020 / 1020 / 51 | 572 / 572 / 28 | 720 / 720 / 30 | yes  |
| k4_eiafade_move | 351 / 351 / 117 | 186 / 186 / 62 | 192 / 192 / 64 | yes  |
| k4_ngpre_mto | 121 / 121 / 118 | 63 / 63 / 61 | 65 / 65 / 64 | yes  |
| k4_ngpre_msince | 351 / 351 / 118 | 181 / 181 / 61 | 191 / 191 / 64 | yes  |
| k4_ovr_ret | 3366 / 3366 | 1794 / 1794 | 1854 / 1854 | yes  |
| k4_ovr_pct | 3366 / 3270 | 1794 / 1698 | 1854 / 1758 | yes  |
| k5_ovr_ret | 1683 / 1683 | 897 / 897 | 927 / 927 | yes  |
| k5_ovr_pct | 1683 / 1635 | 897 / 849 | 927 / 879 | yes  |
| g01_ret30 | 27586 / 22289 | 15513 / 14401 | 19417 / 18157 | yes  |
| g02_ret60 | 26164 / 22286 | 15513 / 14401 | 19417 / 18157 | yes  |
| g03_ret120 | 24742 / 22283 | 15216 / 14129 | 18798 / 17578 | yes  |
| g04_ret_day | 29008 / 22292 | 16469 / 15292 | 20948 / 19588 | yes  |
| g05_gap | 28276 / 21636 | 15970 / 14693 | 20552 / 19192 | yes  |
| g06_rv60 | 29008 / 27968 | 16469 / 15289 | 20948 / 19588 | yes  |
| g07_range | 29008 / 22292 | 16469 / 15292 | 20948 / 19588 | yes  |
| g08_prev_ret | 29008 / 22292 | 16469 / 15292 | 20948 / 19588 | yes  |
| g09_vol_state | 29008 / 16944 | 16469 / 8933 | 20948 / 11744 | yes  |
| g10_logvol30 | 29008 / 27968 | 16469 / 15289 | 20948 / 19588 | yes  |
| g11_t_index | 29008 / 29008 | 16469 / 16469 | 20948 / 20948 | yes  |
| g12_dow | 29008 / 29008 | 16469 / 16469 | 20948 / 20948 | yes  |
| g16_month_end | 29008 / 29008 | 16469 / 16469 | 20948 / 20948 | yes  |
| g17_nq | 26748 / 26748 | 15273 / 15273 | 18484 / 18484 | yes  |
| g17_zn | 17968 / 17968 | 10417 / 10417 | 13532 / 13532 | yes  |
| g17_6e | 26800 / 26800 | 15285 / 15285 | 19712 / 19712 | yes  |
| g17_cl | 24520 / 24520 | 14077 / 14077 | 18476 / 18476 | yes  |
| g17_gc | 26764 / 26764 | 15273 / 15273 | 19712 / 19712 | yes  |
| g17_zc | 22183 / 22183 | 12000 / 12000 | 14788 / 14788 | yes  |
| rod_ret | 28276 / 28224 | 15970 / 15911 | 20552 / 20484 | yes  |
| rod_absratio | 28276 / 25104 | 15970 / 12491 | 20552 / 16404 | yes  |

Calendar-only control (member tables left frozen): finite applicable rows per window

| Feature | W1 | W2 | W3 |
|---|---|---|---|
| k1_vwap_dist | 0 | 0 | 0 |
| k2_auction_mto | 0 | 0 | 0 |
| k2_auction_msince | 0 | 0 | 0 |
| k2_monthend_msince | 0 | 0 | 0 |
| k4_eiafade_move | 0 | 0 | 0 |
| k4_ngpre_mto | 0 | 0 | 0 |
| k4_ngpre_msince | 0 | 0 | 0 |
| k4_ovr_ret | 3366 | 1794 | 1854 |
| k4_ovr_pct | 0 | 0 | 0 |
| k5_ovr_ret | 1683 | 897 | 927 |
| k5_ovr_pct | 0 | 0 | 0 |

Windows: W1: 2010-07-01..2012-09-28, 13 vehicles, 29008 rows (0 excluded by ruling 2), 2.9 s; W2: 2014-12-15..2016-02-26, 15 vehicles, 16469 rows (291 excluded by ruling 2), 1.7 s; W3: 2017-07-10..2018-09-28, 17 vehicles, 20948 rows (0 excluded by ruling 2), 2.0 s

## 2. Removing one leg's frames stops the build

| Root | Builder | compute_signals | Stops |
|---|---|---|---|
| NQ | KeyError: 'NQ' | SignalInputMissing: the context holds no bars for NQ | True |
| RTY | KeyError: 'RTY' | SignalInputMissing: the context holds no bars for RTY | True |
| ZT | KeyError: 'ZT' | SignalInputMissing: the context holds no bars for ZT | True |
| ZF | KeyError: 'ZF' | SignalInputMissing: the context holds no bars for ZF | True |
| ZN | KeyError: 'ZN' | SignalInputMissing: the context holds no bars for ZN | True |
| TN | KeyError: 'TN' | SignalInputMissing: the context holds no bars for TN | True |
| ZB | KeyError: 'ZB' | SignalInputMissing: the context holds no bars for ZB | True |
| UB | KeyError: 'UB' | SignalInputMissing: the context holds no bars for UB | True |
| 6E | KeyError: '6E' | SignalInputMissing: the context holds no bars for 6E | True |
| CL | KeyError: 'CL' | SignalInputMissing: the context holds no bars for CL | True |
| NG | KeyError: 'NG' | SignalInputMissing: the context holds no bars for NG | True |
| GC | KeyError: 'GC' | SignalInputMissing: the context holds no bars for GC | True |
| ZC | KeyError: 'ZC' | SignalInputMissing: the context holds no bars for ZC | True |
| ZS | KeyError: 'ZS' | SignalInputMissing: the context holds no bars for ZS | True |
| ZL | KeyError: 'ZL' | SignalInputMissing: the context holds no bars for ZL | True |
| HE | KeyError: 'HE' | SignalInputMissing: the context holds no bars for HE | True |
| LE | KeyError: 'LE' | SignalInputMissing: the context holds no bars for LE | True |

## 3. Declared row losses (plan 10.1) and ruling 2's exclusions (PR-18)

| Root | Trade dates | Kept dates | Dates losing every row | Share | Declared | Reproduced | With sigma/G9 warm-up | Ruling 2 excluded (t_index: rows) | B1 first date lost (no d-1 bars) |
|---|---|---|---|---|---|---|---|---|---|
| NQ | 2280 | 2203 | 6 | 0.3% | 6 (2280) | True | 141 | - | 2010-07-01: True |
| RTY | 466 | 451 | 0 | 0.0% | 0 (None) | True | 134 | - | 2017-07-10: True |
| ZT | 2279 | 2182 | 313 | 13.7% | 313 (2279) | True | 313 | - | 2010-07-01: True |
| ZF | 2279 | 2182 | 313 | 13.7% | 313 (2279) | True | 313 | - | 2010-07-01: True |
| ZN | 2279 | 2182 | 313 | 13.7% | 313 (2279) | True | 313 | - | 2010-07-01: True |
| TN | 851 | 827 | 0 | 0.0% | 0 (None) | True | 135 | - | 2016-01-11: True |
| ZB | 2279 | 2182 | 313 | 13.7% | 313 (2279) | True | 313 | - | 2010-07-01: True |
| UB | 2279 | 2182 | 313 | 13.7% | 313 (2279) | True | 313 | - | 2010-07-01: True |
| 6E | 2280 | 2182 | 6 | 0.3% | 6 (2280) | True | 138 | - | 2010-07-01: True |
| CL | 2278 | 2203 | 0 | 0.0% | 0 (None) | True | 132 | - | 2010-07-01: True |
| NG | 2278 | 2203 | 0 | 0.0% | 0 (None) | True | 132 | - | 2010-07-01: True |
| GC | 2278 | 2203 | 0 | 0.0% | 0 (None) | True | 132 | - | 2010-07-01: True |
| ZC | 2225 | 2199 | 477 | 21.4% | 477 (2225) | True | 610 | - | 2010-07-01: None |
| ZS | 2225 | 2199 | 477 | 21.4% | 477 (2225) | True | 610 | - | 2010-07-01: None |
| ZL | 2225 | 2199 | 477 | 21.4% | 477 (2225) | True | 610 | - | 2010-07-01: None |
| HE | 460 | 453 | 0 | 0.0% | 0 (None) | True | 136 | - | 2017-07-05: True |
| LE | 1103 | 1086 | 63 | 5.7% | 63 (1103) | True | 171 | {1: 296} | 2014-12-15: True |

Counts use sentinel bars from the trade date before each window, as the calendar-only table assumes d-1 bars; in B1 the bars start at the window's first date, whose rows are then lost too (last column). None marks the frozen ports._cp3 IndexError on a frame without any port-complete day (grains 2010, whose first dates lack their own 08:30 bar anyway).

The warm-up column adds sigma_X,d's 20 complete dates and G9's 120 sigma values; for every root it includes the window-start warm-up, for the grains also the restart after 2012-05-21 (plan 10.1: about 615).

## 4. Ruling 4's reach (PR-16): nominal fills in the fallback windows

nominal fill minutes (entry at t; exit at t + h when within F, or F); the D9.5a deferral and ruling 3's session-end exits are not applied here

| Vehicle | Types without 2010-2019 rows | Kept dates | Entries affected | Share | Exits affected | Share |
|---|---|---|---|---|---|---|
| MNQ | CPI, ISM_SERVICES, NFP | 2203 | 2203 / 8812 | 25.0% | 0 / 24233 | 0.0% |
| M2K | ISM_SERVICES, NFP | 451 | 451 / 1804 | 25.0% | 0 / 4961 | 0.0% |
| ZT | NFP | 2182 | 2182 / 8728 | 25.0% | 0 / 24002 | 0.0% |
| ZF | NFP | 2182 | 2182 / 8728 | 25.0% | 0 / 24002 | 0.0% |
| ZN | ISM_SERVICES, NFP | 2182 | 2182 / 8728 | 25.0% | 0 / 24002 | 0.0% |
| TN | NFP | 827 | 827 / 3308 | 25.0% | 0 / 9097 | 0.0% |
| ZB | ISM_SERVICES, NFP | 2182 | 2182 / 8728 | 25.0% | 0 / 24002 | 0.0% |
| UB | NFP | 2182 | 2182 / 8728 | 25.0% | 0 / 24002 | 0.0% |
| 6E | NFP | 2182 | 2182 / 8728 | 25.0% | 0 / 24002 | 0.0% |
| MCL | API_WSB | 2203 | 0 / 8812 | 0.0% | 0 / 24233 | 0.0% |
| NG | - | 2203 | 0 / 8812 | 0.0% | 0 / 24233 | 0.0% |
| MGC | CPI, G17, NFP | 2203 | 2203 / 8812 | 25.0% | 0 / 24233 | 0.0% |
| ZC | CROP, CROP_ANNUAL, CROP_PROGRESS, WASDE | 2199 | 2199 / 8796 | 25.0% | 3709 / 24189 | 15.3% |
| ZS | CROP, CROP_ANNUAL, WASDE | 2199 | 2199 / 8796 | 25.0% | 3709 / 24189 | 15.3% |
| ZL | CROP, CROP_ANNUAL, WASDE | 2199 | 2199 / 8796 | 25.0% | 3709 / 24189 | 15.3% |
| HE | CROP, CROP_ANNUAL, WASDE | 453 | 453 / 1812 | 25.0% | 906 / 4983 | 18.2% |
| LE | CROP, CROP_ANNUAL, WASDE | 1086 | 1086 / 4344 | 25.0% | 1580 / 11946 | 13.2% |

| Vehicle | Type | CT minutes | t_index | Horizon | Side | Affected / fills |
|---|---|---|---|---|---|---|
| MNQ | ISM_SERVICES | 09:00 | t1 | all | entry | 2203 / 2203 |
| M2K | ISM_SERVICES | 09:00 | t1 | all | entry | 451 / 451 |
| ZT | NFP | 07:30 | t1 | all | entry | 2182 / 2182 |
| ZF | NFP | 07:30 | t1 | all | entry | 2182 / 2182 |
| ZN | NFP | 07:30 | t1 | all | entry | 2182 / 2182 |
| TN | NFP | 07:30 | t1 | all | entry | 827 / 827 |
| ZB | NFP | 07:30 | t1 | all | entry | 2182 / 2182 |
| UB | NFP | 07:30 | t1 | all | entry | 2182 / 2182 |
| 6E | NFP | 07:30 | t1 | all | entry | 2182 / 2182 |
| MGC | CPI | 07:30 | t1 | all | entry | 2203 / 2203 |
| MGC | NFP | 07:30 | t1 | all | entry | 2203 / 2203 |
| ZC | CROP | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZC | CROP | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZC | CROP | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZC | CROP | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZC | CROP_ANNUAL | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZC | CROP_ANNUAL | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZC | CROP_ANNUAL | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZC | CROP_ANNUAL | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZC | WASDE | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZC | WASDE | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZC | WASDE | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZC | WASDE | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZS | CROP | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZS | CROP | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZS | CROP | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZS | CROP | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZS | CROP_ANNUAL | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZS | CROP_ANNUAL | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZS | CROP_ANNUAL | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZS | CROP_ANNUAL | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZS | WASDE | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZS | WASDE | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZS | WASDE | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZS | WASDE | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZL | CROP | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZL | CROP | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZL | CROP | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZL | CROP | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZL | CROP_ANNUAL | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZL | CROP_ANNUAL | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZL | CROP_ANNUAL | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZL | CROP_ANNUAL | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| ZL | WASDE | 11:00 | t3 | all | entry | 2199 / 2199 |
| ZL | WASDE | 11:00 | t1 | h60 | exit | 689 / 2199 |
| ZL | WASDE | 11:00 | t1 | h120 | exit | 1510 / 2199 |
| ZL | WASDE | 11:00 | t2 | h60 | exit | 1510 / 2199 |
| HE | CROP | 11:00 | t3 | all | entry | 453 / 453 |
| HE | CROP | 11:00 | t1 | h120 | exit | 453 / 453 |
| HE | CROP | 11:00 | t2 | h60 | exit | 453 / 453 |
| HE | CROP_ANNUAL | 11:00 | t3 | all | entry | 453 / 453 |
| HE | CROP_ANNUAL | 11:00 | t1 | h120 | exit | 453 / 453 |
| HE | CROP_ANNUAL | 11:00 | t2 | h60 | exit | 453 / 453 |
| HE | WASDE | 11:00 | t3 | all | entry | 453 / 453 |
| HE | WASDE | 11:00 | t1 | h120 | exit | 453 / 453 |
| HE | WASDE | 11:00 | t2 | h60 | exit | 453 / 453 |
| LE | CROP | 11:00 | t3 | all | entry | 1086 / 1086 |
| LE | CROP | 11:00 | t1 | h120 | exit | 790 / 1086 |
| LE | CROP | 11:00 | t2 | h60 | exit | 790 / 1086 |
| LE | CROP_ANNUAL | 11:00 | t3 | all | entry | 1086 / 1086 |
| LE | CROP_ANNUAL | 11:00 | t1 | h120 | exit | 790 / 1086 |
| LE | CROP_ANNUAL | 11:00 | t2 | h60 | exit | 790 / 1086 |
| LE | WASDE | 11:00 | t3 | all | entry | 1086 / 1086 |
| LE | WASDE | 11:00 | t1 | h120 | exit | 790 / 1086 |
| LE | WASDE | 11:00 | t2 | h60 | exit | 790 / 1086 |

## Exclusions (rulings 5 and 6) and reopenings (ruling 7)

{'MCL': ['2012-11-01'], 'HE': ['2017-10-09', '2017-11-10', '2018-10-08', '2018-11-12'], 'LE': ['2014-12-24', '2014-12-25', '2014-12-26', '2014-12-31', '2015-01-01', '2015-01-02', '2015-10-12', '2015-11-11', '2016-10-10', '2016-11-11', '2017-10-09', '2017-11-10', '2018-10-08', '2018-11-12']}

{'convention': 'tenor from the EC-AUC row id (original security term), as E.2b', 'rows_in_window_by_tenor': {'2Y': 97, '5Y': 107, '10Y': 106, '30Y': 106}}

