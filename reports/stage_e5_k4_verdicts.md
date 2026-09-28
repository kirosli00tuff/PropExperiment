# Stage E.5 K4 confirmation verdicts

From the verdict module (`python -m screening.stage_e_verdict`, harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87) on the runner's records
(reports/stage_e5_k4_confirmation/, one run 19:15:54-19:22:07 PDT, 12 members, 0 refused) and the hashed list
reports/stage_e5_k4_confirmation_list.json (sha256 22388c6b3cbfb2b32809cba1ffbcd6a72ad6ff2b0bff0890474d80a65037d46c, commit 4161032). JSON: reports/stage_e5_k4_verdicts.json (sha256 b574b4c1edcb394297941fd3ec4dde3ca25efa8622d3bcfc0a43d4df461987b1).
Cluster freeze 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a; K = 9; program N = 150. Units: net ticks per contract per day of the
vehicle (zeros on window dates without a trip). These figures are recomputed independently in reports/stage_e5_k4_audit.md Part 2.

## Per trial (null test at eps_X; NULL_CRITERIA_E 3)

| Ord | Trial | Tier | Days | Closed trips | theta_hat | UCB95 | SE_boot | p (theta <= 0) | eps_X | Null power | UCB95 < eps | Status | UCB95 / trip | Labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K4-cp1-01 MCL | B | 586 | 563 | -6.9332 | -3.9889 | 1.7825 | 0.9999 | 21 | 1.0000 | yes | null | -4.152 | source-overlap |
| 2 | K4-cp1-01 NG | B | 1070 | 1024 | -1.4306 | +0.6634 | 1.2571 | 0.8749 | 8 | 1.0000 | yes | null | +0.693 | source-overlap |
| 3 | K4-cp2-01 MCL | B | 586 | 585 | -2.7009 | +3.0883 | 3.4614 | 0.7799 | 21 | 1.0000 | yes | null | +3.094 | source-overlap |
| 4 | K4-cp2-01 NG | B | 1070 | 1061 | +1.4390 | +5.4655 | 2.3455 | 0.2601 | 8 | 0.9613 | yes | null | +5.512 | source-overlap |
| 5 | K4-cp3-01 MCL | B | 586 | 280 | -1.7862 | +5.3481 | 4.2274 | 0.6593 | 21 | 0.9996 | yes | null | +11.193 | source-overlap |
| 6 | K4-cp3-01 NG | B | 1070 | 455 | -5.4139 | -1.7005 | 2.2949 | 0.9900 | 8 | 0.9672 | yes | null | -3.999 | source-overlap |
| 7 | K4-ngpre-01 NG | A | 1070 | 198 | -0.0823 | +1.7735 | 1.1106 | 0.5375 | 8 | 1.0000 | yes | null | +9.584 | calendar partly unverified |
| 8 | K4-apipre-01 MCL | B | 586 | 93 | -0.4384 | +1.6168 | 1.2389 | 0.6343 | 21 | 1.0000 | yes | null | +10.188 | source-overlap |
| 9 | K4-eiafade-01 MCL | B | 586 | 55 | -2.7267 | -0.7509 | 1.2374 | 0.9833 | 21 | 1.0000 | yes | null | -8.000 | source-overlap |
| 10 | K4-eiamom-01 MCL | B | 586 | 100 | -0.0879 | +0.4682 | 0.3266 | 0.5992 | 21 | 1.0000 | yes | null | +2.744 | source-overlap |
| 11 | K4-ovr-01 MCL | B | 586 | 587 | -5.2969 | -0.1226 | 3.1556 | 0.9533 | 21 | 1.0000 | yes | null | -0.122 | source-overlap |
| 12 | K4-ovr-01 NG | B | 1070 | 1091 | -1.0121 | +1.5175 | 1.5558 | 0.7500 | 8 | 0.9998 | yes | null | +1.488 | source-overlap |

## Tier A edge chain (D5 with V14)

| Step | Figure | Criterion | Passes |
|---|---|---|---|
| Holm (K = 9, m = 1) | p = 0.5375 | p <= 0.005556 | False |
| Composite (robust zero-edge gate + drift) | not built | V14 (a): built only if the rest passes | pending |
| DSR at N = 150 | 3.1e-05 | > 0.95; Sharpe variance 0.002042 over all 12 run trials (V14 c; Tier A has one member) | False |
| Daily t | -0.069 | > 3.0 | False |
| CSCV PBO | 0.6429 | < 0.5; over all 12 run trials (L-E5-3), 1154 union dates, 8 blocks of 144, 70 splits | False |

**K4-ngpre-01 NG: no edge** (first failing step: holm). It is not source-overlap; it carries "calendar partly unverified".
Sign check (catalog, reported beside the verdict, not a test): over its 198 trips the mean price move from the T - 90 open to the T + 30
open was -1.27 ticks (the mechanism predicts negative), sd 91.3, t -0.20, 52% of moves negative: no evidence of the storage-day drift.

## Cluster null statement (NULL_CRITERIA_E 1 and 7)

Verdict: **null**. Covered: all 12 trials (Tier A and B). Not covered by design: none. Blocking: none. Null by
inactivity: none (every trial has at least 55 closed trips).

> For intraday strategies on CME energy futures in cluster K4, tested on the pre-registered confirmation windows (trade dates
> S_X to 2024-02-29: MCL 2021-07-12, NG 2019-05-06): the members executed through the engine with market orders at the per-product
> modelled retail cost, at the risk-matched size q_X of the exposure's vehicle, every position flat by the product's XFA flatten
> time: for every member of the cluster, a net edge of at least eps_X on its exposure is rejected at one-sided 95% (the upper
> confidence bound on the member's mean net daily P&L is below eps_X), with achieved null power of at least 80%. Per-exposure
> resolution: the table below; no member is null by inactivity; no member was declared inconclusive by design. Members and
> their definitions: reports/stage_e5_k4_confirmation_list.md and .json (sha256 22388c6b...); criteria: docs/NULL_CRITERIA_E.md.

| Exposure (vehicle) | eps_X ticks/ct/day | eps_X $/day at q_c | q_c | Fewest closed trips | Largest per-trade upper bound (ticks) | Null by inactivity | Not covered |
|---|---|---|---|---|---|---|---|
| MCL | 21 | $84.00 | 4 | K4-eiafade-01 MCL (55) | 11.193 (K4-cp3-01 MCL) | none | none |
| NG | 8 | $80.00 | 1 | K4-ngpre-01 NG (198) | 9.584 (K4-ngpre-01 NG) | none | none |

What the statement does not say (NULL_CRITERIA_E 7): nothing about CME energy futures in general, other sizes, fill types, horizons,
accounts or constructions outside the list; the MES record is separate (docs/NULL_CRITERIA.md). The confirmation windows' 2019-2023
flatten times include the v5 derived Topstep holiday rows (July 3 unsettled: 2019-07-03 and 2023-07-03 held to the regular flatten).
