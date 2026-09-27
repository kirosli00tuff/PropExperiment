# Stage E.2b G4: MLTestCoder-OpusXHigh worker report (the ML route's test side, M7.8)

Worker: MLTestCoder-OpusXHigh (worker-xhigh, Opus 5.5). 2026-09-26, about 13:58 to 14:47 PDT. The
lead's follow-up (OC-P and the rulings on section 7) was applied from 14:33 PDT.

Synthetic data only. No bar parquet of any Stage E product was opened; no holdout, TopstepX,
Databento or git state was touched. No file outside ml_route/ and my own new tests was edited,
with one exception: the one existing test the lead allowed (D-2).

One outside fetch: the DSR paper PDF, a single curl to the author's site with no WebSearch, to
read Appendix 3 (RA-4).

## 0. Lead rulings recorded (follow-up brief, 14:3x PDT)

- **OC-P (on Q-E1, Q-E2, Q-E3).** Frozen M5 fixes the aggregation. Step 1: "M4's
  one-open-position rule applies in time order per product ... A product's daily P&L is the sum
  of its trades' P&L on that date, and zero on a date with rows and no trade; the portfolio's
  daily P&L is the mean over the products with rows on that date". ML-A10 applies the same to
  steps 3-4.
  - E.ML-test runs each exposure of a route rule as its own Stage E engine run with ONE traded
    leg (the exposure's vehicle), plus the legs that exposure's features read: its price path
    and its F16 lead.
  - D11.5's missing-bar rule applies to that run's own legs, and K6's two calendars never meet
    in one run.
  - The rule's daily series is the mean, over the exposures with rows on that date, of the
    per-exposure daily series; the units must be stated (see below).
  - The engine_second_leg_position path for route rules and the K6 refusal are removed. RR-11
    stays unchanged for catalog members.

  **Applied** in `ml_route/stage_e_adapter.py` (a rewrite: `exposure_plans` and
  `build_exposure_member`; the multi-leg member is gone) and `ml_route/test.py` (per-exposure
  runs, `rule_daily_series`, the K6 refusal removed).

  **Units, as asked.** The rule's test series is in NULL_CRITERIA_E 3's unit, as ML-A15 sets it
  for a route rule. Each exposure's daily net USD at its q_c is divided by (q_c x tick value) of
  the rule's primary leg; M5's mean is then taken over the exposures with rows on the date. So the
  series is in net ticks per contract per day of the primary vehicle.

  Because E.ML-test runs once, the same mean in M5's own sigma_X,d units is recorded beside it as
  `series_m5_sigma` (descriptive): each trip's net vehicle ticks per contract divided by its price
  path's sigma_X,d, summed per exposure and date. Switching units later needs no second
  research-window read.

  Each exposure's own series (net ticks per contract of its own vehicle) is kept for the
  per-exposure nulls.
- **Q-T1 to Q-T4** stay as named "not computed" items (user questions).
- **Q-C1** (a price path reads its vehicle's release list; a differing list is refused) is
  confirmed.
- **Q-R1** (`--route-manifest-sha256`) is accepted.
- **RA-1 to RA-5** are accepted as readings.
- **Stale-test note (D-2)** is fixed as instructed (section 8).
- **RT-4 ruling (second follow-up, applied 16:4x PDT).** Route rules "are pre-registered and
  tested as ordinary members" (NULL_CRITERIA_E 3, U6), so the member convention governs the test
  series: "zeros on window dates without a trip", over every research-window date after the
  runner's exclusions.
  - On a date where at least one exposure has rows, the value is M5's mean over the exposures
    with rows. On a window date where none has rows (the F17 warm-up included), it is 0.0 and is
    not left out.
  - Applied in `ml_route/test.py`: `rule_daily_series(values, rows, window_dates)`. The rule's
    window is the union of its exposure runs' member windows, each after the runner's
    exclusions. `series_m5_sigma` uses the same axis.
  - Each rule's record and the summary's rule list carry `window_dates` and
    `window_dates_without_rows` (the record also has `first_date_with_rows`), and the summary has
    a `warm_up_finding` note for the user.
  - On the synthetic test (about 190 window dates) more than 100 dates have no rows. On real data
    it is about 139 of about 300.
- **RT-5 ruling.** Kept: one exposure failing D9's coverage check excludes the whole rule (D9 plus
  lead ruling OC-H). Unchanged in the code.
- **Re-run after the RT-4 change** (heavy.sh, 16:52 PDT): tests/test_ml_route_*.py,
  tests/test_leakage_canaries.py and CanaryCoder's tests/test_stage_e_canaries.py (which has
  landed and uses `exposure_plans` / `build_exposure_member`): **367 passed, 24 xfailed** (the
  xfails are CanaryCoder's strict xfails). My entry tests now also prove that the warm-up dates
  are zeros in the series, that the count is recorded, and that `rule_daily_series` puts 0.0 on
  a window date without rows (known answer).

## 1. Files

- **Created:**
  - `ml_route/stage_e_adapter.py`: the per-exposure Stage E member (OC-P).
  - `ml_route/test.py`: the E.ML-test entry (`python -m ml_route.test`).
  - `ml_route/accounting.py`: M6's training-window DSR and PBO.
  - `ml_route/freeze_scope.py`: M7.8's scope list and the harness-manifest check.
  - Tests: `tests/test_ml_route_stage_e_inputs.py` (22), `tests/test_ml_route_stage_e_adapter.py`
    (21), `tests/test_ml_route_accounting.py` (19), `tests/test_ml_route_test_entry.py` (26).
- **Modified:**
  - `ml_route/inputs.py`: the S_X and calendar wiring. Adds `ReleaseListMismatch`,
    `event_calendar_from_release`, `EventCalendar.first/last/require_coverage`, and a
    `repo_root` parameter on `load_event_calendar`, `load_start_dates` and `load_route_inputs`.
  - `ml_route/rows.py`: OC-M, with the new function `deferred_exit`.
  - `ml_route/rule_wrapper.py`: `Decision` gains `trade_date`, defaulting to None, so the
    rows-per-date rule can be applied.
  - `tests/test_ml_route_distil_entry.py`: ONLY
    `TestInputs::test_unwired_inputs_refuse_by_name`, as the lead allowed.
- **Not touched:** everything else, including screening/ and the runner (RR-11 is unchanged for
  catalog members) and the frozen files.

## 2. How each brief item is met

**1. Adapter (`ml_route/stage_e_adapter.py`, rewritten for OC-P).** The interface is in the
module docstring, for CanaryCoder:

```python
for plan in exposure_plans(rule_json, products):          # one per exposure, primary first
    member = build_exposure_member(rule_json, plan, products, costs, events, trade_dates, blackout)
    result = run_engine({leg.root: frames[leg.root] for leg in plan.legs}, member, plan.legs,
                        StageERules(...))
    member.decisions                                       # [Decision(t_ns, complete, fired, acted, trade_date)]
```

- **Legs.** `plan.legs` is the vehicle (traded), then, as signal legs, the price-path contract
  when it differs from the vehicle and the cluster's F16 lead price path when the exposure is not
  the lead. Examples:

  | Exposure | Legs |
  |---|---|
  | MNQ | MNQ, NQ |
  | M2K | M2K, RTY, NQ |
  | ZN | ZN |
  | ZF | ZF, ZN |
  | MCL | MCL, CL |
  | NG | NG, CL |
  | HE | HE, ZC |
- **Primary leg.** The primary is the rule's `primary_leg`, the vehicle of the lead (ML-A15).
  Any other primary is refused by name.
- **Each minute:** the lead's bar goes to `observe_lead`; the wrapper runs on its own price-path
  bar with its vehicle's position and pending contracts; its orders become LegIntents on the
  vehicle.
- **Engine.** D8, D9, the D9.5a guard and F are the engine's. The trading windows are the D6 day
  session of each leg.

**2. E.ML-test entry (`ml_route/test.py`).**

```
python -m ml_route.test --route-dir DIR --route-manifest-sha256 SHA --research-root DIR \
    --out-dir DIR --harness-sha256 SHA
```

All five arguments are required. The steps, in order:
1. `preflight` runs first.
2. The M7.8 scope check.
3. The whole frozen route is verified:
   - the manifest's file sha256 and body hash, and its harness;
   - every ledger chain, and its fits;
   - every selected model file (`verify_model_file`);
   - every surrogate tree;
   - M5 step 4 re-run on the survivors;
   - every rule file: `rule_spec_from_json`, equality with the kept rule, its manifest entry,
     and its model, tree and harness;
   - RULES.md, and that rules/ holds nothing else.

   M6's training accounting is then computed from the verified ledgers.
4. The frozen inputs: the vehicle, cost and calendar hashes equal the manifest's, and the
   research window is covered.
5. Every rule's exposure runs are planned, each with exactly one traded leg and recorded
   research sha256s, and the output directory must be new. No bar is read before this point.
6. Per rule:
   - the research bars of every leg are loaded once (hash-checked, holdout rows refused);
   - each exposure gets its own run: member window, coverage, `run_engine` with `StageERules`,
     trips, trade rate, floor labels, decisions, rows dates, and its own-vehicle series with
     moments and daily t;
   - then the rule's series (OC-P, in the units of section 0), its moments and daily t, and
     `series_m5_sigma`.
7. The summary:
   - `program_trials_added` = the number of tested rules (M6);
   - the untested rules, by name;
   - the search counts and the training-window accounting;
   - the family's Sharpe variance (ML-A15) and PBO on 8 contiguous blocks;
   - Q-T1 to Q-T4 as named "not computed" entries.

Records are written once, through the runner's `write_record`.

**3. Training-window DSR and PBO (`ml_route/accounting.py`).** Unchanged by OC-P; RA-1 to RA-5
are accepted.
- **Series.** Per configuration, the per-date mean over its 4 validating CPCV splits. The 36
  series share one date axis (zeros on dates without rows).
- **DSR.** Reported at 36, at Appendix 3's N_hat and at the literal full-search count, using the
  pinned `deflated_sharpe_ratio` and D.1's moments.
- **PBO.** The pinned CSCV on 8 contiguous blocks.

**4. Shared S_X and release calendar (`ml_route/inputs.py`).**
- **S_X.** `load_start_dates(roots=None, repo_root=REPO_ROOT)` calls
  `screening.stage_e_start_dates.start_date(root, root=repo_root)` lazily for the 28 price paths
  with a vehicle. Each failure is refused by name, and no root is skipped.
- **Calendar.** `load_event_calendar(products=None, repo_root=REPO_ROOT)` reads the runner's file
  through `load_release_calendar(repo_root)`.
  - A price path reads its vehicle's list (Q-C1, confirmed). A differing listed path list gives
    `ReleaseListMismatch`, and an unlisted vehicle is refused.
  - CPI instants are exact int64 ns.
- **`load_route_inputs(repo_root=REPO_ROOT)`** requires the calendar to cover the training
  window.
- **Status.** Neither shared file existed at 14:44 PDT, so both loaders are tested with
  monkeypatch.

**5. OC-M (`ml_route/rows.py`).** Guarded exits are deferred to the first bar at or after
release + 2 min, repeated while that bar is itself guarded. The D8 event cost applies inside 30
minutes of a release. A deferral that reaches F_X becomes the forced flatten at F_X (exempt,
RR-3), and exit_ns holds the deferred time.
- **Counts.** `target_<h>_exit_deferred_event_guard` and
  `target_<h>_exit_guard_forced_at_flatten`, in `row_counts`.
- **Entries.** An entry in the guard cannot arise, because M4 excludes those decision times.
- **Engine agreement.** Proven per exposure run: each exit time equals the training row's, and
  the engine's `fill_guard_deferral` count equals the deferred trips.

**6. M7.8 completeness.** The table is in section 3.
- `ml_route/freeze_scope.check_harness_scope` refuses, naming each file, when the harness
  manifest leaves out an ml_route module or an M7 test.
- E.ML-test calls it right after the preflight.

## 3. M7.8: every item it names, where it lives

| M7.8 item | Code (file: function) | Tests |
|---|---|---|
| feature builders | features.py: `build_daily`, `decision_grid`; rows.py: `build_rows`, `validate_availability`; dataset.py: `build_dataset`, `build_from_bars`; lstm_data.py: `five_minute_bars`, `sequence_index`; store.py: `read_product_bars`, `assert_store_root`, `assert_window`; inputs.py | test_ml_route_features (14), test_ml_route_store (13), test_ml_route_stage_e_inputs (22) |
| target builders | rows.py: `_targets`, `deferred_exit` (OC-M) | test_ml_route_features; test_ml_route_stage_e_inputs::TestOcmTargets and ::TestDeferredExitKnownAnswers |
| block cut | blocks.py: `training_calendar`, `cut_blocks`, `frozen_block_cut` | test_ml_route_blocks_selection::TestBlockCut |
| CPCV splitter | blocks.py: `cpcv_splits`, `split_masks`, `assert_fold` | test_ml_route_blocks_selection::TestCpcv |
| selection | selection.py: `split_score`, `configuration_score`, `select`; train.py: `run_fit`; adapters.py, lgbm.py, lstm.py; ledger.py | test_ml_route_blocks_selection, test_ml_route_models, test_ml_route_e2e |
| surrogate | surrogate.py: `fit_surrogate`, `leaves`, `candidate_sign` | test_ml_route_distil_entry |
| pre-test | surrogate.py: `rule_result`, `pretest`; train.py: `run_distil` | test_ml_route_distil_entry |
| ranking | surrogate.py: `keep_per_cluster` (also re-run by E.ML-test) | test_ml_route_distil_entry; test_ml_route_test_entry::test_an_edited_survivor_list_is_refused |
| write-up | surrogate.py: `rule_json`, `render_entry`; manifest.py: `finalize_route` | test_ml_route_distil_entry::TestManifest; test_ml_route_test_entry (RULES.md) |
| every M7 test | tests/test_ml_route_*.py (12 files) + tests/test_leakage_canaries.py + tests/test_stage_e_canaries.py (CanaryCoder) | `freeze_scope.required_files` / `check_harness_scope`; test_ml_route_test_entry::TestM78Scope |
| E.ML-train refuses on a differing hashed file | train.py: `cmd_fit` / `cmd_finalize`, preflight first | test_ml_route_distil_entry::TestEntryPreflight |
| E.ML-test refuses on a differing hashed file | test.py: `run_test` (preflight, scope, `load_frozen_route`, `load_test_inputs`) | test_ml_route_test_entry (preflight tests and TestFrozenRouteRefusals, 11 cases) |
| M7.6 hash chain at the test | test.py: `load_frozen_route` | as above |
| M7.7 wrapper through the engine | rule_wrapper.py (MES engine); stage_e_adapter.py (Stage E engine, one exposure per run) | test_ml_route_wrapper (6), test_ml_route_stage_e_adapter (21), CanaryCoder's canaries |

**Not closed here.**
- The harness manifest (Task 6, the lead's) does not exist yet. Its builder must list every file
  of `freeze_scope.required_files()`, plus the test helpers those tests import
  (tests/_stage_e_synthetic.py, tests/__init__.py).
- E.ML-train does not call the scope check (D-1).

## 4. Tests (88 new, all passing) and what each proves

**tests/test_ml_route_stage_e_inputs.py (22)**
- **S_X (4).** A fake shared module gives the 28 S_X, and RB, HO and SI are not read. A missing
  root is refused naming ZL. A non-date value is refused. An absent module is refused by name.
- **Calendar (8).**
  - Known answers: NQ reads MNQ's list, RTY reads M2K's, CPI is exact ns, and sha256 and source
    are carried.
  - An unlisted path takes its vehicle's list.
  - A differing path list gives `ReleaseListMismatch`; an identical one is accepted.
  - An unlisted vehicle (MCL) is refused.
  - Training-window coverage is enforced.
  - The runner's refusal becomes a named `RouteInputMissing`.
  - `load_route_inputs` wires both loaders.
- **`deferred_exit` known answers (5).** Not guarded; deferred to release + 2 min; a missing bar
  moves the fill to the next bar; chained releases defer again; a deferral reaching F is the
  flatten at F.
- **OC-M on real rows (3).** On synthetic NQ, with costs recomputed by hand from the raw JSON:
  - an h30 exit in the guard gets exit_ns = t + 31, and its y and cost match to 1e-12;
  - hF exits at F with the event cost, and the forced-at-flatten count is 12;
  - the target is no longer missing.
- **Other (2).** CPI conversion is exact. `repo_root` reaches both shared loaders (new).

**tests/test_ml_route_stage_e_adapter.py (21).** A K1 rule on MNQ (legs MNQ, NQ) and M2K (legs
M2K, RTY, NQ), with each exposure's own `run_engine` / `StageERules` run over about 165 synthetic
dates, and a 10:29 CT release on the late dates.
- **Plans and protocol (1).** One plan per exposure, one traded leg each, and each run reads only
  its own path and the lead. `StageEMember` holds, and the D6 windows are [08:30, 15:00).
- **Decision parity (2, MNQ and M2K).** Each exposure's complete and fired sets equal the training
  rows (M2K's need F16 from NQ). Every decision carries its trade date.
- **Fill timing (2).** Every trip opens at t + 1 min from a decision row and closes at the
  training `exit_ns`. At least one deferred exit per run, and the engine's `fill_guard_deferral`
  count equals the deferred trips.
- **D8 net (2).** Each trip's net cents equals y x sigma x 50 cents x q_c (1 or 3) within
  2 cents.
- **Independence (1, OC-P).** No `engine_second_leg_position` counter in any run, and MNQ and M2K
  positions overlap in time, as in M5's per-product P&L.
- **Acted decisions (2).** Acted decisions equal the intents from flat, and no intent is refused.
- **Refusals (7).** A non-lead primary; a vehicle outside the cluster; repeated exposures or a
  primary missing from them; K8; a changed rule hash; missing trade dates, or a plan that is not
  the rule's; construction-refusal pass-through.
- **Other clusters (3).** K2 plans (ZN alone; ZF with ZN). K6 ZC, HE and LE as separate runs on
  the grains and livestock calendars. K4 MCL with CL, and NG with CL.
- **Schema (1).** The frames are in the store schema.

**tests/test_ml_route_accounting.py (19).** Unchanged from the first delivery.
- The pinned helpers equal D.1's `_moments` and `_blocks`.
- Series construction, with its known answer and four named refusals.
- N_hat: 3, 2.0, and undefined by name.
- DSR at 36 and 51, N_hat's DSR, and PBO, each equal to hand calls of the program functions.
- The remainder dates are left out of the PBO blocks.
- The accounting is computed from real Ledger files, and chain or grid defects are refused.

**tests/test_ml_route_test_entry.py (26).** A synthetic frozen route built by the REAL
`finalize_route`, with two K1 rules: lgbm_h30 on MNQ and M2K, lstm_h30 on MNQ. The research store
holds NQ, MNQ, RTY and M2K for 2025-04-01..2025-12-31.
- **End to end (5).**
  - Both rules have status "run", `program_trials_added` = 2, and 36 configurations are
    accounted.
  - The records carry the primary MNQ, the per-exposure legs (one traded each) and bar sha256s,
    the series unit, the three DSR counts and `series_m5_sigma`.
  - **The OC-P known answer:** on every date, the 2-exposure rule's value equals the mean over
    the exposures with rows of each own-vehicle value x (q_c x tick value) / MNQ's, the
    exposures-with-rows count matches, and more than 20 dates have both. The 1-exposure rule's
    series equals its exposure's series on exactly its rows dates, so warm-up dates are not in
    it (RT-4).
  - The family's PBO and the named not-computed items.
  - A second run is refused.
- **Preflight and CLI (3).** A raising preflight reads nothing; the real preflight refuses a
  wrong hash; every argument is required.
- **Frozen-route refusals before any bar (11).** A changed rule; a re-hashed changed rule; a
  model file; a ledger line; the manifest hash; the manifest body; another harness; RULES.md or
  an extra rule file; the survivor list; a surrogate tree; another calendar.
- **Other (7).**
  - K6 plans pass the leg check with no refusal (OC-P).
  - A run with two traded legs is refused.
  - `rule_daily_series` by hand: mean over the exposures with rows, 0 on a date with rows and no
    trade, and no date without rows.
  - Write-once.
  - M7.8 scope (3).

**Coverage** (my four test files):

| Module | Line coverage |
|---|---|
| stage_e_adapter | 98% |
| test | 93% |
| accounting | 97% |
| freeze_scope | 100% |
| inputs | 91% |
| rows | 96% |
| rule_wrapper | 96% |

## 5. Commands run (results)

| Command | Result |
|---|---|
| `pytest -q` on each new file, after OC-P | 22, 21, 19 and 26 passed |
| `pytest -q "tests/test_ml_route_distil_entry.py::TestInputs::test_unwired_inputs_refuse_by_name"` | passed |
| `reports/stage_e2b_briefs/heavy.sh uv run --no-sync pytest -q tests/test_ml_route_*.py tests/test_leakage_canaries.py` (14:40 PDT) | **183 passed** in 136 s: the 80 existing route tests (the edited one included), the 15 existing canaries and my 88. tests/test_stage_e_canaries.py did not exist yet. The pre-OC-P run at 14:22 had 174 passed |
| `pytest -q tests/test_cross_platform_static.py` | 6 passed |
| `ruff check ml_route/ tests/test_ml_route_*.py` | clean |
| Coverage run | see the table in section 4 |
| Timing probe | see section 9 |

## 6. Readings

**Accepted by the lead: RA-1 to RA-5 (`ml_route/accounting.py`).**
- **RA-1.** A configuration's series is the per-date mean over its 4 validating splits. That is
  the mean of CPCV's four paths under any split-to-path assignment.
- **RA-2.** One union date axis, with zeros where a configuration has no rows.
- **RA-3.** The DSR is reported at 36, at N_hat and at the full search (36 + candidates +
  survivors). The Sharpe variance is over the 36.
- **RA-4.** Appendix 3's N_hat = rho_hat + (1 - rho_hat) M, with Eq. 8's average correlation.
  - The formula is reconstructed from the fetched text: "Given an estimated average correlation
    [rho_hat], we could therefore interpolate between these two extreme outcomes to obtain (9)",
    where the extremes are "as [rho -> 1], then [N -> 1]. Similarly, as [rho -> 0], then
    [N -> M]" (symbols lost in extraction).
  - N_hat is undefined by name for a constant series or a matrix that is not positive-definite.
    PCA is not computed.
- **RA-5.** CSCV on 8 contiguous blocks.

**Readings of the entry** (RT-1 to RT-3 were reported before; RT-4 and RT-5 are new with OC-P;
none is ruled on yet):
- **RT-1.** The legs and trading windows of the per-exposure plans (D6 day session).
- **RT-2.** A rule excluded by coverage or refused by the engine is not tested and adds nothing
  to N; it is listed by name.
- **RT-3.** The family PBO puts the rules' series on the union of their dates, with zeros
  elsewhere.
- **RT-4 (rows at the test; superseded by the lead's RT-4 ruling in section 0, which is what
  the code does).** An exposure "has rows" on a window date of its run when the wrapper has a
  decision with complete features there. That is training's rows less the target,
  which is unknown at a decision.
  - Dates on which no exposure has rows are NOT in the rule's series, as in M5's portfolio
    series. So the research window's warm-up dates (ML-A19's known cost; about the first 139
    trade dates) do not enter as zeros.
  - This differs from the zeros-on-every-window-date convention of hand-written members.
  - The own-vehicle per-exposure series keep the runner's zeros on every window date.
- **RT-5 (the rule is the member).** For D9's coverage check, if any exposure run's leg is below
  0.95, the rule is excluded before screening (no run). An engine-refused case in any run
  refuses the rule.
- **OC-M's cap at F.** As before.

## 7. Questions

**Resolved by the lead:**
- Q-E1 to Q-E3: resolved by OC-P and applied.
- Q-C1: confirmed.
- Q-R1: accepted; the session prompt for E.ML-test must state the route manifest's sha256.
- Q-A1: RA-1 to RA-5 accepted as readings. Which DSR count M6's "that count" means stays with the
  lead; all three are reported.

**Still open:**
- **Q-T1 to Q-T4** (user questions, named "not computed" in the summary): Holm at 0.05 / (K + 1)
  and the route's p-value construction; DSR at the cumulative program N; the composite verdict;
  the per-exposure null test's bootstrap seed (no member ordinal).
- **RT-4 and RT-5: RULED** (section 0). The warm-up enters as zeros; RT-5 is kept. The original
  question, kept for the record: confirm that:
  - dates with no exposure rows (the warm-up) are left out of the rule's test series rather than
    entered as zeros;
  - one exposure's coverage failure excludes the whole rule.

  The first changes the series length (about 300 window dates against about 160 dates with rows
  on real data) and so the daily t.

## 8. Deviations, observations and anything unfinished

- **D-1 (scope check not in E.ML-train).** `train.py` does not call `check_harness_scope`. The
  existing e2e and entry tests patch only `preflight`, and I may not edit them. Enforcement is at
  E.ML-test and should also go in the lead's manifest builder.
- **D-2 (fixed).** `tests/test_ml_route_distil_entry.py::TestInputs::test_unwired_inputs_refuse_by_name`
  now calls `load_route_inputs(repo_root=tmp_path)` and `load_start_dates(repo_root=tmp_path)`,
  so it keeps passing after reports/stage_e2b_release_calendar.json and
  reports/stage_e_start_rule_*.json land. With the shared module present, `start_date` raises
  `StartRuleMissing` under the empty root, which becomes "no frozen S_X for ...". This is the
  only edit to MLPipelineCoder's files.
- **O-1 (catalog members only now).** The engine's same-open fill order is traded-leg order, so an
  entry on one leg can precede another leg's pending exit at the same open. Route rules no longer
  have two traded legs in a run, so this now concerns catalog members only. It is RR-11's domain
  and unchanged.
- **API change for CanaryCoder.** `route_legs` and `build_route_member` (the multi-leg member)
  were removed by OC-P and replaced by `exposure_plans` and `build_exposure_member`. No canary
  file existed yet at 14:33 PDT, so nothing broke. The preliminary version of this report showed
  the old names.
- **Not done here.** The Stage E canaries through the adapter are CanaryCoder's (Task 3). There
  is no real-data run of anything.

## 9. Timing probe: one exposure at research-window size (synthetic)

- **Setup.** `probe_etest.py` in the session scratchpad, run through heavy.sh at nice 10 with 2
  BLAS threads, 14:29 PDT. It is exactly one OC-P exposure run: NQ price path plus MNQ vehicle
  over 2025-04-01..2026-06-19, 316 trade dates of about 23-hour sessions, 436,617 bars per leg.
- **Result.**
  - 85 s in `run_engine` with the wrapper; peak RSS 439 MB.
  - 3,708 decision times, of which 1,896 were complete after the warm-up; 886 acted.
- **An earlier run** with an empty release list gave 0 complete decisions (F13 and F14 are
  missing without releases) in 83 s.
- **Extrapolation (a guess).** With OC-P a rule costs about 1.5 minutes per exposure, a little
  more for runs with a lead leg. A 7-exposure K3 or K6 rule should take about 10 to 12 minutes,
  and at most 14 rules about 1 to 2 hours. It is not probed on real bars.

## 10. Follow-up review fixes (lead's Task 8 ruling on reports/stage_e2b_harness_review.md, 17:5x to 18:45 PDT)

Everything below is in ml_route/ and my tests. The one addition to an existing test is
`tests/test_ml_route_review_fixes.py`, which is new. No existing test was edited.

**(1) NOTE-4: store bookings (`ml_route/store.py`).**
- `read_product_bars` now calls `book_rows`, which books every row's timestamp on the product's
  group calendar with `data.stage_e_bars.check_bookings(root, calendar, frame, "step2", where)`,
  as the runner and compute/datarules do.
- A `StageEBarRefusal` becomes `StoreRefused("REFUSED: <root>: <class>: ...")` in three cases:
  - an unbookable row;
  - a row booked to a date outside the step 2 store or to a forbidden class (the March 2024
    embargo, holdout-2 or holdout-1, so every date on or after 2024-03-01);
  - a row whose label differs from its booking (`TradeDateMismatch`).
- The label checks run first, so the existing planted-label test keeps its message.
- Tests:
  - an honest store books cleanly;
  - a 2024-03-04 bar labelled 2024-02-29 gives `HoldoutRowRefused` (embargo);
  - the review's scenario, a 2025-05-01 bar relabelled 2023-12-01, gives `HoldoutRowRefused`
    (outside the step 2 store);
  - a row labelled with the previous trade date gives `TradeDateMismatch`.

**(2) NOTE-5: no silent CPU fallback; the device in every fit record.**
- `ml_route.adapters._gpu_or_cpu` and `lstm_batch_size` are removed.
- `LstmAdapter` now takes `batch_size` and `device` explicitly. A training adapter (one with a
  machine record) on anything but "cuda" is refused by name.
- `adapter_for(challenger, store_root, inputs, route_dir, harness_sha256)` builds the LSTM
  through `ml_route.lstm_machine.ensure_lstm_machine`, which refuses by name
  (`LstmMachineRefused`, a `RouteInputMissing`) when `torch.cuda.is_available()` is False. This
  happens before any store read.
- Only `ml_route.probes` may still run on the CPU.
- Every ledger record (10 splits and the refit) carries `"device"`: "cpu" for LightGBM, "cuda"
  for the LSTM.
- Tests: no CUDA is refused and writes nothing; the training adapter refuses before any read; a
  CPU training adapter is refused; `run_fit` with a stub adapter writes the device into all 11
  records.

**(3) NOTE-11 (V10-2): the LSTM machine record (`ml_route/lstm_machine.py`, new).**
- **First fit.** Before the first LSTM fit, `ensure_lstm_machine` runs M8's A-1 ladder on this
  card and writes `lstm_machine.json` into the route directory, write-once:
  - host, GPU name, and total VRAM (nvidia-smi `memory.total`);
  - the A-1 steps and the planned batch size (512 -> 256 -> 128 -> 64, the first that leaves
    0.5 GB free);
  - the harness sha256 and the time.

  A ladder that fits no batch stops to the user, and nothing is written.
- **Later fits.** Every later fit re-measures A-1 at the recorded batch on the card it runs on,
  and refuses unless that card holds the batch with at least 0.5 GB free. The fit runs with the
  recorded batch (`LstmAdapter.fit` calls `check_fit_batch`, which refuses any other batch).
- **Shared measure.** The A-1 measure is `ml_route.probes.a1_step`, factored out of
  `batch_probe` without changing its output. peak = max_memory_reserved + CUDA context;
  free = card total - peak.
- **Manifest.** The route manifest carries `lstm_machine`.
- **Reading R-M1.** The card's total is nvidia-smi's `memory.total`. On the RTX 3050 Laptop GPU
  that is 4096 MiB, M8's "4 GB"; on another card it is that card's total.
- **Tests (fakes for the card and the measure):**
  - the first fit writes the record with batch 256 when 512 leaves too little;
  - a later fit keeps the file byte-identical and passes at 700 MiB free;
  - a later fit is refused at 400 MiB free;
  - no fitting batch stops to the user;
  - a corrupt record is refused;
  - a fit with another batch is refused;
  - the manifest reads the record.
- **Real CUDA test.** One test runs on this machine's real CUDA card: the record gets an A-1
  batch in the ladder, and a second call passes the check.
- **Existing end-to-end test.** `tests/test_ml_route_e2e.py::test_lstm_fit_entry_end_to_end` now
  writes and uses the record on the real card, and passes.
- **Caveat.** On a machine without CUDA, that existing test would now refuse by name rather
  than fit on the CPU. This is intended by V7, but I may not add a skip to it.

**(4) F-4: the Holm entry (`ml_route/test.py`).**
- The E.ML-test summary's Holm entry, still "not computed", now names:
  - `screening.stage_e_stats.k_from_tiers(tiers, route_tested=True)`: the clusters with a
    non-empty Tier A plus the route family, at most 9;
  - `screening.stage_e_stats.holm_alpha_k`, with `alpha_rule` "0.05 / (K + 1)".
- ml_route has no call to either function, so there was nothing else to update.
- Test: the entry names both, `route_tested` is keyword-only with no default, and
  `MAX_FAMILIES` is 9. It checks ScreenStatsCoder's landed code, so the named function stays
  valid.

**(5) F-3 (b), the lead's addition: the training store is pinned to the start rule.**
- **Inputs.** `ml_route.inputs.load_start_rule(roots, repo_root)` reads the shared
  `screening.stage_e_start_dates.start_dates_for`. It returns S_X and, per root, the
  `step2_sha256` the start rule recorded (InputsCoder's "Follow-up F-3" field). It refuses by
  name:
  - an S_X whose source files do not include set ML's reports/stage_e_start_rule_ML.json;
  - a missing or malformed sha256;
  - any loader refusal (missing, empty window, conflict, inconsistent), wrapped.

  `load_start_dates` is now its first half. `load_route_inputs` fills
  `RouteInputs.step2_sha256`; it is None only for synthetic inputs.
- **Reader.** `read_product_bars(..., expected_sha256=...)` hashes the parquet and refuses a file
  that differs from the pinned sha256. `ProductBars.file_sha256` records what was read.
- **Training reads.** Both training reads pass the pin, and a pinned mapping without the root is
  refused:
  - `ml_route.dataset.build_dataset`, which keeps the shas in `table.store_sha256`;
  - `ml_route.adapters.five_minute_store`, the LSTM's second read.
- **Fit and manifest.** `fit` writes `step2_store_sha256` into its candidates file. `finalize`
  (`ml_route.manifest.store_hashes`) records `step2_store_sha256` in the route manifest, and
  refuses:
  - two fits that read different parquets for a root;
  - for pinned inputs, a traded root whose recorded sha256 is missing or differs from the start
    rule's.
- **Tests.**
  - A doctored store (one close changed, labels intact): the reader passes on the pinned sha256
    before the change and refuses the doctored file after.
  - `build_dataset` refuses a wrong pin and a missing pin, and records the right one.
  - `store_hashes`: records the shas; refuses conflicting fits, a differing pin and a root with
    no recorded store.
  - `load_start_rule`: returns the sha from set ML, and refuses another set's file and a
    malformed sha.
  - My input tests' fake loader now implements `start_dates_for`.

**Runs.**

| Command | Result |
|---|---|
| `heavy.sh uv run --no-sync pytest -q tests/test_ml_route_*.py tests/test_stage_e_canaries.py` (18:43 PDT) | **395 passed** in 234 s |
| `pytest -q tests/test_cross_platform_static.py` | 6 passed |
| `ruff check ml_route/ tests/test_ml_route_*.py` | clean |

**New test file.** `tests/test_ml_route_review_fixes.py` has 18 tests. Line coverage:

| Module | Line coverage |
|---|---|
| lstm_machine | 98% |
| store | 96% |
| dataset | 96% |
| inputs | 91% |

**Not done.**
- E.ML-test does not re-check `step2_store_sha256` or `lstm_machine`. They are hashed inside the
  route manifest, which E.ML-test verifies, and the test reads no step 2 bar.
- The M7.8 list now includes `ml_route/lstm_machine.py`.
