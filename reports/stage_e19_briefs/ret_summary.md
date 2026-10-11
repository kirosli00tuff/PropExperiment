## 1. Verdict summary

**No: at zero edge the Topstep funnel loses money for the user.** Inside the policy band (daily risk at most 0.25
of the drawdown distance), all 1,500 zero-edge configurations are negative: every size, path, pricing, DLL and Back2Funded choice and
sensitivity (a cycle: one subscription through its funded XFA).
Best case, 50K with Standard payout and pricing: **-$250 per cycle**, -$31 per Combine purchase. 100K loses $1,063
per cycle and 150K $2,696. It depends on costs (a gross edge just covering trading costs
and the $14.50/month API fee leaves 50K near break-even) and on sizing (sizing beyond the terms reaches break-even
at best).

**Break-even net Sharpe** (after costs, best sizing): 50K about 0, 100K 0.34 to 0.52, 150K 0.54 to 0.86. Zero gross edge is about
-0.5 net.

**Best setup:** 50K, Consistency path, DLL at purchase, Standard pricing, Back2Funded (keep-D payouts, tested
separately, add more). At a net Sharpe of 0.5 it makes +$906 per cycle (+$477 without Back2Funded).

**Cash targets** (five 50K accounts, Standard path; 50% / 80% probability):

| Target | Edge | Combine purchases | Fees |
|---|---|---|---|
| $5,000 withdrawn | zero | 112 / 164 | $7.9K / $11.5K |
| $5,000 withdrawn | net Sharpe 0.5 | 51 / 76 | $4.1K / $5.9K |
| $10,000 withdrawn | net Sharpe 0.5 | 86 / 121 | $6.9K / $9.5K |

**Risk of losing all fees:** at zero edge, 48% (Standard) to 74% (Consistency) of cycles pay nothing; at 0.5, 36% /
54%.

**Terms:** bots may trade the Combine and XFA via the API from the user's own machine, never a Live Funded account. Prohibited: account stacking, excessive Combine or Reset purchases, cross-account hedging, and full
size into news. No thresholds are published.

Fable reproduced the headline (0 BLOCKING). No purchase; N stays 480.
