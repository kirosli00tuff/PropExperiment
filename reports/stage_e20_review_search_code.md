# Stage E.20 Step 6b: independent review of pattern_search/ (SearchReviewer-FableXHigh)

Brief: reports/stage_e20_briefs/brief_search_review.md. Reviewed against reports/stage_e20_plan.md
(441 lines, mtime 2026-10-11 17:13:11 PDT, sha256 be6702e5644de2ab59423b598ada2b5ce6ac69c8e1080d5cfb88f86fc246595e;
the plan was still being edited while this review ran: an earlier read in the same session saw a
430-line file) and reports/stage_e20_rulings.md sections 4, 4b and 5. Build record:
reports/stage_e20_briefs/search_build.md; dry check: reports/stage_e20_dry_check_step6.md.
Synthetic data only; no store, GEX file or stage result opened; nothing under pattern_search/,
tests/ or any frozen directory edited; no ledger write; nothing registered or run with
`python -m pattern_search run`. Review written 2026-10-11, about 17:20-17:50 PDT.

## Verdict

**APPROVE WITH FIXES.** 0 BLOCKING, 1 SHOULD FIX (SC-1, a run-discipline gap: the real loader
path is first exercised only after the registration, contrary to rulings section 5 item 7), 8 NOTE.
No leakage was found in the composition path; the gating computations (admissibility, nested CPCV
arguments, the screen's three numbers, the final-selection condition, the explicit N = 528) match
the plan; no hashed file is edited and no frozen attribute is modified in the search path; the
registry check precedes every bar read and every fit. The existing suite passes (111 passed in
99.6 s, rerun by the reviewer) and a reviewer-written perturbation extension at all four decision
times found no leak.

## Method

Read by module (constants, guard, rows, features, panel, search, oos, run, preflight, stages,
results, world, freeze_manifest, backward by section, dry_check by def map), with the frozen call
targets opened by signature or body only: ml_route_v2.panel.Panel and build_panel,
normalize.zscore_causal, signals.assert_causal and _core.result, clock.ROW_COLUMNS,
targets.build_targets (the `nominal <= flat` rule, y_gross), pipeline.build_world_panel / _filter /
score_fn_for / split_risk_fn / record_figures / _stats / assemble_record, cpcv.nested_cpcv /
final_selection / _prepare / _compute_units / _fit_and_score / _guarded_score / split_masks /
split_risk / _config_daily / _path_series, cost_filter (inputs), configs.ConfigLedger,
portfolio.fixed_d_daily_pnl, screening.trial_registry.require_registered and FIELDS,
phase1.world.RootStart / load_root / _root_record / frozen_start_agreement, data.stage_e_bars and
data.step2_store path builders, rules.sessions' module globals. Tests read: leakage and run in
full, the others by test name against the build record's table. The suite
`tests/test_pattern_search*.py` was rerun to a scratch log (111 passed, 99.6 s). Two scratch
probes (session scratchpad, not under tests/): manifest coverage of lazily imported ml_route_v2
modules; a perturbation extension (below).

## 1. Composition and hashed files (brief item 3)

- `git diff --stat` over ml_route_v2, screening, rules, sim, data, base_rules, c1_replication,
  h6_rod, strategy, signals and tests/ is empty; `git status --porcelain` on those directories
  lists nothing untracked. No frozen file is edited.
- grep for `setattr`, `monkeypatch`, `.patch(`, `__dict__[`, `importlib.reload`, `sys.modules[`
  across pattern_search/: the only runtime attribute writes are backward.py:466 and :472 (the B1
  swap context `backward_context`, setattr with restore in a finally block; plan 10.1 sanctions
  setattr "as C1 did"). dry_check.py has none of its own. The search path (run.py -> world,
  panel, search, oos) never imports backward and never enters the swap context (section 5).
- The composed builder (panel.build_search_panel:49-77) is pipeline.build_world_panel
  (pipeline.py:269-299) step for step: assert_bars_on_session_grid, decision_rows with
  own_blackout (rows.frozen_rows), SignalContext with sigma_d, build_targets, build_panel with
  `signals=` the KEPT tuple, the calendar cut with the same two counts, assert_window("train"),
  the empty-panel refusal. Added, in order: guard.check_frames after the grid check, attach_rod
  between build_panel and the calendar cut, check_panel at the end. Nothing frozen is skipped.
- build_panel's own avail_max <= decision_ts_ns check (panel.py:126 of ml_route_v2) still runs on
  the 34 KEPT signals; attach_rod repeats it on the union (features.py:157) and check_panel a
  third time (pattern_search/panel.py:110).
- The CPCV input fingerprint is not bypassed: search.run_nested / run_final call the frozen
  nested_cpcv / final_selection, whose _prepare (cpcv.py:528-549) registers the configs in the
  ConfigLedger before the first fit and pins the JsonlStore to input_fingerprint(panel.frame,
  extra) with the constants fingerprint (C-01). The state-dir ledger is the frozen ConfigLedger
  at state_dir/ledger.jsonl (search.ledger:69-72).

## 2. Leakage through the composition path (brief item 1)

Checked and clean:
- t4 rows (rows.py:50-70): decision_ts_ns = flatten_ts_ns - 60 min on the frozen clock's kept
  dates; the CT minute is asserted equal to rules.sessions' regular F minus 60 for every group
  (so an early-close date, which the frozen clock already excludes, cannot slip in), and t4 is
  asserted later than the date's t3. Identifier columns are copied from the date's first frozen
  row (ROW_COLUMNS = root, path_root, cluster, group, trade_date, t_index, decision_ts_ns,
  flatten_ts_ns). Sort and dtypes restored (with_t4:73-83).
- h120 on t4: build_targets' own rule (targets.py:206 `nominal <= flat`) makes t4 + 120 > F
  unavailable; check_panel refuses any t4 row with ok_h120 True (panel.py:104). h60 on t4 exits at
  the bar opening at F (nominal == flat passes `<=`), the same bar as hF, as plan 4 says
  (tests/test_pattern_search_rows.py:97).
- rod_ret (features.py:45-71): P(t) is close[own["it"]] (the bar closing at t, the G1-G4
  convention), P(prior C) is close[c1_idx of the previous group trade date] (the bar opening at
  C-1, closing at C, on d-1); avail = max(ts) + 1 min = t (asserted by assert_causal in
  rod_frame:113). Not applicable when d-1 is an early-halt date (halt_flags on the group
  calendar); missing (row dropped) when either bar or the previous date is absent. The frozen
  _core.result sets avail = t where not applicable and -1 where missing, and assert_causal flags
  present-and-late or present-and-negative, so the conventions match.
- rod_absratio (features.py:74-98): per (vehicle, t_index), the eligible rows sorted by date,
  rolling median of |rod_ret| over 60 with min_periods 60, then shift(1): the median is over the
  60 most recent eligible earlier dates, strictly before d (one row per date per t_index is
  asserted, so shift(1) cannot reach the same date). Warm-up -> NaN with app True -> dropped as
  missing; zero median -> not applicable; not applicable when rod_ret is not. avail = t.
- Normalization: rod_z masks non-applicable values to NaN and calls the frozen zscore_causal
  (250 / 60 / clip 5) over all ctx.rows per root (features.py:117-126), exactly as build_panel
  does for the KEPT signals (ml_route_v2/panel.py:76, before its row drop). normalize.py's
  docstring (lines 4-9): the window is the product's trailing 250 row dates strictly before d and
  "Same-date rows never use each other", so pooling t4 into the per-vehicle windows (plan 6) adds
  no same-day look-ahead.
- attach_rod's three rules (features.py:134-168): not applicable -> z 0, flag 0; applicable and
  missing, or applicable with no z statistic -> row dropped (counted); avail_max is the maximum of
  the panel's and the applicable rod avails and is asserted <= decision_ts_ns on every kept row.
- Risk table: the whole-panel table from pipeline._filter (plan 8's one pass) is passed only as
  score_fn_for's partial default. cpcv._guarded_score (cpcv.py:435-453) calls
  `score_fn(rows, r_hat, config, risk=risk.copy())` whenever a split risk is given, and a call-time
  kwarg overrides a functools.partial default, so every CPCV score (inner, outer, final-selection
  outer) uses the split's own training-row table from split_risk_fn (cpcv.py:552-598; the thunk
  is risk_fn on data.rows[train]). _cpcv_kwargs always passes risk_fn (search.py:75-83).
  oos.Refits.fit (oos.py:96-97) builds the same per-split table from the split's training rows.
  The cost filter and risk table read y_gross's sd and quantile and the cost columns only
  (cost_filter.py:6-10, 49-56): volatility, cost and loss size, never a sign or a fit.
- Purge and embargo: oos.Refits.fit uses cpcv.split_masks (frozen) and refuses any refit whose
  model sha256 differs from the CPCV record (oos.py:90-94); nothing re-implements the masks.
  Fits are keyed (model_id, horizon, split) as _groups shares them across k.
- Admissibility (search.admissibility:59-66): one call of the frozen pipeline._filter on the
  whole panel; an empty set raises EmptyAdmissible, which run._filter_stage turns into a failed
  screen (run.py:156-162, 194-195, 247-250). The frozen `adm or None` path (no filter) is never
  reached; horizon_data gets None only when the set is empty, and then no stage past filter runs.
- 2024-03-01: guard.check_bars (ts_event >= 2024-03-01 00:00 UTC, stricter than the frozen 00:00
  CT; trade_date >= 2024-03-01 as strings) runs after every load_root (world.py:146) and again on
  the whole world in build_search_panel (panel.py:59); world.search_calendar refuses a calendar
  reaching 2024-03-01 (world.py:165). The frozen refuse_late runs inside load_root as well.
- Reported items that re-score trades (oos.py) are self-verifying: each split's replicated daily
  must equal score_split's within $1e-6 (_check_same), the assembled 1.0 x record must equal
  nested.path_daily, and the final configuration's 15-split P&L must equal 5 x config_daily.
  fixed_d_daily_pnl (portfolio.py:336-373) sums pre-sized trades (the `contracts` column), so the
  t4-subset P&L is a true subset sum, not a re-sizing.
- Test coverage (tests/test_pattern_search_leakage.py): the perturbation test moves bars after
  cuts at t1, t2 and every group's t4 (14:08, 12:18, 12:03 CT) and compares all 36 raw/app/z
  columns on more than 5,000 rows; two planted variants (a bar 59 min after t; a centered 61-row
  median) are shown to fail it; the frozen fold test runs on hF with t4 rows and catches a planted
  exit overlap; a t4 planted-edge canary (plant on a copy of the bars) is found and attributed to
  t4; the cross-date target shuffle and the unplanted world show |median t| < 2.
- Reviewer's extension (scratchpad probe_perturb_all_t.py, synthetic world_small, seed 777+i): 24
  cuts at t1, t2, t3 and t4 of every group on two dates; 226,390 row comparisons over the 105
  raw/app/z columns of feature_frame (all 34 KEPT and both rod features): no column at or before
  a cut moved with bars after it.

## 3. Faithfulness to the plan (brief item 2)

- The 34 KEPT names (constants.KEPT_SIGNALS) equal plan 5.1's list name for name and in order;
  N_KEPT 34; the two rod features appended; ACCEPTED_PART_A empty (plan 5.3). build_search_panel
  passes `signals=tuple(K.KEPT_SIGNALS)` and check_panel refuses any other signal_names or
  feature_cols (panel.py:95-98).
- 45 configurations: constants.config_ids zips E20S-01..E20S-45 with configs.CONFIGS in order and
  refuses a grid of another length; search.frozen_configs likewise; label E20S; the registry
  regexes accept them (preflight.registry_names_valid).
- nested_cpcv / final_selection arguments (search.py:75-103): (panel, the 45 CONFIGS,
  score_fn_for(risk), ledger=ConfigLedger(state_dir/ledger.jsonl), state_dir=state_dir/cpcv,
  admissible=tuple(pairs), calendar=tuple(training calendar), risk_fn=split_risk_fn(panel)); the
  frozen pipeline's own call (pipeline.py:577-590) uses the same names.
- Screen (search.screen:129-158): item 1 = median over the 5 paths of pipeline._daily_t (mean /
  (sd ddof 1 / sqrt n)) via record_figures, >= 2.0; item 2 = cpcv.pbo_cscv(config_daily) with the
  frozen PBO_BLOCKS = 16, < 0.5, with raise / degenerate / NaN all counted as not < 0.5
  (pbo_record:114-126, PR-11); item 3 = _sharpe_daily(path_daily.mean(axis=1)) x sqrt(252) in
  [0.5, 4.0], above 4.0 fails and sets leakage_alarm (PR-3); the final-selection condition. Pass
  iff all four. path_daily is the frozen nested record with zeros on dates without a daily
  (cpcv._path_series:621-628), over the training calendar's block dates.
- DSR reported with N_total = 528 passed explicitly (search.dsr_record; run.assemble:255),
  sharpe_variance over the finite config_sharpes (the population-sd daily Sharpes of
  config_daily, as pipeline._stats); preflight.check_registered refuses a registry line whose
  (n_before, n_after) is not (483, 528) (preflight.py:172-176), so the explicit N cannot disagree
  with the registry.
- Reported items present: per-configuration table (search.config_table), the final
  configuration's own CPCV OOS t and Sharpe two ways (final_own_record), per-product round trips
  per path with the median-path reading the lead chose in rulings 5.1 plus the other two
  (oos.round_trip_table), the 1.5 x slippage re-pricing with the 1.0 x identity check
  (oos.nested_record), the t4 share and the r_ROD share with both P&L figures (oos.final_record;
  rod z columns zeroed at prediction, no refit, app columns untouched, as plan 9 words it), the
  ruin status text (run.RUIN_FAILED / RUIN_PASSED, PR-6).

## 4. Guard and run discipline (brief item 4)

- Primary path check (guard.check_store_path): only the 17 real step 2 paths are allowed,
  whatever step2_root is passed; the loader (data.stage_e_bars._step2_parquet_path) and the guard
  (data.step2_store.step2_parquet_path) build the same path. Refusal names the class
  (processed_hist, sealed/holdout from data.holdout and data.step2_seal, processed, other). The
  audit hook repeats it for Python-level opens; the CLI installs it first (run.main:303).
  backward_permitted() is False: no process can open processed_hist in Step 6 code.
- Planted cases (tests/test_pattern_search_guard.py, 28 tests): processed_hist before and after a
  registration and with a marker, sealed, both holdout blobs and parquets, MES research and step 2
  paths, a research store, another root's store, vendor, a symlink, a path outside every store
  root, the audit hook in a subprocess, 2024-03-01 bars by trade_date and by UTC open, the loader
  wrapper refusing before the frozen loader runs, guarded hashing, every module imports the guard
  first. Matches plan 3's list.
- Registry before any fit: run.run_search (run.py:287-298) calls check(), then _registered()
  (require_registered on the real REGISTRY_PATH unless test_mode, exact id list, label E20S, the
  given freeze sha256, N 483 -> 528), and only then builds the stages; the panel stage
  (hooks.world) is the first stage. tests/test_pattern_search_run.py:168-179 plants a world hook
  that raises if called before the registry check and shows no stage directory is created.
  check() itself hashes the 17 stores as bytes behind the guard (no decode), reads the S_X record
  and E.17 manifest, the release calendar and the training calendar: no bar.
- Freeze manifest check (preflight.check_freeze): its own sha256 from the command line, every
  listed file present with size and sha256 (through guarded_sha256, so no forbidden path is ever
  hashed), every required file listed (plan, pattern_search/*.py, the tests and helper, the
  inputs, the data/calendars modules, every ml_route_v2 module imported at check time, the 17
  stores). The manifest is written once with O_EXCL.
- Resumability: cpcv_units.jsonl per (config, split) by the frozen store; pattern_search.stages
  pickles each stage (panel, filter, cpcv, final, oos) under a pin of (constants fingerprint,
  freeze sha256, world source) and refuses a file written under another pin; the probe used
  another state directory and pin.
- State and reports directories: ~/.cache/propexp_e20_search and reports/stage_e20_search/,
  reports/stage_e20_search.json and .md (constants.py:96-99), never E.12's.

## 5. The backward swap context (plan 10.1)

B1-only code, not in the search path; read for whether it can touch the search and for plan
faithfulness. It gets its own review at Step 8 (B1 prereg and freeze).
- PATCHES (backward.py:100-120) cover S1 (data.group_session.load_group_calendar,
  ml_route.inputs._group_calendar), S2 (rules.sessions._DEFAULT, _DEFAULT_LATE), S3
  (TOPSTEP_HOLIDAYS, TOPSTEP_EARLY_CLOSE_LEAD), S4 (EQUITY_FULL_SESSIONS), S5
  (TREASURY_AUCTIONS), S6 (monthend.EVENT_DATES), S7 (eiafade.make_mcl), S8 (ngpre.make_ng), S9
  (ENERGY_FULL_SESSIONS in k4._calendar and k4.ovr with _FULL_SESSIONS and _FULL_ORDINALS), S10
  (the metals equivalents). S11 is the release-calendar argument (backward_release_rules,
  apply_fallback_costs), S12 needs no swap. The swap table's rows S1-S12 are all accounted for.
- rules.sessions._DEFAULT and _DEFAULT_LATE are lazily filled module globals returned by
  default_holidays() / default_late_opens() (rules/sessions.py:265-276), so setattr reaches every
  reader; `_CLOSED` is a None sentinel, not a cache. lru caches in 27 modules (CACHE_MODULES) are
  cleared before the swap, after it and on exit (clear_caches).
- backward_context (backward.py:450-475): lock, no nesting, restore in reverse order inside
  finally, caches cleared on exit; tests cover swap-and-restore, restore on exception, refusal of
  nesting, the frozen clock forming 2010-2019 rows for every group inside the context, member
  tables being the hist ones inside and the frozen ones outside.
- Sources are read by pinned sha256 (SOURCES, read_source:149-161): the seven hist2010 calendars,
  E.14 releases and energy full sessions, EC-AUC 2010-2019, the frozen E.2b calendar. None is a
  bar store. The dry check builds synthetic sentinel bars; it never opens a parquet.
- Rulings: 2 (late_always_applicable_mask:579-596), 3 (session_end_exits:599-673: the last bar's
  close, exit_ts_ns = that bar's close, y = (close - entry) x per_unit consistent with the frozen
  (exit open - entry open) x per_unit, the event flag at that bar), 4 (fallback_hits,
  apply_fallback_costs: cost columns only, before 2019-05-01, [m, m + 30)), 5 and 6
  (b1_exclusions), 7 (reopening_record). See SC-8 for the ordering dependency between rulings 3
  and 4.

## 6. Timing probe (brief item 5)

search_build.md section 5: synthetic 17-vehicle world at the real window, 45 configurations, 4
decision times, 621 s; panel 15 s at 2.1 GB peak RSS (66,632 rows, 94 feature columns), cpcv 568
s at 1.0 GB (3,375 units, 1,125 fits), oos 35 s at 1.5 GB. Plausibility: E.12's 28-root real
panel took 266 s at 2.9 GB; here 17 bar frames and 17 x 4 = 68 (root, decision time) units
against 28 x 3 = 84, so a real panel of about 3-5 min and 2.5-3.5 GB is consistent. The CPCV cost
scales with rows x fits; the synthetic row count (warm-up 0) is of the real panel's order, so the
15-30 min total guess is reasonable, with the upside risk the coder names (more candidates per
validation set on real data). Memory: 10.6 GB available at the probe, peak 2.1 GB, one heavy job
at nice 10, LightGBM at the frozen 8 threads (within half of 20 logical CPUs): inside CLAUDE.md's
limits. Stage pickles (the panel about 60 MB) are small. The real run should stay out of the
AiTrader window (15:30-16:00 PT on weekdays) if it spans it.

## 7. Open items the reviewer could not check

- world.real_world and run.check's store hashing against real stores (forbidden here; the build
  record says the same). See SC-1.
- Determinism of the LightGBM refit sha256 on real data (oos.Refits refuses a mismatch; the
  synthetic probe reproduced all records).
- The swap table's S4-S10 derivations against their generator scripts line by line (the tests
  and the dry check show equality with the frozen tables on the 2019-05 overlap; accepted on
  that evidence; B1's own review covers it).

## Findings

| Id | Severity | Where | Finding |
|---|---|---|---|
| SC-1 | SHOULD FIX | run.py:116-130 (check), :139-153 (_panel_stage), :287-298; world.py:170-198 | **The real loader path is first exercised only after the registration.** `check` hashes the 17 stores as bytes, reads the S_X record and the E.17 manifest, the release calendar and the training calendar, but never calls world.real_world. The frozen phase1.world.load_root with the composed RootStart (positional fields verified: root, s_x, v_ref None, STEP2_STORE, path, sha256, research None, None, entry, ()), _summary_degraded (requires reports/step2/bars_<ROOT>.json's `parquet.sha256` to equal the store's), refuse_late, compact_bars, signal_coverage(unavailable=MES) and the 17-vehicle training_calendar all run for the first time inside `run`, which refuses until the E20S line exists. Rulings section 5 item 7 says "real_world and the store hashing run for the first time at the real check; any failure there is a pre-registration failure"; as built, a real_world failure is a post-registration failure. Why it matters: pattern_search/*.py is hashed in the freeze manifest the registration cites, so a code fix after registration changes the manifest and invalidates the registration's sha256 (a new line or a documented amendment). Fix (lead decision): (a) if the plan's PR-13 wording ("no filter statistic, fit or score exists before the registry line"; plan 15 "then the real panel") permits reading search-window bars before registration, add a world-only step to `check` (real_world called and discarded: no rows, no signals, no panel, no statistic); or (b) keep the code and, before registering, hand-check the two inputs the loader will compare (each reports/step2/bars_<ROOT>.json `parquet.sha256` against the E.17 manifest's step 2 sha256; the S_X record's sha256 likewise, which check already does) and pre-declare in STATE what happens to the registration if real_world fails. Either way, correct rulings 5.7's statement. |
| SC-2 | NOTE | features.py:45-71; search_build.md section 2 choice 3 | rod_ret has no instrument_id check across a roll: when d-1 is the roll date (its own rows are excluded by the vehicle's blackout, d's are not), P(prior C) is the outgoing contract's close and P(t) the incoming one's. This is G5's frozen behaviour and plan 5.2 names G5's pattern, so it is plan-faithful; disclose it beside rod_ret in the result, as a property shared with g05_gap. |
| SC-3 | NOTE | guard.py:97-108 (refusal_reason), :133-149 (audit_decision) | refusal_reason returns None for a path under none of the forbidden prefixes (for example a parquet copied to /tmp), so the audit hook admits it. The primary check (check_store_path:116-125) refuses it (default REASON_OTHER) and tests/test_pattern_search_guard.py:83 covers that, so the gap is in the defense-in-depth layer only. Optional fix: have the hook refuse any `.parquet` / `.dbn*` open whose real path is not in the allowed set. |
| SC-4 | NOTE | tests/test_pattern_search_run.py:182-191; tests/test_pattern_search_search.py:102; tests/test_pattern_search_guard.py:193 | Three tests monkeypatch frozen ml_route_v2 or loader attributes in the test process (pipeline._filter, the PBO function, the frozen loader) to reach refusal paths. pytest restores them and no run-path code is affected, but the hashed test files then contain patches of frozen functions, which the project otherwise avoids (plan 14). Cleaner: inject through pattern_search's own seams (a filter callable on _filter_stage, a pbo callable on pbo_record, the Hooks dataclass). Not required before the registration. |
| SC-5 | NOTE | freeze_manifest.py:34-58 (V2_MODULES, loaded_v2_files) | At check time 36 of the 48 ml_route_v2 files are imported and listed; the 12 not listed (engine_stage, gate0, killswitch, payout_sim, phase1/__main__, _io, build, cli, gate0_stage, probe, signals/synthetic_bars, simulate) are all in the v2 freeze (91 files) that check verifies at its pinned sha256, and none is in the search path (reviewer probe). run._write records `v2_modules_loaded_at_write`, so the lead can confirm after the run that nothing outside the manifest's list was loaded. No fix needed; worth one line in STATE. |
| SC-6 | NOTE | reports/stage_e20_plan.md (mtime 17:13:11) vs search_build.md (17:12) and the dry check (17:10) | The plan was edited after the build record and the dry check were written (rulings 5 added section 9's criterion-6 reading and 10.1's additions). The freeze manifest must be built after the last plan edit; check then pins it. Process reminder only. |
| SC-7 | NOTE | oos.py:60-99 (Refits), :214-255 (final_record) | The reported items refit 15 outer models per selected configuration and the final configuration (fits shared across k). Each refit is checked against the CPCV record's sha256 and the daily against score_split, so a non-deterministic LightGBM refit on real data would stop the run at the oos stage with OOSCheckError rather than report a wrong figure. Acceptable (the screen itself is already computed and saved by then; `report` could not finish without the oos stage). If that happens, the lead decides whether the reported items are rebuilt from the CPCV record alone. |
| SC-8 | NOTE (B1) | backward.py:540-577 (apply_fallback_costs), :599-673 (session_end_exits) | The docstrings require session_end_exits to run before apply_fallback_costs (the latter re-prices from the adjusted exit_ts_ns), but no code enforces the order and no single B1 function calls both. For Step 8: one composed B1 targets post-step that applies ruling 3 then ruling 4, with a test of the combined effect on a grains t4 h60 row. Not in the search path. |
| SC-9 | NOTE | constants.py:87-89 | HARNESS_SHA256 (v12) and V2_FREEZE_SHA256 are literals; check refuses any other harness sha and verifies the v2 freeze at the literal. Correct for this stage; if the harness is re-frozen before the run, the constant (and so the manifest) changes. Recorded so the lead sees the dependency. |

## Numbers quoted in this review and their source

- 111 passed in 99.6 s: scratchpad/pytest_ps.log (reviewer's rerun, 2026-10-11).
- 24 cuts, 226,390 row comparisons, 105 columns, no leak: scratchpad/probe_perturb_all_t.py.
- 36 of 48 ml_route_v2 files loaded at check time; 12 missing, all in the 91-file v2 freeze:
  scratchpad/probe_manifest_cov.py.
- Probe timings and peaks: reports/stage_e20_briefs/search_build.md section 5 (not rerun).
