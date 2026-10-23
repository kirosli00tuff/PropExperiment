# Stage E.31 canary check (structure only)

Written 2026-10-23T05:56:16-07:00. structure only: no fill, markout, spread statistic or price summary is computed. Exit code 3.

## Findings

- Z1 2024-01: 27828 T records with no F after them
- Z1 2024-01: 17387 T records whose F sizes sum above the T size
- Z1 2024-02: 23577 T records with no F after them
- Z1 2024-02: 14877 T records whose F sizes sum above the T size

## Notes (not findings)

- Z4 2024-01: ZM min_price_increment_amount ['1.0'] as found (not checked: not the USD tick value, and the engine uses min_price_increment x unit_of_measure_qty)
- Z4 2024-01: ZS min_price_increment_amount ['1.0'] as found (not checked: not the USD tick value, and the engine uses min_price_increment x unit_of_measure_qty)
- Z4 2024-01: ZL min_price_increment_amount ['0.06'] as found (not checked: not the USD tick value, and the engine uses min_price_increment x unit_of_measure_qty)
- Z4 2024-02: ZM min_price_increment_amount ['1.0'] as found (not checked: not the USD tick value, and the engine uses min_price_increment x unit_of_measure_qty)
- Z4 2024-02: ZS min_price_increment_amount ['1.0'] as found (not checked: not the USD tick value, and the engine uses min_price_increment x unit_of_measure_qty)
- Z4 2024-02: ZL min_price_increment_amount ['0.06'] as found (not checked: not the USD tick value, and the engine uses min_price_increment x unit_of_measure_qty)

## 2024-01

### Z4 outrights

| root | match_algorithm | tick | tick x size | unit | tick USD | outrights |
|---|---|---|---|---|---|---|
| ZM | {'K': 713} | 0.1 | 10.0 | USD | 10.0 | 27 |
| ZS | {'K': 605} | 0.25 | 1250.0 | US cents | 12.5 | 23 |
| ZL | {'K': 713} | 0.01 | 600.0 | US cents | 6.0 | 27 |

### Z1

- records 20,404,528; snapshot cells 46, missing 0; T/F: n_T 526503, n_F 892091, T_without_F 27828, T_F_sum_equal_size 452624, T_F_sum_below_size 28664, T_F_sum_above_size 17387, F_without_T 0
- T runs (info only): F_sum_above_T_sum_not_twice 1538, F_sum_below_T_sum 28926, F_sum_equal_T_sum 452362, F_sum_twice_T_sum 15849, runs 525384, runs_with_several_T 967, runs_without_F 26709

| midnight | symbol | instrument | raw | clear | adds | F_LAST |
|---|---|---|---|---|---|---|
| 2024-01-01 | ZM.v.0 | 506263 | ZMH4 | yes | 484 | yes |
| 2024-01-01 | ZM.v.1 | 759433 | ZMK4 | yes | 238 | yes |
| 2024-01-02 | ZM.v.0 | 506263 | ZMH4 | yes | 484 | yes |
| 2024-01-02 | ZM.v.1 | 759433 | ZMK4 | yes | 238 | yes |
| 2024-01-03 | ZM.v.0 | 506263 | ZMH4 | yes | 477 | yes |
| 2024-01-03 | ZM.v.1 | 759433 | ZMK4 | yes | 217 | yes |
| 2024-01-04 | ZM.v.0 | 506263 | ZMH4 | yes | 590 | yes |
| 2024-01-04 | ZM.v.1 | 759433 | ZMK4 | yes | 253 | yes |
| 2024-01-05 | ZM.v.0 | 506263 | ZMH4 | yes | 621 | yes |
| 2024-01-05 | ZM.v.1 | 759433 | ZMK4 | yes | 278 | yes |
| 2024-01-08 | ZM.v.0 | 506263 | ZMH4 | yes | 448 | yes |
| 2024-01-08 | ZM.v.1 | 759433 | ZMK4 | yes | 225 | yes |
| 2024-01-09 | ZM.v.0 | 506263 | ZMH4 | yes | 469 | yes |
| 2024-01-09 | ZM.v.1 | 759433 | ZMK4 | yes | 204 | yes |
| 2024-01-10 | ZM.v.0 | 506263 | ZMH4 | yes | 470 | yes |
| 2024-01-10 | ZM.v.1 | 759433 | ZMK4 | yes | 176 | yes |
| 2024-01-11 | ZM.v.0 | 506263 | ZMH4 | yes | 547 | yes |
| 2024-01-11 | ZM.v.1 | 759433 | ZMK4 | yes | 193 | yes |
| 2024-01-12 | ZM.v.0 | 506263 | ZMH4 | yes | 519 | yes |
| 2024-01-12 | ZM.v.1 | 759433 | ZMK4 | yes | 196 | yes |
| 2024-01-15 | ZM.v.0 | 506263 | ZMH4 | yes | 319 | yes |
| 2024-01-15 | ZM.v.1 | 759433 | ZMK4 | yes | 174 | yes |
| 2024-01-16 | ZM.v.0 | 506263 | ZMH4 | yes | 395 | yes |
| 2024-01-16 | ZM.v.1 | 759433 | ZMK4 | yes | 187 | yes |
| 2024-01-17 | ZM.v.0 | 506263 | ZMH4 | yes | 453 | yes |
| 2024-01-17 | ZM.v.1 | 759433 | ZMK4 | yes | 219 | yes |
| 2024-01-18 | ZM.v.0 | 506263 | ZMH4 | yes | 421 | yes |
| 2024-01-18 | ZM.v.1 | 759433 | ZMK4 | yes | 236 | yes |
| 2024-01-19 | ZM.v.0 | 506263 | ZMH4 | yes | 453 | yes |
| 2024-01-19 | ZM.v.1 | 759433 | ZMK4 | yes | 271 | yes |
| 2024-01-22 | ZM.v.0 | 506263 | ZMH4 | yes | 491 | yes |
| 2024-01-22 | ZM.v.1 | 759433 | ZMK4 | yes | 281 | yes |
| 2024-01-23 | ZM.v.0 | 506263 | ZMH4 | yes | 376 | yes |
| 2024-01-23 | ZM.v.1 | 759433 | ZMK4 | yes | 278 | yes |
| 2024-01-24 | ZM.v.0 | 506263 | ZMH4 | yes | 448 | yes |
| 2024-01-24 | ZM.v.1 | 759433 | ZMK4 | yes | 285 | yes |
| 2024-01-25 | ZM.v.0 | 506263 | ZMH4 | yes | 454 | yes |
| 2024-01-25 | ZM.v.1 | 759433 | ZMK4 | yes | 305 | yes |
| 2024-01-26 | ZM.v.0 | 506263 | ZMH4 | yes | 465 | yes |
| 2024-01-26 | ZM.v.1 | 759433 | ZMK4 | yes | 287 | yes |
| 2024-01-29 | ZM.v.0 | 506263 | ZMH4 | yes | 332 | yes |
| 2024-01-29 | ZM.v.1 | 759433 | ZMK4 | yes | 211 | yes |
| 2024-01-30 | ZM.v.0 | 506263 | ZMH4 | yes | 344 | yes |
| 2024-01-30 | ZM.v.1 | 759433 | ZMK4 | yes | 192 | yes |
| 2024-01-31 | ZM.v.0 | 506263 | ZMH4 | yes | 447 | yes |
| 2024-01-31 | ZM.v.1 | 759433 | ZMK4 | yes | 232 | yes |

### Z2 records per trade date

| trade date | in session | before session |
|---|---|---|
| 2024-01-02 | 273,534 | 17 |
| 2024-01-03 | 276,107 | 55 |
| 2024-01-04 | 247,534 | 61 |
| 2024-01-05 | 233,223 | 69 |
| 2024-01-08 | 322,361 | 43 |
| 2024-01-09 | 302,470 | 97 |
| 2024-01-10 | 308,663 | 42 |
| 2024-01-11 | 288,319 | 64 |
| 2024-01-12 | 482,235 | 41 |
| 2024-01-16 | 361,139 | 42 |
| 2024-01-17 | 346,096 | 53 |
| 2024-01-18 | 298,420 | 51 |
| 2024-01-19 | 261,903 | 51 |
| 2024-01-22 | 241,982 | 85 |
| 2024-01-23 | 219,847 | 56 |
| 2024-01-24 | 232,833 | 62 |
| 2024-01-25 | 272,046 | 72 |
| 2024-01-26 | 226,480 | 51 |
| 2024-01-29 | 269,577 | 52 |
| 2024-01-30 | 250,137 | 52 |
| 2024-01-31 | 264,680 | 55 |

### Z3 records per trade date

| trade date | in session | before session |
|---|---|---|
| 2024-01-02 | 158,951 | 29 |
| 2024-01-03 | 180,602 | 41 |
| 2024-01-04 | 142,683 | 175 |
| 2024-01-05 | 140,332 | 96 |
| 2024-01-08 | 197,108 | 69 |
| 2024-01-09 | 168,890 | 48 |
| 2024-01-10 | 176,204 | 47 |
| 2024-01-11 | 170,396 | 274 |
| 2024-01-12 | 218,566 | 662 |
| 2024-01-16 | 211,722 | 98 |
| 2024-01-17 | 195,213 | 73 |
| 2024-01-18 | 158,521 | 64 |
| 2024-01-19 | 171,505 | 39 |
| 2024-01-22 | 183,104 | 83 |
| 2024-01-23 | 158,694 | 147 |
| 2024-01-24 | 176,413 | 118 |
| 2024-01-25 | 194,813 | 128 |
| 2024-01-26 | 167,886 | 56 |
| 2024-01-29 | 198,231 | 362 |
| 2024-01-30 | 184,367 | 48 |
| 2024-01-31 | 185,366 | 331 |

## 2024-02

### Z4 outrights

| root | match_algorithm | tick | tick x size | unit | tick USD | outrights |
|---|---|---|---|---|---|---|
| ZM | {'K': 650} | 0.1 | 10.0 | USD | 10.0 | 26 |
| ZS | {'K': 550} | 0.25 | 1250.0 | US cents | 12.5 | 22 |
| ZL | {'K': 650} | 0.01 | 600.0 | US cents | 6.0 | 26 |

### Z1

- records 17,414,123; snapshot cells 42, missing 0; T/F: n_T 449295, n_F 750233, T_without_F 23577, T_F_sum_equal_size 385401, T_F_sum_below_size 25440, T_F_sum_above_size 14877, F_without_T 0
- T runs (info only): F_sum_above_T_sum_not_twice 1394, F_sum_below_T_sum 25634, F_sum_equal_T_sum 385207, F_sum_twice_T_sum 13483, runs 448494, runs_with_several_T 695, runs_without_F 22776

| midnight | symbol | instrument | raw | clear | adds | F_LAST |
|---|---|---|---|---|---|---|
| 2024-02-01 | ZM.v.0 | 506263 | ZMH4 | yes | 523 | yes |
| 2024-02-01 | ZM.v.1 | 759433 | ZMK4 | yes | 244 | yes |
| 2024-02-02 | ZM.v.0 | 506263 | ZMH4 | yes | 438 | yes |
| 2024-02-02 | ZM.v.1 | 759433 | ZMK4 | yes | 265 | yes |
| 2024-02-05 | ZM.v.0 | 506263 | ZMH4 | yes | 380 | yes |
| 2024-02-05 | ZM.v.1 | 759433 | ZMK4 | yes | 260 | yes |
| 2024-02-06 | ZM.v.0 | 506263 | ZMH4 | yes | 382 | yes |
| 2024-02-06 | ZM.v.1 | 759433 | ZMK4 | yes | 271 | yes |
| 2024-02-07 | ZM.v.0 | 506263 | ZMH4 | yes | 453 | yes |
| 2024-02-07 | ZM.v.1 | 759433 | ZMK4 | yes | 312 | yes |
| 2024-02-08 | ZM.v.0 | 506263 | ZMH4 | yes | 405 | yes |
| 2024-02-08 | ZM.v.1 | 759433 | ZMK4 | yes | 244 | yes |
| 2024-02-09 | ZM.v.0 | 506263 | ZMH4 | yes | 324 | yes |
| 2024-02-09 | ZM.v.1 | 759433 | ZMK4 | yes | 147 | yes |
| 2024-02-12 | ZM.v.0 | 506263 | ZMH4 | yes | 301 | yes |
| 2024-02-12 | ZM.v.1 | 759433 | ZMK4 | yes | 169 | yes |
| 2024-02-13 | ZM.v.0 | 506263 | ZMH4 | yes | 329 | yes |
| 2024-02-13 | ZM.v.1 | 759433 | ZMK4 | yes | 208 | yes |
| 2024-02-14 | ZM.v.0 | 506263 | ZMH4 | yes | 338 | yes |
| 2024-02-14 | ZM.v.1 | 759433 | ZMK4 | yes | 242 | yes |
| 2024-02-15 | ZM.v.0 | 506263 | ZMH4 | yes | 329 | yes |
| 2024-02-15 | ZM.v.1 | 759433 | ZMK4 | yes | 257 | yes |
| 2024-02-16 | ZM.v.0 | 759433 | ZMK4 | yes | 238 | yes |
| 2024-02-16 | ZM.v.1 | 506263 | ZMH4 | yes | 262 | yes |
| 2024-02-19 | ZM.v.0 | 759433 | ZMK4 | yes | 235 | yes |
| 2024-02-19 | ZM.v.1 | 506263 | ZMH4 | yes | 242 | yes |
| 2024-02-20 | ZM.v.0 | 759433 | ZMK4 | yes | 257 | yes |
| 2024-02-20 | ZM.v.1 | 506263 | ZMH4 | yes | 275 | yes |
| 2024-02-21 | ZM.v.0 | 759433 | ZMK4 | yes | 281 | yes |
| 2024-02-21 | ZM.v.1 | 506263 | ZMH4 | yes | 274 | yes |
| 2024-02-22 | ZM.v.0 | 759433 | ZMK4 | yes | 346 | yes |
| 2024-02-22 | ZM.v.1 | 506263 | ZMH4 | yes | 260 | yes |
| 2024-02-23 | ZM.v.0 | 759433 | ZMK4 | yes | 299 | yes |
| 2024-02-23 | ZM.v.1 | 506263 | ZMH4 | yes | 162 | yes |
| 2024-02-26 | ZM.v.0 | 759433 | ZMK4 | yes | 249 | yes |
| 2024-02-26 | ZM.v.1 | 506263 | ZMH4 | yes | 128 | yes |
| 2024-02-27 | ZM.v.0 | 759433 | ZMK4 | yes | 297 | yes |
| 2024-02-27 | ZM.v.1 | 506263 | ZMH4 | yes | 100 | yes |
| 2024-02-28 | ZM.v.0 | 759433 | ZMK4 | yes | 296 | yes |
| 2024-02-28 | ZM.v.1 | 506263 | ZMH4 | yes | 62 | yes |
| 2024-02-29 | ZM.v.0 | 759433 | ZMK4 | yes | 411 | yes |
| 2024-02-29 | ZM.v.1 | 506263 | ZMH4 | yes | 26 | yes |

### Z2 records per trade date

| trade date | in session | before session |
|---|---|---|
| 2024-02-01 | 272,941 | 37 |
| 2024-02-02 | 240,960 | 61 |
| 2024-02-05 | 280,471 | 54 |
| 2024-02-06 | 237,296 | 79 |
| 2024-02-07 | 271,894 | 65 |
| 2024-02-08 | 322,568 | 76 |
| 2024-02-09 | 227,661 | 58 |
| 2024-02-12 | 209,444 | 67 |
| 2024-02-13 | 218,458 | 103 |
| 2024-02-14 | 243,201 | 69 |
| 2024-02-15 | 235,789 | 65 |
| 2024-02-16 | 202,650 | 102 |
| 2024-02-20 | 235,281 | 85 |
| 2024-02-21 | 187,926 | 78 |
| 2024-02-22 | 185,411 | 67 |
| 2024-02-23 | 122,706 | 57 |
| 2024-02-26 | 273,435 | 67 |
| 2024-02-27 | 265,777 | 76 |
| 2024-02-28 | 264,282 | 59 |
| 2024-02-29 | 317,370 | 66 |

### Z3 records per trade date

| trade date | in session | before session |
|---|---|---|
| 2024-02-01 | 200,038 | 368 |
| 2024-02-02 | 168,281 | 103 |
| 2024-02-05 | 194,644 | 140 |
| 2024-02-06 | 184,834 | 55 |
| 2024-02-07 | 205,653 | 65 |
| 2024-02-08 | 236,988 | 96 |
| 2024-02-09 | 234,838 | 175 |
| 2024-02-12 | 173,620 | 82 |
| 2024-02-13 | 189,165 | 88 |
| 2024-02-14 | 192,512 | 140 |
| 2024-02-15 | 196,321 | 45 |
| 2024-02-16 | 148,161 | 82 |
| 2024-02-20 | 159,952 | 87 |
| 2024-02-21 | 128,930 | 50 |
| 2024-02-22 | 219,626 | 474 |
| 2024-02-23 | 192,064 | 56 |
| 2024-02-26 | 220,262 | 62 |
| 2024-02-27 | 214,342 | 41 |
| 2024-02-28 | 193,563 | 193 |
| 2024-02-29 | 202,176 | 111 |
