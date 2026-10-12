### Part C: the search (reports/stage_e20_search.json/.md; plan reports/stage_e20_plan.md, FROZEN; freeze 94ee86b0...)

Plan reviewed by PlanReviewer-FableXHigh (BLOCK on PR-1, then APPROVE WITH FIXES on recheck), code reviewed by
SearchReviewer-FableXHigh (APPROVE WITH FIXES, no leak found). Step 6 dry check passed before the freeze: all 36 features
compute and are applicable on their event rows under the 2010-2019 swaps; removing any leg stops the build; the declared
row losses reproduced (reports/stage_e20_dry_check_step6.md). check --world on the real stores passed after one correction
(the grid assertion on real bars, removed per V2.2b; rulings section 7). Registered 17:43:59 as r005-E20S (N 483 -> 528),
before any panel or fit; run 17:44:15-17:52:20 (8:05 wall, 1.88 GB peak).

- Panel: 57,775 decision rows (13,587 at t4) on 17 vehicles over 1,248 training-calendar dates; usable rows h60 57,377,
  h120 43,988, hF 56,783; 36 features (34 frozen + rod_ret, rod_absratio), 94 feature columns with flags and identifiers.
  Closure bars counted and kept: 30 in all (NQ 7, RTY 6, LE 3, ZS 3, ZL 3, ZC 2, HE 2, ZT 1, ZF 1, 6E 1).
- Admissibility (tau 0.167, one pass): 51 of 51 (vehicle, horizon) pairs admissible.
- Nested CPCV: 15 outer splits, 4 inner folds, 45 configurations; selected per split: ridge in 14 of 15 (lambda 0.01 in 7,
  0.1 in 6, 1.0 in 1), LightGBM depth 2 in 1; horizons h60 in 8, hF in 6, h120 in 1.

SCREEN (F7): FAIL on all three items.

| Item | Value | Bar | Passes |
|---|---|---|---|
| 1. Median-path daily t (paths -1.33, -0.78, -0.87, -1.40, -1.57) | -1.334 | >= 2.0 | no |
| 2. PBO (CSCV, 16 blocks, 12,870 combinations, not degenerate) | 0.596 | < 0.5 | no |
| 3. Annualized net Sharpe at 50K (path average) | -0.826 | >= 0.5 and <= 4.0 | no |
| final_selection returns a configuration | ridge_l0.1_k2_h60 (E20-S13) | a configuration | yes |

Reported, not gating:
- DSR at N = 528: 0.00001 (observed daily Sharpe -0.052, expected maximum under the null 0.068; 1,248 dates).
- Daily mean of the nested record: -$5.55 at 50K (daily sd $106.6).
- 1.5 x slippage: median-path t -1.479, Sharpe -1.018.
- Every one of the 45 configurations has a negative CPCV OOS daily t (best: E20-S13 ridge_l0.1_k2_h60, -0.33, Sharpe
  -0.15; worst: E20-S30 lgbm_d2_k1.5_hF, -3.24). The final configuration's own CPCV record: daily t -0.327, Sharpe
  -0.147, 8,356 outer trades.
- t4 share of the final configuration's CPCV OOS net P&L: -0.079 (t4 trades +$597 of a -$7,544 total over 15 splits);
  1,398 of 9,822 trades at t4.
- r_ROD share: -1.309. With the rod_* z columns set to 0 at prediction, the final configuration's P&L falls from -$7,544
  to -$17,419: the two r_ROD features reduced losses but did not make the model profitable. The planning brief's
  expectation that a surviving late-session signal would be H6 found again does not arise: nothing survived.
- Per-product OOS round trips (median over the 5 paths; the lead's reading of V2.9 criterion 6): MNQ 779, M2K 532,
  MCL 422, MGC 232; below 30 and flagged: ZF 17, ZT 16, ZC 11, ZN 1, 6E 0; the other eight vehicles (NG, TN, ZB, UB, ZS,
  ZL, HE, LE) never traded.
- Ruin probability: not computed (the screen failed; no real-data engine path exists; plan section 9, review PR-6).

A failed screen ends Part C (F7): no B1 freeze, no dry check against a frozen model, no backward read; E20-B1 is not
registered; Steps 8 and 9 did not run. The 2010-2019 stores were hashed as bytes at start and end and never decoded.

Per-configuration table (the 45 registered configurations; ids E20-S01..S45 = registry E20S-01..45):
