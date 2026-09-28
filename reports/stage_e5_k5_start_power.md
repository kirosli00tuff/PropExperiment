# Stage E.5 K5: start rule (C1) and power check (C2)

Harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87. JSON: reports/stage_e5_k5_start_power.json (sha256 3f8febf7fc1b183e16b29778d20cc162248e47534cd7b9905fcd73b7489a54dc).

## Start rule (`python -m screening.stage_e_start_dates --set K5`, reports/stage_e_start_rule_K5.json, sha256 d5965f1718c20c824d45e2da8d72ec03ec16bfb71b9018362b278c239644b70e)

| Root | S_X (0.25) | 0.15 | 0.40 | V_ref | M* (0.15 / 0.25 / 0.40) | Day session CT |
|---|---|---|---|---|---|---|
| MGC | None | 2023-10-02 | None | 299.0 | 2023-10 / None / None | 07:20-12:30 |
| MHG | 2022-06-01 | 2022-05-04 | None | 11.0 | 2022-05 / 2022-06 / None | 07:10-12:00 |

Monthly medians (day-session one-minute volume, bars present) are in the JSON and the start-rule file. No refusal.

## Power check per trial (D4, at eps_X; the research series; the confirmation supply after exclusions)

C2: a research re-run under v6 via python -m screening.stage_e_runner --all --window research into reports/stage_e5_power_k5/, which first matched E.4 field by field apart from power, harness_sha256, created_utc and the trip files record_sha256 (reports/stage_e5_briefs/c2_compare_k5.md); its power field is the frozen stage_e_stats_power.power_check at the supply confirmation_supply_days gives (seed 20260922 + ordinal).

| Ord | Trial | Supply days | eps | n_b chosen (analytic, sim) | n_a | sd/day | Label | Flags |
|---|---|---|---|---|---|---|---|---|
| 1 | K5-cp1-01 MGC | 0 | 71 | 9 (9, 9.0) | 22 | 79.46 | inconclusive by design | sim_censored_below_grid_b |
| 2 | K5-cp1-01 MHG | - | - | - | - | - | not run (excluded_before_screening, coverage_below_0.95) | - |
| 3 | K5-cp2-01 MGC | 0 | 71 | 44 (44, 44.4) | 114 | 200.56 | inconclusive by design | - |
| 4 | K5-cp2-01 MHG | - | - | - | - | - | not run (excluded_before_screening, coverage_below_0.95) | - |
| 5 | K5-cp3-01 MGC | 0 | 71 | 62 (62, 61.9) | 160 | 184.25 | inconclusive by design | zero_variance_draws |
| 6 | K5-cp3-01 MHG | 425 | 27 | 52 (52, 59.3) | 135 | 80.35 | power sufficient | zero_variance_draws |
| 7 | K5-preauc-01 MGC | 0 | 71 | 6 (6, 6.0) | 14 | 62.73 | inconclusive by design | sim_smaller_ignored_a, sim_censored_below_grid_b |
| 8 | K5-pmfix-01 MGC | 0 | 71 | 11 (11, 10.0) | 28 | 78.34 | inconclusive by design | sim_censored_below_grid_b |
| 9 | K5-fomc-01 MGC | 0 | 71 | 1 (1, 2.0) | 2 | 21.90 | inconclusive by design | zero_variance_draws, sim_censored_below_grid_a, sim_censored_below_grid_b |
| 10 | K5-ovr-01 MGC | 0 | 71 | 29 (29, 26.1) | 75 | 185.38 | inconclusive by design | - |
| 11 | K5-ovr-01 MHG | 425 | 27 | 18 (18, 13.3) | 54 | 48.66 | power sufficient | zero_variance_draws, sim_used_larger_a, sim_smaller_ignored_b |
