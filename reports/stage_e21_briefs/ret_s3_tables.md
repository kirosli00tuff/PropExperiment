### Verdict table (base case; Holm step-down at family alpha 0.025; N 532)

| Test | n | mean (capital units/day) | sd | t | t NW | p (t) | p (NW) | p | Sharpe (ann.) | 95% CI | Holm rejects | Sharpe >= 0.3 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 3205 | 0.00032871 | 0.0104765 | 1.776 | 1.729 | 0.0379 | 0.0419 | 0.0419 | 0.498 | [-0.063, 1.053] | False | True | FAIL |
| T2 | 3205 | 0.000224288 | 0.00815743 | 1.557 | 1.525 | 0.0598 | 0.0637 | 0.0637 | 0.436 | [-0.109, 0.982] | False | True | FAIL |
| T3 | 3319 | 0.000101562 | 0.0110445 | 0.530 | 0.523 | 0.2982 | 0.3003 | 0.3003 | 0.146 | [-0.399, 0.706] | False | False | FAIL |
| T4 | 3331 | 0.0558588 | 7.58019 | 0.425 | 0.430 | 0.3353 | 0.3335 | 0.3353 | 0.117 | [-0.369, 0.600] | False | False | FAIL |

### Cost cases (reported; the prompt's stress case is 1.5 x slippage)

| Test | Case | t | p | Sharpe | gross | costs | net | costs / gross |
|---|---|---|---|---|---|---|---|---|
| T1 | base (D8) | 1.776 | 0.0419 | 0.498 | 1.1352 | 0.0817 | 1.0535 | 0.072 |
| T1 | D8 + 1 tick/side | 1.614 | 0.0583 | 0.453 | 1.1352 | 0.1778 | 0.9574 | 0.157 |
| T1 | 1.5 x slippage | 1.726 | 0.0465 | 0.484 | 1.1352 | 0.1112 | 1.0240 | 0.098 |
| T2 | base (D8) | 1.557 | 0.0637 | 0.436 | 0.7973 | 0.0785 | 0.7188 | 0.098 |
| T2 | D8 + 1 tick/side | 1.348 | 0.0935 | 0.378 | 0.7973 | 0.1746 | 0.6227 | 0.219 |
| T2 | 1.5 x slippage | 1.495 | 0.0716 | 0.419 | 0.7973 | 0.1069 | 0.6904 | 0.134 |
| T3 | base (D8) | 0.530 | 0.3003 | 0.146 | 0.4279 | 0.0908 | 0.3371 | 0.212 |
| T3 | D8 + 1 tick/side | 0.462 | 0.3239 | 0.127 | 0.4279 | 0.1338 | 0.2941 | 0.313 |
| T3 | 1.5 x slippage | 0.500 | 0.3108 | 0.138 | 0.4279 | 0.1101 | 0.3179 | 0.257 |
| T4 | base (D8) | 0.425 | 0.3353 | 0.117 | n/a | n/a | n/a | n/a |
| T4 | D8 + 1 tick/side | 0.466 | 0.3205 | 0.128 | n/a | n/a | n/a | n/a |
| T4 | 1.5 x slippage | 0.449 | 0.3269 | 0.123 | n/a | n/a | n/a | n/a |

### Per calendar year (base case)

| Year | T1 n | T1 Sharpe | T2 n | T2 Sharpe | T3 n | T3 Sharpe | T4 n | T4 Sharpe |
|---|---|---|---|---|---|---|---|---|
| 2010 |  |  |  |  | 44 | 2.80 |  |  |
| 2011 | 110 | 1.31 | 110 | 1.29 | 251 | 0.42 | 236 | 0.62 |
| 2012 | 255 | -0.16 | 255 | -0.90 | 247 | 1.14 | 255 | 0.02 |
| 2013 | 252 | 1.06 | 252 | -0.12 | 249 | 1.19 | 252 | 0.91 |
| 2014 | 254 | 1.01 | 254 | 0.99 | 243 | -0.61 | 254 | -0.94 |
| 2015 | 254 | 1.22 | 254 | 0.40 | 250 | -0.71 | 254 | -0.78 |
| 2016 | 255 | -1.38 | 255 | -0.83 | 251 | -1.04 | 255 | -1.04 |
| 2017 | 253 | 0.08 | 253 | 0.42 | 249 | 0.79 | 253 | 1.33 |
| 2018 | 254 | -1.17 | 254 | -0.20 | 248 | -0.40 | 254 | -0.00 |
| 2019 | 252 | 0.51 | 252 | 0.08 | 246 | -0.31 | 252 | 0.14 |
| 2020 | 254 | 1.85 | 254 | 1.56 | 251 | 1.34 | 254 | 1.08 |
| 2021 | 254 | -0.19 | 254 | 1.12 | 251 | 0.09 | 254 | 1.08 |
| 2022 | 258 | 2.24 | 258 | 1.90 | 250 | -0.37 | 258 | 1.09 |
| 2023 | 257 | -0.53 | 257 | -0.77 | 248 | 0.81 | 257 | -1.30 |
| 2024 | 43 | 3.22 | 43 | 1.89 | 41 | -3.11 | 43 | 2.53 |

### Per root, T1 (base case)

| Root (T1) | contribution (sum, base) | own t | fills | gross | costs (base) |
|---|---|---|---|---|---|
| ZT | 0.2736 | 2.69 | 252 | 0.2870 | 0.0134 |
| NQ | 0.2654 | 2.67 | 252 | 0.2678 | 0.0024 |
| ZF | 0.1569 | 1.58 | 256 | 0.1625 | 0.0057 |
| NG | 0.1511 | 1.39 | 456 | 0.1586 | 0.0075 |
| ZN | 0.1037 | 1.06 | 252 | 0.1091 | 0.0054 |
| UB | 0.0627 | 0.62 | 252 | 0.0658 | 0.0031 |
| ZL | 0.0627 | 0.75 | 225 | 0.0681 | 0.0054 |
| ZC | 0.0576 | 0.82 | 153 | 0.0624 | 0.0048 |
| CL | 0.0542 | 0.55 | 452 | 0.0627 | 0.0084 |
| 6E | 0.0446 | 0.46 | 252 | 0.0469 | 0.0024 |
| ZB | 0.0401 | 0.40 | 252 | 0.0447 | 0.0046 |
| TN | 0.0372 | 0.55 | 142 | 0.0392 | 0.0020 |
| LE | 0.0201 | 0.33 | 159 | 0.0247 | 0.0046 |
| GC | -0.0394 | -0.42 | 278 | -0.0338 | 0.0055 |
| HE | -0.0638 | -1.36 | 99 | -0.0623 | 0.0015 |
| ZS | -0.0797 | -0.95 | 237 | -0.0758 | 0.0039 |
| RTY | -0.0936 | -1.55 | 112 | -0.0925 | 0.0011 |

### Per root, T2 (base case)

| Root (T2) | contribution (sum, base) | own t | fills | gross | costs (base) |
|---|---|---|---|---|---|
| NG | 0.1506 | 1.73 | 456 | 0.1565 | 0.0059 |
| NQ | 0.1397 | 1.87 | 252 | 0.1425 | 0.0027 |
| UB | 0.1243 | 1.61 | 252 | 0.1274 | 0.0031 |
| ZB | 0.0900 | 1.18 | 252 | 0.0948 | 0.0048 |
| CL | 0.0735 | 0.87 | 452 | 0.0803 | 0.0068 |
| ZN | 0.0539 | 0.73 | 252 | 0.0600 | 0.0061 |
| 6E | 0.0414 | 0.52 | 252 | 0.0438 | 0.0024 |
| TN | 0.0403 | 0.78 | 142 | 0.0424 | 0.0021 |
| LE | 0.0365 | 0.76 | 159 | 0.0403 | 0.0037 |
| ZF | 0.0364 | 0.49 | 256 | 0.0424 | 0.0060 |
| ZT | 0.0284 | 0.37 | 252 | 0.0432 | 0.0149 |
| ZL | 0.0283 | 0.44 | 225 | 0.0330 | 0.0047 |
| ZC | 0.0251 | 0.48 | 153 | 0.0296 | 0.0045 |
| HE | -0.0294 | -0.83 | 99 | -0.0281 | 0.0013 |
| GC | -0.0315 | -0.41 | 278 | -0.0267 | 0.0048 |
| ZS | -0.0385 | -0.65 | 237 | -0.0351 | 0.0034 |
| RTY | -0.0501 | -1.03 | 112 | -0.0490 | 0.0011 |

### Per root, T3 (base case)

| Root (T3) | contribution (sum, base) | own t | fills | gross | costs (base) |
|---|---|---|---|---|---|
| NQ | 0.4317 | 0.87 | 308 | 0.5047 | 0.0730 |
| RTY | -0.0946 | -0.38 | 146 | -0.0768 | 0.0178 |

### Fills by kind

- T1: {"rebalance": {"fills": 2121, "abs_contracts_per_capital": 0.004784476300964327}, "roll_in": {"fills": 980, "abs_contracts_per_capital": 0.006832929382010042}, "roll_out": {"fills": 980, "abs_contracts_per_capital": 0.006832929382010042}}
- T2: {"rebalance": {"fills": 2121, "abs_contracts_per_capital": 0.008584819324259887}, "roll_in": {"fills": 980, "abs_contracts_per_capital": 0.004644594738277805}, "roll_out": {"fills": 980, "abs_contracts_per_capital": 0.004644594738277805}}
- T3: {"entry": {"fills": 227, "abs_contracts_per_capital": 0.04294261376031261}, "exit": {"fills": 227, "abs_contracts_per_capital": 0.04294261376031261}}
- T4: {}

### Exclusions and counters (all reasons, per test)

- T1: return undefined: previous mark missing 1343; rebalance moved: roll blackout 819; rebalance moved earlier 465; no signal (lookback: missing bar) 171; no signal (no reference (no trade date)) 143; UB: return undefined: previous mark missing 113; ZT: return undefined: previous mark missing 111; CL: return undefined: previous mark missing 110; rebalance moved: early halt 106; ZF: return undefined: previous mark missing 104; NQ: return undefined: previous mark missing 103; ZB: return undefined: previous mark missing 103; ZN: return undefined: previous mark missing 103; GC: return undefined: previous mark missing 99; NG: return undefined: previous mark missing 96; 6E: return undefined: previous mark missing 90; TN: return undefined: previous mark missing 71; no signal (no reference (outside window)) 60; RTY: return undefined: previous mark missing 50; LE: return undefined: previous mark missing 43; ZL: return undefined: previous mark missing 40; ZC: return undefined: previous mark missing 39; ZS: return undefined: previous mark missing 38; HE: return undefined: previous mark missing 30; rebalance moved: missing bar 27; series dates added (value booked on a non-series date) 22; flat month 2019-04 (store boundary or window end) 17; flat month 2024-02 (store boundary or window end) 17; return undefined: missing bar 17; hold excluded: contract change 12; ZC: return undefined: missing bar 7; rebalance moved: fill guard 6; closed at the first eligible date after month end 4; no eligible rebalance date 4; LE: return undefined: missing bar 3; ZS: return undefined: missing bar 3; HE: return undefined: missing bar 2; ZL: return undefined: missing bar 2; hold excluded: missing roll bar (fill guard) 1; rebalance moved: unsourced calendar date 1; forced close (backstop) 0
- T2: return undefined: previous mark missing 1343; rebalance moved: roll blackout 819; rebalance moved earlier 465; no signal (lookback: missing bar) 171; no signal (no reference (no trade date)) 117; UB: return undefined: previous mark missing 113; ZT: return undefined: previous mark missing 111; CL: return undefined: previous mark missing 110; rebalance moved: early halt 106; ZF: return undefined: previous mark missing 104; NQ: return undefined: previous mark missing 103; ZB: return undefined: previous mark missing 103; ZN: return undefined: previous mark missing 103; GC: return undefined: previous mark missing 99; NG: return undefined: previous mark missing 96; 6E: return undefined: previous mark missing 90; no signal (no reference (outside window)) 86; TN: return undefined: previous mark missing 71; RTY: return undefined: previous mark missing 50; LE: return undefined: previous mark missing 43; ZL: return undefined: previous mark missing 40; ZC: return undefined: previous mark missing 39; ZS: return undefined: previous mark missing 38; HE: return undefined: previous mark missing 30; rebalance moved: missing bar 27; series dates added (value booked on a non-series date) 22; flat month 2019-04 (store boundary or window end) 17; flat month 2024-02 (store boundary or window end) 17; return undefined: missing bar 17; hold excluded: contract change 12; ZC: return undefined: missing bar 7; rebalance moved: fill guard 6; closed at the first eligible date after month end 4; no eligible rebalance date 4; LE: return undefined: missing bar 3; ZS: return undefined: missing bar 3; HE: return undefined: missing bar 2; ZL: return undefined: missing bar 2; hold excluded: missing roll bar (fill guard) 1; rebalance moved: unsourced calendar date 1; forced close (backstop) 0
- T3: T3 units traded 227; return undefined: previous mark missing 153; NQ: return undefined: previous mark missing 103; RTY: return undefined: previous mark missing 50; T3 unit excluded: sigma warm-up 6; T3 unit excluded: exit: early halt 4; T3 unit excluded: entry: early halt 3; T3 unit excluded: store boundary 2; T3 unit excluded: window end 2; forced close (backstop) 0
- T4: grid dates 3391; series dates 3331; warmup 60

### Fill diagnostics (T1 notes)

```
{
 "fills": 4081,
 "fills in an event window": 14,
 "fills in an uncalibrated bucket (R-B2)": 74,
 "diag: fills the limit-lock test flags (not moved)": 14,
 "diag: 2010-2019 fill bars with high == low": 454,
 "diag: forced fills inside a guard window": 0
}
```
