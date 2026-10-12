## 1. Verdict summary

**H6 (rest-of-day to last-half-hour momentum on NQ at MNQ cost, 2020-06-01..2024-02-29): FAIL on all three tests.**
- T1 (every eligible date): FAIL. 893 trades; mean gross 1.25 ticks (0.38 bp), net -2.83 ticks (-0.39 bp) against a
  4.08-tick round trip; t_B -0.53, one-sided p 0.70; net Sharpe -0.27.
- T2 (|r_ROD| above its 60-date median): FAIL. 446 trades; gross -3.27 ticks (-0.35 bp), net -7.35 (-1.11 bp); t_B
  -0.95, p 0.83; Sharpe -0.48.
- T3 (previous day's GEX negative; ran, the source cleared under its terms): FAIL. 134 trades; gross -3.52 ticks
  (-0.52 bp), net -7.60 (-1.33 bp); t_B -0.38, p 0.65; Sharpe -0.19.
- No Holm rejection (m = 3, 0.025). Fable reproduced every number independently.

**Search screen: FAIL.** Median-path daily t -1.33 (bar 2.0), PBO 0.60 (bar < 0.5), annualized net Sharpe at 50K -0.83
(bar 0.5); DSR at N = 528 about 0. All 45 configurations were negative out of sample (best -0.33). The final
configuration would have been ridge, lambda 0.1, k 2, h60. A failed screen ends Part C: no freeze, no backward read,
E20-B1 not run.

**N: 480 -> 483 (H6) -> 528 (45 configurations).**

**Features:** 33 of the 67-signal library dropped by F6 (legs outside the 17 roots, or calendars absent in 2010-2019,
including k2_fomc_mto after the plan review); 34 kept; 2 added (rod_ret, rod_absratio); 0 Part A features accepted (7
proposed, none with a published post-2015 size above 1.5 x the D8 round trip for the hold it would serve).

**What it means.** The one published intraday effect whose historical size cleared the cost wall, Baltussen et al.'s
rest-of-day momentum, is absent on NQ after the paper's sample at retail cost: gross 1.25 ticks against 4.08, and the
gamma and magnitude subsets are negative. The ML route's net pipeline, run on 17 roots with late-session features,
found nothing either; the r_ROD features reduced its losses but did not make it profitable. Across 528 registered
trials nothing has passed, and E.19 showed the Topstep funnel loses money without an edge. Both lines tested here are
closed (section 7).
