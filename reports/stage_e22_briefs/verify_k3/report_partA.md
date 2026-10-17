# Stage E.22 Part A step 4: independent recomputation of the K3 confirmation verdict

VerdictVerifier-K3-FableXHigh (Fable 5.1), 2026-10-16, Vancouver time. Brief:
reports/stage_e22_briefs/brief_verdict_verify.md (KX = K3). Own code throughout
(reports/stage_e22_briefs/verify_k3/verify_k3.py, extra_checks.py, event_cost_check.py; numpy, math,
statistics). `funnel.null_generator.stationary_bootstrap_indices` was called only to cross-check my own
index builder on three seeds (equal, and equal to a pure-Python loop); `funnel.multiple_comparisons`
only as a second check after my own DSR, t and PBO formulas (stated per item). Nothing under
screening/ was imported or run. No bar store was read. Figures: verify_k3/figures.json,
extra_checks.json, event_cost_check.json.

Inputs: list reports/stage_e22_k3_confirmation_list.json (sha256 43456def... recomputed, equal to
commit ccd7fa7's message), marker reports/stage_e22_K3_RUN_ONCE.json, 30 member records and 30
trip files under reports/stage_e22_confirm_k3/, the cluster record, log confirm_k3.log, verdict
reports/stage_e22_k3_verdict.json (written 18:48:54 PDT), costs reports/stage_e2a_costs.json,
epsilon reports/stage_e2a_epsilon.json, criteria NULL_CRITERIA_E 1, 3, 4, 5, 6, 7; STAGE_E_DESIGN D5;
V14; partA_rulings R-E22-A10/A11/A12/A13/A15/A16; L-E5-3, L-E5-5.

## Summary table

| item | verdict | evidence |
|---|---|---|
| 0 run inputs = hashed list | VERIFIED WITH NOTES | Every record's harness_sha256 (v13 dd2bcc60...), cluster_freeze_sha256 (c4fb5da4...), member, ordinal, window ("confirmation"; window_dates first/last = the list's confirmation_window [2019-05-06, 2024-02-29] for all 7 vehicles), s_x, legs and price_path ({}) equal the list; 0 field mismatches over 30 records. The marker names this list's path and sha256, harness v13, freeze sha, members 30, not_run [], created 01:36:27Z; the 30 records were created 01:36:31Z to 01:48:19Z, all after the marker. Record set: 30 records = the 30 list trials. Notes: (a) the three trials listed run: false (cp1-01 6S, cp1-01 6N, cp2-01 6N; tier "excluded") have records with status `excluded_before_screening` and label `coverage_below_0.95`, exactly the declared label; the verdict marks them "not run; record present and not used". (b) Two trials listed run: true, Tier B, "power sufficient" (cp2-01 6S ordinal 13; cp3-01 6N ordinal 21) came back `excluded_before_screening` with no series: the harness's confirmation-window coverage check (6S 516011/552583 = 0.9338; 6N 444013/473295 = 0.9381; threshold 0.95). 25 run trials carry a series. |
| 1 per-trial figures (25 run trials) | VERIFIED | My stationary bootstrap (seed 20260923 + ordinal, mean block 5, B = 10,000, np.quantile 0.95, SE = std ddof 0, p_upper = (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1)) reproduces theta_hat, UCB95, SE_boot, p_upper, n_days (1191 for all), n_trips, r, theta_hat / r, UCB95 / r, Phi(eps_X / SE_boot - 1.645) and the status for all 25 trials within 1e-9 relative; 25 "null", 0 "null by inactivity", 0 inconclusive among the series-bearing trials. n_trips agrees across series.n_trips, trade_rate.n_trips, the trips file's n_trips and its trip count for every trial. eps_X equals the operative eps of stage_e2a_epsilon.json (6E 12, 6A 11, 6B 8, 6C 9, 6J 10, 6S 13, 6N 10) and eps_usd = eps x tick value x q_c for all 25. Table below. |
| 2 Holm | VERIFIED | Tier A = {K3-ldnrev-01 6E} (m = 1 = screened Tier A size; no Tier A trial without a record, so R-E22-A13 is not exercised). K = 5: alpha_k = 0.01, p = 0.7974202579742026 (7974 of 10,000 centred resample means at or above theta_hat), threshold 0.01, not rejected. Descriptive K = 9: alpha_k = 0.005556, same p, not rejected. Both tables equal the verdict's row for row. |
| 3 DSR, t, PBO | VERIFIED | One Tier A series, so V14 (c): Sharpe variance over the 25 run series (population variance) = 0.002417324705454372 (verdict 0.002417324705454373). E[max SR] at N = 533 = 0.15102360353 (verdict 0.15102360348; relative difference 3.7e-10, from funnel's rational-approximation ppf against statistics.NormalDist; within 1e-9). Moments of ldnrev 6E's own series: n 1191, mean -0.107086, population sd 4.378730, skew -2.21846, raw kurtosis 74.98688, Sharpe -0.0244559. DSR = 3.0364072367561334e-10 (equal to every printed digit); daily t = -0.84399447711 (equal); PBO over the 25 run series aligned on the union of window dates (1191 dates, identical for all 25), 8 blocks of 148 days (1184 of 1191 days used; the last 7 fall outside the 8 blocks, as D.1b's `_blocks` defines), 70 splits: 38/70 = 0.5428571428571428 (equal), winner mean OOS -854.846 ticks (equal), P(winner OOS > 0) = 20/70 = 0.2857 (equal). Second check with funnel.deflated_sharpe_ratio, harvey_liu_zhu_verdict and probability_of_backtest_overfitting: equal to my figures. |
| 4 chain verdict, wording, statement, resolution | VERIFIED WITH NOTES | Chain for ldnrev 6E: Holm fails (first failing step "holm"), DSR 3e-10 < 0.95, t -0.84 < 3.0, PBO 0.543 >= 0.5; verdict "no edge"; the word "edge" alone appears nowhere; composite "pending" (V14 a). Statement: covered (run, not by design) = 27 trials; blocking = {cp2-01 6S, cp3-01 6N} (inconclusive: no series) -> "no statement"; equal to the verdict. Not covered = the 3 listed-excluded trials with reason "not run: excluded (not Tier A or B)"; null_by_inactivity = []. Resolution table (7 vehicles): my fewest-trip trial and count and my largest UCB95 / r trial and value equal the verdict's for every vehicle (6A cp3 544 trips / 2.2603; 6B cp3 548 / 4.4859; 6C cp3 538 / cp2 -0.1767; 6E ldnrev 55 / cp3 5.3279; 6J ldnrev 53 / tkypre 7.1663; 6N none; 6S ldnrev 55 / 4.5915). Notes N4-a, N4-b, N4-c below. |
| 5 trip rebuild (Tier A ldnrev 6E; also 6J, 6S) | VERIFIED | From the 55 trips: net_cents / 100 / 6.25 / contracts, summed per trade date over the 1191 window dates, equals the record's series exactly (max abs diff 0.0 ticks), and daily_net_usd = series x 6.25 x q_c (1). Every trip's cost = 422 cents commission (Topstep RT $4.22) + per side ceil-to-the-cent of (bucket side slippage ticks x $6.25): 51 trips in the 10:00 CT bucket (1198 cents), 4 in the 11:00 CT bucket (1216 cents) on 2019-10-31, 2020-10-30, 2022-10-31, 2023-10-31, the dates when London had left BST and Chicago was still on CDT (the member fires at 16:05 London, 15:05Z in summer, 16:05Z otherwise). Same exact rebuild for ldnrev 6J (53 trips; 1172 / 1184 cents) and 6S (55 trips; 1626 cents). All cents are integers (no 'p/q' fractions). Across all 25 run trials, all 20,611 trips match the frozen table under that rule, with the event-window side ticks on the side(s) the release calendar places inside an event window (207 fills: cp2-01 6E/6A/6B/6C/6J and one cp3-01 6S fill). MGC-on-GC tick check: not applicable to K3 (price_paths {} in the list and every record; all seven vehicles run on their own bars). |
| 6 contradictions verdict vs list / records | VERIFIED WITH NOTES | No figure contradicts the list or a record. verdict.list_sha256, harness_sha256, k_holm 5, program_n 533 (program_n_check equal, registry 533), constants (seed base, B, mean block, quantile, 1.645, 0.80, 30, 0.95, 3.0, 8 blocks, 0.5) equal the list's bootstrap block and rules; every trial row's seed, eps, tier, labels, run flag equal the list. The notes are the labelling points N4-a and N4-b. |

## Tier A trial K3-ldnrev-01 6E (ordinal 22, seed 20260945, eps_X 12 ticks = $75.00/day at q_c 1)

| figure | mine | verdict |
|---|---|---|
| theta_hat (ticks/ct/day) | -0.10708581024349285 | -0.10708581024349285 |
| UCB95 | 0.10315183879093195 | 0.10315183879093195 |
| SE_boot | 0.12870179119251665 | 0.12870179119251665 |
| p_upper | 0.7974202579742026 | 0.7974202579742026 |
| n_days / n_trips / r | 1191 / 55 / 0.04617968094038623 | same |
| theta_hat / r, UCB95 / r | -2.3188945454545453, 2.233706181818181 | same |
| null power Phi(12 / 0.1287 - 1.645) | 1.0 | 1.0 |
| status | null (UCB95 < 12, power >= 0.80, 55 >= 30 trips) | null |
| Holm K = 5 / K = 9 | p 0.79742 vs 0.01 / 0.005556: not rejected | same |
| DSR (N 533, var 0.0024173 over 25) | 3.0364072367561334e-10 | 3.0364072367561334e-10 |
| daily t | -0.8439944771093136 | -0.8439944771093135 |
| PBO (25 series, 70 splits) | 0.5428571428571428 | 0.5428571428571428 |
| chain verdict | no edge; first failing step holm | no edge; holm |

With theta_hat < 0, p_upper > 0.5 by construction of D.1f's one-sided p; the figure is the frozen
definition's, accepted as given.

## The 14 FX_FULL_SESSIONS dates the harness flattens at 11:30 CT (R-A2-1, kept as frozen)

2022-01-17, 02-21, 05-30, 06-20, 07-04, 09-05, 11-24; 2023-01-16, 02-20, 05-29, 06-19, 07-04, 09-04,
11-23 (tests/test_e4_k3_members_b.py V5_FLATTENED_FX_DATES). 13 lie in the window; 2023-06-19 is a
roll-blackout date (excluded from every K3 window). No ldnrev trip (6E, 6J or 6S) falls on any of
them: ldnrev trades once a month at the month-end London fix, and the 14 are US holidays. For the
other run trials the harness applied its rule: 163 trips fall on those dates; cp3-01 (all six
vehicles), ecbfix-01 6E and one cp2-01 6J trip were closed `forced_flatten` at 11:30 CT (a few at
11:31-11:34, the next filled bar); the rest (cp2-01, ldnmom-01, tkypre/tkypost-01) closed by strategy
before 11:30. Per-member counts in verify_k3/extra_checks.json.

## Per-trial figures, all 25 run trials (mine / verdict; p_upper, power, UCB95/r are mine, equal to the verdict within 1e-9)

