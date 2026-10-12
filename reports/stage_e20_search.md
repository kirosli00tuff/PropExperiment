# Stage E.20 Part C search: result

Written 2026-10-11T17:52:20-07:00 (PDT). World: real. Freeze manifest sha256 94ee86b02d1c...

## SCREEN: FAIL

| Item | Value | Bar | Passes |
|---|---|---|---|
| 1_median_path_t | -1.334 | >= 2.0 | False |
| 2_pbo | 0.596 | < 0.5 | False |
| 3_sharpe_annual | -0.826 | >= 0.5 and <= 4.0 | False |
| final_selection | ridge_l0.1_k2_h60 | a configuration | True |

## Reported, not gating

- DSR at N = 528: 0.000 (status computed)
- Final configuration: ridge_l0.1_k2_h60 (E20S-13)
- t4 share of its CPCV OOS net P&L: -0.079; r_ROD share: -1.309 (P&L fitted -7543.69, rod zeroed -17419.48)
- Ruin probability: not computed: the screen failed; the ruin probability (V2.9 criterion 7) needs engine trade records and no real-data engine path exists in the frozen code (plan 9, review PR-6)
- Per-configuration table: /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e20_search/configs.csv
- Per-product round trips: /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e20_search/round_trips.csv

## Stages

| Stage | Status | Wall s | Peak RSS MB |
|---|---|---|---|
| panel | computed | 52.7 | 1873 |
| filter | computed | 0.1 | 1226 |
| cpcv | computed | 412.9 | 1299 |
| final | computed | 1.7 | 1299 |
| oos | computed | 14.2 | 1833 |
