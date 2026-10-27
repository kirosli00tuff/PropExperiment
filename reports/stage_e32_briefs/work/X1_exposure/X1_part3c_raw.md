Primary population (ZM.v.0, DAY session, buy and sell pooled; ticks; 95% day-block intervals):

| Statistic | (a) K | (b) FIFO, back of queue | (c) trade-through (gate) |
|---|---|---|---|
| placements | 85,568 | 85,568 | 85,568 |
| fills (rate) | 60,216 (0.704) | 61,078 (0.714) | 44,045 (0.515) |
| half-spread captured, mean | +0.341 | +0.359 | -0.425 |
| 10 s markout vs mid, mean | -0.629 | -0.611 | -0.545 |
| 10 s edge E_10, mean | -0.287 [-0.303, -0.273] | -0.252 [-0.267, -0.239] | -0.970 [-0.988, -0.950] |
| 10 s edge net of Topstep's fee per fill | -0.551 | -0.516 | **-1.234 [-1.252, -1.214]** |
| 60 s edge E_60, mean | -0.290 | -0.253 | -0.979 |
| loop round trips per DAY date, mean | 207.7 | 215.1 | 111.6 [109.6, 113.5] |

Kill rule (spec v2 section 7), model (c): K1 holds (FAIL): lower bound -1.2524 under both variants; information only,
at 0.528 per fill: -1.5164. K2 clear: 44,045 fills. K3 clear: 111.568 over 764 dates. **Verdict: FAIL.**

Reported beside, deciding nothing (gross 10 s edge, model (c)): overnight front month -0.997 (fill rate 0.132);
second month (ZM.v.1) DAY -1.186; model (a) from 2023-11-01 alone, front DAY -0.281. All five firms' nets are negative
for every model and horizon (Tradeify's 0.460 fee per fill makes it the worst). Conditioning, model (c), front DAY,
10 s edge: fills after a ZS move against the order in the prior 1 s average -1.100, after a ZS move with it -0.652;
fills 0-5 minutes after a USDA release -8.98 (68 fills); no imbalance, ZS, ZL or USDA bucket is positive for any
model. Implied liquidity, front DAY: 5.5% of aggressor prints (3.6% of their volume) found no displayed resting
quantity at their price, 11.8% (26.0% of volume) found less than their size, and 9.1% of prints carry no aggressor side.

