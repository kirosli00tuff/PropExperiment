# Stage E.5 harness v5 plan (Task A1, lead)

Written 2026-09-27 12:35-12:55 PDT by the E.5 lead against the E.5 prompt, before any change. Section 1 is
the inventory the prompt asks for; section 2 the holiday gap; section 3 the change set HarnessBuilder
implements (Task A2) and HarnessReviewer checks (Task A3); section 4 the lead's rulings made here.

## 1. Inventory: NULL_CRITERIA_E section 3 (and the items it points to) against the code

"Exists" means a function computes the item today; "missing" means no Stage E function does. The
program functions D.1f pinned (reports/stage_d1f_confirmation_list.md 3.1-3.4) live in
strategy/research/_d1f_decisions.py and strategy/research/_d1b_accounting.py, which the Stage E
harness manifest (reports/stage_e2b_harness_freeze.json, 1,034 files) does NOT list; they rest on
funnel/null_generator.py and funnel/multiple_comparisons.py, which it does list.

| # | Item (NULL_CRITERIA_E 3, D4, D5, V14) | Status | Where |
|---|---|---|---|
| 1 | Unit: daily net series, ticks per contract per day of the vehicle, zeros on no-trip dates; multi-leg by primary leg | exists | screening/stage_e_stats_units.py:160 `daily_series_from_trips`, :175 `daily_series_from_leg_dollars`; the runner writes it per record (screening/stage_e_runner.py:392 `_series`, record field `series`) |
| 2 | theta_hat (mean) | exists (D.1f), missing (Stage E) | strategy/research/_d1f_decisions.py:170 `summarize_means` (`theta_hat`); no Stage E function reads a confirmation record |
| 3 | UCB95 and SE_boot: stationary block bootstrap, mean block 5, B = 10,000, fresh generator per member seeded 20260923 + list ordinal, np.quantile 0.95 | exists with D.1f's seed only; missing for Stage E | _d1f_decisions.py:155 `resampled_means(daily, n_resamples, seed, mean_block)` (seed is a parameter; D.1f's default 20260921) on funnel/null_generator.py:176 `stationary_bootstrap_indices`; :170 `summarize_means` (UCB95 = np.quantile(means, 0.95), SE_boot = np.std(means) ddof 0); :182 `bootstrap` hard-wires 20260921 |
| 4 | One-sided p for H0 theta <= 0 (Holm input): (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1) | exists (D.1f), missing (Stage E) | _d1f_decisions.py:170 `summarize_means` (`p_upper`) |
| 5 | Achieved null power Phi(eps_X / SE_boot - 1.645) >= 0.80; SE_boot = 0 fails | exists (D.1f, eps a parameter), missing (Stage E eps_X) | _d1f_decisions.py:187 `null_power(se_boot, epsilon)`; eps_X from screening/stage_e_stats_units.py:83 `frozen_epsilon(vehicle)` |
| 6 | Null per member (UCB95 < eps_X and power >= 0.80); zero trips or SE_boot = 0 inconclusive; fewer than 30 closed trips "null by inactivity" (NULL_CRITERIA_E 6) | missing (Stage E) | D.1f's MES constants only: _d1f_decisions.py:89-90, :104 |
| 7 | Holm over the cluster's Tier A one-sided p at 0.05 / K, K = 9 (V14 b) | exists | screening/stage_e_stats.py:317 `holm_tier_a(pvalues, k_clusters)`, :288 `holm_alpha_k` (K in 1..9) |
| 8 | DSR > 0.95 at the cumulative program N (150), moments on the member's own series, Sharpe variance over the cluster's Tier A daily Sharpes, or over all its run confirmation series when Tier A has one member (V14 c) | exists (D.1f), the V14 (c) variance set missing | funnel/multiple_comparisons.py:81 `deflated_sharpe_ratio`; _d1b_accounting.py:73 `_moments`; _d1f_decisions.py:230 `_dsr`, :247 `dsr_table` (variance = statistics.pvariance of the daily Sharpes) |
| 9 | Daily t > 3.0 one-sided: harvey_liu_zhu_verdict(mean, population sd, n) | exists | funnel/multiple_comparisons.py:116 `harvey_liu_zhu_verdict`; _d1f_decisions.py:241 `_t_stat`; screening/stage_e_stats.py:152 (research screen) |
| 10 | CSCV PBO < 0.5 on 8 contiguous blocks of n_days // 8 dates | exists (D.1f), the Stage E series set missing | funnel/multiple_comparisons.py:143 `probability_of_backtest_overfitting`; _d1b_accounting.py:100 `_blocks`; _d1f_decisions.py:261 `pbo`, :217 `aligned_series` (D.1f ruling (a): full window date list, 0 off a member's own dates) |
| 11 | Source-overlap gate (NULL_CRITERIA_E 3): a labelled member supports a null, but an edge on it cannot be claimed or discussed without a registered holdout read | missing | labels only in reports/stage_e2a_source_window_amendment.md (frozen input; K4-ngpre-01 NOT source-overlap; K4 cp1-3, apipre, eiafade, eiamom, ovr and every K5 member keep it) |
| 12 | Inconclusive-by-design exception (NULL_CRITERIA_E 1, 5; D4): a member labelled before the run is named as not covered and does not block the statement | label exists, exception missing | screening/stage_e_stats_power.py:85 `LABEL_INCONCLUSIVE`, :507 `power_check(series, cluster, ordinal, supply_days)`; the statement logic is nowhere |
| 13 | V14 (a): a trial passing Holm, DSR, t > 3.0 and PBO reads "edge candidate, composite pending", never "edge" | missing | nowhere (the D.1f composite is MES-only: screening/runner.py, screening/drift.py) |
| 14 | The cluster null statement and the section 7 per-exposure resolution table (eps_X ticks and $ at q_X, vehicle and q_X, fewest-trade member and count, largest per-trade upper bound, labels, members not covered) | missing | nowhere |
| 15 | D4 power check at the confirmation supply | exists | screening/stage_e_stats_power.py:507 `power_check`; the runner calls it on a research run once S_X and the step 2 store exist: screening/stage_e_runner.py:507 `_research_statistics`, :315 `confirmation_supply_days` |
| 16 | D9-excluded trials (OC-H: coverage below 0.95; the trade-rate floor) are neither Tier A nor B | exists (tiers) | screening/stage_e_stats.py:241 `assign_tiers`; the confirmation runner's `--all` runs every frozen member (screening/stage_e_runner.py:529), `--member` one |

Confirmation runs record `screen: None, power: None` (screening/stage_e_runner.py:482-483): every figure
of items 2-6, 8-14 has to come from a new module reading the records.

## 2. The holiday gap in rules/sessions.py (audit E.4c N-1)

- `TOPSTEP_HOLIDAYS` (rules/sessions.py:87-132) holds 38 rows, 2024-01-15..2027-01-01, transcribed from
  Topstep's articles (source ids `topstep_8284222_2024`, `_2025`, `topstep_13350348_2026`).
  `TOPSTEP_EARLY_CLOSE_LEAD` (:134) holds 2024 and 2025 (30 minutes) and 2026 (15 minutes);
  `TOPSTEP_SCHEDULE_YEARS` (:137) is derived from it and used by nothing but the docstring (:26).
- `day_rule` (:205): F = min(regular F, a group-calendar EARLY_HALT minus 15 minutes, the year's
  Topstep lead before that halt when Topstep's schedule does not list the date, Topstep's close-by);
  a group FULL_CLOSURE or a Topstep "markets closed" row closes the date.
- For 2019-2023 no row and no lead exist. On a US holiday that a group's CME calendar lists as an early
  halt, F is the halt minus 15 minutes (energy and metals: 13:15 CT on a 13:30 halt); on one it does
  not list at all, F is the regular 15:08 CT. The audit named 15 such FX dates (2019-07-03, 2022-01-17,
  02-21, 05-30, 07-04, 09-05, 11-24, 2023-01-16, 02-20, 05-29, 06-19, 07-03, 07-04, 09-04, 11-23). In
  2024-2026 the same holidays flatten every group at Topstep's 11:30 or 11:45 CT close-by.
- Lead probe (12:32, reports/stage_e5_briefs/, read-only): the rule "each weekday the frozen EQUITY
  calendar (data.cme_calendar.HOLIDAYS) lists in year Y: FULL_CLOSURE -> markets closed; EARLY_HALT at h
  -> close-by h minus Y's published lead" reproduces 37 of the 38 published rows exactly. The misses:
  2024-07-03 (published 11:30, rule 11:45: the equity halt was 12:15); and three rule dates Topstep
  did not publish: 2024-01-01 (before the 2024 article's first row; the 2023 article is not held),
  2025-01-09 (the unscheduled national day of mourning, closed by CME after the schedule was
  published) and 2025-07-03 (omitted from Topstep's 2025 schedule). The energy, metals, FX and rates
  calendars reproduce 20 to 30 rows fewer. Topstep's schedule therefore follows the equity calendar,
  except on July 3.

## 3. The change set (Task A2, HarnessBuilder-OpusXHigh; nothing else changes)

### 3a. rules/sessions.py: the 2019-2023 Topstep schedule
- Rule H-1 (the rule that produced the published rows): for each weekday D in 2019-05-01..2023-12-31
  that data.cme_calendar.HOLIDAYS (the equity group) lists: FULL_CLOSURE -> a "markets closed" row;
  EARLY_HALT at h -> a row with close_by = h minus the year's lead.
- The lead for 2019-2023 is 30 minutes: Topstep published no schedule the program holds for those years,
  and the earliest published lead (2024 and 2025) is 30 minutes (lead ruling L-E5-2 below). Add
  2019..2023 to `TOPSTEP_EARLY_CLOSE_LEAD` at 30 minutes, so a group-calendar early halt that the
  equity calendar does not list gets the lead exactly as 2024-2025 dates do. Keep
  `TOPSTEP_SCHEDULE_YEARS` meaning the PUBLISHED years ({2024, 2025, 2026}, written out, no longer
  derived from the lead table) and add `TOPSTEP_DERIVED_YEARS = frozenset(range(2019, 2024))`.
- Unsettled dates are listed, not guessed: every July 3 (the one date the rule does not reproduce in the
  published years). A July 3 in 2019-2023 that the equity calendar lists gets NO row; it is written in a
  literal tuple `TOPSTEP_UNSETTLED_DATES` with the reason, and the engine applies D9.1 plus the year's
  lead to the group calendars on it, exactly as it does on 2025-07-03 today. Any other date whose equity
  entry is not an ordinary holiday (an unscheduled closure such as a national day of mourning, a
  holiday name the published years never carry) is also listed, not written as a row.
- The rows are literal `TopstepHoliday(date(...), time(...) or _CLOSED, _TS_DERIVED)` lines with one
  source id `topstep_derived_e5_equity_calendar` (a constant), in the same dict, after a comment block
  that states Rule H-1, the lead and the unsettled list. Trade dates only 2019-05-01..2023-12-31.
- Validation, as a test: (i) Rule H-1 applied to 2024, 2025 and 2026 with each year's published lead
  reproduces every published row except the four named in section 2, and the test names those four with
  their reasons (so a fifth mismatch fails it); (ii) the 2019-2023 literal rows equal Rule H-1's output
  minus the unsettled dates, and the unsettled tuple equals the rule's July 3 (and other non-ordinary)
  dates; (iii) no row lies outside 2019-05-01..2023-12-31 or in 2024-2026 beyond the 38 published;
  (iv) `day_rule` on one derived early-close date per group gives min(regular F, group halt - 15,
  group halt - 30, the derived close-by) and on the 15 FX dates of the audit gives the derived
  close-by (11:30 or 11:45) or closed, instead of 15:08; (v) nothing in 2024-2026 changes (every
  `day_rule` result for every group and every weekday 2024-01-01..2026-12-31 equals the v4 result:
  compute the v4 results in the test from a frozen copy of the old tables, or compare against
  expected values pinned in the test).
- The docstring's 2019-2023 paragraph is updated to say what is derived and what is unsettled.

### 3b. screening/stage_e_verdict.py: the confirmation verdicts (new module)
- Pure functions on the runner's confirmation member records (JSON, as written by
  screening/stage_e_runner.py) and the hashed confirmation list (JSON, schema below). No bar is read.
  Harness pattern (screening/stage_e_stats_power.py:6-10): the D.1f functions are RESTATED here on
  funnel/null_generator.py and funnel/multiple_comparisons.py, which the manifest lists, so the frozen
  harness carries them; the tests import strategy/research/_d1f_decisions.py and _d1b_accounting.py and
  prove equality function for function (bootstrap means array-equal for a given seed, summarize, null
  power, moments, blocks, DSR, t, PBO). The module imports nothing from strategy/.
- Constants: BOOTSTRAP_SEED_BASE = 20260923 (NULL_CRITERIA_E 3; seed = base + list ordinal),
  BOOTSTRAP_RESAMPLES = 10_000, MEAN_BLOCK_DAYS = 5.0, UCB_QUANTILE = 0.95, NULL_Z = 1.645,
  NULL_POWER_MIN = 0.80, INACTIVITY_MIN = 30, HOLM_K = 9 (V14 b), DSR_MIN = 0.95,
  T_MIN = funnel.multiple_comparisons.HLZ_HURDLE (3.0), PBO_MAX = 0.5, N_PBO_BLOCKS = 8. Labels:
  "source-overlap", "calendar partly unverified", "inconclusive by design" (import LABEL_INCONCLUSIVE),
  "null by inactivity", "edge candidate, composite pending" (V14 a).
- Per run trial (Tier A and Tier B): theta_hat, UCB95, SE_boot, p_upper (item 4), n_days, n_trips,
  trips per window day r, per-trade theta_hat / r and UCB95 / r, achieved null power at eps_X,
  `ucb_below_eps`, `power_ok`, and the null status: "null", "null by inactivity" (both conditions,
  n_trips < 30), or "inconclusive" (either condition failing, zero trips, or SE_boot = 0). A trial
  labelled "inconclusive by design" in the list keeps its figures and status but is "not covered".
- Tier A edge chain (every step computed and reported whatever an earlier step gives): Holm via
  screening.stage_e_stats.holm_tier_a(p_upper of the Tier A trials, HOLM_K); composite "pending"
  (V14 a: not built); DSR at the list's program N with moments on the trial's own series and the Sharpe
  variance (statistics.pvariance of the daily Sharpes) over the Tier A trials when there are two or
  more, else over every run trial of the cluster (V14 c); t = harvey_liu_zhu_verdict(mean, population
  sd, n) on its own series; PBO over the Tier A series when there are two or more, else over every run
  trial of the cluster (lead ruling L-E5-3), each series aligned on the union of the run trials' window
  dates with 0 off its own dates (D.1f ruling (a)), blocks of n_days // 8 dates. Chain verdict:
  "edge candidate, composite pending" when Holm rejects and DSR > 0.95 and t > 3.0 and PBO < 0.5, else
  "no edge" with the first failing step named; a source-overlap trial that passes reads "edge
  candidate, composite pending; source-overlap: no edge claim without a registered holdout read". The
  word "edge" alone never appears as a verdict.
- Cluster: the null statement per NULL_CRITERIA_E 1 and 7: "null" when every run trial that is not
  labelled "inconclusive by design" is "null" or "null by inactivity" and at least one trial is covered;
  otherwise "no statement", naming the inconclusive trials. Trials the list marks "not run" (D9-excluded,
  OC-H) and "inconclusive by design" trials are named as not covered and block nothing. The per-exposure
  resolution table (section 7): per vehicle, eps_X in ticks and dollars at q_c, q_c, the covered trial
  with the fewest closed trips and its count, the largest per-trade upper bound UCB95 / r over its
  covered trials, the inactivity labels and the trials not covered.
- Refusals by name (a `VerdictRefusal`): a record whose harness sha256, cluster freeze sha256, member,
  ordinal, window ("confirmation") or S_X differs from the list; a list trial marked run without a
  record, or a record not in the list; a series whose dates are not strictly increasing or whose values
  are not finite; a list whose K is not 9 or whose seed base is not 20260923.
- Input schema, the hashed list (written by the lead in Task C4; the module reads only these fields):
  `{"schema": "stage_e_confirmation_list/1", "cluster", "harness_sha256", "cluster_freeze_sha256",
  "k_holm": 9, "program_n", "bootstrap": {"seed_base": 20260923, "resamples": 10000, "mean_block": 5.0,
  "ucb_quantile": 0.95}, "start_dates": {root: "YYYY-MM-DD"}, "trials": [{"ordinal", "member",
  "vehicle", "q_c", "eps_ticks", "eps_usd_per_day_at_q", "tier": "A"|"B"|"excluded", "run": bool,
  "labels": [...], "bootstrap_seed", "power": {...} or null}]}`.
- CLI: `python -m screening.stage_e_verdict --harness-sha256 SHA --list LIST.json --records DIR --out
  OUT.json`: `screening.harness_freeze.preflight` first, then the list and the records (member records
  `<cluster>_<member>_confirmation.json` in DIR; the trip files are not read), then one JSON written once
  (an existing file is refused), carrying the harness sha256 and the list's sha256. Rendering to
  markdown is the lead's.
- Known-answer tests for every item: synthetic series with hand-computed mean, UCB, p, power at a given
  eps; the inactivity and zero-trip and SE_boot = 0 branches; Holm at K = 9 with one and with three Tier A
  trials; DSR with the V14 (c) variance switch at one Tier A member (variance over all run trials) and
  at two (variance over Tier A); t; PBO with the switch and with unequal window dates (alignment); the
  source-overlap and composite-pending wording; the null statement with an inconclusive-by-design trial,
  an excluded trial, an inconclusive trial and an all-null cluster; every refusal.

### 3c. data/config.py and data/pull_step2.py: the E.5 spend block and the gate that reads it
- data/config.py, after the E.2b block: `STAGE_E5_SESSION_ID = "stage-E.5-2026-09-27"`,
  `E5_SESSION_CAP_USD = 0.00`, `E5_REQUEST_CAP_USD = 0.00`, with a comment in the file's style (Stage E.5
  step 2 purchase of K4 and K5 on acct-2; the lead sets both caps in Task B1 from the fresh quote; 0.00
  refuses every billable request until then). Then the active step 2 purchase policy, three names the
  gate reads: `STEP2_PURCHASE_SESSION_ID = STAGE_E5_SESSION_ID`, `STEP2_SESSION_CAP_USD =
  E5_SESSION_CAP_USD`, `STEP2_REQUEST_CAP_USD = E5_REQUEST_CAP_USD`, with a comment that a later
  purchase session adds its own block and repoints these three (a config-only edit, as E.2b's design
  intended). The E.2b block and every other value stay byte-identical.
- data/pull_step2.py: `step2_gate` builds `LockedQuoteGate(STEP2_PURCHASE_SESSION_ID,
  session_cap_usd=STEP2_SESSION_CAP_USD, request_cap_usd=STEP2_REQUEST_CAP_USD, account=ACTIVE_ACCOUNT,
  **overrides)`; the import list, the `step2_gate` docstring, `require_buy_caps`' message ("a purchase
  session sets its own caps in data/config.py first") and the module docstring's gate sentence follow.
  Nothing else in the file changes (not the chunk plan, the seals, the byte check, the quote writer or
  the paths).
- Tests: tests/test_e2b_pull_step2.py's assertions that name the E.2b session or caps move to the
  active-policy names; a new test pins that the gate's session id is "stage-E.5-2026-09-27" on acct-2,
  that with the caps at 0.00 `--buy` refuses before any vendor call (RC_REFUSED, no client built), and
  that `--quote-only` ledgers its lines under the E.5 session id (tmp ledger).

### 3d. Tests and the suite
- New or changed tests only under tests/ (names matching the harness TEST_PATTERNS where they are Stage
  E tests, e.g. tests/test_stage_e_verdict.py, tests/test_stage_e_sessions_holidays.py). The full suite
  (`uv run pytest -q`, no PYTHONPYCACHEPREFIX, as E.3 established) passes; the start count is 4043
  passed, 2 skipped, 1 xfailed.
- Files the change set may touch: rules/sessions.py, screening/stage_e_verdict.py (new),
  data/config.py, data/pull_step2.py, tests/. Anything else stops the worker, which reports to the lead.
  The manifest (reports/stage_e2b_harness_freeze.json) is NOT rebuilt by the worker.

## 4. Lead rulings made in Task A1 (also in the return's Open choices)

- **L-E5-1 (the gate wiring).** The prompt's A2 (c) names only data/config.py, but data/pull_step2.py's
  `step2_gate` reads the E.2b names directly (data/pull_step2.py:84-87, :369-374), so an E.5 block in
  config alone would never reach the gate and `--buy` would refuse at the E.2b caps ($0.00). E.2b's own
  design says a later purchase session "sets its own session id and caps" (data/config.py E.2b comment,
  data/pull_step2.py:36-38). The lead rules the gate's reading of the E.5 block part of item (c): the
  two-file wiring above, reviewed by Fable, replayed and frozen in v5 with the rest. Not a change of
  scope: no chunk, seal, cap arithmetic or path changes.
- **L-E5-2 (the 2019-2023 lead).** 30 minutes, the earliest published lead, for the derived rows and
  the lead table. The rule settles which dates flatten early from the frozen equity calendar; the lead
  is the one value Topstep's held articles do not give for those years.
- **L-E5-3 (PBO with one Tier A member).** CSCV PBO is undefined for one strategy. Where a cluster's
  Tier A has one member, PBO is taken over every run confirmation series of the cluster (Tier A and B),
  aligned on the union of their window dates with zeros off each trial's dates: the same set V14 (c)
  uses for DSR's variance, and the whole family of screened configurations the selection chose from.
  Declared in each hashed list before its hash.
- **L-E5-4 (verdict code restated, not imported).** strategy/research/ is outside the harness
  directories and the manifest does not list _d1f_decisions.py; importing it would pin a verdict to
  unfrozen code. The module restates the functions on the manifest's funnel/ files, and the tests prove
  them equal (the stage_e_stats_power.py pattern). screening/harness_freeze.py is not changed.
- **L-E5-5 (excluded trials).** A trial OC-H excluded (not Tier A or B) is listed with its label, not
  run, and named in the statement as not covered; it does not block the statement (NULL_CRITERIA_E 3:
  "every member (Tier A and Tier B)").
