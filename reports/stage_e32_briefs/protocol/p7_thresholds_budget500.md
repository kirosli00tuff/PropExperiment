[MathReview C-10 (lead: accepted, resolved): the power table below uses z 2.128 while the binding test bar is higher; superseded by reports/stage_e32_briefs/protocol/p7_final.py and p7_final_budget300.md, which use one bar everywhere.]

[MathReview C-11 (lead: accepted, resolved): the program verdict's DSR uses the population variance of the tested Sharpes; the protocol (P9) freezes the bar as that verdict plus a protocol-added DSR at V = 1/(T_test - 1); see p7_final.py.]

# P7/P8 thresholds (budget 500, N after E.33 = 538 + 500 = 1038)

- Discovery trade dates 2020-12-01..2024-02-29: 816 (weekdays minus grain full closures; before E.33's own exclusions)
- Test trade dates 2017-05-01..2020-11-30: 905

## Deflated Sharpe at N (daily Sharpe, T = discovery trade dates)

| c in V = c/(T-1) | V | E[max SR] daily | SR for DSR>=0.95, normal | annualised x sqrt(252) | SR for DSR>=0.95, skew -0.5 kurt 6 | annualised |
|---|---|---|---|---|---|---|
| 0.5 | 0.000613 | 0.0809 | 0.1388 | 2.20 | 0.1412 | 2.24 |
| 1.0 | 0.001227 | 0.1144 | 0.1724 | 2.74 | 0.1755 | 2.79 |
| 2.0 | 0.002454 | 0.1618 | 0.2201 | 3.49 | 0.2242 | 3.56 |

## Multiple testing over the search's 500 configurations (one-sided)

| Rule | alpha per test (first step) | z | t equivalent (large n) |
|---|---|---|---|
| Bonferroni / Holm step 1 at m = budget | 0.0001 | 3.719 | 3.72 |
| Bonferroni at m = N after E.33 | 4.82e-05 | 3.900 | 3.90 |
| BH q = 0.05, rank 1 (same as Bonferroni) | 0.0001 | 3.719 | 3.72 |
| BH q = 0.05, rank 10 | 0.001 | 3.090 | 3.09 |
| Holm step 1 over the 3 test candidates | 0.0167 | 2.128 | 2.13 |
| Harvey-Liu-Zhu hurdle t > 3.0 | 0.00135 | 3.000 | 3.00 |

## Power of the one-shot test (905 trade dates, alpha 0.0167 one-sided = Holm step 1 over 3, power 0.8)

sigma per trade = 3.15 * sqrt(h) ticks (random walk, stated assumption); trades per day capped by non-overlapping holds in the 290-minute day session.

| hold h (min) | sigma/trade (ticks) | max trades/day | mu net (ticks) | trades needed | trades/day needed | feasible |
|---|---|---|---|---|---|---|
| 5 | 7.04 | 58 | 0.25 | 7,000 | 7.74 | yes |
| 5 | 7.04 | 58 | 0.5 | 1,750 | 1.93 | yes |
| 5 | 7.04 | 58 | 1.0 | 438 | 0.48 | yes |
| 5 | 7.04 | 58 | 1.5 | 194 | 0.21 | yes |
| 5 | 7.04 | 58 | 2.0 | 109 | 0.12 | yes |
| 15 | 12.20 | 19 | 0.25 | 21,001 | 23.21 | no |
| 15 | 12.20 | 19 | 0.5 | 5,250 | 5.80 | yes |
| 15 | 12.20 | 19 | 1.0 | 1,313 | 1.45 | yes |
| 15 | 12.20 | 19 | 1.5 | 583 | 0.64 | yes |
| 15 | 12.20 | 19 | 2.0 | 328 | 0.36 | yes |
| 30 | 17.25 | 9 | 0.25 | 42,003 | 46.41 | no |
| 30 | 17.25 | 9 | 0.5 | 10,501 | 11.60 | no |
| 30 | 17.25 | 9 | 1.0 | 2,625 | 2.90 | yes |
| 30 | 17.25 | 9 | 1.5 | 1,167 | 1.29 | yes |
| 30 | 17.25 | 9 | 2.0 | 656 | 0.73 | yes |
| 60 | 24.40 | 4 | 0.25 | 84,005 | 92.82 | no |
| 60 | 24.40 | 4 | 0.5 | 21,001 | 23.21 | no |
| 60 | 24.40 | 4 | 1.0 | 5,250 | 5.80 | no |
| 60 | 24.40 | 4 | 1.5 | 2,333 | 2.58 | yes |
| 60 | 24.40 | 4 | 2.0 | 1,313 | 1.45 | yes |
| 120 | 34.51 | 2 | 0.25 | 168,011 | 185.65 | no |
| 120 | 34.51 | 2 | 0.5 | 42,003 | 46.41 | no |
| 120 | 34.51 | 2 | 1.0 | 10,501 | 11.60 | no |
| 120 | 34.51 | 2 | 1.5 | 4,667 | 5.16 | no |
| 120 | 34.51 | 2 | 2.0 | 2,625 | 2.90 | no |
| 240 | 48.80 | 1 | 0.25 | 336,022 | 371.30 | no |
| 240 | 48.80 | 1 | 0.5 | 84,005 | 92.82 | no |
| 240 | 48.80 | 1 | 1.0 | 21,001 | 23.21 | no |
| 240 | 48.80 | 1 | 1.5 | 9,334 | 10.31 | no |
| 240 | 48.80 | 1 | 2.0 | 5,250 | 5.80 | no |

## The one-shot test's bar on daily Sharpe (T = 905 test trade dates, N = 1038)

| bar | daily SR at the bar | true daily SR for 80% power | annualised (x sqrt 252) |
|---|---|---|---|
| daily t > 3.0 | 0.0997 | 0.1277 | 2.03 |
| DSR > 0.95, V = 0.25/(T-1) | 0.1092 | 0.1372 | 2.18 |
| DSR > 0.95, V = 0.5/(T-1) | 0.1317 | 0.1597 | 2.54 |
| DSR > 0.95, V = 1.0/(T-1) | 0.1637 | 0.1917 | 3.04 |
| DSR > 0.95, V = 2.0/(T-1) | 0.2089 | 0.2369 | 3.76 |

## Net edge per trade for 80% power at the binding bar (c = 1): true daily SR 0.1917

| hold h (min) | sigma/trade (ticks) | trades/day n | mu net (ticks/trade) | mu x n (ticks/day) |
|---|---|---|---|---|
| 5 | 7.04 | 1 | 1.35 | 1.35 |
| 5 | 7.04 | 2 | 0.95 | 1.91 |
| 5 | 7.04 | 4 | 0.68 | 2.70 |
| 5 | 7.04 | 8 | 0.48 | 3.82 |
| 5 | 7.04 | 12 | 0.39 | 4.68 |
| 15 | 12.20 | 1 | 2.34 | 2.34 |
| 15 | 12.20 | 2 | 1.65 | 3.31 |
| 15 | 12.20 | 4 | 1.17 | 4.68 |
| 15 | 12.20 | 8 | 0.83 | 6.61 |
| 15 | 12.20 | 12 | 0.68 | 8.10 |
| 30 | 17.25 | 1 | 3.31 | 3.31 |
| 30 | 17.25 | 2 | 2.34 | 4.68 |
| 30 | 17.25 | 4 | 1.65 | 6.61 |
| 30 | 17.25 | 8 | 1.17 | 9.35 |
| 60 | 24.40 | 1 | 4.68 | 4.68 |
| 60 | 24.40 | 2 | 3.31 | 6.61 |
| 60 | 24.40 | 4 | 2.34 | 9.35 |
