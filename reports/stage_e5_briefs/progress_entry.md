
## 2026-09-27 — Stage E.5: harness v5 and v6, the K4 and K5 step 2 purchase, K4 confirmed null, K5 stopped before its list

Lead Opus 5.5 xhigh. **Harness v5** (2c0bfe0, ba925a97...) adds the 2019-2023 Topstep holiday rows (48 rows derived from the
equity calendar; July 3 unsettled), the confirmation-verdict module and the E.5 spend block. Fable review: 0 blocking, 2 should-fix,
both fixed. **v6** (ce3cb66, 9a8ebe73...) sets the caps. **Bought** MCL, NG, MGC and MHG step 2 history for $21.196568, exactly the
fresh quote; all 52 holdout-2 chunks sealed on arrival, 0 unlocks. acct-2 has $0.33 left. S_X: MCL 2021-07-12, NG 2019-05-06, MHG
2022-06-01; **MGC none (empty window)**. Five of 252 NGS dates dropped from K4-ngpre-01's table by C9 (41d6adf; freeze 7abcde17...).
K4 list 22388c6b... (4161032), run once. **K4 is null:** all 12 trials have UCB95 < eps_X at power >= 0.96. The Tier A trial
K4-ngpre-01 NG has theta -0.08 ticks/day and p 0.54, so it fails Holm (no edge). Fable recomputed every figure with no discrepancy.
**K5 stopped before its list:** six of its eight tiered trials (Tier A K5-fomc-01 among them) have supply 0, and GC bars as MGC's
price path (U8) are the user's decision. The machine crashed at 13:50 and the user paused 13:58-17:35; nothing was lost. Full
record: reports/E.5_RETURN.md.
{COST}
