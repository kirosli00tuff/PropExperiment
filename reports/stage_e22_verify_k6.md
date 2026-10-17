# Stage E.22 Part A step 4: independent verification of the K6 confirmation verdict

VerdictVerifier-K6 (Fable 5.1, xhigh; a different model from the Opus authors). Brief:
reports/stage_e22_briefs/brief_verdict_verify.md with KX = K6. Written 2026-10-16 (PDT; see the
footer for the clock reading). Scratch: reports/stage_e22_briefs/verify_k6/ (verify_k6.py, figures.json,
run1.log, trial_table.md).

Method. Every figure below was recomputed in my own code (numpy, math, statistics; statistics.NormalDist
for Phi and its inverse) from the member records and trip lists, never by importing or calling
screening/stage_e_verdict.py. The one program function called in the main path is
funnel.null_generator.stationary_bootstrap_indices, so that the seeded draw sequence (np.random.default_rng(seed),
B = 10,000 draws of n indices, mean block 5) is the frozen one; funnel.multiple_comparisons
(deflated_sharpe_ratio, harvey_liu_zhu_verdict, probability_of_backtest_overfitting) was run only as a second
check after my own formulas, and the tables say which figure is which. No bar store was opened, no web, no commits;
holdout untouched.

## Inputs read (hashes computed by me)

| Input | sha256 (12) | Matches |
|---|---|---|
| reports/stage_e22_k6_confirmation_list.json | ebb3d034ed00 | commit ccd7fa7 message, marker `list.sha256`, verdict `list_sha256` |
| harness (list, marker, every record, verdict) | dd2bcc602514 | v13, all equal |
| cluster_freeze (list, marker, records, verdict); reports/stage_e_k6_member_freeze.json | a6f8b497eee7 | file hash equals the declared freeze |
| reports/stage_e2a_costs.json | f4360bb77272 | every record's frozen_tables.costs |
| reports/stage_e2a_epsilon.json | 4e2c773182a2 | every record's frozen_tables.epsilon |
| reports/stage_e2a_vehicle_sizes.json / reports/stage_e2a_vehicles.json | 280d7e9df195 / 1f1cafee4330 | every record's frozen_tables.sizes / .vehicles |
| reports/stage_e22_price_paths.json | 860f4b11d75a | every record's price_path_declaration (K6 maps no root) |
| reports/stage_e2b_release_calendar.json | 839f2437bedb | every record's release_calendar_sha256 |
| strategy/members/k6/limitcont.py | 9b142644bc4f | the freeze's file entry (as frozen) |
| the list's 35 `inputs` entries (27 power records, 8 docs/tables) | all 35 | each file's current sha256 equals the list's |

Run marker reports/stage_e22_K6_RUN_ONCE.json: 27 members, not_run [], created 2026-10-17T01:50:02Z (18:50:02 PDT); log
reports/stage_e22_briefs/confirm_k6.log: 27 members, 0 refused, rc 0, 18:50:00 to 18:59:17 PDT; verdict 18:59:17 to 18:59:25.

## Item table

| Item | Verdict | Evidence |
|---|---|---|
| 0. Run inputs equal the hashed list | VERIFIED | Marker names list sha ebb3d034..., harness dd2bcc60..., freeze a6f8b497..., members 27, not_run []. The record set (27 `K6_<member>_confirmation.json` + 27 `_trips.json`) is exactly the list's 27 run trials; the cluster record lists the 27 members in list order, refused {}. For all 27 records: harness_sha256, cluster_freeze_sha256, member, ordinal, window "confirmation", s_x, leg roots (in order), price_path {} and primary vehicle equal the list; status "run"; series length = window_dates.n; first/last date inside the list's window; the roll-blackout exclusions are absent from the series dates; each trips file's record_sha256 equals its record file's hash and its n_trips equals len(trips) = series.n_trips = trade_rate.n_trips. Note (not a mismatch): K6-crushgap-01 ZS's record marks ZM and ZL `traded: false`; the list carries roots only ("ZS ZM ZL"); the freeze entry (ordinal 22) has the same flags, and crushgap.py trades ZS alone with ZM, ZL as signal legs; all 516 trips are ZS. No not-run trial exists, so no not-run record or label to check. |
| 1. Per-trial figures (27 trials) | VERIFIED | theta_hat, UCB95, SE_boot, p_upper, achieved null power, r, theta_hat / r, UCB95 / r: relative difference 0.0 on every figure of every trial (bit-identical; same seeded draw sequence, np.quantile linear at 0.95, std ddof 0, p = (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1)). n_days, n_trips, status and reasons identical for all 27; every seed equals 20260923 + ordinal; eps_X equals the list's. Statuses: 25 "null", K6-limitcont-01 HE "null by inactivity" (10 trips < 30; UCB95 0.3869 < 7; power 1.0), K6-limitcont-01 LE "inconclusive" (0 trips, SE_boot 0, power 0). Table below. |
| 2. Holm at K = 5; descriptive K = 9 | VERIFIED | Tier A = {K6-limitcont-01 HE}, m = 1 (no not-run Tier A trial, so no p = 1 entry). alpha_5 = 0.01: p 0.40875912408759124 > 0.01, not rejected (rank 1, threshold 0.01). K = 9: threshold 0.005555555555555556, not rejected. Both equal the verdict's rows. |
| 3. DSR at N = 533, daily t, CSCV PBO | VERIFIED WITH NOTES | One Tier A series, so V14 (c): Sharpe variance over all 27 run series (my population variance 0.0035193020674824027 = verdict, rel 0.0; the 27-member variance_over list equals the verdict's). E[max SR] at N = 533: mine 0.18222401260407103 vs verdict 0.1822240125368865 (rel 3.7e-10: my Phi^-1 is NormalDist.inv_cdf, the program's is Acklam's approximation, |err| < 1.15e-9). DSR (HE moments on its own series, raw kurtosis): mine 5.7666434960e-09 vs verdict 5.7666436071e-09 (rel 1.9e-8, absolute 1.1e-16: the ppf difference propagated through the far tail, z = -5.7; the program function on my moments gives the verdict's value exactly). DSR fails (< 0.95) either way. t = mean / (population sd / sqrt n) = 0.23711834968385337 vs 0.2371183496838534 (rel 1.2e-16). PBO over the 27 run series aligned on the union of window dates (1214 dates, 2019-05-06..2024-02-29, zeros off a trial's own dates): 8 blocks of 1214 // 8 = 151 days, 70 splits, 39 splits with the in-sample winner at or below the OOS median: 0.5571428571428572 = verdict (rel 0.0); winner mean OOS -1086.0722752380952 ticks (verdict -1086.0722752380957, rel 4e-16), P(winner OOS > 0) = 3/70 = 0.04285714285714286 = verdict. Note 1: the floor convention drops the last 1214 mod 8 = 6 union dates (2024-02-22, 23, 26, 27, 28, 29) from PBO; that is D.1b's `_blocks` pinned by D5 ("pinned to the program's functions"). Sensitivity, decides nothing: np.array_split (every day used, widths 152/151) gives PBO 0.5857 (41/70), also >= 0.5. Note 2: the ppf-implementation differences are below 1e-9 relative on E[max SR] and only exceed it on DSR because DSR is 6e-9 itself; no verdict is near a threshold. |
| 4. Tier A chain verdict, wording, null statement, resolution table | VERIFIED | Chain for K6-limitcont-01 HE: Holm fails (first failing step "holm"), DSR 5.8e-9 < 0.95 fails, t 0.237 < 3.0 fails, PBO 0.557 >= 0.5 fails; composite "pending" (V14 a, not built); verdict wording "no edge" = the file's; the string "edge" alone or "edge exists" appears nowhere in the verdict JSON. Statement: covered = all 27 run trials (none labelled inconclusive by design); blocking = K6-limitcont-01 LE, status inconclusive, reasons ["zero trips", "SE_boot = 0", "null power < 0.80"], edge_chain null (Tier B); therefore "no statement" (NULL_CRITERIA_E 1, 6; R-E22-A16 accepted before the read); null_by_inactivity = [K6-limitcont-01 HE]; not_covered = []. Resolution table (7 exposures, HE LE ZC ZL ZM ZS ZW): q_c 1, eps_X (7, 8, 4, 11, 5, 5, 4 ticks; $70, $80, $50, $66, $50, $62.50, $50 a day), fewest-trip covered trial and count, largest UCB95 per trade, inactivity label, not covered: every field of every row equals the verdict's (HE: fewest K6-limitcont-01 HE 10 trips, largest UCB95/trade 42.70968499999997 ticks on the same trial). |
| 5. Series rebuilt from trips and the frozen cost table (K6-limitcont-01 HE) | VERIFIED | All 10 trips: net_cents = gross_cents - 522 (2 x 261 commission, $5.22 RT) - entry slippage - exit slippage, with slippage per side = ceil(round(qty x slip_ticks x 1000 cents, 6)), slip_ticks from the HE bucket at the fill bar's CT open (buy = sell in every HE bucket), or the event-window figure 0.7214883966802668 ticks (722 cents) when the exit reason is price_limit_exit (the engine's force_event) or the fill lies in [release, release + 30 min) for HE (234 HE release instants in the frozen calendar; none hit). Entry 08:45 CT, bucket 08:30, 722 cents on all 10; exits: 7 price_limit_exit at 722 (event), 2 strategy exits at 12:59 CT bucket 12:30 at 615, 1 mll_liquidation at 10:46 CT bucket 10:30 at 676. Daily sum of net / contracts (all 1) / 1000 on the 1104 window dates reproduces the record's series to 1.4e-14 ticks (10 nonzero days, mean 0.04945652173913042 = theta_hat), and daily_net_usd to 1e-9. Beyond the brief: the daily-sum step (trips to series) reproduces all 27 records to 2.8e-14 ticks (for crushgap, combined net over the one traded leg / (q_c x ZS tick value)); the cost model was re-applied to the HE trial only. Frozen-rule checks on the 10 HE trips: every trade date is in LIVESTOCK_FULL_SESSIONS; d-1 is a full session with no early halt; L(d-1) from LIMIT_PERIODS[HE] is 120 ticks ($0.03) on 2019-10-07, 2020-03-12, 2020-04-07, 2021-08-05; 150 ($0.0375) on 2020-05-26, 2023-09-29, 2023-12-14; 190 ($0.0475) on 2022-03-04, 2022-04-25, 2023-05-30; DROPPED_LIMIT_DATES[HE] is empty; hold_minutes equals close - open for all 10; the record's counters (price_limit_exit 7, mll_liquidation 1) equal the trip reasons, plus price_limit_zone_no_entry 1 and engine_not_a_window_date 1 (entries refused by the engine's guards, no trip). The settlement proxies S(c, d-1), S(c, d-2) and the exact +-L event condition need bars and are out of this brief's scope (listed under unchecked). The series' dates are the 1214 livestock trade dates in the window minus the 110 roll-blackout dates = 1104. K6 has no GC/MGC trial, so the MGC tick check does not apply. |
| 6. Verdict JSON vs list and records | VERIFIED | list_sha256, harness, freeze, k_holm 5, program_n 533 (program_n_check equal, registry 533), constants (seed_base 20260923, resamples 10000, mean_block 5.0, ucb_quantile 0.95, null_z 1.645, power 0.8, inactivity 30, dsr 0.95, t 3.0, pbo 8 blocks / 0.5) equal the list and the criteria; per trial: ordinal, vehicle, tier, q_c, labels, run, seed, eps_ticks, d4_power (equals the list's power block verbatim, including LE's "power check undefined"), covered, record_status, n_days (= window_dates.n), n_trips (= series.n_trips) all equal; composite "pending"; statement.covered equals the list's covered trials. Nothing contradicts the list or the records. |

**No DISCREPANCY.** Items 0, 1, 2, 4, 5, 6 VERIFIED; item 3 VERIFIED WITH NOTES (two implementation notes, neither
bears on a verdict).

## Tier A: K6-limitcont-01 HE (ordinal 23, seed 20260946, eps_X 7 ticks = $70/day at q_c 1)

| Figure | Mine | Verdict file | Relative difference |
|---|---|---|---|
| n_days / n_trips | 1104 / 10 | 1104 / 10 | equal |
| theta_hat (ticks/contract/day) | 0.04945652173913041 | 0.04945652173913041 | 0.0 |
| UCB95 | 0.3868630887681157 | 0.3868630887681157 | 0.0 |
| SE_boot | 0.2067856086350752 | 0.2067856086350752 | 0.0 |
| p_upper | 0.40875912408759124 | 0.40875912408759124 | 0.0 |
| null power Phi(7 / SE - 1.645) | 1.0 | 1.0 | 0.0 |
| r = trips/day; theta/r; UCB95/r | 0.009057971014492754; 5.459999999999997; 42.70968499999997 | same | 0.0 |
| status | null by inactivity | null by inactivity | equal |
| Holm K = 5 (alpha 0.01), K = 9 (0.00556) | not rejected; not rejected | same | equal |
| Sharpe variance (27 run series) | 0.0035193020674824027 | 0.0035193020674824027 | 0.0 |
| E[max SR] at N = 533 | 0.18222401260407103 | 0.1822240125368865 | 3.7e-10 (ppf implementation) |
| DSR | 5.7666434960523816e-09 (own); 5.766643607074684e-09 (program fn on my moments) | 5.766643607074684e-09 | 1.9e-8 own (abs 1e-16); 0.0 program fn |
| daily t | 0.23711834968385337 | 0.2371183496838534 | 1.2e-16 |
| PBO (27 series, 8 x 151 days, 70 splits) | 0.5571428571428572 (39/70) | 0.5571428571428572 | 0.0 |
| winner mean OOS; P(winner OOS > 0) | -1086.0722752380952; 0.04285714285714286 | -1086.0722752380957; 0.04285714285714286 | 4e-16; 0.0 |
| chain | holm fails first; no edge; composite pending | same | equal |

Moments of K6-limitcont-01 HE's own 1104-day series used for DSR and t (mine): n 1104, mean 0.04945652173913041, population sd 6.930154907082029, skew -4.993068765802831, raw kurtosis 215.37542946753217, daily Sharpe 0.007136423702245104; DSR z = -5.70648528623413.

## Per-trial figures (all 27 run trials; mine / verdict file)

| Ord | Trial | Tier | n_days | n_trips | theta_hat (mine / verdict) | UCB95 (mine / verdict) | SE_boot (mine / verdict) | p_upper | power | r | theta/r | UCB95/r | status (mine / verdict) | max rel diff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | B | 1130 | 1060 | -1.56302 / -1.56302 | -1.20709 / -1.20709 | 0.218152 / 0.218152 | 1 | 1 | 0.9381 | -1.6662 | -1.2868 | null / null | 0.0e+00 |
| 2 | K6-cp1-01 ZW | B | 1129 | 1075 | -1.17433 / -1.17433 | -0.652883 / -0.652883 | 0.315895 / 0.315895 | 0.9998 | 1 | 0.9522 | -1.2333 | -0.68568 | null / null | 0.0e+00 |
| 3 | K6-cp1-01 ZS | B | 1136 | 1109 | -1.70146 / -1.70146 | -1.17318 / -1.17318 | 0.326125 / 0.326125 | 1 | 1 | 0.9762 | -1.7429 | -1.2017 | null / null | 0.0e+00 |
| 4 | K6-cp1-01 ZM | B | 1106 | 1075 | -1.20969 / -1.20969 | -0.690187 / -0.690187 | 0.311947 / 0.311947 | 0.9999 | 1 | 0.972 | -1.2446 | -0.71009 | null / null | 0.0e+00 |
| 5 | K6-cp1-01 ZL | B | 1129 | 1076 | -2.48779 / -2.48779 | -1.62962 / -1.62962 | 0.517243 / 0.517243 | 1 | 1 | 0.9531 | -2.6103 | -1.7099 | null / null | 0.0e+00 |
| 6 | K6-cp1-01 HE | B | 1104 | 833 | -1.0354 / -1.0354 | -0.472904 / -0.472904 | 0.343314 / 0.343314 | 0.9986 | 1 | 0.7545 | -1.3723 | -0.62675 | null / null | 0.0e+00 |
| 7 | K6-cp1-01 LE | B | 1109 | 915 | -2.09537 / -2.09537 | -1.61021 / -1.61021 | 0.299967 / 0.299967 | 1 | 1 | 0.8251 | -2.5396 | -1.9516 | null / null | 0.0e+00 |
| 8 | K6-cp2-01 ZC | B | 1130 | 1008 | -1.67114 / -1.67114 | -1.06771 / -1.06771 | 0.369545 / 0.369545 | 1 | 1 | 0.892 | -1.8734 | -1.1969 | null / null | 0.0e+00 |
| 9 | K6-cp2-01 ZW | B | 1129 | 1070 | -0.838459 / -0.838459 | 0.362255 / 0.362255 | 0.717589 / 0.717589 | 0.880712 | 0.999957 | 0.9477 | -0.88469 | 0.38223 | null / null | 0.0e+00 |
| 10 | K6-cp2-01 ZS | B | 1136 | 1077 | -1.71636 / -1.71636 | -0.443369 / -0.443369 | 0.778685 / 0.778685 | 0.984502 | 0.999999 | 0.9481 | -1.8104 | -0.46766 | null / null | 0.0e+00 |
| 11 | K6-cp2-01 ZM | B | 1106 | 1033 | -1.32353 / -1.32353 | -0.120416 / -0.120416 | 0.728822 / 0.728822 | 0.966603 | 1 | 0.934 | -1.4171 | -0.12893 | null / null | 0.0e+00 |
| 12 | K6-cp2-01 ZL | B | 1129 | 1081 | -2.08666 / -2.08666 | -0.124944 / -0.124944 | 1.21292 / 1.21292 | 0.953105 | 1 | 0.9575 | -2.1793 | -0.13049 | null / null | 0.0e+00 |
| 13 | K6-cp2-01 HE | B | 1104 | 906 | -1.00582 / -1.00582 | 0.386021 / 0.386021 | 0.859232 / 0.859232 | 0.874713 | 1 | 0.8207 | -1.2256 | 0.47038 | null / null | 0.0e+00 |
| 14 | K6-cp2-01 LE | B | 1109 | 973 | -2.92271 / -2.92271 | -1.83205 / -1.83205 | 0.672736 / 0.672736 | 1 | 1 | 0.8774 | -3.3312 | -2.0881 | null / null | 0.0e+00 |
| 15 | K6-cp3-01 ZC | B | 1130 | 501 | -1.1126 / -1.1126 | -0.240342 / -0.240342 | 0.530972 / 0.530972 | 0.981002 | 1 | 0.4434 | -2.5095 | -0.54209 | null / null | 0.0e+00 |
| 16 | K6-cp3-01 ZW | B | 1129 | 472 | -1.59157 / -1.59157 | -0.0889733 / -0.0889733 | 0.898156 / 0.898156 | 0.964304 | 0.997512 | 0.4181 | -3.807 | -0.21282 | null / null | 0.0e+00 |
| 17 | K6-cp3-01 ZS | B | 1136 | 511 | -1.93502 / -1.93502 | -0.333213 / -0.333213 | 0.965026 / 0.965026 | 0.977002 | 0.999797 | 0.4498 | -4.3017 | -0.74076 | null / null | 0.0e+00 |
| 18 | K6-cp3-01 ZM | B | 1106 | 515 | -1.41505 / -1.41505 | 0.0896404 / 0.0896404 | 0.89327 / 0.89327 | 0.945205 | 0.999961 | 0.4656 | -3.0389 | 0.19251 | null / null | 0.0e+00 |
| 19 | K6-cp3-01 ZL | B | 1129 | 482 | -1.10388 / -1.10388 | 1.32054 / 1.32054 | 1.47589 / 1.47589 | 0.768323 | 1 | 0.4269 | -2.5857 | 3.0931 | null / null | 0.0e+00 |
| 20 | K6-cp3-01 HE | B | 1104 | 480 | -1.62965 / -1.62965 | 0.161198 / 0.161198 | 1.1061 / 1.1061 | 0.926807 | 0.999999 | 0.4348 | -3.7482 | 0.37075 | null / null | 0.0e+00 |
| 21 | K6-cp3-01 LE | B | 1109 | 487 | -1.81526 / -1.81526 | -0.50064 / -0.50064 | 0.796919 / 0.796919 | 0.987501 | 1 | 0.4391 | -4.1337 | -1.1401 | null / null | 0.0e+00 |
| 22 | K6-crushgap-01 ZS | B | 1028 | 516 | -2.57729 / -2.57729 | -0.625697 / -0.625697 | 1.19405 / 1.19405 | 0.982202 | 0.994496 | 0.5019 | -5.1346 | -1.2465 | null / null | 0.0e+00 |
| 23 | K6-limitcont-01 HE | A | 1104 | 10 | 0.0494565 / 0.0494565 | 0.386863 / 0.386863 | 0.206786 / 0.206786 | 0.408759 | 1 | 0.009058 | 5.46 | 42.71 | null by inactivity / null by inactivity | 0.0e+00 |
| 24 | K6-limitcont-01 LE | B | 1109 | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 | 0 | 0 | None | None | inconclusive / inconclusive | 0.0e+00 |
| 25 | K6-wasdepre-01 ZC | B | 1130 | 55 | -0.253402 / -0.253402 | 0.0387134 / 0.0387134 | 0.17764 / 0.17764 | 0.926407 | 1 | 0.04867 | -5.2063 | 0.79538 | null / null | 0.0e+00 |
| 26 | K6-wasdepre-01 ZS | B | 1136 | 57 | -0.44579 / -0.44579 | 0.172379 / 0.172379 | 0.3788 / 0.3788 | 0.878212 | 1 | 0.05018 | -8.8845 | 3.4355 | null / null | 0.0e+00 |
| 27 | K6-wasdepost-01 ZC | B | 1130 | 54 | -0.0691108 / -0.0691108 | 0.148248 / 0.148248 | 0.135097 / 0.135097 | 0.706829 | 1 | 0.04779 | -1.4462 | 3.1022 | null / null | 0.0e+00 |

Max relative difference over all 27 trials and all eight figures: 0.0. No status, reason, seed, eps or count differs.

## Trip rebuild: K6-limitcont-01 HE (cents; HE tick value $10 = 1000 cents; commission 522 RT)

| Trade date | Entry CT | Exit CT | Close reason | Gross | Entry bucket / slip | Exit bucket / slip (kind) | Net rebuilt | Net record | Match |
|---|---|---|---|---|---|---|---|---|---|
| 2019-10-08 | 08:45 | 09:18 | price_limit_exit | -44000 | 08:30 / 722 | 09:00 / 722 (event, limit exit) | -45966 | -45966 | yes |
| 2020-03-13 | 08:45 | 09:49 | price_limit_exit | 84000 | 08:30 / 722 | 09:30 / 722 (event, limit exit) | 82034 | 82034 | yes |
| 2020-04-08 | 08:45 | 11:27 | price_limit_exit | -125000 | 08:30 / 722 | 11:00 / 722 (event, limit exit) | -126966 | -126966 | yes |
| 2020-05-27 | 08:45 | 12:59 | strategy | 6000 | 08:30 / 722 | 12:30 / 615 (bucket) | 4141 | 4141 | yes |
| 2021-08-06 | 08:45 | 09:07 | price_limit_exit | 34000 | 08:30 / 722 | 09:00 / 722 (event, limit exit) | 32034 | 32034 | yes |
| 2022-03-07 | 08:45 | 10:46 | mll_liquidation | -109000 | 08:30 / 722 | 10:30 / 676 (bucket) | -110920 | -110920 | yes |
| 2022-04-26 | 08:45 | 09:34 | price_limit_exit | 77000 | 08:30 / 722 | 09:30 / 722 (event, limit exit) | 75034 | 75034 | yes |
| 2023-05-31 | 08:45 | 08:53 | price_limit_exit | 28000 | 08:30 / 722 | 08:30 / 722 (event, limit exit) | 26034 | 26034 | yes |
| 2023-10-02 | 08:45 | 11:29 | price_limit_exit | 36000 | 08:30 / 722 | 11:00 / 722 (event, limit exit) | 34034 | 34034 | yes |
| 2023-12-15 | 08:45 | 12:59 | strategy | 87000 | 08:30 / 722 | 12:30 / 615 (bucket) | 85141 | 85141 | yes |

Sum of net = 54,600 cents = 54.6 ticks over 1104 days = 0.04945652 ticks/day = theta_hat. The record's series has exactly these
10 nonzero days (values net / 1000) and zeros elsewhere; the record's daily_net_usd equals net / 100 on each date.

## Resolution table (mine; equal to the verdict's in every field)

| Exposure | q_c | eps_X ticks ($/day) | Fewest trips (covered) | Largest UCB95 per trade | Null by inactivity | Not covered |
|---|---|---|---|---|---|---|
| HE | 1 | 7 ($70.00) | K6-limitcont-01 HE, 10 | K6-limitcont-01 HE, 42.7097 ticks | K6-limitcont-01 HE | none |
| LE | 1 | 8 ($80.00) | K6-limitcont-01 LE, 0 | K6-cp3-01 LE, -1.14006 ticks | none | none |
| ZC | 1 | 4 ($50.00) | K6-wasdepost-01 ZC, 54 | K6-wasdepost-01 ZC, 3.10222 ticks | none | none |
| ZL | 1 | 11 ($66.00) | K6-cp3-01 ZL, 482 | K6-cp3-01 ZL, 3.09313 ticks | none | none |
| ZM | 1 | 5 ($50.00) | K6-cp3-01 ZM, 515 | K6-cp3-01 ZM, 0.192509 ticks | none | none |
| ZS | 1 | 5 ($62.50) | K6-wasdepre-01 ZS, 57 | K6-wasdepre-01 ZS, 3.43548 ticks | none | none |
| ZW | 1 | 4 ($50.00) | K6-cp3-01 ZW, 472 | K6-cp2-01 ZW, 0.38223 ticks | none | none |

## What I could not check

- The settlement proxies S(c, d-1), S(c, d-2), S(c, d-3) and the exact +-L(d-1) event condition behind each of the 10
  HE trips, and why the 7 price-limit exits fired when they did: these need the HE bars, and the brief rules out bar
  reads. The trips are consistent with the frozen rules in every bar-free respect listed under item 5.
- The cost model was re-applied trip by trip for K6-limitcont-01 HE only; for the other 26 trials I verified the
  trips-to-series step (daily sums, contracts, tick value), not each trip's net against the bucket table.
- The engine's account handling (limitcont HE: accounts_started 2 after the 2022-03-07 MLL liquidation; crushgap ZS:
  35 MLL liquidations) is the frozen harness's rule and not a verdict figure; I did not audit it.
- The research-window Tier A screen (t 1.002 on a single trip, as the list notes) and the power records are frozen
  inputs whose hashes I confirmed; I did not recompute them.
- No TopstepX API, no credentials, no Databento spend, no commits, no bar store opened. Holdout status was not run by me
  (the lead's invariant); nothing in this task touches data/holdout.

Report written 2026-10-16 19:12:05 PDT (clock read with `date`). Verifier run: reports/stage_e22_briefs/verify_k6/run1.log (59 s wall, nice 10). Figures: reports/stage_e22_briefs/verify_k6/figures.json.
