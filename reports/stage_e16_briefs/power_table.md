# Stage E.16 Task 3: power table (calendar-only counts)

Written 2026-10-09T01:22:42-07:00. Seed 20261009, 4000 simulations per cell. Priors (net Sharpe, annual): H1 0.3-0.8, H2 0.4-0.9, H3 0.3-0.7, H4 0.2-0.6, H5 0.8-1.5.

Pass = p <= threshold (the larger of plain-t and Newey-West p), mean > 0, n >= 30 and year stability; 0.01 is Holm's first step (0.05/5), 0.05 its last. Analytic = one-sided t power at the same threshold (noncentral t).

| window | test | prior | SR | units | units/yr | SR/unit | qual. yrs | pass@0.01 | pass@0.05 | analytic@0.01 | analytic@0.05 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full | H1 | low | 0.3 | 3385 | 249.0 | 0.0190 | 15 | 0.110 | 0.247 | 0.111 | 0.295 |
| full | H1 | high | 0.8 | 3385 | 249.0 | 0.0507 | 15 | 0.707 | 0.853 | 0.733 | 0.904 |
| full | H2 | low | 0.4 | 60 | 7.4 | 0.1468 | 8 | 0.105 | 0.258 | 0.112 | 0.301 |
| full | H2 | high | 0.9 | 60 | 7.4 | 0.3302 | 8 | 0.534 | 0.750 | 0.569 | 0.811 |
| full | H3 | low | 0.3 | 424 | 36.7 | 0.0495 | 12 | 0.091 | 0.234 | 0.095 | 0.265 |
| full | H3 | high | 0.7 | 424 | 36.7 | 0.1155 | 12 | 0.478 | 0.712 | 0.518 | 0.767 |
| full | H4 | low | 0.2 | 3385 | 249.0 | 0.0127 | 15 | 0.056 | 0.156 | 0.056 | 0.182 |
| full | H4 | high | 0.6 | 3385 | 249.0 | 0.0380 | 15 | 0.432 | 0.640 | 0.454 | 0.715 |
| full | H5 | low | 0.8 | 3381 | 251.8 | 0.0504 | 15 | 0.698 | 0.844 | 0.727 | 0.901 |
| full | H5 | high | 1.5 | 3381 | 251.8 | 0.0945 | 15 | 0.999 | 1.000 | 0.999 | 1.000 |
| fallback | H1 | low | 0.3 | 1193 | 252.2 | 0.0189 | 6 | 0.037 | 0.146 | 0.047 | 0.160 |
| fallback | H1 | high | 0.8 | 1193 | 252.2 | 0.0504 | 6 | 0.265 | 0.521 | 0.278 | 0.537 |
| fallback | H2 | low | 0.4 | 15 | 8.0 | 0.1414 | 2 | 0.000 | 0.000 | 0.034 | 0.131 |
| fallback | H2 | high | 0.9 | 15 | 8.0 | 0.3182 | 2 | 0.000 | 0.000 | 0.113 | 0.318 |
| fallback | H3 | low | 0.3 | 101 | 38.0 | 0.0487 | 3 | 0.030 | 0.112 | 0.033 | 0.123 |
| fallback | H3 | high | 0.7 | 101 | 38.0 | 0.1136 | 3 | 0.103 | 0.275 | 0.115 | 0.305 |
| fallback | H4 | low | 0.2 | 1193 | 252.2 | 0.0126 | 6 | 0.024 | 0.098 | 0.029 | 0.113 |
| fallback | H4 | high | 0.6 | 1193 | 252.2 | 0.0378 | 6 | 0.141 | 0.354 | 0.153 | 0.367 |
| fallback | H5 | low | 0.8 | 1156 | 253.0 | 0.0503 | 6 | 0.247 | 0.494 | 0.268 | 0.526 |
| fallback | H5 | high | 1.5 | 1156 | 253.0 | 0.0943 | 6 | 0.806 | 0.926 | 0.810 | 0.941 |

## Calendar-only unit counts per year (after warm-up)

- full H1: {'2010': 105, '2011': 249, '2012': 246, '2013': 247, '2014': 247, '2015': 247, '2016': 250, '2017': 248, '2018': 247, '2019': 247, '2020': 248, '2021': 250, '2022': 256, '2023': 255, '2024': 43}
- full H2: {'2016': 7, '2017': 8, '2018': 7, '2019': 7, '2020': 7, '2021': 7, '2022': 8, '2023': 8, '2024': 1}
- full H3: {'2012': 14, '2013': 34, '2014': 36, '2015': 33, '2016': 41, '2017': 36, '2018': 39, '2019': 34, '2020': 37, '2021': 38, '2022': 39, '2023': 37, '2024': 6}
- full H4: {'2010': 105, '2011': 249, '2012': 246, '2013': 247, '2014': 247, '2015': 247, '2016': 250, '2017': 248, '2018': 247, '2019': 247, '2020': 248, '2021': 250, '2022': 256, '2023': 255, '2024': 43}
- full H5: {'2010': 65, '2011': 249, '2012': 246, '2013': 250, '2014': 251, '2015': 253, '2016': 255, '2017': 249, '2018': 251, '2019': 250, '2020': 253, '2021': 253, '2022': 258, '2023': 255, '2024': 43}
- fallback H1: {'2019': 141, '2020': 248, '2021': 250, '2022': 256, '2023': 255, '2024': 43}
- fallback H2: {'2022': 6, '2023': 8, '2024': 1}
- fallback H3: {'2021': 19, '2022': 39, '2023': 37, '2024': 6}
- fallback H4: {'2019': 141, '2020': 248, '2021': 250, '2022': 256, '2023': 255, '2024': 43}
- fallback H5: {'2019': 101, '2020': 248, '2021': 251, '2022': 258, '2023': 255, '2024': 43}

## Exclusions (calendar-only, per test)

- full H1 (product-dates): {'early halt': 2270, 'eligible': 78819, 'no reference': 1868, 'not listed': 27, 'roll blackout': 5685, 'settlement unsourced': 1024, 'unsourced calendar date': 29}
- full H4 (product-dates): {'early halt': 2270, 'eligible': 78818, 'missing bar (calendar)': 1, 'no reference': 1868, 'not listed': 27, 'roll blackout': 5685, 'settlement unsourced': 1024, 'unsourced calendar date': 29}
- full H2: {'no reference': 4, 'no entry bar': 26, 'early halt': 21, 'roll blackout': 33, 'eligible': 80}
- full H3: {'auction not a trade date': 20, 'same-tenor overlap': 7, 'window end': 111, 'outside window': 4, 'eligible': 504, 'roll blackout': 105, 'early halt': 27, 'store boundary': 2}
- fallback H1 (product-dates): {'early halt': 687, 'eligible': 29955, 'no reference': 660, 'roll blackout': 2148}
- fallback H4 (product-dates): {'early halt': 687, 'eligible': 29955, 'no reference': 660, 'roll blackout': 2148}
- fallback H2: {'early halt': 8, 'eligible': 35, 'roll blackout': 14, 'no reference': 1}
- fallback H3: {'auction not a trade date': 20, 'same-tenor overlap': 7, 'window end': 111, 'outside window': 415, 'eligible': 181, 'roll blackout': 37, 'early halt': 9}

## Assumptions

- Roll blackout: 3 trade dates per ESTIMATED splice (the splice and the two before), splices from each product's full listed cycle (`cycles_assumed`, an upper bound on the volume roll's count): equity and FX on the contract month's third Friday minus 8 days, every other product on the 5th-last trade date of the month before each listed month. The run uses the stores' real roll metadata.
- Early halts, unsourced dates, open intervals: the frozen calendars; a required minute outside the trade date's open intervals is `missing bar (calendar)`.
- Missing bars inside the session: 0. Zero signals: 0 (not knowable without bars).
- Per-unit returns i.i.d. normal; SR/unit = SR annual / sqrt(units per full year).

