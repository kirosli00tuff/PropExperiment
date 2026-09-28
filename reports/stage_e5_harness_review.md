# Stage E.5 Task A3: independent review of the harness v5 change set (HarnessReviewer-FableXHigh)

Written 2026-09-27, 13:05 to 13:45 PDT, against reports/stage_e5_briefs/A3_harness_reviewer.md. Reviewed: `git diff
HEAD` on data/config.py, data/pull_step2.py, rules/sessions.py, tests/test_e2a_rules.py, tests/test_e2b_pull_step2.py,
tests/test_e4_k3_members_b.py; the untracked screening/stage_e_verdict.py, tests/test_stage_e_verdict.py,
tests/test_stage_e_sessions_holidays.py. Spec: reports/stage_e5_harness_plan.md sections 3 and 4; builder's report
reports/stage_e5_harness_change.md; rulings reports/stage_e5_harness_rulings.md. Read-only on the repository; scratch
under reports/stage_e5_briefs/review_scratch/ (holidays_recompute.py and its output holidays_out.txt, replay_diff.py,
verdict_figures.py). No commit, no manifest build, no vendor call, no web, no Stage E entry point on real data.

Result: 0 BLOCKING, 2 SHOULD FIX, 10 NOTE. Every figure the builder reported that I recomputed reproduces (section 1
and 5 below). The change set is fit to freeze as v5 once the lead decides the two SHOULD FIX items (neither can change a
K4 or K5 figure on the data the clusters hold).

## Findings

| id | class | file:line | what is wrong | why it matters | suggested fix |
|---|---|---|---|---|---|
| SF-1 | SHOULD FIX | screening/stage_e_verdict.py:483 and :198 | When the cluster has exactly one run trial with a series, `dsr_over` has one member and `statistics.pvariance([x])` returns 0.0 silently; `expected_max_sharpe(N, 0.0)` is 0, so DSR collapses to the undeflated PSR (verified: sharpe 0.12, n 200, N 150 gives DSR 0.954, passing 0.95 with no deflation) | V14 (c) says a one-member variance is undefined; the code makes DSR easiest to pass in exactly that case. Not reachable for K4 or K5 unless 10 of their 11 trials are refused | In `edge_chain`, when `len(dsr_over) < 2` set `table = None` with `dsr_undefined = "variance over fewer than 2 series"` so the DSR step fails as undefined; add a known-answer test for the single-series cluster |
| SF-2 | SHOULD FIX | tests/test_e4_k3_members_b.py:350, :363, :375 (ruling R-A2-1) | `xfail(strict=True)` on the three K3 pin tests masks every other cause of failure: `test_every_source_file_has_the_pinned_sha256` fails on any of the 16 pinned sources, so drift in data/calendars/fx.py or the generator would now pass as an expected failure; `test_both_modules_are_exactly_the_generators_output` is masked entirely. No other test references the K3 freeze (grep c4fb5da4 in tests/ and screening/: none) | The frozen K3 inputs lose their test-time guard until K3's session; the new 14-date test guards FX_FULL_SESSIONS only | Replace the xfail with precise assertions: every pinned sha matches except rules/sessions.py, whose sha is asserted equal to v5's (a7401d7026c663af...); the regenerated FX table differs from the frozen one by exactly V5_FLATTENED_FX_DATES. Same substance as R-A2-1, tighter form |
| N-1 | NOTE | rules/sessions.py:207-208, docstring :26-27; tests/test_stage_e_sessions_holidays.py:308, :322 | The 2019 lead applies to the whole calendar year, not to the derived span: equity F on 2019-01-21 (MLK) and 2019-02-18 (Presidents Day) moves 11:45 to 11:30 (recomputed v4 against v5). Neither test covers 2019-01-01..2019-04-30, and the docstring says trade dates 2019-05-01..2023-12-31 | Immaterial to any Stage E window (earliest S_X 2019-05-06, bars begin 2019-05-06) but an undeclared change | State it in the docstring; extend `test_v5_changes_only_2019_2023_holiday_dates` to 2019-01-01 and pin the two changes, or key the derived lead on `TOPSTEP_DERIVED_FIRST` |
| N-2 | NOTE (lead decision, O-3) | rules/sessions.py:222-226 | On the unsettled 2019-07-03 and 2023-07-03 no row exists and no group calendar lists a halt (FX, rates, crypto, energy, metals all have no entry; verified), so F stays the regular 15:08, later than every Topstep precedent for July 3 (2024 published 11:30, 2026 11:45, the rule's own 11:45) | The "no row" reading is the least restrictive of the three candidates on the two dates; it touches K3's FX dates and K4/K5 only if a trip is open past 11:45 on them | None required; the lead may prefer the rule's 11:45 with the 2024 caveat. Recording the choice in the docstring either way |
| N-3 | NOTE (lead decision, O-5) | screening/stage_e_verdict.py:485-486 | With two or more Tier A series, PBO is over Tier A but aligned on the union of EVERY run trial's dates. If the Tier A trials share a vehicle whose S_X is later than another vehicle's in the cluster (K4: MCL against NG), both Tier A series get leading all-zero blocks, and CSCV's 8 blocks carry fewer informative ones | Changes a PBO figure only in that configuration; the alternative (union over the PBO set) does not | Lead's call before the first list hash; pin whichever in the list |
| N-4 | NOTE | screening/stage_e_verdict.py:511-512; tests/test_stage_e_verdict.py:396 | An undefined PBO (fewer than 2 run series) gives the trial "no edge" with `first_failing_step` "pbo" while `edge_chain.pbo.undefined` says why | A missing statistic reads as a failed one in the verdict string | Word it "no edge (pbo undefined)" or carry `undefined` into the trial verdict; cannot arise for K4/K5 unless 10 of 11 trials are refused |
| N-5 | NOTE | screening/stage_e_verdict.py:308, :667 | `frozen_epsilon` raises KeyError for a vehicle absent from the frozen E.2a table; `main` catches VerdictRefusal, HarnessFreezeError, OSError, ValueError only, so a list with an unknown vehicle ends in a traceback (rc 1) instead of a named refusal (rc 2) | Robustness of the CLI's refusals | Catch KeyError in `_trial` and raise VerdictRefusal |
| N-6 | NOTE | screening/stage_e_verdict.py:396-410 | The series' `unit` string and window bounds (first date >= the vehicle's S_X, last date <= 2024-02-29) are not checked; only S_X map, vehicle, monotone dates, finite values and n_trips are | The runner under the same harness guarantees them; two cheap extra refusals would make the module self-sufficient | Add both checks to `_series` |
| N-7 | NOTE (O-11) | screening/harness_freeze.py:233 | ENTRY_MODULES does not name screening.stage_e_verdict, so the freeze does not verify its import closure | Today harmless: every import is a listed harness file (funnel/multiple_comparisons.py, funnel/null_generator.py, screening/harness_freeze.py, stage_e_stats.py, stage_e_stats_power.py, stage_e_stats_units.py all in the manifest; no strategy import, test-pinned) | Add it at the next harness_freeze.py change (the plan keeps the file unchanged in v5) |
| N-8 | NOTE (for Task C4) | screening/stage_e_verdict.py:96, :372-383 | The label vocabulary is closed (`LIST_LABELS`: source-overlap, calendar partly unverified, inconclusive by design, the four runner D9 labels) and every list ordinal must equal the runner's declaration ordinal, else the verdict refuses | The lead's hashed list must use exactly these strings and the E.1 ordinals | None; informational |
| N-9 | NOTE (lead decision) | screening/stage_e_verdict.py:539-560 | A trial can be "null" (UCB95 < eps_X, power >= 0.80) and "edge candidate, composite pending" at once (an edge below eps_X: Holm rejects, DSR, t, PBO pass); the statement stays "null" and the chain verdict sits beside it | NULL_CRITERIA_E 2 allows a real edge below eps_X; the rendered statement should say what it does with such a trial | Decide the rendering rule before the first verdict; no code change needed |
| N-10 | NOTE (O-10) | data/pull_step2_report.py:39 | The quote markdown still prints "(quotes only)" beside the request cap | Cosmetic, outside the change set's five paths | Fix in a later config/report edit |
| N-11 | NOTE (R-A2-2) | tests/test_e2b_pull_step2.py:649-723 | No test pins the config's caps at 0.00 (by design, so Task B1 leaves the suite green); the frozen 0.00 state is guarded by the manifest hash alone | Consistent with the ruling; recorded so nobody expects a test to catch a cap edit | None |
| N-12 | NOTE | reports/stage_e5_harness_plan.md section 2, 3a (v) | The plan's "38 published rows" is 37 (O-7); the plan's (iv) formula "group halt - 30" is not what `day_rule` does on a date with a row (O-4) | Both already ruled; the tests pin the code's behaviour | None |

## 1. The holiday rule (rules/sessions.py)

Method: reports/stage_e5_briefs/review_scratch/holidays_recompute.py loads the v4 module from `git show
HEAD:rules/sessions.py` as `sessions_v4` beside the working-tree v5 module and recomputes Rule H-1 from
data.cme_calendar.HOLIDAYS itself (not from the test's helper). Output: review_scratch/holidays_out.txt.

- Rule H-1 on 2024-01-01..2026-12-31 with leads 30/30/15: 39 rule dates, 37 published rows, 35 in-domain matches.
  The only differences: 2024-07-03 (rule 11:45, published 11:30), 2024-01-01, 2025-01-09 (rule 08:00) and 2025-07-03
  (rule dates not published), and 2027-01-01 (published, outside the calendar). Exactly the four named exceptions;
  the builder's O-7 count (37, not 38) is right.
- The v5 table from 2024-01-01 equals the v4 table row for row and source for source (37 = 37). Lead table: v4
  {2024: 30, 2025: 30, 2026: 15}; v5 adds 2019..2023 at 30. TOPSTEP_SCHEDULE_YEARS {2024, 2025, 2026}, DERIVED_YEARS
  2019..2023.
- Rule H-1 on 2019-05-01..2023-12-31 at 30 minutes: 51 rule dates; 48 literal rows; rule minus the 3 unsettled dates
  equals the rows exactly (no value mismatch, no row outside the rule, all rows weekdays in span).
- Unsettled list completeness: the rule's July 3s in the span are 2019-07-03, 2020-07-03, 2023-07-03 (2021 and 2022
  fall on weekends), all three listed. Every other equity entry in the span (listed in holidays_out.txt, 51 weekday
  entries) is a holiday whose base name Topstep published in 2024-2026 (Memorial Day, Independence Day and its
  observed day, Labor Day, Thanksgiving Day, Day after Thanksgiving, Christmas Eve, Christmas Day, New Year's Day,
  MLK, Presidents Day, Good Friday and its abbreviated jobs-report form, Juneteenth); no unscheduled closure lies in
  the span (the day of mourning is 2025-01-09). 2022-06-20 "Juneteenth (observed)" is ordinary under the lead's O-2.
- day_rule, every group, every weekday 2024-01-01..2027-12-31: 8,360 results, 0 differences v4 against v5 (closed
  flag, F and reasons). 2019-05-01..2023-12-31: 251 (group, date) changes on 42 dates; per group equity 41, crypto 40,
  rates 39, fx 39, energy 37, metals 37, grains 9, livestock 9; none moves F later; the one changed date outside the
  equity calendar is 2020-07-02 (grains 11:50 to 11:35, livestock 12:00 to 11:45). All equal to the builder's 3.6.
  New: 2019-01-01..2019-04-30 has 2 changes (equity 2019-01-21 and 2019-02-18, 11:45 to 11:30), finding N-1.
- The 15 FX dates of E.4c N-1 (6E): 13 move 15:08 to 11:30 with reasons `Topstep close-by 11:30
  (topstep_derived_e5_equity_calendar)`; 2019-07-03 and 2023-07-03 stay 15:08 (unsettled, FX calendar empty). 26
  further FX dates change (the 2019-2021 halts 11:45 to 11:30 or 12:00 to 11:45, 2022-06-20 15:08 to 11:30, and the
  abbreviated Good Fridays 2021-04-02 and 2023-04-07 10:00 to 07:45).
- Energy (CL) and metals (GC), every calendar entry 2019-05..2023-12: 37 changes each, all equal to the builder's 3.4
  and 3.5 tables (12:00 halts 11:45 to 11:30, 12:45 halts 12:30 to 11:45, 13:30 halts 13:15 to 11:30, 2020-07-03
  11:45 to 11:30 by the 2020 lead). Every derived-row date has an energy and a metals entry (early halt, or a full
  closure on 2019-12-25, 2020-01-01, 2020-04-10, 2020-12-25, 2021-01-01, 2021-04-02, 2021-12-24, 2022-04-15,
  2022-12-26, 2023-01-02, 2023-04-07, 2023-12-25); the only dates without an entry are the two unsettled July 3s,
  unchanged at 15:08. So R-A2-1's claim about K4 and K5 holds: ENERGY_FULL_SESSIONS and METALS_FULL_SESSIONS (every
  trade date with early_halt_ct None, generated from data/calendars/energy.py and metals.py, which v5 does not touch)
  contain no date whose engine F changes under v5.
- Tests: `uv run pytest -q tests/test_stage_e_sessions_holidays.py tests/test_stage_e_verdict.py tests/test_e2a_rules.py
  tests/test_e4_k3_members_b.py`: 261 passed, 3 xfailed (5.1 s). The three xfails are the K3 pins (reasons shown with
  -rx). The K3 new test pins exactly the 14 dates of R-A2-1.

## 2. The verdict functions (screening/stage_e_verdict.py)

Read against docs/NULL_CRITERIA_E.md 1, 3, 6, 7, reports/stage_d1f_confirmation_list.md 3.1-3.4,
strategy/research/_d1f_decisions.py 155-280, _d1b_accounting.py 73-110, funnel/multiple_comparisons.py,
funnel/null_generator.py 176-193, screening/stage_e_stats.py holm_tier_a and docs/DECISIONS.md V14.

- Unit: the runner's series in net ticks per contract per day, zeros on window dates without a trip
  (screening/stage_e_stats_units.py `_aggregate_trips`); the module checks the series vehicle equals the list's.
- Bootstrap: `resampled_means` is D.1f's line for line on `stationary_bootstrap_indices(rng, n, n, 5.0)`, a fresh
  `np.random.default_rng(seed)` per call, seed = list `bootstrap_seed`, refused unless 20260923 + ordinal (:313-315);
  B = 10,000 (`evaluate` default, and the list's `bootstrap.resamples` must be 10000); UCB95 `np.quantile(means,
  0.95)` (linear); SE `np.std` (ddof 0); p_upper = (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1). All as 3.1.
- Null power `0.5 (1 + erf((eps / SE - 1.645) / sqrt 2))`, 0.0 at SE = 0 (:150-154); status "null" when UCB95 < eps_X
  and power >= 0.80; "null by inactivity" when both hold with n_trips < 30; "inconclusive" otherwise, with zero trips
  and SE_boot = 0 as explicit reasons (:421-441). Matches 3.3, 3.4 and NULL_CRITERIA_E 6.
- Holm: `holm_tier_a(p_upper of every Tier A trial, 9)` (:481); a Tier A trial without a series enters at p = 1
  (O-6, accepted). Threshold 0.05 / 9 / (m - i); verified against D.1f `holm` at alpha 0.05 / 9 by the test.
- DSR: `deflated_sharpe_ratio(sharpe, n, program_n, variance, skew, kurtosis)` with `moments` = D.1b `_moments` on
  the trial's own series; variance `statistics.pvariance` over Tier A series when two or more, else over every run
  series (V14 c) (:483-484). See SF-1 for the one-series degenerate case.
- t: `harvey_liu_zhu_verdict(mean, population sd, n)["t_stat"]`, strict > 3.0 (:510).
- PBO: `pbo` is D.1f's (blocks of n_days // 8, CSCV over 70 splits); set = Tier A when two or more, else every run
  series (L-E5-3); alignment `aligned_series` = D.1f ruling (a) on the union of run trials' dates (:485-486, :526-535).
  See N-3 on the union.
- Chain verdict: "edge candidate, composite pending" only when Holm rejects and DSR > 0.95 and t > 3.0 and PBO < 0.5,
  else "no edge" with the first failing step (:500-521); a source-overlap trial that passes reads the holdout-read
  sentence (:105-106); composite is "pending" (V14 a). The string "edge" alone is never produced.
- Null statement (:539-560): "null" when every covered trial (run, not "inconclusive by design") is "null" or "null by
  inactivity" and at least one trial is covered; else "no statement" naming the blocking trials with their reasons
  and, for Tier A, their chain verdict; not-covered lists the by-design and excluded trials (L-E5-5). Resolution table
  per vehicle (:563-586): eps_X ticks and dollars at q_c, q_c, fewest-trip covered trial and its count, largest
  UCB95 / r, inactivity labels, trials not covered. Matches NULL_CRITERIA_E 1 and 7.
- Refusals (:294-330, :372-410, :596-606, :623-636, :679-683): every one the plan names, plus schema, tier/run
  agreement, unknown labels, the frozen E.2a epsilon table, duplicate members and ordinals, series alignment, a
  record file of the cluster not in the list, a list for another harness, an existing output file.
- CLI: preflight first (:678), then the output-exists check, the list, the harness match, the records (only
  `<cluster>_*_confirmation.json`; trip files never read), one JSON written with `open("x")`, carrying the harness
  sha256 and the list's sha256 (:679-687).
- Independent re-derivations (review_scratch/verdict_figures.py, all equal to the module or the test): summary known
  answer UCB 95.05, SE sqrt((100^2 - 1) / 12) = 28.866, p 2/101; null power Phi(0) = 0.5 and Phi(z_80) = 0.80; Holm
  thresholds at K = 9, m = 3: 0.001852, 0.002778, 0.005556 (0.002 <= 0.05/18 true, 0.003 false, so (0.001, 0.003,
  0.004) rejects x only); the alternating null series at seed 20260923, B = 400: UCB 0.04, SE 0.02266, p 0.6035,
  power 1.0, status "null", each recomputed by hand from the means array; a different seed gives a different means
  array; my own CSCV loop equals funnel's PBO on a random 3 x 8 matrix (1.0, 70 splits); DSR by the Bailey and Lopez de
  Prado formula equals funnel's to 1e-10. The frozen eps table read by the fixtures: NG 8 ticks q 1 $80.00; MCL 21 q 4
  $84.00; MGC 71 q 1 $71.00; MHG 27 q 2 $67.50.

## 3. Equality with D.1f

tests/test_stage_e_verdict.py imports strategy/research/_d1f_decisions.py and _d1b_accounting.py and compares outputs
on generated inputs: bootstrap means arrays (`np.array_equal`, three seeds at B = 500 and one at B = 10,000),
`summarize_means` field by field, `null_power` on six (SE, eps) pairs including 0 and 1e-9, `moments` and `blocks` on
four series, `dsr`, `t_stat` and `dsr_table` on five series including a flat one, `pbo` and `aligned_series` on three
unequal windows (through `d1f.Member`), Holm on four p-value sets against `d1f.holm(alpha=0.05/9)`, and the constants
(seed base 20260923 against D.1f's 20260921 by name). Real, not tautological: each side is the other module's own
function. `test_the_module_imports_nothing_from_strategy` parses the module's AST.

## 4. data/config.py and data/pull_step2.py

- config.py: `git diff HEAD` shows 15 added lines, 0 removed, after STEP2_ROOT and before DATABENTO_KEY_ENV: the E.5
  block (STAGE_E5_SESSION_ID "stage-E.5-2026-09-27", E5_SESSION_CAP_USD 0.00, E5_REQUEST_CAP_USD 0.00) and the three
  active names pointing at it. The E.2b block and every other value are byte-identical.
- pull_step2.py: the diff touches the module docstring's gate sentence (:36-41), the import list (:86-88, three names
  swapped), `step2_gate` (:371-378) and `require_buy_caps`' message (:394-395). Nothing else: no chunk plan, seal,
  byte check, quote writer or path line changes. `main` (:780-794): gate_factory, banner, plan, then for --buy the
  harness preflight and `require_buy_caps` BEFORE `key_loader()` and `client_factory(key)`, so caps at 0.00 refuse
  with RC_REFUSED before any key or client.
- Tests: `uv run pytest -q tests/test_e2b_pull_step2.py`: 44 passed (155 s with the lead's suite running). The new
  tests pin the E.5 session id on acct-2 at both cap pairs, refusal before any vendor call at 0.00 (key_loader and
  client_factory would fail the test if called; ledger empty), and quote-only ledger lines under the E.5 id.

## 5. The replay reports

review_scratch/replay_diff.py compares every JSON in reports/stage_e4_k4_screen with reports/stage_e5_replay_k4
(25 files, same names) and reports/stage_e4b_k5_screen with reports/stage_e5_replay_k5 (23 files), recursively, field
by field, ignoring only harness_sha256, created_utc and, in `*_trips.json`, record_sha256: 25/25 and 23/23 match. The
old files carry harness 82ae8536... only, the new b720c5aa... only; the 12 (K4) and 11 (K5) trip record_sha256 values
differ as expected. `uv run --no-sync python -m screening.harness_freeze verify --expected b720c5aa...`: preflight OK.

## 6. Scope, imports, vendor references

- Tracked changes: data/config.py, data/pull_step2.py, rules/sessions.py, tests/ (four files), plus the manifest the
  lead rebuilt. Untracked code: screening/stage_e_verdict.py and two test files. Nothing under live/, ops/, sim/,
  strategy/ or docs/. tests/test_e2a_rules.py and tests/test_e4_k3_members_b.py are outside the manifest (not
  TEST_PATTERNS); the manifest's four changed entries are the four listed files, plus the three added ones.
- The verdict module imports funnel.multiple_comparisons, funnel.null_generator, screening.harness_freeze,
  screening.stage_e_stats, screening.stage_e_stats_power, screening.stage_e_stats_units: every one is a listed harness
  file; strategy/research is imported by the tests only (L-E5-4).
- grep -i for topstepx, databento, api_key, requests, urllib, http over the three new files: no match.

## 7. The lead's rulings

L-E5-1 to L-E5-5, R-A2-2, O-2, O-4, O-6, O-7 (37 rows confirmed): consistent with the code and the frozen texts.
R-A2-1: right in substance (K3 frozen, deferred, the 14 dates pinned), but the xfail form masks other drift (SF-2).
O-3 (July 3 unsettled): a defensible reading of the plan; recorded as N-2 because it is the least restrictive of the
three candidates on the two dates. O-5 (union over every run trial): recorded as N-3 with the concrete K4 case.
O-10 and O-11: N-10 and N-7.

## Not checked

- The full test suite (the lead's run was in progress; not started again).
- The verdict module on real records (none exist; the fixtures are synthetic).
- K3's FX_FULL_SESSIONS drift beyond what the new test pins (14 dates); the K3 cluster is deferred.
- Whether the frozen E.2a group calendars are right on 2019-07-03 and 2023-07-03 (no energy, metals or FX entry):
  frozen inputs, outside this review.
