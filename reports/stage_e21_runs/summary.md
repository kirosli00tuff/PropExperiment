# Stage E.21 evaluation (one run)

Holm at family alpha 0.025 over the four tests; PASS iff Holm rejects and the annualized net Sharpe >= 0.3. N at the verdict: 532 (expected 532).

| Test | n | mean | t | t_NW | p | Sharpe | 95% CI | Holm | PASS |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 3205 | 0.000329 | 1.776 | 1.729 | 0.0419 | 0.498 | [-0.063, 1.053] | False | False |
| T2 | 3205 | 0.000224 | 1.557 | 1.525 | 0.0637 | 0.436 | [-0.109, 0.982] | False | False |
| T3 | 3319 | 0.000102 | 0.530 | 0.523 | 0.3003 | 0.146 | [-0.399, 0.706] | False | False |
| T4 | 3331 | 0.055859 | 0.425 | 0.430 | 0.3353 | 0.117 | [-0.369, 0.600] | False | False |

Reported only (stress, 1.5 x slippage), costs as a share of gross:

- T1: stress Sharpe 0.453, slip150 Sharpe 0.484, base costs/gross 0.072
- T2: stress Sharpe 0.378, slip150 Sharpe 0.419, base costs/gross 0.098
- T3: stress Sharpe 0.127, slip150 Sharpe 0.138, base costs/gross 0.212
- T4: stress Sharpe 0.128, slip150 Sharpe 0.123, base costs/gross n/a
