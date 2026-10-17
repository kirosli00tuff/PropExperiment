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

| ord | trial | tier | eps | n_trips | theta_hat (mine / verdict) | UCB95 (mine / verdict) | SE_boot (mine / verdict) | p_upper | power | UCB95/r | status (mine / verdict) | agree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K3-cp1-01 6E | B | 12 | 1134 | -0.447784 / -0.447784 | 0.330568 / 0.330568 | 0.467969 / 0.467969 | 0.827917 | 1.0000 | 0.3472 | null / null | yes |
| 2 | K3-cp1-01 6A | B | 11 | 1100 | -1.658455 / -1.658455 | -0.991134 / -0.991134 | 0.402424 / 0.402424 | 1.000000 | 1.0000 | -1.0731 | null / null | yes |
| 3 | K3-cp1-01 6B | B | 8 | 1107 | -0.368355 / -0.368355 | 0.134731 / 0.134731 | 0.306411 / 0.306411 | 0.884912 | 1.0000 | 0.1450 | null / null | yes |
| 4 | K3-cp1-01 6C | B | 9 | 1131 | -1.320378 / -1.320378 | -0.784670 / -0.784670 | 0.323925 / 0.323925 | 1.000000 | 1.0000 | -0.8263 | null / null | yes |
| 5 | K3-cp1-01 6J | B | 10 | 1118 | -1.208496 / -1.208496 | -0.623257 / -0.623257 | 0.346183 / 0.346183 | 0.999800 | 1.0000 | -0.6640 | null / null | yes |
| 8 | K3-cp2-01 6E | B | 12 | 1183 | -3.408717 / -3.408717 | -1.628616 / -1.628616 | 1.065072 / 1.065072 | 0.999300 | 1.0000 | -1.6396 | null / null | yes |
| 9 | K3-cp2-01 6A | B | 11 | 1184 | -1.579609 / -1.579609 | 0.010790 / 0.010790 | 0.943752 / 0.943752 | 0.956504 | 1.0000 | 0.0109 | null / null | yes |
| 10 | K3-cp2-01 6B | B | 8 | 1186 | -1.705608 / -1.705608 | -0.535418 / -0.535418 | 0.702813 / 0.702813 | 0.992001 | 1.0000 | -0.5377 | null / null | yes |
| 11 | K3-cp2-01 6C | B | 9 | 1182 | -1.391397 / -1.391397 | -0.175363 / -0.175363 | 0.727523 / 0.727523 | 0.971103 | 1.0000 | -0.1767 | null / null | yes |
| 12 | K3-cp2-01 6J | B | 10 | 1173 | -1.319953 / -1.319953 | -0.028170 / -0.028170 | 0.778321 / 0.778321 | 0.957104 | 1.0000 | -0.0286 | null / null | yes |
| 15 | K3-cp3-01 6E | B | 12 | 513 | 0.222732 / 0.222732 | 2.294884 / 2.294884 | 1.276108 / 1.276108 | 0.429157 | 1.0000 | 5.3279 | null / null | yes |
| 16 | K3-cp3-01 6A | B | 11 | 544 | -1.023646 / -1.023646 | 1.032422 / 1.032422 | 1.219787 / 1.219787 | 0.805019 | 1.0000 | 2.2603 | null / null | yes |
| 17 | K3-cp3-01 6B | B | 8 | 548 | 0.262228 / 0.262228 | 2.064045 / 2.064045 | 1.055653 / 1.055653 | 0.399660 | 1.0000 | 4.4859 | null / null | yes |
| 18 | K3-cp3-01 6C | B | 9 | 538 | -2.306657 / -2.306657 | -0.640050 / -0.640050 | 1.008632 / 1.008632 | 0.989201 | 1.0000 | -1.4169 | null / null | yes |
| 19 | K3-cp3-01 6J | B | 10 | 543 | -0.203873 / -0.203873 | 1.684978 / 1.684978 | 1.160319 / 1.160319 | 0.572843 | 1.0000 | 3.6958 | null / null | yes |
| 20 | K3-cp3-01 6S | B | 13 | 497 | -0.588245 / -0.588245 | 1.518957 / 1.518957 | 1.289762 / 1.289762 | 0.677532 | 1.0000 | 3.6400 | null / null | yes |
| 22 | K3-ldnrev-01 6E | A | 12 | 55 | -0.107086 / -0.107086 | 0.103152 / 0.103152 | 0.128702 / 0.128702 | 0.797420 | 1.0000 | 2.2337 | null / null | yes |
| 23 | K3-ldnrev-01 6J | B | 10 | 53 | -0.131371 / -0.131371 | 0.020273 / 0.020273 | 0.096092 / 0.096092 | 0.906909 | 1.0000 | 0.4556 | null / null | yes |
| 24 | K3-ldnrev-01 6S | B | 13 | 55 | -0.031980 / -0.031980 | 0.212032 / 0.212032 | 0.148256 / 0.148256 | 0.586341 | 1.0000 | 4.5915 | null / null | yes |
| 25 | K3-ldnmom-01 6E | B | 12 | 1063 | -1.590078 / -1.590078 | -0.732822 / -0.732822 | 0.511291 / 0.511291 | 0.998600 | 1.0000 | -0.8211 | null / null | yes |
| 26 | K3-ldnmom-01 6J | B | 10 | 1033 | -2.149160 / -2.149160 | -1.541020 / -1.541020 | 0.373365 / 0.373365 | 1.000000 | 1.0000 | -1.7767 | null / null | yes |
| 27 | K3-mehedge-01 6J | B | 10 | 55 | -0.113439 / -0.113439 | 0.247627 / 0.247627 | 0.220415 / 0.220415 | 0.695530 | 1.0000 | 5.3623 | null / null | yes |
| 28 | K3-ecbfix-01 6E | B | 12 | 2301 | -1.228506 / -1.228506 | 3.348395 / 3.348395 | 2.694806 / 2.694806 | 0.675332 | 0.9975 | 1.7331 | null / null | yes |
| 29 | K3-tkypre-01 6J | B | 10 | 224 | 0.728481 / 0.728481 | 1.347812 / 1.347812 | 0.368364 / 0.368364 | 0.027097 | 1.0000 | 7.1663 | null / null | yes |
| 30 | K3-tkypost-01 6J | B | 10 | 1091 | -1.061324 / -1.061324 | 0.671391 / 0.671391 | 1.028277 / 1.028277 | 0.855014 | 1.0000 | 0.7329 | null / null | yes |

Trials not in the table: cp1-01 6S, cp1-01 6N, cp2-01 6N (listed not run, tier excluded; records
present with status excluded_before_screening, label coverage_below_0.95; not covered); cp2-01 6S
and cp3-01 6N (listed run, Tier B; records excluded_before_screening on the confirmation-window
coverage check, no series; classed inconclusive, blocking).

Coverage pattern of the 6S and 6N records (expected / present / ratio): cp1 6S 38528 / 35485 /
0.9210 and cp1 6N 38528 / 35323 / 0.9168 (listed excluded); cp2 6S 552583 / 516011 / 0.9338 and
cp2 6N 552583 / 510913 / 0.9246 (6N listed excluded, 6S listed run); cp3 6S 473295 / 449710 / 0.9502
(run, passes) and cp3 6N 473295 / 444013 / 0.9381 (listed run, excluded); ldnrev 6S 76148 / 73967 /
0.9714 (run). The ratios are taken from the records; no store was read.

## Notes (none bears on a figure)

- **N0-a.** The marker's not_run is [] and members 30: the runner was given no not-run declaration
  for K3 (R-E22-A9's only declaration is K8-wkndbtc-01) and processed all 30 members; the three
  listed-excluded trials were excluded by its coverage check and the verdict ignores their records,
  as the brief's item 0 allows ("a not-run record, if any, carries exactly the declared label").
- **N4-a (classification of cp2-01 6S and cp3-01 6N).** The verdict classes the two run trials
  without a series as inconclusive and blocking, so K3 gets no statement. This follows the written
  criteria: NULL_CRITERIA_E 6 makes any member that neither passes nor meets both null conditions
  inconclusive (zero trips included), and section 1's only exception is the "inconclusive by design"
  label declared in the hashed list before the run; L-E5-5 covers trials listed not run, which these
  were not. Both were listed run: true with "power sufficient" from the research window. Whether a
  confirmation-window coverage exclusion (the harness's data-quality rule, not a P&L outcome) should
  form a not-covered class of its own is a lead decision that was not taken before the run; this
  report does not take it.
- **N4-b (resolution table).** The per-exposure table names the two blocking trials nowhere: 6N
  reads fewest_trips null, largest null, not_covered [cp1-01 6N, cp2-01 6N], as if 6N had no run
  trial, although cp3-01 6N was run and returned inconclusive; 6S lists cp1-01 6S only. They appear
  in statement.blocking. A reader of the resolution table alone would not see them.
- **N4-c (the word "covered").** statement.covered (27) is the code's "run and not by design" set
  and includes the two inconclusive trials; in NULL_CRITERIA_E 1's sense ("members ... not covered")
  nothing is covered because no statement is made. No statement text is affected.
- **N3.** The PBO blocks use 8 x 148 = 1184 of the 1191 union dates (D.1b's `_blocks`); the last 7
  dates enter no block. Frozen definition, not a discrepancy.
- **N3-b.** E[max SR] differs at 3.7e-10 relative between funnel's `_norm_ppf` (rational
  approximation) and statistics.NormalDist.inv_cdf; within the brief's 1e-9.

## Not checked

- No bar store was read (brief): the series-to-trips link is verified exactly; trips-to-bars, the
  coverage ratios, the start rule and the roll blackouts are taken from the records.
- The event-window membership of the 207 cp2/cp3 fills was inferred by matching their cents to the
  table's event_window_side_ticks, not checked against the release calendar (sha 839f2437...).
- The 11:30 CT flatten on the 14 dates is reported as the harness applied it (close_reason and CT
  close minute in the trip files); the rule itself was not re-derived.
- registry_current_n = 533 is the verdict's own check (program_n_check.equal true); the registry was
  not re-read.
- p_upper's definition is D.1f's frozen one-sided p, accepted as given.
- screening/stage_e_verdict.py was not run (brief).

## Files

- This report: reports/stage_e22_verify_k3.md
- Code and figures: reports/stage_e22_briefs/verify_k3/verify_k3.py, figures.json; extra_checks.py,
  extra_checks.json; event_cost_check.py, event_cost_check.json; table_trials.md.
