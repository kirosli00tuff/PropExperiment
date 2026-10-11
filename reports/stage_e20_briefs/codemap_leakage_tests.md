# Stage E.20 code map: leakage tests (ml_route_v2 V2.9 controls)

Read-only map, written 2026-10-11 by the leakage-tests mapper. No data store opened. Code read by section only.
Line numbers are against the working tree at the time of writing.

## 0. Freeze status of the test layer (fact)

reports/stage_e12_ml_v2_freeze.json hashes 91 files. They include every `tests/test_ml_v2_*.py`,
`tests/ml_v2_fixtures.py`, `ml_route_v2/synthetic.py`, `ml_route_v2/clock.py`, `ml_route_v2/constants.py`,
`ml_route_v2/panel.py`, `ml_route_v2/pipeline.py`, `ml_route_v2/signals/__init__.py`, `ml_route_v2/signals/generic.py`
and `ml_route_v2/signals/synthetic_bars.py`. So **any edit to an existing ml_v2 test or fixture is an edit to a
hashed file**. Running the controls on the E.20 universe without an amendment means new test files (for example
under pattern_search's tests) that import the frozen helpers and call them.

## 1. The ml_v2 test files (one line each; test counts are top-level `def test_*`, before parametrize)

| file | lines | tests | subject |
|---|---|---|---|
| tests/test_ml_v2_blackout.py | 118 | 3 | V2.2 roll-blackout rule (E.11 lead ruling 2026-10-03) |
| tests/test_ml_v2_clock.py | 117 | 13 | V2.2 decision clock, DecisionRows; pins DECISION_TIMES_CT |
| tests/test_ml_v2_configs.py | 91 | 6 | the 45-config grid, V2.9 tie-break, ledger |
| tests/test_ml_v2_cpcv.py | 606 | 26 | blocks, splits, purge, embargo, paths, nested CPCV, PBO, DSR |
| tests/test_ml_v2_decide.py | 182 | 16 | cost gate (gross default, V23 item 1) |
| tests/test_ml_v2_e2e.py | 297 | 16 | pipeline end to end on a 4-vehicle synthetic world |
| tests/test_ml_v2_engine_stage.py | 192 | 9 | engine-stage memory and per-path checkpoints |
| tests/test_ml_v2_gate0.py | 221 | 12 | Gate 0 families A/B, Holm, registration |
| tests/test_ml_v2_k9.py | 168 | 7 | K9 announcement-day flag |
| tests/test_ml_v2_killswitch.py | 101 | 11 | KS1-KS5 |
| tests/test_ml_v2_leakage.py | 590 | 27 | V2.9 canaries + Gate 0 canary semantics (main subject below) |
| tests/test_ml_v2_models.py | 126 | 9 | ridge / LightGBM, determinism, payload sha256 |
| tests/test_ml_v2_normalize.py | 137 | 9 | zscore_causal (strictly earlier dates, warm-up, clip) |
| tests/test_ml_v2_panel.py | 187 | 9 | panel layout, c/sigma filter, window guard |
| tests/test_ml_v2_payout.py | 657 | 34 | account parameters, payout simulator |
| tests/test_ml_v2_phase1_freeze.py | 108 | 7 | v2 freeze check and CLI gates |
| tests/test_ml_v2_phase1_gate0.py | 301 | 14 | phase-1 build/register/run on fixture stores |
| tests/test_ml_v2_phase1_support.py | 264 | 0 | fixture stores (helpers only) |
| tests/test_ml_v2_phase1_world.py | 359 | 22 | phase-1 world on fixture stores |
| tests/test_ml_v2_portfolio.py | 525 | 32 | caps, accept_trades, V2.9 selection metric |
| tests/test_ml_v2_probe.py | 91 | 6 | runtime probe CLI |
| tests/test_ml_v2_signals.py | 482 | 24 | registry, per-signal causality/perturbation, hand values |
| tests/test_ml_v2_simulate.py | 572 | 24 | v2 portfolio on the frozen engine |
| tests/test_ml_v2_sizing.py | 187 | 22 | sizing.contracts |
| tests/test_ml_v2_state_fingerprint.py | 152 | 8 | resumable-state fingerprints (C-01) |
| tests/test_ml_v2_targets.py | 216 | 8 | gross moves, D8 round trips, normalized targets |
| tests/ml_v2_fixtures.py | 202 | 0 | shared helpers (world cache, perturbation, peeking normalizers) |

## 2. Shared machinery the controls use

**ml_route_v2/synthetic.py**
- `synthetic_universe(roots: Sequence[str], first: date, last: date, *, seed: int, plant: Mapping | Sequence[Mapping] | None = None, warmup_dates: int = WARMUP_DATES, vol_ticks: Mapping[str, float] | None = None, sigma_cost_multiple: float = SIGMA_COST_MULTIPLE, compact: bool = False, eager_frames: bool = True) -> SyntheticWorld` (synthetic.py:412).
  `roots` are vehicle roots of constants.UNIVERSE. Bars cover each vehicle's price path, plus the cluster leads (G17), MES and the legs
  (`legs_by_vehicle`, :133). WARMUP_DATES = 210 (:68).
- `SyntheticWorld` fields (:87-101): vehicles, first, last, bars_first, calendar, bars, frames, releases, costs, blackout, legs,
  vol_ticks, seed, plant.
- Plant kinds `PLANT_KINDS = ("sign", "noise", "shift", "leak")` (:78), documented at :36-60.
- **The sign plant uses the 3-time clock.** `_decision_ts(vehicle, days)` (:282-284) calls `clock.decision_rows`, so a planted
  edge exists only at t1..t3. The plant does not touch t4 rows.
- `nominal_cost_ticks(vehicle: str) -> float` (:154) averages over `DECISION_TIMES_CT[session_group(vehicle)]` (:167), the 3 times.
- `leak_column(ts, closes, minutes)` (:326) builds the planted `leak_fwd` column.

**tests/ml_v2_fixtures.py** (hashed)
- `world(roots, first, last, *, seed, plant=None, **kwargs) -> SyntheticWorld` (:45): cached `synthetic_universe`.
- `world_rows(w) -> pd.DataFrame` (:54-57) = `clock.decision_rows(w.vehicles, ..., exclude=own_blackout(...))`. **3 times only, no
  rows parameter.**
- `context(rows, bars, releases, blackout=None) -> SignalContext` (:60).
- `perturb_after(bars, cut_ns, *, seed, shift_minutes=None, leak_minutes=60) -> dict[str, pd.DataFrame]` (:65): randomizes
  prices (+-5%) and volume of bars opening at or after the cut.
- `perturbation_check(w, features: Callable[[SignalContext], pd.DataFrame], cuts, *, seed=1, shift_minutes=None, bars=None) -> int`
  (:107-129). It builds rows internally via `world_rows(w)` (:113). `features` is any callable of a SignalContext.
- `cuts_of_date(w, day) -> list[int]` (:132): decision times of that day, taken from `world_rows` (3 times).
- `zscore_peek_future`, `zscore_peek_today` (:156, :162): deliberately wrong normalizers. `normalizer_check(fn, raw, rows, cols, moved, compare, **kw)` (:171).
- `raw_rows(n_dates=90, roots=("MNQ","MGC"), seed=5)` (:183): hard-codes `t_index in (1, 2, 3)` (:188).

**Frozen production path (not injectable for rows):** `pipeline.build_world_panel(world, *, check_grid=True, signals=None)`
(pipeline.py:269) calls `clock.decision_rows` itself (:282), then `SignalContext`, `targets.build_targets`, `panel.build_panel`.
- `clock.decision_times_from(open_ct, flatten_ct)` (clock.py:70-80) always returns 3 times, `(first_k, k2, k3)`. `_date_rows` (:145-160)
  enumerates them. `N_DECISION_TIMES = 3` (constants.py:43).
- `compute_signals(ctx, names=None)` (signals/__init__.py:94) raises KeyError for any name not in the `REGISTRY` MappingProxyType (:49, :99-101).
- `build_panel(ctx, targets, *, mode="train", signals=None) -> Panel` (panel.py:107) reads features only through
  `compute_signals` (`_features`, :67).
- `Panel` is a frozen dataclass `(frame, feature_cols, signal_names, horizons, avail_max_ts_ns, counts)` (panel.py:43-50).
  `cpcv.horizon_data(panel, horizon, admissible=None)` (cpcv.py:324) reads `panel.feature_cols` (:328).
- `targets.py:11`: an h60/h120 exit exists only if t + h <= F_X. A t4 = F_X - 60 row is therefore not ok for h120 under the frozen
  target code. The F horizon's code id is `"hF"` (constants.py:44).
- `signals/generic.py`: `g11_t_index` (:267-269, :380) uses t_index as its value, and `_base_ratio` (:167-177) groups by t_index.
  Both run with t_index = 4 without code change. Whether that is wanted is not established here.

## Q1. The V2.9 controls as implemented

Below, "config-only" means a new test file that imports and calls frozen code, with no edit to a hashed file.

### 1a. Feature-timestamp validator
- Code: `assert_causal(signal_frame, rows)` (signals/__init__.py:123-142). It raises `CausalityError("... late ...")`, and `compute_signals`
  calls it on every run (:116). There is also a runtime guard in `build_panel` (panel.py:126-127).
- Tests: `test_values_available_by_t` (test_ml_v2_signals.py:143-153, parametrized over REGISTRY), `test_assert_causal_raises_on_a_planted_late_signal` (:259),
  `test_compute_signals_refuses_a_planted_leak` (:275).
- World: the signals test builds a 28-vehicle world, `decision_rows(tuple(UNIVERSE), ...)` on `session_bars` 2021-09-01..2021-11-12 (:41, :49-53).
- E.20: `assert_causal` takes any frame with raw_/app_/avail_ columns aligned to the rows. New features and t4 rows can be checked
  by composition.

### 1b. Perturbation test (bars after t randomized; features and predictions at t unchanged)
- Feature level, every library signal plus z-scores: `test_control_every_library_signal_passes_the_perturbation_test`
  (test_ml_v2_leakage.py:203-206). World `pert_world()` (:75-77) has vehicles `PERT_VEHICLES = ("MNQ","MGC","6E","MCL","ZN","ZC","MBT","HE")`,
  dates 2021-03-01..2021-04-15, cut day 2021-04-07 (:63-64), plant `{"kind":"leak","roots":("NQ",),"minutes":60}`. Features come from
  `registry_features` (:186-195: compute_signals + zscore_causal). The test asserts `compared > 1000`.
- Per signal: `test_bars_not_closed_by_t_do_not_move_values` (test_ml_v2_signals.py:156-165), with cuts at 55% and 80% of decision
  times and 20% of late bars dropped (:99-108), and `test_perturbation_is_not_vacuous` (:168).
- **Prediction level: no test found.** grep "perturb" in tests/test_ml_v2_*.py finds only the leakage and signals files, and both work at
  feature level. Nothing perturbs bars and then refits or predicts. UNKNOWN whether a prediction-level check exists elsewhere.
- E.20, config-only? Partly. `perturbation_check` accepts any features callable, so r_ROD and |r_ROD|/median can be passed as
  a callable. However its rows always come from `world_rows` (3 times) and `cuts_of_date` uses the same rows, so **t4 rows are not
  covered by calling the helper as is**. A new test can do this by composition with `perturb_after` + `context` + its own rows that
  include t4. `_changed` (fixtures:96) is private but importable. Editing `world_rows` or `perturbation_check` would be an edit to the
  hashed tests/ml_v2_fixtures.py. A 17-root world is a `roots` argument: all 17 vehicles (NG MNQ ZN 6E MGC ZC ZT ZF ZB UB TN MCL ZL
  ZS M2K HE LE) are keys of `constants.UNIVERSE` (constants.py:22-33).

### 1c. Fold test (purge and embargo)
- Code: `split_masks(split, trade_date, decision_ts_ns, exit_ts_ns) -> (train, test)` (cpcv.py:269), `assert_fold(split, trade_date, decision_ts_ns, exit_ts_ns, train, test) -> None` (cpcv.py:285),
  `outer_splits(blocks, n_test_blocks=N_TEST_BLOCKS, embargo=EMBARGO_DATES)` (:175), `inner_splits(outer, blocks, embargo=EMBARGO_DATES)` (:203),
  `calendar_blocks(dates, n_blocks=N_BLOCKS)` (:153). Constants: N_BLOCKS 6, N_TEST_BLOCKS 2, EMBARGO_DATES 1 (constants.py:128-130).
- Tests in test_ml_v2_cpcv.py: `test_outer_splits_test_embargo_and_train_dates` (:144), `test_inner_splits_stay_inside_the_outer_training_dates` (:175),
  `test_planted_inner_fold_reading_an_outer_test_date_is_caught` (:189), `test_purge_removes_a_label_overlapping_the_test_fold` (:212),
  `test_purge_is_on_timestamps_not_dates` (:234), `test_row_level_isolation_guard_catches_an_overlapping_inner_label` (:340, uses
  `cpcv._assert_rows_isolated`), `test_planted_inner_split_leak_makes_nested_cpcv_raise` (:324).
- World: synthetic date lists `_dates(n)` (:129) and `make_panel(n_dates=120, roots=("AA","BB"), n_signals=3, *, seed, edge, sigma, cost, first)` (:51).
  `make_panel` hard-codes 3 decisions per (root, date) (:57-61).
- E.20: these guards act on (trade_date, decision_ts, exit_ts) arrays and are independent of root count and t_index. They run inside
  `nested_cpcv` on any panel. They are config-only in the sense that the frozen code checks a t4 panel as it is. Rerunning the
  `make_panel` tests with 4 times would need a new fixture (the existing one is hashed).

### 1d. Window test (no date >= 2024-03-01 in any fit or normalization)
- Code: `assert_window(panel_or_rows, mode="train")` (panel.py:53), with `FORBIDDEN_FROM = date(2024, 3, 1)` (constants.py:17). It is called in
  build_panel (:112, :131) and build_world_panel (pipeline.py:296).
- Tests: `test_window_guard_refuses_a_planted_row_on_or_after_2024_03_01` (test_ml_v2_leakage.py:578, on `g0_panel(None)`),
  `test_pipeline_refuses_a_world_that_reaches_2024_03_01` (:587, world `("MNQ",)` 2024-02-20..2024-03-05, warmup_dates=5),
  and `test_window_guard_refuses_a_planted_date` (test_ml_v2_panel.py:100).
- E.20: the E.20 range ends at 2024-02-29, so the guard applies unchanged. Config-only: call `assert_window` on the composed panel.

### 1e. Normalization test
- Code: `zscore_causal(raw, rows, cols, *, window_dates=Z_WINDOW_DATES, min_dates=Z_MIN_DATES, clip=Z_CLIP)` (normalize.py:79). Z_WINDOW_DATES 250, Z_MIN_DATES 60 (constants.py:65-66).
- Tests: `test_peeking_normalizers_are_caught_and_zscore_causal_is_not` (test_ml_v2_leakage.py:327-345). It runs on `raw_rows()`
  (2 roots, 90 business dates, t_index 1..3), window 40, min 10. The later-dates check is :332-338. The same-date check (moves t3 rows,
  checks t1 rows) is :340-345. test_ml_v2_normalize.py has 9 tests, including `test_rows_before_a_date_do_not_see_later_changes` (:24)
  and `test_same_date_rows_do_not_use_each_other` (:38). Its `_frame(n_dates=120, per_day=3, roots=("ZN","6E"))` (:12) is
  parametrizable per_day.
- E.20: `normalizer_check` and `zscore_causal` take any rows/raw. A t4 or new-feature version is composition. `raw_rows` itself
  pins 3 times.
- Not established: the "|r_ROD| over its median of the previous 60 trade dates" feature is its own normaliser. No existing test
  covers a 60-date median ratio. The nearest is `_base_ratio` (generic.py:167, 20 dates, per t_index, `.shift(1)`).

### 1f. Model hash chain
- Code: `FittedModel.sha256` is the sha256 of the payload, and `predict` re-hashes it and raises on a mismatch (models.py:14-15, `fit_model(spec, X, y, *, seed=SEED)` :125,
  `predict(model, X)` :141). Nested CPCV records `selected_sha256` per outer split (cpcv.py:641, :687). The pipeline refit must
  match that record or raise `PipelineError` (pipeline.py:456-467).
- Tests: `test_ridge_payload_layout_and_determinism` (test_ml_v2_models.py:47), `test_lgbm_is_deterministic_and_learns_a_planted_signal` (:67),
  `test_predict_rejects_tampered_payload_and_wrong_width` (:80), `test_nested_cpcv_is_deterministic` (test_ml_v2_cpcv.py:281, compares selected_sha256),
  `test_determinism_two_runs_identical_models_and_daily_pnl` (test_ml_v2_e2e.py:93).
- No test found that plants a refit-sha mismatch to trigger pipeline.py:466.
- E.20: the checks are data-agnostic. A 17-root t4 run inherits them through `nested_cpcv`.

### 1g. Planted canaries (all in tests/test_ml_v2_leakage.py)

| canary | test function(s) | line | world / fixture |
|---|---|---|---|
| future bar | `test_future_bar_with_its_true_timestamp_fails_assert_causal`; `test_future_bar_stamped_at_t_fails_the_perturbation_test`; `test_future_leaking_column_fails_the_perturbation_test` | 209; 220; 227 | pert_world; test signals `future_bar_signal` (:131), `leak_column_signal` (:147, reads MNQ/NQ `leak_fwd`) |
| future release | `test_future_release_with_its_true_timestamp_fails_assert_causal`; `test_future_release_stamped_at_t_fails_the_perturbation_test` | 248; 259 | pert_world; `future_release_signal` (:160); cut from `_release_cut` (:235, an MGC row) |
| cross-date target shuffle | `test_shuffled_target_fails_gate0_and_has_no_nested_edge` (asserts control t >= 3.0, shuffled \|t\| < 2.0, Gate 0 fails); documentation test `test_within_date_shuffle_is_not_a_null_here_finding` | 298; 310 | `g0_panel(STRONG_EDGE_C=10)`: G0_VEHICLES ("MNQ","MGC","MCL"), 2021-01-04..2022-02-28, seed SEED+1 (:65-66, :80-93); `shuffle_targets` (:267); `_nested_median_t` runs `nested_cpcv` on SHUFFLE_CONFIGS ("ridge_l0.1_k1.5_h60","ridge_l1_k1.5_h60") (:71, :288) |
| peeking normalizer | `test_peeking_normalizers_are_caught_and_zscore_causal_is_not` | 327 | `raw_rows()` |
| selection sees test block | `test_score_fn_returning_test_block_pnl_is_refused`; `test_score_fn_counting_rows_it_was_not_given_is_refused`; `test_inner_fold_handed_an_outer_test_block_is_refused` (monkeypatches `cpcv.inner_splits`) | 354; 366; 379 | `_small_cpcv_inputs()` (:348): g0_panel(10) + config ridge_l0.1_k1.5_h60. Also test_ml_v2_cpcv.py:351 `test_a_score_fn_that_reads_the_test_block_is_detected` |
| label overlapping test fold | `test_purge_removes_a_training_label_that_crosses_into_a_test_date` | 395 | 12 business dates from 2021-06-01, split with test_blocks (2,3), hand row table |
| product shifted by one minute | `test_shifted_product_leaks_into_features_and_the_perturbation_test_catches_it`; `test_shifted_product_fails_the_session_grid_guard_and_the_pipeline_refuses`; control `test_control_unshifted_bars_pass_the_session_grid_guard` | 429; 436; 444 | `shifted_world()` (:419): ("MNQ",), plant shift NQ -1 min; features `mnq_features` (:424, g01-g04); guard `assert_bars_on_session_grid(bars)` (pipeline.py:237) |
| Gate 0 (a) pure noise | `test_gate0_a_pure_noise_fails` | 451 | g0_panel(None); asserts `n_tests > 3 * len(REGISTRY)` |
| Gate 0 (b) planted gross edge | `test_gate0_b_planted_gross_edge_passes_and_the_cost_gate_trades_it` | 479 | g0_panel(10); `run_gate0` (:96); asserts > 100 trades at k = 1.5 |
| Gate 0 (c)/(d) sub-hurdle | (c) `test_gate0_c_binary_edge_between_bars_passes_gate0` :490, `..._rejected_at_every_k_under_the_net_reading` :508, `..._traded_by_the_k15_gate_under_the_gross_reading` :518, strict xfail :534; (d) `test_gate0_d_sub_cost_edge_fails_gate0_and_the_cost_gate_rejects_it` :542, `..._under_net` :557, strict xfail `..._under_gross` :571 | 490-576 | g0_panel(MID 2.0 or SUB 0.5, LOW_SIGMA_C 3.0); `_oracle_rhat` (:473) uses `nominal_cost_ticks` and `z_g02_ret60` |

Changes needed to rerun each on a 17-root, t4, new-feature universe without editing a hashed file:
- Universe: every world above is built through `world(roots, ...)`, so the vehicles tuple is an argument (config). Hard-wired
  roots inside test bodies: `leak_column_signal` reads only MNQ/NQ (:151-152), `_release_cut` picks MGC (:242), `shifted_world`
  and `mnq_features` use MNQ/NQ, and the plant `roots` are NQ. All of these are among the 17 roots.
- t4: every canary that goes through `world_rows`, `cuts_of_date`, `build_world_panel` or `run_pipeline` gets rows only from
  `clock.decision_rows`, which has 3 times (clock.py:70-80, constants.py:43). Covering t4 needs a new row builder in pattern_search
  plus re-composition of `build_world_panel`'s steps (pipeline.py:279-299: SignalContext, build_targets, build_panel, calendar cut,
  assert_window). Editing clock.py, constants.py, pipeline.py or the fixtures needs a v2 amendment. The synthetic sign plant
  (synthetic.py:282) also stays on t1..t3, so a planted-edge canary at t4 is not available without editing synthetic.py.
- New features: they are not in `REGISTRY`, so `compute_signals`, `build_panel`, `registry_features` and `mnq_features` cannot carry them. Two
  composition routes exist: callables passed to `perturbation_check`/`assert_causal`, and a `dataclasses.replace(panel, frame=..., feature_cols=...)` panel
  for `nested_cpcv`/`horizon_data`. Adding a SignalSpec to REGISTRY is an edit to the hashed signals/__init__.py or a family module.
- Gate 0 canaries: Gate 0 is waived in E.20. The canaries call `gate0_family_a/b`, `gate0_verdict` and `cost_gate` directly and still run on a
  composed panel. `nominal_cost_ticks` averages over the 3 pinned times, so it does not see t4.

## Q2. Suite duration and slow tests (from logs, by grep)
- Whole ml_v2 suite at the E.12 freeze: 795 passed, 2 xfailed in 270.92 s (08:48:08-08:52:39 PDT, 2026-10-03,
  reports/stage_e12_briefs/pytest_mlv2_prefreeze.{start,out}). The final run took 272.64 s: 803 passed, 2 xfailed
  (pytest_mlv2_final, 09:20:47-09:25:20). reports/stage_e12_STATE.md:71 gives the same 08:48-08:52.
- E.11: 546 passed, 2 xfailed in 173.36 s (reports/stage_e11_briefs/t5_pytest_all.out:9); 683 passed in 217.85 s (designfix_pytest.out:11).
- Leakage file alone (E.11): 23 passed, 1 xfailed in 58.34 s (t5_pytest_leakage.out:15). Slowest: shuffled-target 20.08 s, library
  perturbation control 10.73 s, Gate 0 (c) 5.27 s, (d) 5.23 s, (a) 4.75 s, future bar 2.61 s, leak column 2.60 s, unshifted control 2.03 s.
  The file now has 27 tests; it was not re-timed after E.11 (UNKNOWN).
- e2e file (E.11): 9 passed, 1 xfailed in 96.51 s. The module fixture `runs` takes 82.83 s (setup of test_run_completes_with_timing_records).
  `test_gate0_failure_stops_the_pipeline_and_force_continues` takes 7.88 s (t5_pytest_e2e.out).
- E.12 review subset (phase1_*, k9, gate0, decide, portfolio): 141 passed in 31.8 s (reports/stage_e12_review.md:8).
- No `slow` marker exists in tests/test_ml_v2_*.py (only parametrize and two strict xfails, leakage :530, :566).
- E.20's own start run (reports/stage_e20_briefs/pytest_start.out) was still in progress when read and has no duration line yet.

## Q3. Tests that pin 3 decision times or the 28-product universe
3 decision times:
- test_ml_v2_clock.py:24-30 `test_rule_reproduces_the_pinned_table` / `test_whole_table_pinned`: rule == DECISION_TIMES_CT (3-tuples, constants.py:49-59).
- test_ml_v2_clock.py:53-68 `test_rows_schema_sort_and_times`: `len(rows) == 3 * len(roots)`, with roots = all 28 (:58), and per-root times == the table.
- test_ml_v2_clock.py:103-107 `test_flatten_is_after_every_horizon`: t_index == 3 rows have F - t >= 120 min.
- test_ml_v2_panel.py:73 `test_rows_kept_are_complete_and_causal`: `set(z_g11_t_index) <= {1.0, 2.0, 3.0}`.
- test_ml_v2_targets.py:121 (`i = len(rows) - 1  # t3`), test_ml_v2_signals.py:313-315 `_row` (selects by t_index k).
- Fixtures that build 3 times: tests/ml_v2_fixtures.py:188 `raw_rows`, test_ml_v2_cpcv.py:57-61 `make_panel`, test_ml_v2_normalize.py:12 `_frame(per_day=3)` (a parameter).
- Code pins (not tests): constants N_DECISION_TIMES = 3 (:43), MAX_ENTRIES_PER_PRODUCT_DAY = 3 (:47), clock.decision_times_from (:70-80).
28 products:
- test_ml_v2_probe.py:21-22 `test_products_are_28_or_the_8_standin`: `probe.products_of(28) == tuple(UNIVERSE)`; :34 parses `--products 28`.
- test_ml_v2_clock.py:42-44 `test_every_vehicle_has_a_session_group` (over all UNIVERSE), :53 and :103 iterate `tuple(UNIVERSE)`.
- test_ml_v2_panel.py:52 and :74: the panel layout pins one `id_root_<v>` column for every UNIVERSE vehicle (28). This follows from
  `panel._identifiers` (panel.py:99-104), so on a 17-root panel 11 id_root columns are all zero.
- test_ml_v2_signals.py:49-53 (world over all of UNIVERSE), :207 (`len(vs) == len(UNIVERSE)`), :422 `test_pooled_ports_cover_all_21_families_and_every_product`.
These pins act on the frozen modules' own behaviour. A pattern_search layer that composes rows or panels outside clock.py/panel.py
does not trip them. Changing the frozen clock or universe would trip them and edit hashed files.
