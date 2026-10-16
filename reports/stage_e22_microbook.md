# Stage E.22 Part B: the micro trend book, design study (B2-B3)

**These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.** No p-value is computed anywhere in this study.

Lead rulings applied (2026-10-16): S8 B-R1..B-R5; R-B6 the main greedy uses the 0.5 correlation shrink (the November 2021 post states shrinking without a value; B-R5 takes the code's 0.5), the no-shrink greedy is a sensitivity row; R-B7 E22-F1 rounds with the SIMPLE method (rounded and buffered): forward/config_f1.json rounding_method = simple, the greedy stays in forward/core.py as the study's comparison method, not used by E22-F1.

Run 2026-10-16T01:34:27-07:00 .. 2026-10-16T01:35:04-07:00 (microbook.run study). Spec: reports/stage_e22_briefs/lead_spec_B.md (S1-S8). Code: microbook/, forward/core.py. Machine-readable: reports/stage_e22_microbook.json. Constants: forward/config_f1.json.

## 1. Universe (S1)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

| Micro | Exposure | Owned path | Multiplier | Tick | Costs | Data | Status |
|---|---|---|---|---|---|---|---|
| MNQ | Nasdaq-100 | NQ | 2 USD per price unit | 0.25 / $0.50 | frozen | 2010-07-01..2024-02-29 | modelled |
| M2K | Russell 2000 | RTY | 5 USD per price unit | 0.1 / $0.50 | frozen | 2017-07-10..2024-02-29 | modelled |
| MGC | Gold | GC | 10 USD per price unit | 0.1 / $1.00 | frozen | 2010-07-01..2024-02-29 | modelled |
| MCL | WTI crude | CL | 100 USD per price unit | 0.01 / $1.00 | frozen | 2010-07-01..2024-02-29 | modelled |
| MNG | Henry Hub gas | NG | 1000 USD per price unit | 0.001 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| M6E | EUR/USD | 6E | 12500 USD per price unit | 0.0001 / $1.25 | extension | 2010-07-01..2024-02-29 | modelled |
| 2YY | 2-year yield | ZT (yield proxy, D 1.9, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 10 USD per bp | 0.1 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| 10Y | 10-year yield | ZN (yield proxy, D 6.5, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 10 USD per bp | 0.1 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| 30Y | 30-year yield | ZB (yield proxy, D 15.0, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 10 USD per bp | 0.1 / $1.00 | extension | 2010-07-01..2024-02-29 | modelled |
| MZC | Corn | ZC | 500 USD per price unit | 0.005 / $2.50 | extension | 2010-07-01..2024-02-29 | modelled |
| MZS | Soybeans | ZS | 500 USD per price unit | 0.005 / $2.50 | extension | 2010-07-01..2024-02-29 | modelled |
| MZL | Soybean oil | ZL | 6000 USD per price unit | 0.0002 / $1.20 | extension | 2010-07-01..2024-02-29 | modelled |
| SIL |  |  |  |  |  |  | not modelled: no owned silver path (SI not owned) |
| MHG |  |  |  |  |  |  | not modelled: only owned path HG/MHG step 2 2019-05..2024-02, never read by E.21; Part A K5 confirmation data |
| M6A |  |  |  |  |  |  | not modelled: only owned path 6A step 2, never read by E.21; Part A K3 confirmation data |
| M6B |  |  |  |  |  |  | not modelled: only owned path 6B step 2, never read by E.21; Part A K3 confirmation data |
| MCD |  |  |  |  |  |  | not modelled: only owned path 6C step 2, never read by E.21; Part A K3 confirmation data |
| MJY |  |  |  |  |  |  | not modelled: only owned path 6J step 2, never read by E.21; Part A K3 confirmation data |
| MZW |  |  |  |  |  |  | not modelled: only owned path ZW step 2, never read by E.21; Part A K6 confirmation data |
| MZM |  |  |  |  |  |  | not modelled: only owned path ZM step 2, never read by E.21; Part A K6 confirmation data |
| MES |  |  |  |  |  |  | not modelled: no owned 2010-2024 path (only MES's Stage D 2019-2024 store, a Part A leg) |
| MTN | Ultra 10-year (micro) | TN | 100 | 0.0078125 / $1.562 | extension |  | sensitivity only ($25K, in place of 10Y/30Y) |
| MWN | Ultra bond (micro) | UB | 100 | 0.03125 / $3.125 | extension |  | sensitivity only ($25K, in place of 10Y/30Y) |

Specs: E.13 T-28 (AMP contract specifications; quotes per row in forward/config_f1.json and microbook/universe.py). Costs 'frozen' = base_rules' D8 vehicle tables (settlement bucket, base); 'extension' = FLAGGED S6 D8 extension (commission per side + 1 tick per side). Yield-micro and micro-grain commissions are UNSOURCED (declared $1.92 RT, the largest frozen micro figure). Yield-proxy durations ZT 1.9, ZN 6.5, ZB 15.0 are a declared approximation, UNSOURCED.

## 2. Constants (S3, S4, S8)

| Constant | Value | Source |
|---|---|---|
| capital_usd | 25,000.000000 | reports/stage_e22_prereg_F1.md (draft) title: '$25,000' |
| rounding_method | simple | lead ruling R-B7 (2026-10-16): E22-F1 uses Carver's rounded-and-buffered baseline (key 'simple_rounding'); the greedy code and its parameters (key 'greedy') stay in forward/core.py and are NOT used by E22-F1 |
| ewmac.speeds | [[8, 32], [16, 64], [32, 128], [64, 256]] | lead_spec_B S3.2; CS A2 (C-CH15:28-63 'Lfast: 8 Lslow: 32' ... 'Lfast: 64 Lslow: 256') |
| ewmac.ewma_definition | pandas ewm(span=L, min_periods=1).mean() | CS A1 (C-EWMAC:120-124 'fast_ewma = price.ewm(span=Lfast, min_periods=1).mean()') |
| ewmac.scalars | {'8/32': 5.949404365193165, '16/64': 4.104172020369661, '32/128': 2.786994330124792, '64/256': 1.9093945630747895} | lead ruling S8 B-R1; CS A6b (C-ROB:364-368 'momentum8: 5.949404365193165', 'momentum16: 4.104172020369661', 'momentum32: 2.786994330124792', 'momentum64: 1.9093945630747895') |
| ewmac.denominator | the mixed daily price-difference vol (key 'vol') | lead ruling S8 B-R2; CS A3, A5 (C-DEF:112-119 'func: "sysquant.estimators.vol.mixed_vol_calc"') |
| forecast_cap | 20.000000 | lead_spec_B S3.2-3; CS A8 (C-DEF:141 'forecast_cap: 20.0') |
| average_abs_forecast | 10.000000 | CS A7 (C-DEF:143 'average_absolute_forecast: 10.0') |
| vol.recent_span | 35 | CS A5, A12 (C-DEF:116 'days: 35'; C-VOL:188 'ewm(adjust=True, span=days, min_periods=min_periods).std()') |
| vol.min_periods | 10 | CS A5 (C-DEF:117 'min_periods: 10') |
| vol.slow_vol_years | 10 | CS A12b (C-DEF:118 'slow_vol_years: 10') |
| vol.business_days_per_year | 256.000000 | CS A12c (C-DATE:26 'BUSINESS_DAYS_IN_YEAR = 256.0'); slow span = years x 256 (C-VOL:170) |
| vol.proportion_of_slow_vol | 0.300000 | lead_spec_B S3.4; CS A12b (C-DEF:119 'proportion_of_slow_vol: 0.3') |
| vol.vol_abs_min | 0.000000 | CS A12d (C-DEF:120 'vol_abs_min: 0.0000000001') |
| vol.annualisation | 16.000000 | CS A12c (sqrt(256), C-DATE:27 'ROOT_BDAYS_INYEAR = BUSINESS_DAYS_IN_YEAR**0.5') |
| vol.dollar_vol_definition | multiplier x 16 x daily price-difference vol | lead ruling (coordinator message 2026-10-16): sigma_% := sigma(dP)/P |
| vol_target | 0.200000 | lead_spec_B S3.5 (tau = 0.20, the stage prompt) |
| fdm.weights | [0.25, 0.25, 0.25, 0.25] | lead_spec_B S3.3 (equal weight) |
| fdm.dm_max | 2.500000 | CS A9 (C-DM:76 'dm_max: float = 2.5') |
| fdm.floor_at_zero | True | CS A9b (C-DEF:162 'floor_at_zero: True') |
| fdm.estimate | Pearson correlation of the four scaled, capped forecasts, weekly (W-FRI last), pooled (stacked) over the 12 instruments' | lead_spec_B S3.3; weekly frequency from CS A9b (C-DEF:155 'frequency: "W"') |
| idm.dm_max | 2.500000 | CS A10 (C-DEF:253 'dm_max: 2.5') |
| idm.floor_at_zero | True | CS A10b (C-DEF:247 'floor_at_zero: True') |
| idm.estimate | Pearson correlation of weekly (W-FRI sum) instrument subsystem returns (unrounded position F/10 / annual $ vol, filled a | lead_spec_B S3.5; weekly frequency and subsystem returns from CS A10b (C-DEF:240, C-PORT:415) |
| warmup_diffs | 256 | MicroBookCoder choice (microbook/README.md): an instrument is live once 256 daily differences exist (the slowest EWMAC span); not a Carver figure |
| simple_rounding.buffer_size | 0.100000 | lead ruling S8 B-R3; CS A13 (C-DEF:297 'buffer_size: 0.10'; P-NOV21 'a simple 10% of average position') |
| simple_rounding.trade_to_edge | True | CS A13 (C-DEF:298 'buffer_trade_to_edge: True'), A13b (C-ABS:197-208) |
| simple_rounding.rounding | half away from zero | lead ruling S8 B-R3 (posts silent; pysystemtrade rounds half to even) |
| greedy.used_by_e22_f1 | False | lead ruling R-B7: E22-F1 rounds with 'simple_rounding'; the greedy is the study's comparison method only |
| greedy.shadow_cost | 250.000000 | lead ruling S8 B-R4; CS B.1 step 5 (P-NOV21 .txt:136-141 'Shadow cost 250') |
| greedy.te_buffer | 0.012500 | lead ruling S8 B-R4; CS B.1 step 7 (P-NOV21 .txt:140-141 'Buffer size 0.0125'); not rescaled to tau 20% |
| greedy.start | zero | CS B.1 step 4 (P-OCT21, P-NOV21 .txt:73 'the algo always starts at zero') |
| greedy.direction | sign of the unrounded optimum; sign(0) = +1 | CS B.1 step 4; B.2 (C-GEN:142-157 sign(0) = 1.0) |
| greedy.trade_rounding | half away from zero | lead ruling S8 B-R3 (P-NOV21: 'And then round them, obviously.') |
| greedy.all_zero_result | accepted (no fallback to prior) | MicroBookCoder choice: the post has no fallback; C-OPT:164-170's error fallback is code-only (CS B.3 D7) |
| greedy.cost_per_contract | the per-side cost of section 'costs' (USD, base case), undeflated | lead ruling S8 B-R4 (no end-of-sample look-ahead); the backtest charges the same undeflated cost |
| greedy.correlation.returns | percentage returns dP/P of the held contract (yield micros: yield changes) | CS B.2 (C-PORT:1117 get_daily_percentage_returns); yields per the lead's sigma ruling |
| greedy.correlation.return_days | 7 | lead ruling S8 B-R5; CS B.2 (C-DEF:313 'frequency: "7D"'), windows ending on the decision date |
| greedy.correlation.ew_span | 75 | lead ruling S8 B-R5; CS B.2 (C-DEF 'ew_lookback: 75', a pandas span, C-EXPC:151-152) |
| greedy.correlation.min_periods | 10 | lead ruling S8 B-R5; CS B.2 (C-DEF 'min_periods: 10') |
| greedy.correlation.years | 5 | lead ruling S8 B-R5; CS B.2 (C-DEF 'rollyears: 5', date_method rolling) |
| greedy.correlation.clip | 0.990000 | lead ruling S8 B-R5; CS B.2 (C-DEF 'clip: 0.99') |
| greedy.correlation.offdiag | 0.000000 | lead ruling S8 B-R5; CS B.2 (C-DEF 'offdiag: 0.0') |
| greedy.correlation.floor_at_zero | False | CS B.1 step 3 (P-JUN21 .txt:70 'We don't floor_at_zero'); C-DEF 'floor_at_zero: False' |
| greedy.correlation.shrinkage | 0.500000 | lead ruling R-B6 (2026-10-16): P-NOV21 .txt:153 states shrinking ('What eventually came to the rescue ... was shrinking the correlation matrix') without a value, so B-R5 takes the code's 0.5 toward a zero off-diagonal (C-STAGE:285-286, C-CORR:95) |
| greedy.correlation.reestimate | every decision date | MicroBookCoder choice (code re-estimates weekly in backtests; P-JUN21 'will need to be done every day in production') |
| greedy.volatility | annual $ vol per contract (key 'vol') | CS B.2 (stdev = annualised mixed vol, C-PORT:1263) |
| fills | orders from data through settle(t) fill at settle(t+1), the instrument's next settlement | lead_spec_B S3.7 |

## 3. Estimates (frozen for E22-F1)

- FDM = 1.1314 (pooled weekly forecast correlation, 7,555 instrument-weeks, floored at 0, cap 2.5).
- IDM (12 instruments) = 2.3518; mean IDM over the series span with the live sub-matrix = 2.3364.
- FDM correlation (8/32, 16/64, 32/128, 64/256): [1.00, 0.88, 0.62, 0.38]; [0.88, 1.00, 0.88, 0.62]; [0.62, 0.88, 1.00, 0.88]; [0.38, 0.62, 0.88, 1.00]

| Speed | Mean |scaled capped forecast| (pooled, live days) | Target |
|---|---|---|
| 8/32 | 8.57 | 10 |
| 16/64 | 8.52 | 10 |
| 32/128 | 8.49 | 10 |
| 64/256 | 8.76 | 10 |
| combined | 8.48 | 10 |

IDM correlation (weekly subsystem returns, before flooring):

|  | MNQ | M2K | MGC | MCL | MNG | M6E | 2YY | 10Y | 30Y | MZC | MZS | MZL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MNQ | 1.00 | 0.51 | -0.00 | 0.02 | 0.04 | 0.14 | -0.03 | -0.14 | -0.15 | -0.00 | 0.00 | 0.00 |
| M2K | 0.51 | 1.00 | -0.07 | 0.20 | 0.01 | 0.20 | -0.00 | -0.01 | 0.03 | 0.05 | 0.15 | 0.17 |
| MGC | -0.00 | -0.07 | 1.00 | -0.04 | 0.02 | 0.14 | 0.11 | 0.22 | 0.18 | 0.04 | 0.01 | 0.01 |
| MCL | 0.02 | 0.20 | -0.04 | 1.00 | 0.07 | 0.07 | 0.05 | 0.04 | 0.09 | 0.12 | 0.11 | 0.20 |
| MNG | 0.04 | 0.01 | 0.02 | 0.07 | 1.00 | 0.03 | -0.07 | -0.02 | 0.02 | 0.00 | -0.01 | 0.00 |
| M6E | 0.14 | 0.20 | 0.14 | 0.07 | 0.03 | 1.00 | 0.04 | 0.05 | 0.01 | 0.11 | 0.07 | 0.14 |
| 2YY | -0.03 | -0.00 | 0.11 | 0.05 | -0.07 | 0.04 | 1.00 | 0.72 | 0.51 | 0.03 | 0.01 | 0.02 |
| 10Y | -0.14 | -0.01 | 0.22 | 0.04 | -0.02 | 0.05 | 0.72 | 1.00 | 0.89 | -0.01 | 0.01 | 0.05 |
| 30Y | -0.15 | 0.03 | 0.18 | 0.09 | 0.02 | 0.01 | 0.51 | 0.89 | 1.00 | -0.02 | 0.03 | 0.08 |
| MZC | -0.00 | 0.05 | 0.04 | 0.12 | 0.00 | 0.11 | 0.03 | -0.01 | -0.02 | 1.00 | 0.49 | 0.26 |
| MZS | 0.00 | 0.15 | 0.01 | 0.11 | -0.01 | 0.07 | 0.01 | 0.01 | 0.03 | 0.49 | 1.00 | 0.43 |
| MZL | 0.00 | 0.17 | 0.01 | 0.20 | 0.00 | 0.14 | 0.02 | 0.05 | 0.08 | 0.26 | 0.43 | 1.00 |

## 4. Returns by capital and method (S5)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

Daily net $ P&L series from the first fill of the unrounded book (2011-07-08) to 2024-02-29; annualised x252 (mean) and x sqrt(252) (sd, Sharpe). Fixed capital, no compounding. Stress = 2 x slippage (S6).

| Book | Mean $/yr | Sd $/yr | Mean % | Sd % (target 20) | SR gross | SR net | SR net stress | Net SR loss vs unrounded | Corr with unrounded |
|---|---|---|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 1,047 | 2,208 | 10.5 | 22.1 | 0.61 | 0.47 | 0.40 | 0.00 | 1.00 |
| $10,000 simple (rounded + buffered) | 945 | 2,010 | 9.5 | 20.1 | 0.57 | 0.47 | 0.41 | 0.00 | 0.84 |
| $10,000 greedy (Nov 2021, shrink 0.5) | 80 | 1,089 | 0.8 | 10.9 | 0.09 | 0.07 | 0.07 | 0.40 | 0.48 |
| $25,000 unrounded (reference) | 2,619 | 5,519 | 10.5 | 22.1 | 0.61 | 0.47 | 0.40 | 0.00 | 1.00 |
| $25,000 simple (rounded + buffered) | 2,219 | 5,461 | 8.9 | 21.8 | 0.51 | 0.41 | 0.34 | 0.07 | 0.95 |
| $25,000 greedy (Nov 2021, shrink 0.5) | 1,150 | 4,033 | 4.6 | 16.1 | 0.31 | 0.29 | 0.27 | 0.19 | 0.75 |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 2,144 | 5,325 | 8.6 | 21.3 | 0.52 | 0.40 | 0.33 | 0.00 | 1.00 |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 1,878 | 5,388 | 7.5 | 21.6 | 0.44 | 0.35 | 0.29 | 0.05 | 0.95 |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 1,033 | 4,334 | 4.1 | 17.3 | 0.27 | 0.24 | 0.22 | 0.16 | 0.78 |
| $50,000 unrounded (reference) | 5,237 | 11,039 | 10.5 | 22.1 | 0.61 | 0.47 | 0.40 | 0.00 | 1.00 |
| $50,000 simple (rounded + buffered) | 5,048 | 10,968 | 10.1 | 21.9 | 0.57 | 0.46 | 0.40 | 0.01 | 0.99 |
| $50,000 greedy (Nov 2021, shrink 0.5) | 2,521 | 8,023 | 5.0 | 16.0 | 0.35 | 0.31 | 0.30 | 0.16 | 0.81 |

## 5. Turnover and costs (S5, S6)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

| Book | Contracts traded/yr | Roll fills/yr | Round turns/yr | Cost $/yr | Cost % of capital | Cost (SR units) | Cost $/yr stress |
|---|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 81 | 53 | 67 | 296 | 2.96 | 0.134 | 471 |
| $10,000 simple (rounded + buffered) | 51 | 40 | 46 | 206 | 2.06 | 0.102 | 328 |
| $10,000 greedy (Nov 2021, shrink 0.5) | 5 | 5 | 5 | 15 | 0.15 | 0.014 | 23 |
| $25,000 unrounded (reference) | 202 | 133 | 168 | 741 | 2.96 | 0.134 | 1,178 |
| $25,000 simple (rounded + buffered) | 131 | 127 | 129 | 572 | 2.29 | 0.104 | 910 |
| $25,000 greedy (Nov 2021, shrink 0.5) | 23 | 44 | 33 | 120 | 0.48 | 0.030 | 185 |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 157 | 119 | 138 | 648 | 2.59 | 0.121 | 1,055 |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 102 | 111 | 107 | 502 | 2.01 | 0.093 | 818 |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 28 | 48 | 38 | 137 | 0.55 | 0.031 | 213 |
| $50,000 unrounded (reference) | 404 | 266 | 335 | 1,481 | 2.96 | 0.134 | 2,357 |
| $50,000 simple (rounded + buffered) | 262 | 259 | 260 | 1,154 | 2.31 | 0.105 | 1,837 |
| $50,000 greedy (Nov 2021, shrink 0.5) | 53 | 98 | 75 | 273 | 0.55 | 0.034 | 420 |

## 6. Drawdowns (S5)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

Bootstrap: circular blocks of 21 days, 10,000 resamples of 252 days, seed 20261016 (a fresh generator per series); expected = mean, worst = 95th percentile, also the 99th.

| Book | Realized max DD $ | % of capital | Peak .. trough | Exp. 1y max DD $ | p95 $ | p99 $ | Exp. % | p95 % | p99 % |
|---|---|---|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 5,471 | 54.7 | 2015-01-30 .. 2017-09-27 | 2,088 | 3,771 | 4,678 | 20.9 | 37.7 | 46.8 |
| $10,000 simple (rounded + buffered) | 3,342 | 33.4 | 2015-01-30 .. 2017-09-29 | 1,927 | 3,491 | 4,413 | 19.3 | 34.9 | 44.1 |
| $10,000 greedy (Nov 2021, shrink 0.5) | 3,340 | 33.4 | 2012-02-28 .. 2017-02-07 | 1,101 | 2,080 | 2,633 | 11.0 | 20.8 | 26.3 |
| $25,000 unrounded (reference) | 13,677 | 54.7 | 2015-01-30 .. 2017-09-27 | 5,221 | 9,428 | 11,695 | 20.9 | 37.7 | 46.8 |
| $25,000 simple (rounded + buffered) | 15,874 | 63.5 | 2015-01-30 .. 2017-09-28 | 5,501 | 9,851 | 12,348 | 22.0 | 39.4 | 49.4 |
| $25,000 greedy (Nov 2021, shrink 0.5) | 9,064 | 36.3 | 2022-05-05 .. 2024-01-12 | 4,040 | 7,614 | 9,872 | 16.2 | 30.5 | 39.5 |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 13,951 | 55.8 | 2015-03-17 .. 2019-12-03 | 5,083 | 8,962 | 11,187 | 20.3 | 35.8 | 44.7 |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 14,949 | 59.8 | 2022-05-05 .. 2024-01-31 | 5,232 | 9,481 | 11,848 | 20.9 | 37.9 | 47.4 |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 10,781 | 43.1 | 2022-05-05 .. 2024-01-05 | 4,373 | 8,045 | 10,232 | 17.5 | 32.2 | 40.9 |
| $50,000 unrounded (reference) | 27,354 | 54.7 | 2015-01-30 .. 2017-09-27 | 10,441 | 18,856 | 23,389 | 20.9 | 37.7 | 46.8 |
| $50,000 simple (rounded + buffered) | 22,896 | 45.8 | 2015-01-30 .. 2017-09-27 | 10,342 | 18,622 | 23,360 | 20.7 | 37.2 | 46.7 |
| $50,000 greedy (Nov 2021, shrink 0.5) | 14,340 | 28.7 | 2022-10-20 .. 2024-01-05 | 7,650 | 14,068 | 17,837 | 15.3 | 28.1 | 35.7 |

## 7. Instruments at zero and margin (S5)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

Margin: /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e22_briefs/ibkr_margins.json (IBKR overnight initial per contract, as fetched in 2026, applied to every date: a present-day rate on historical positions; since sizing gives more contracts when prices are lower, the early years' margin is biased upward, notably for MNQ and MGC). The unrounded book's margin uses fractional contracts.

| Book | Mean share of live instruments at 0 | Margin mean $ | p95 $ | max $ | % of capital (mean/p95/max) | Margin not sourced |
|---|---|---|---|---|---|---|
| $10,000 unrounded (reference) | 0.00 | 5,749 | 10,615 | 13,671 | 57.5 / 106.2 / 136.7 | none |
| $10,000 simple (rounded + buffered) | 0.70 | 3,994 | 9,715 | 14,625 | 39.9 / 97.2 / 146.2 | none |
| $10,000 greedy (Nov 2021, shrink 0.5) | 0.95 | 1,673 | 6,632 | 10,350 | 16.7 / 66.3 / 103.5 | none |
| $25,000 unrounded (reference) | 0.00 | 14,373 | 26,538 | 34,178 | 57.5 / 106.2 / 136.7 | none |
| $25,000 simple (rounded + buffered) | 0.40 | 12,990 | 26,021 | 34,835 | 52.0 / 104.1 / 139.3 | none |
| $25,000 greedy (Nov 2021, shrink 0.5) | 0.71 | 7,828 | 16,982 | 24,850 | 31.3 / 67.9 / 99.4 | none |
| $25,000 WITHOUT yield proxies, unrounded (reference) | 0.00 | 12,601 | 28,617 | 36,153 | 50.4 / 114.5 / 144.6 | none |
| $25,000 WITHOUT yield proxies, simple (rounded + buffered) | 0.39 | 11,505 | 28,675 | 36,827 | 46.0 / 114.7 / 147.3 | none |
| $25,000 WITHOUT yield proxies, greedy (Nov 2021, shrink 0.5) | 0.66 | 9,415 | 22,796 | 30,200 | 37.7 / 91.2 / 120.8 | none |
| $50,000 unrounded (reference) | 0.00 | 28,745 | 53,076 | 68,356 | 57.5 / 106.2 / 136.7 | none |
| $50,000 simple (rounded + buffered) | 0.22 | 27,654 | 52,010 | 67,071 | 55.3 / 104.0 / 134.1 | none |
| $50,000 greedy (Nov 2021, shrink 0.5) | 0.57 | 16,561 | 33,288 | 46,421 | 33.1 / 66.6 / 92.8 | none |

## 8. Capital sweep: Sharpe loss against unrounded (S5)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

| Capital | SR net unrounded | SR net simple | SR net greedy | Loss simple | Loss greedy | Zero share simple | Zero share greedy |
|---|---|---|---|---|---|---|---|
| $10,000 | 0.47 | 0.47 | 0.07 | 0.00 | 0.40 | 0.70 | 0.95 |
| $15,000 | 0.47 | 0.79 | 0.39 | -0.31 | 0.09 | 0.56 | 0.87 |
| $25,000 | 0.47 | 0.41 | 0.29 | 0.07 | 0.19 | 0.40 | 0.71 |
| $35,000 | 0.47 | 0.43 | 0.15 | 0.04 | 0.33 | 0.31 | 0.64 |
| $50,000 | 0.47 | 0.46 | 0.31 | 0.01 | 0.16 | 0.22 | 0.57 |
| $75,000 | 0.47 | 0.46 | 0.31 | 0.01 | 0.17 | 0.15 | 0.51 |
| $100,000 | 0.47 | 0.48 | 0.30 | -0.01 | 0.18 | 0.11 | 0.49 |
| $250,000 | 0.47 | 0.48 | 0.29 | -0.01 | 0.19 | 0.04 | 0.40 |

## 9. Per instrument (S5)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

Cost per round turn: mean over live days of buy + sell per-side cost (base). In Sharpe units: cost per round turn / median annual $ vol per contract; Carver's 0.01 SR test reported, not applied (E.13 T-18). Minimum capital: Carver's formula 4 contracts x $ vol / (tau x IDM x weight) (E.13 Part B, T-25), with ours (tau 0.20, the study IDM, w = 1/12) and with his report's assumptions (25%, IDM 2.5, w 0.04), at the median $ vol.

| Micro | Path | Live from | Multiplier | Cost/RT $ | Cost/RT SR | 0.01 test | Median $ vol/contract | Min capital (ours) | Min capital (his assumptions) | Mean |F| |
|---|---|---|---|---|---|---|---|---|---|---|
| MNQ | NQ | 2011-07-08 | 2 | 2.10 | 0.0013 | pass | 1,634 | 166,707 | 261,375 | 11.26 |
| M2K | RTY | 2018-07-18 | 5 | 2.18 | 0.0011 | pass | 1,982 | 202,296 | 317,175 | 7.50 |
| MGC | GC | 2011-07-07 | 10 | 4.08 | 0.0018 | pass | 2,218 | 226,343 | 354,877 | 6.92 |
| MCL | CL | 2011-07-13 | 100 | 3.16 | 0.0015 | pass | 2,081 | 212,411 | 333,034 | 7.82 |
| MNG | NG | 2011-07-19 | 1000 | 3.92 | 0.0030 | pass | 1,306 | 133,275 | 208,959 | 8.97 |
| M6E | 6E | 2011-07-11 | 12500 | 3.50 | 0.0030 | pass | 1,154 | 117,781 | 184,666 | 8.15 |
| 2YY | ZT (yield proxy, D 1.9, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 2011-07-15 | 10 | 3.92 | 0.0094 | pass | 415 | 42,399 | 66,476 | 9.28 |
| 10Y | ZN (yield proxy, D 6.5, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 2011-07-11 | 10 | 3.92 | 0.0054 | pass | 730 | 74,495 | 116,799 | 8.84 |
| 30Y | ZB (yield proxy, D 15.0, declared approximation, UNSOURCED (lead_spec_B S3.6)) | 2011-07-11 | 10 | 3.92 | 0.0063 | pass | 620 | 63,271 | 99,201 | 8.59 |
| MZC | ZC | 2011-07-11 | 500 | 6.92 | 0.0126 | fail | 548 | 55,931 | 87,693 | 7.97 |
| MZS | ZS | 2011-07-11 | 500 | 6.92 | 0.0060 | pass | 1,148 | 117,192 | 183,743 | 7.52 |
| MZL | ZL | 2011-07-11 | 6000 | 4.32 | 0.0091 | pass | 472 | 48,210 | 75,588 | 8.37 |

Per instrument: % of live days held at zero (unrounded: never zero by construction).

| Micro | $10K simple | $10K greedy | $25K simple | $25K greedy | $50K simple | $50K greedy |
|---|---|---|---|---|---|---|
| MNQ | 77.5 | 80.3 | 51.6 | 52.3 | 32.2 | 32.8 |
| M2K | 97.6 | 88.4 | 70.3 | 53.0 | 36.6 | 44.8 |
| MGC | 99.5 | 99.0 | 78.8 | 75.1 | 50.3 | 48.3 |
| MCL | 99.3 | 99.2 | 71.9 | 66.2 | 44.0 | 33.4 |
| MNG | 87.6 | 100.0 | 43.3 | 57.9 | 21.3 | 40.9 |
| M6E | 83.5 | 98.9 | 38.2 | 57.8 | 19.3 | 34.7 |
| 2YY | 31.2 | 96.5 | 11.9 | 77.1 | 6.5 | 71.4 |
| 10Y | 54.4 | 82.0 | 22.9 | 54.5 | 12.2 | 49.3 |
| 30Y | 49.7 | 90.7 | 21.4 | 67.0 | 10.5 | 60.1 |
| MZC | 51.1 | 100.0 | 21.0 | 100.0 | 10.0 | 97.1 |
| MZS | 82.4 | 100.0 | 45.3 | 89.8 | 25.7 | 81.7 |
| MZL | 43.6 | 100.0 | 17.0 | 93.0 | 9.4 | 84.6 |

Per instrument: net $ per year.

| Micro | $10K unrounded | $10K simple | $10K greedy | $25K unrounded | $25K simple | $25K greedy | $50K unrounded | $50K simple | $50K greedy |
|---|---|---|---|---|---|---|---|---|---|
| MNQ | 268 | 214 | 108 | 670 | 361 | 355 | 1,339 | 1,430 | 1,181 |
| M2K | -52 | -15 | 184 | -130 | -115 | 143 | -259 | -194 | -8 |
| MGC | -39 | 18 | -63 | -98 | -95 | -296 | -197 | -552 | -491 |
| MCL | 154 | -12 | -106 | 384 | 363 | 582 | 768 | 600 | 1,123 |
| MNG | 116 | 81 | 0 | 290 | 364 | 344 | 579 | 591 | 240 |
| M6E | 93 | 119 | -72 | 233 | 120 | 159 | 467 | 638 | 421 |
| 2YY | 136 | 111 | 9 | 340 | 331 | 151 | 679 | 748 | 561 |
| 10Y | 102 | 15 | 27 | 254 | 236 | 189 | 509 | 522 | 180 |
| 30Y | 127 | 101 | -7 | 318 | 266 | -62 | 637 | 601 | -41 |
| MZC | 31 | 100 | 0 | 78 | 75 | 0 | 156 | 203 | -90 |
| MZS | 55 | 88 | 0 | 138 | 187 | -278 | 276 | 191 | -221 |
| MZL | 60 | 128 | 0 | 149 | 132 | -133 | 299 | 283 | -327 |

## 10. Sensitivities at $25,000 (S5)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

| Sensitivity | Method | SR net | Sd % | Loss vs unrounded | Cost $/yr |
|---|---|---|---|---|---|
| without the yield proxies (9 instruments) | unrounded | 0.40 | 21.3 | 0.00 | 648 |
| without the yield proxies (9 instruments) | simple | 0.35 | 21.6 | 0.05 | 502 |
| without the yield proxies (9 instruments) | greedy | 0.24 | 17.3 | 0.16 | 137 |
| book forecast scalars 5.3/3.75/2.65/1.87 (FDM, IDM held) | unrounded | 0.48 | 21.1 | 0.00 | 698 |
| book forecast scalars 5.3/3.75/2.65/1.87 (FDM, IDM held) | simple | 0.47 | 20.9 | 0.01 | 526 |
| book forecast scalars 5.3/3.75/2.65/1.87 (FDM, IDM held) | greedy | 0.18 | 15.6 | 0.29 | 115 |
| MTN/MWN on TN/UB in place of 10Y/30Y | unrounded | 0.50 | 21.9 | 0.00 | 728 |
| MTN/MWN on TN/UB in place of 10Y/30Y | simple | 0.42 | 22.2 | 0.08 | 568 |
| MTN/MWN on TN/UB in place of 10Y/30Y | greedy | 0.24 | 17.1 | 0.26 | 118 |
| greedy WITHOUT the 0.5 correlation shrink at $10,000 | greedy | 0.25 | 18.1 | 0.22 | 49 |
| greedy WITHOUT the 0.5 correlation shrink at $25,000 | greedy | 0.20 | 19.6 | 0.28 | 200 |
| greedy WITHOUT the 0.5 correlation shrink at $50,000 | greedy | 0.37 | 19.6 | 0.10 | 405 |

Shrink: lead ruling R-B6 (P-NOV21 .txt:153 states shrinking the correlation matrix without a value; B-R5 takes the code's 0.5): the main greedy rows use the 0.5 shrink; the rows above show the greedy without it.

## 10b. Diagnostic: the greedy's tracking error against plain rounding

Every 7th decision date: the greedy integer solution from zero with shadow cost 0 (no buffer) versus rounding each unrounded position half away from zero, tracking error to the unrounded optimum under the same covariance. The greedy steps one contract at a time in the sign of each optimum and cannot step back, so with highly correlated instruments (10Y/30Y about 0.9) it can overshoot one and leave the other short.

| Capital | Dates | Share greedy TE > rounding TE | Median TE ratio greedy/rounding | p90 ratio |
|---|---|---|---|---|
| $10,000 | 457 | 0.04 | 0.98 | 1.00 |
| $15,000 | 457 | 0.06 | 0.97 | 1.00 |
| $25,000 | 457 | 0.11 | 0.98 | 1.01 |
| $35,000 | 457 | 0.12 | 0.98 | 1.04 |
| $50,000 | 457 | 0.16 | 0.98 | 1.10 |
| $75,000 | 457 | 0.29 | 0.99 | 1.30 |
| $100,000 | 457 | 0.30 | 0.99 | 1.48 |
| $250,000 | 457 | 0.52 | 1.01 | 3.12 |

## 11. Optimiser and data counters

Greedy steps per decision date (main greedy, 0.5 correlation shrink). Step 3's x (tracking error of the current against the integer-optimised positions) and the buffer b = 0.0125 are both annualised tracking-error standard deviations as a fraction of capital (weights = contracts x multiplier x price / capital, covariance of annualised percentage returns; pinned by tests/test_forward_core_rounding.py). An adjustment of 0 almost always means x = 0: at small capital one contract is several % of tracking error, so step 1 rarely holds, and the shadow-cost penalty (250 x per-side cost / capital per contract traded) makes the current positions the greedy's best integer portfolio on most days.

| Capital | Decision dates | Inside buffer (step 1) | x = 0: integer optimum = current | 0 < x <= b | Trades round to 0 | Traded | All-zero integer result |
|---|---|---|---|---|---|---|---|
| $10,000 | 3197 | 7 | 3132 | 0 | 0 | 58 | 1638 |
| $15,000 | 3197 | 7 | 3054 | 0 | 0 | 136 | 555 |
| $25,000 | 3197 | 8 | 2882 | 11 | 37 | 259 | 76 |
| $35,000 | 3197 | 9 | 2656 | 7 | 151 | 374 | 16 |
| $50,000 | 3197 | 10 | 2155 | 30 | 547 | 455 | 9 |
| $75,000 | 3197 | 11 | 1627 | 202 | 815 | 542 | 9 |
| $100,000 | 3197 | 13 | 1176 | 409 | 983 | 616 | 5 |
| $250,000 | 3197 | 15 | 373 | 990 | 712 | 1107 | 3 |

| Micro | Path | Marks | Rolls | Listed dates without a mark (dropped) | Splices removed (no bar between) | Store boundary chained | Undefined moves |
|---|---|---|---|---|---|---|---|
| MNQ | NQ | 3402 | 54 | 129 | 0 | 1 | 0 |
| M2K | RTY | 1656 | 26 | 61 | 0 | 1 | 0 |
| MGC | GC | 3422 | 68 | 105 | 0 | 1 | 0 |
| MCL | CL | 3401 | 164 | 126 | 0 | 1 | 0 |
| MNG | NG | 3413 | 166 | 114 | 0 | 1 | 0 |
| M6E | 6E | 3425 | 54 | 106 | 0 | 1 | 0 |
| 2YY | ZT | 3401 | 55 | 129 | 0 | 1 | 0 |
| 10Y | ZN | 3412 | 55 | 118 | 0 | 1 | 0 |
| 30Y | ZB | 3411 | 54 | 119 | 0 | 1 | 0 |
| MZC | ZC | 3401 | 90 | 41 | 13 | 1 | 0 |
| MZS | ZS | 3402 | 82 | 40 | 6 | 1 | 0 |
| MZL | ZL | 3400 | 88 | 42 | 4 | 1 | 0 |

Series grid: 3,453 dates (252.7 per calendar year; the union of the 12 paths' mark dates).

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge.

