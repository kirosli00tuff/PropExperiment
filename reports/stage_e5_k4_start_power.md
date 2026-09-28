# Stage E.5 K4: start rule (C1) and power check (C2)

Harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87. JSON: reports/stage_e5_k4_start_power.json (sha256 efa74de2ac86c9cc6b2a0dc08810ba97c0dc66e5e1e9b8db596e088f1f2da566).

## Start rule (`python -m screening.stage_e_start_dates --set K4`, reports/stage_e_start_rule_K4.json, sha256 523f2e25a7f5855901856c3b17a0eaf9fb8ddd1135526b03f80814f26bd34a6b)

| Root | S_X (0.25) | 0.15 | 0.40 | V_ref | M* (0.15 / 0.25 / 0.40) | Day session CT |
|---|---|---|---|---|---|---|
| MCL | 2021-07-12 | 2021-07-12 | 2021-07-12 | 54.0 | 2021-07 / 2021-07 / 2021-07 | 08:00-13:30 |
| NG | 2019-05-06 | 2019-05-06 | 2019-05-06 | 127.0 | 2019-05 / 2019-05 / 2019-05 | 08:00-13:30 |

Monthly medians (day-session one-minute volume, bars present) are in the JSON and the start-rule file. No refusal.

## Power check per trial (D4, at eps_X; the research series; the confirmation supply after exclusions)

C2: a research re-run under v6 via python -m screening.stage_e_runner --all --window research into reports/stage_e5_power_k4/, which first matched E.4 field by field apart from power, harness_sha256, created_utc and the trip files record_sha256 (reports/stage_e5_briefs/c2_compare_k4.md); its power field is the frozen stage_e_stats_power.power_check at the supply confirmation_supply_days gives (seed 20260922 + ordinal).

| Ord | Trial | Supply days | eps | n_b chosen (analytic, sim) | n_a | sd/day | Label | Flags |
|---|---|---|---|---|---|---|---|---|
| 1 | K4-cp1-01 MCL | 586 | 21 | 27 (27, 28.2) | 69 | 37.91 | power sufficient | - |
| 2 | K4-cp1-01 NG | 1070 | 8 | 58 (58, 58.3) | 153 | 22.27 | power sufficient | - |
| 3 | K4-cp2-01 MCL | 586 | 21 | 49 (49, 42.8) | 129 | 75.12 | power sufficient | - |
| 4 | K4-cp2-01 NG | 1070 | 8 | 130 (130, 137.4) | 343 | 41.96 | power sufficient | - |
| 5 | K4-cp3-01 MCL | 586 | 21 | 97 (97, 102.7) | 255 | 78.61 | power sufficient | zero_variance_draws |
| 6 | K4-cp3-01 NG | 1070 | 8 | 209 (209, 195.2) | 550 | 64.32 | power sufficient | zero_variance_draws |
| 7 | K4-ngpre-01 NG | 1070 | 8 | 94 (94, 100.7) | 248 | 29.24 | power sufficient | zero_variance_draws |
| 8 | K4-apipre-01 MCL | 586 | 21 | 15 (15, 10.0) | 39 | 33.72 | power sufficient | zero_variance_draws, sim_smaller_ignored_a, sim_censored_below_grid_b |
| 9 | K4-eiafade-01 MCL | 586 | 21 | 5 (5, 5.0) | 13 | 19.69 | power sufficient | zero_variance_draws, sim_censored_below_grid_a, sim_censored_below_grid_b |
| 10 | K4-eiamom-01 MCL | 586 | 21 | 1 (1, 2.0) | 2 | 7.63 | power sufficient | zero_variance_draws, sim_censored_below_grid_a, sim_censored_below_grid_b |
| 11 | K4-ovr-01 MCL | 586 | 21 | 53 (53, 49.3) | 139 | 60.48 | power sufficient | zero_variance_draws |
| 12 | K4-ovr-01 NG | 1070 | 8 | 91 (91, 91.6) | 239 | 31.96 | power sufficient | - |
