## 1. Verdict summary

**All four tests FAIL.** This is the base case, under Holm step-down at family alpha 0.025. Every
number was recomputed independently by VerdictVerifier-FableXHigh (VERIFIED WITH NOTES, 152 numbers
matched, 0 BLOCKING).

| Test | Net Sharpe [95% CI] | t | p | Fills | Costs / gross |
|---|---|---|---|---|---|
| T1 TSMOM-12 | 0.50 [-0.06, 1.05] | 1.78 | 0.042 | 4,081 | 7.2% |
| T2 trend blend | 0.44 [-0.11, 0.98] | 1.56 | 0.064 | 4,081 | 9.8% |
| T3 turn of month | 0.15 [-0.40, 0.71] | 0.53 | 0.30 | 454 | 21.2% |
| T4 combined book | 0.12 [-0.37, 0.60] | 0.43 | 0.34 | n/a | n/a |

- **T1 and T2 clear the 0.3 Sharpe bar but not Holm**, whose first step needs p ≤ 0.00625. Each is
  a FAIL with a positive point estimate: underpowered, not refuted. A Sharpe of 0.5 would need about
  25 years of data to pass.
- **Published comparison, same window:** AQR's TSMOM factor 0.39 gross; SG Trend 0.35 net (0.24 over
  2010-2025). T3 matches the post-2008 decay of the turn-of-month effect.
- **T4's statistic is dominated by three spikes** from H5's scaling.
- **New N = 532.** The holdout is sealed (0 unlocks), nothing was bought, and the ledger is unchanged.
- **Personal account:** holding the 17-root trend book at one contract or more per root needs about
  $415K-$691K (T1) or $323K-$538K (T2). Live cattle is the binding root.
- **PropEd:** no public page grants automation for any plan. The trend books cannot be held there:
  roots are not listed, and 46-100% of 21-day windows breach the drawdown (One Plan 24-57%). Phidias
  Premium 50K matches PropEd's $2,500 plans. No purchase is recommended.
