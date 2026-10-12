### Part A: 17 product readers (consolidation: reports/stage_e20_product_summary.md)

17 ProductReader-<ROOT>-OpusHigh ran at once (10:33-10:58 PDT), from one shared brief with one assigned reader per
cross-root source. 157 evidence rows. Only H6's equity figure clears 1.5 x a root's D8 round trip on its own window
(Baltussen et al. equity portfolio about 2.7 bp per trade, 2.64 x the MNQ wall at search-window prices). Feature
availability: 35 of the 67-signal library passed F6 at consolidation, then 34 after the plan review (k2_fomc_mto
dropped, PR-2); 33 dropped with reasons (product summary 1.3 and 1.6). Part A features proposed: 7; accepted: 0 (every
one fails rule (c), two also (b); product summary 1.4). GEX ruling: cleared (E.14's copy; terms byte-identical).

| Root | Evidence rows | Proposals (reader ratio to D8) | Accepted |
|---|---|---|---|
| NQ | 10 | none | - |
| RTY | 15 | fomc_r1 (2.51) | no: (c) |
| ZT | 7 | zt_cpnauc (0.75) | no: (c) |
| ZF | 6 | zf_auc10y (0.76 post-2014; 1.53 full sample) | no: (c) |
| ZN | 13 | none | - |
| TN | 6 | none | - |
| ZB | 8 | k2_auc10_mto_zb (0.79) | no: (c) |
| UB | 6 | none | - |
| 6E | 9 | p6e_mehedge_nq (1.14), p6e_post_ldnfix (0.66) | no: (c); (b) |
| CL | 12 | none | - |
| NG | 10 | none | - |
| GC | 14 | none | - |
| ZC | 10 | none | - |
| ZS | 9 | zs_wasde_post_t4 (2.31 upper bound) | no: (b), (c) |
| ZL | 6 | none | - |
| HE | 8 | none | - |
| LE | 8 | none | - |

### Part B: H6 (reports/stage_e20_H6_result.json/.md; prereg reports/stage_e20_prereg_H6.md; freeze 22e606f0...)

Registered 15:36:20 as r004-E20H6 (N 480 -> 483); evaluated once 15:36:34-15:38:15 (marker 15:36:38); verified by
VerdictVerifier-FableXHigh (VERIFIED WITH NOTES; every trade matched to the cent except two MLL liquidations).
c = 4.08 MNQ ticks ($2.04) on every trade; 1.5c = 6.12 ticks; verdict window 971 equity trade dates.

| Test | Verdict | Trades | Mean gross ticks (bp) | Mean net ticks (bp) | t_B | p (one-sided) | Holm (m = 3, 0.025) | Net Sharpe |
|---|---|---|---|---|---|---|---|---|
| E20-H6-T1 (E20H6-T1) | FAIL | 893 | 1.25 (0.38) | -2.83 (-0.39) | -0.528 | 0.701 | not rejected | -0.27 |
| E20-H6-T2 (E20H6-T2) | FAIL | 446 | -3.27 (-0.35) | -7.35 (-1.11) | -0.948 | 0.828 | not rejected | -0.48 |
| E20-H6-T3 (E20H6-T3) | FAIL | 134 | -3.52 (-0.52) | -7.60 (-1.33) | -0.380 | 0.648 | not rejected | -0.19 |

Every test fails all four bars except the trade floor. Descriptive only:
- Per year (T1 trades, mean gross ticks, t, Sharpe): 2020-06..12 139, 0.27, -0.29, -0.37; 2021 239, 1.20, -0.33,
  -0.33; 2022 238, 17.39, 0.97, 0.96; 2023 236, -9.03, -1.61, -1.59; 2024-01..02 41, -29.63, -1.46, -3.53. T2: 2022 the
  only positive year (30.4 ticks, t 1.39); 2021 -21.9 (t -2.25).
- 1.5 x slippage: c 4.92 ticks; T1 Sharpe -0.35, T2 -0.54, T3 -0.22.
- Overlap with the paper's sample, 2019-05-06..2020-05-29 (never in the verdict): T1 254 trades, mean net 13.4 ticks,
  t 1.16, Sharpe 1.11; T2 104, 17.8, t 0.67, Sharpe 0.64; T3 39, 71.9, t 1.19, Sharpe 1.13.
- Eligibility (verdict window): 956 eligible of 971; 15 instrument_change; shortened days carry no trade (engine F = C-30).
  T2 warm-up: 59 of the 60 warm-up dates eligible (one instrument change), so T2's first threshold came one date late.
- MLL: one liquidation each in T1 (2023-11-30) and T2 (2021-10-07); the result's breach_dates field is empty because
  report.py reads DayClose events only (H6V-2; the dates are mll_liquidation_fill_dates).
- Exit types: T1 892 C-2 exits + 1 MLL flatten; T2 445 + 1; T3 134 + 0. No D9.7 exit, no D9.5a deferral, no locked fill.
- T3 power: 148 GEX < 0 rows in the window (count made before the freeze, after T3's status was fixed).

Reading: the rest-of-day to last-half-hour effect, strong in the paper's 1996-2020 NQ sample and positive in the
2019-05..2020-05 overlap here, is absent in 2020-06..2024-02 at MNQ cost: the unconditional gross is 1.25 ticks against
a 4.08-tick round trip; the magnitude-threshold and negative-gamma subsets are negative gross. This matches the
post-2020 decay evidence the readers found (the unreviewed SPX retest, Adams et al.'s draft).
