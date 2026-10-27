
## Table C. E.31's prior exposure on the discovery dates 2020-12..2024-02

Scope: reports/E.31_RETURN.md and reports/stage_e31_briefs/work/pilot/runs/stats31.md (1,595 lines; generated 2026-10-23 12:46:58 PDT by stats31.py from
reports/stage_e31_briefs/work/pilot/runs/measure31: 816 trade dates 2020-12-01 to 2024-02-29; bootstrap 2000 replicates, seed 31, unit trade date; units ticks of
0.10 USD/short ton). Recorded values only; nothing computed. Full verbatim copies of the line ranges listed below are in
reports/stage_e32_briefs/work/X1_exposure/X1_tableC_appendix.md (982 lines, made by X1_tableC_copy.py, which only copies line ranges).
E.31 also wrote stats31.json (E.31_RETURN.md line 178: "the full tables"); it was not opened.

### C1. Statistics E.31 computed, by section name (stats31.md)

Splitting variables that exist in E.31's output: model (a) K, (b) FIFO back of queue, (c) trade-through; symbol ZM.v.0 (front) and ZM.v.1 (second month);
session DAY and OVERNIGHT; side (buy, sell, pooled); markout horizon 1 s, 10 s, 60 s; five firms (fee per fill); ZS move over the prior L = 1 s and 10 s;
ZL move over L = 1 s and 10 s; joint ZS+ZL move; USDA release window; queue imbalance at entry; trade dates from 2023-11-01 alone (model (a) only).

| Section name (stats31.md heading) | Lines | Data rows (excluding header) | Variables and statistics recorded | Steering-relevant content |
|---|---|---|---|---|
| ## Verdict: FAIL | 5-19 | 4 test rows + 2 info lines | K1 (lower bound -1.2524; mean -1.2339 [-1.2524, -1.2142], 44045 fills), K2 (44045), K3 (111.5681 [109.5533, 113.4611]); information-only full round-trip fee: lower bound -1.5164, mean -1.4979 [-1.5164, -1.4782] | fill and markout level for the primary population |
| ## Primary population, the three models side by side (ZM.v.0, DAY, sides pooled) | 21-80 | 55 | placements, fills, fill rate, touch rate, stale share, KM P(fill by 1, 10, 60 s), half-spread captured, markouts, E_1, E_10, E_60, N_10(Topstep), VPO, medians, share E_h > 0, per model | level of markout by horizon |
| ## Net results for the five firms (ZM.v.0, DAY, sides pooled) | 81-102 | 15 | N_h(firm) and VPO_h, h in {1, 10, 60} s, firms Topstep 0.264, Lucid 0.280, Bulenox 0.286, MFFU 0.306, Tradeify 0.460 ticks per fill, three models | firm split |
| ## All cells: (a) K, (b) FIFO, (c) trade-through; ZM.v.0 and ZM.v.1; DAY and OVERNIGHT (12 headings: lines 105, 165, 225, 285, 345, 405, 465, 525, 585, 645, 705, 765) | 103-824 | 55 per block, 660 in all | pooled, buy and sell columns for every statistic above | session, month-of-contract (front vs second), side split |
| ## Model (a), trade dates from 2023-11-01 alone (spec 3.1; decides nothing) (4 headings: lines 829, 889, 949, 1009) | 825-1070 | 55 per block, 220 in all; 82 trade dates | same statistics, dates on or after 2023-11-01 only | recent-period split (model a only) |
| ## Splits (spec 5; reported for every model, they decide nothing) (12 headings: lines 1075, 1115, 1155, 1195, 1235, 1275, 1315, 1355, 1395, 1435, 1475, 1515) | 1071-1554 | 35 per block, 420 in all | families: ZS L=1 s (against, flat, with, missing); ZL L=1 s; ZS L=10 s; ZL L=10 s; ZS+ZL L=1 s (both against, both with, other, missing); ZS+ZL L=10 s; USDA release (pre (-30, 0), post [0, 5), post [5, 30), other); queue imbalance (7 buckets: (-1,-0.6], (-0.6,-0.2], (-0.2,0.2), [0.2,0.6), [0.6,1), outside (-1,1), missing). Columns: placements (fill rate), fills, mean E_1, E_10, E_60, median E_10, share E_10 > 0, mean N_10(Topstep) with 95% interval and label | ZS and ZL moves at fill, USDA windows, queue imbalance at entry |
| ## Feasible round trips: the loop (spec 6; DAY session) | 1555-1564 | 3 | round trips per DAY date by model: (a) 207.662 [204.612, 210.449], (b) 215.137 [212.001, 218.005], (c) 111.568 [109.553, 113.461]; durations 80.75, 77.94, 150.02 s | trade frequency |
| ## Implied-liquidity check (spec 8) | 1565-1575 | 4 | ZM.v.0 DAY: A/B prints 7,823,934, volume 19,702,332; (i) share of prints 0.0552, of volume 0.0360; (ii) 0.1180, 0.2600; side N share 0.0905; OVERNIGHT, ZM.v.1 rows as recorded | displayed-liquidity facts |
| ## Exclusions (days.parquet, spec 2) | 1576-1582 | 2 | ZM.v.0: 816 dates, 764 included, 52 excluded (after_roll_day 20, cme_holiday_or_early_close 4, roll_day 23, scheduled_late_open 5), records 414,363,576; ZM.v.1: 684 included, 132 excluded | calendar facts |
| ## Consistency checks | 1583-1595 | 9 | all 0 or empty | none |

Search result for what is absent (grep, case-insensitive, in stats31.md for "month", "by session", "hour"): no match. No section of stats31.md splits by calendar month, hour of day, day of week, year, volatility state, or contract expiry other than front versus second month and the exclusions table. (Statement of what the file contains, not a conclusion.)
Row count C1: 10 section rows.

### C2. The model (c), ZM.v.0, DAY splits, as recorded (stats31.md lines 1395-1434; the other eleven blocks are in the appendix)

Columns as recorded: family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 [95% interval] label | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) [interval] label.

