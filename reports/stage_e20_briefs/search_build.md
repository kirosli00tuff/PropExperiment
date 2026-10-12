# Stage E.20 Step 6 build record: pattern_search (SearchCoder-OpusXHigh)

Built 2026-10-11, 16:21-17:12 PDT, against reports/stage_e20_plan.md as revised (sections 6, 9, 13, KEPT = 34, section 10.1 filled, the 10.1 "Recheck additions"). Synthetic data only. No store, parquet, dbn, GEX file or E.12 Gate 0 / E.15 / E.17 / E.18 / H6 result was opened (the E.17 manifest and E.12's phase-1 report were read for S_X and the store sha256s, as the brief says). No existing file was edited, nothing was written to a ledger, no commit was made.

## 1. Plan clause to code

| Plan clause | Implemented by |
|---|---|
| 1 universe: 17 vehicles, paths, UNIVERSE check | constants.VEHICLE_PATHS; world.check_universe |
| 2 search window, recorded S_X (D4 rule not rerun), E.17 sha256s | world.recorded_starts (checks plan 2's values), world.manifest_store_sha256, world.store_records (E.12 = E.17) |
| 2 training calendar (union of group dates) | world.search_calendar (frozen synthetic.training_calendar) |
| 2 backward windows | backward.B1_FIRST, B1_LAST |
| 3 guard: path classes (processed_hist, sealed, holdout, processed, other roots' stores, vendor, raw) | guard.forbidden_prefixes, refusal_reason, check_store_path (only the 17 real step 2 files pass) |
| 3 bar bound 2024-03-01 after load | guard.check_bars / check_frames (00:00 UTC, stricter than phase 1's 00:00 CT) |
| 3 primary check on every loader path; audit hook for Python opens | world.load_search_root, preflight.check_stores, preflight.guarded_sha256; guard.install_audit_hook (CLI only) |
| 3 B1-only exception | guard.backward_permitted (False: not built in Step 6; every processed_hist path is refused) |
| 4 t1-t3 frozen, exclusions as frozen | rows.frozen_rows (clock.decision_rows + pipeline.own_blackout) |
| 4 t4 = F_X - 60 on kept dates, t_index 4, identifiers copied, h120 out by build_targets' rule | rows.t4_rows, with_t4, search_rows (t4 minute checked against REGULAR_FLATTEN_CT - 60, t4 > t3) |
| 5.1 the 34 KEPT names passed to build_panel exactly | constants.KEPT_SIGNALS; panel.build_search_panel; panel.check_panel |
| 5.2 rod_ret, rod_absratio, flags, z (250/60/5), build_panel's three rules, assert_causal | features._rod_ret, _rod_absratio, rod_frame, rod_z, attach_rod |
| 5.3 no Part A feature | constants.ACCEPTED_PART_A = () |
| 6 world: frozen loaders per root, release calendar, D8 costs, blackouts, MES never opened | world.real_world, load_search_root (phase1.world.load_root: sha256, L-3, holdout, embargo, store range, roll metadata, refuse_late, degraded-day record, closure_counts, compact_bars) |
| 6 frozen checks re-applied (PR-4) | panel.build_search_panel: assert_bars_on_session_grid, guard.check_frames, build_panel, attach_rod (three rules + assert_causal), calendar cut with counts, empty refusal, assert_window(train); check_panel |
| 6 real panel only after the registrations (PR-13) | run.run_search: registry check before the panel stage |
| 7 45 configs, E20S-nn = CONFIGS[nn-1], label E20S | constants.config_ids, CONFIG_IDS; search.frozen_configs; preflight.registry_names_valid |
| 8 c/sigma filter once, empty set refused | search.admissibility (EmptyAdmissible); run._filter_stage writes a failed screen |
| 8 ConfigLedger in the state dir, nested_cpcv and final_selection with frozen arguments | search.ledger, run_nested, run_final (score_fn_for(risk), split_risk_fn, admissible, training calendar) |
| 9 items 1-3 and the final-selection condition; PBO failure modes; Sharpe > 4 fails + alarm | search.screen, search.pbo_record |
| 9 DSR at N = 528 passed explicitly | search.dsr_record; preflight.check_registered refuses a registry line that is not 483 -> 528 |
| 9 per-configuration table; final config's own CPCV OOS t and Sharpe | search.config_table, search.final_own_record, oos.final_record["path_figures"] |
| 9 per-product round trips, under-30 flag; 1.5 x slippage | oos.nested_record, round_trip_table (1.0 x check against path_daily within $1e-6) |
| 9 t4 share and r_ROD share (rod z set to 0, no refit), both P&L figures | oos.final_record |
| 9 ruin probability not built; reason on fail, pending on pass | run.RUIN_FAILED, RUIN_PASSED |
| 10.1 S1-S10 swaps (rulings 1 and 7) | backward.backward_tables, hist_calendars, derive_* , backward_context, PATCHES, overlap_record |
| 10.1 S11 release rules and ruling 4 | backward.backward_release_rules (base_rules.costs.build_release_rules), touching_types, fallback_hits, apply_fallback_costs |
| 10.1 rulings 2, 3, 5, 6 (B1 only, unused by the search) | backward.late_always_applicable_mask, session_end_exits (PR-17 post-step), unsourced_release_exclusions, unsourced_calendar_exclusions, b1_exclusions |
| 10.1 / 13 sentinel dry check, row losses, PR-16, PR-18 | dry_check.feature_check, leg_check, row_loss_check, fallback_table, run_dry_check; report reports/stage_e20_dry_check_step6.md and .json |
| 11 freeze manifest (plan, package, tests, inputs) | freeze_manifest.build / verify / required_files (schema stage_e20_search_freeze/1) |
| run discipline: harness v12, v2 freeze, manifest sha, stores, registry; resumable stages | run.check, run.run_search, preflight.*, stages.Stages (pinned to the constants fingerprint, freeze sha256 and world); CPCV resumable by cpcv_units.jsonl |

## 2. Choices made, with reasons

1. rod_absratio's 60 dates are the vehicle's earlier decision rows at the same t_index on which rod_ret is applicable and present. The plan says "previous 60 trade dates of the same vehicle and the same t_index", and t_index exists only on rows. This follows the frozen _base_ratio pattern.
2. rod_ret's "previous trade date is an early-halt date" uses the group calendar (signals._daily.halt_flags) on the previous date. G5 reads Daily.halt, which exists only for dates with bars. The two differ only when that date has no bars at all.
3. rod_ret has no instrument_id check across a roll, as G5 has none. The plan names only G5's pattern.
4. The guard accepts only the 17 real step 2 files, whatever step2_root a caller passes. This is stricter than the plan, and it means real_world cannot be tested on fixture stores (section 5).
5. The bar bound is 2024-03-01 00:00 UTC, which is earlier than the frozen 00:00 CT and so stricter.
6. run refuses unless the E20S registry line is exactly E20S-01..E20S-45 with N 483 -> 528. Plan 9 passes N = 528 explicitly, so another N would contradict the plan. The refusal happens before anything is computed.
7. Stage files pin the constants fingerprint, the freeze sha256 and the world source. State written under another freeze, by a test or by the probe is refused.
8. The final configuration's "own CPCV OOS t and Sharpe" is reported two ways: from config_daily (each date is the mean over the 5 splits that test its block) and from its 5 path series (median path t).
9. The t4 and r_ROD shares are taken over the final configuration's 15 outer splits. This counts each block 5 times, and the factor cancels in the ratio. Each refit's sha256 must equal the CPCV record, and the refit P&L must equal 5 x config_daily.
10. The trade-level items reuse score_split's own steps. Each split's daily total must equal score_split's, and the 1.0 x record must equal nested.path_daily. A test shows the 1.5 x record equals pipeline._nested_schedule's.
11. Ruling 3: exit_ts is the close of the last bar before the session close, i.e. the session close (13:15 CT). The cost is priced at that bar's minute with the frozen event flag. B1 must call session_end_exits before apply_fallback_costs. The latter reprices from exit_ts at 13:15, which falls in the same 30-minute bucket as 13:14; the D8 table is calibrated at 13:18, which shares that [13:00, 13:30) bucket.
12. Ruling 2: a row is excluded when an always-applicable KEPT feature is not applicable at its decision time (the ports' known-by times), or is present but available after t. The test is computed with each spec's own function, before compute_signals' causality check would raise.
13. Each S4-S10 derivation copies its generator's rule into backward.py with a file:line citation, instead of importing the generator script. gen_k2_releases.build asserts its 2019-on DROPPED rows, so it cannot run unchanged on the hist rows. Every derived table equals the frozen table on the overlap (checked in backward_tables and in the tests).
14. In the dry check's row-loss count, the sentinel bars start one trade date before each window, because the declared table assumes the d-1 bars exist. A separate column shows the B1 state, in which the window's first date also loses every row.

## 3. Items stopped on, or for the lead

1. **Per-product round trips (V2.9 criterion 6).** The plan does not say which record to use or how to combine the paths. Built: on the nested record (each split's selected configuration), trips per product per path, over all five paths, and the path minimum and median, with the below-30 flag under all three readings. The final configuration's counts over its 15 splits are also reported. The lead picks the reading. Nothing gates on it.
2. **No register command.** The brief lists check | run | report. The lead registers with the frozen CLI: `uv run python -m screening.trial_registry register --test E20S --ids E20S-01 ... E20S-45 --freeze reports/stage_e20_search_freeze.json --freeze-sha256 <sha> --harness-sha256 ece91ae8...`.
3. **check hashes the 17 store files (bytes only) before the registration**, as H6's check did. The freeze builder hashes them too and compares them with E.17. No bar is decoded before the registry line.
4. **B1's first window date.** In B1 the first date of every root loses all its rows: G5's prior C and cp3's prior day are absent because the bars start at the window. That is one date per root, 17 dates. Plan 10.1's declared table does not list them. The dry check reports them.
5. **Frozen ports._cp3 edge case.** It raises IndexError on a frame that has rows but no port-complete day. The B1 full windows never hit this: every grains frame has complete days after 2012-05-21. A B1 sub-window lying wholly in the grains 09:30 era would crash. The dry check's window W1 was extended to 2012-09-28 for this reason.
6. **PR-16 table for plan 10.1.** On every backward kept date the fallback windows catch one decision time's entry, so 25.0% of entries, for ZT, ZF, ZN, TN, ZB, UB, 6E, MGC (t1 07:50; NFP or CPI at 07:30), for MNQ, M2K (t1 09:00; ISM) and for ZC, ZS, ZL, HE, LE (t3 11:00; WASDE and Crop Production). Exits are caught on 15.3% for ZC, ZS, ZL, 18.2% for HE and 13.2% for LE, and 0% for everyone else. MCL and NG are at 0%. The full (vehicle, type, t_index, horizon, side) table is in section 4 of reports/stage_e20_dry_check_step6.md.
7. **Unverified on real data.** world.real_world and run.check's store hashing have not been run against real stores (forbidden here). Tests reach them only through the guard refusals, so the first real `check` and `run` exercise them for the first time. The composition calls the frozen phase1.world.load_root with a RootStart built from E.12's records.

## 4. Tests

`uv run pytest -q -p no:cacheprovider tests/test_pattern_search*.py`: **111 passed in 100.09 s** (17:08:21-17:10:01 PDT; log in the session scratchpad). `ruff check` is clean on pattern_search/ and the test files.

| File | Tests | Covers |
|---|---|---|
| test_pattern_search_guard.py | 28 | every planted path refused (processed_hist before registration, after it, and with a marker; sealed; both holdout blobs and parquets; MES research and step 2 paths; a research store; another root's store; vendor; another file in a search directory); class names; the 17 stores pass; symlink; audit hook in a subprocess; 2024-03-01 bars; the loader wrapper refuses before the frozen loader runs; guarded hashing; the guard is imported first |
| test_pattern_search_rows.py | 9 | t4 per kept date at F - 60; plan CT minutes per group; identifiers; frozen rows untouched; sort and dtypes; targets: h120 never ok on t4, the h60 exit equals the hF exit at F |
| test_pattern_search_features.py | 9 | hand-computed rod_ret on 136 sampled rows; early-halt not applicable (Good Friday, Memorial Day); missing prior C and signal bar; 60-date warm-up and the hand median; fabricated zero median and missing-row cases; availability = t; assert_causal plus a planted late value; attach_rod's rules and z equal to zscore_causal; drop of an applicable missing value |
| test_pattern_search_panel.py | 10 | 34 + 2 features exactly; the 33 dropped; coverage without MES; check_panel; calendar cut; a shifted root raises BarGridError; the 2024-03 guard; assert_window; empty refusal; check_panel's five refusals; horizon_data on every horizon |
| test_pattern_search_grid.py | 5 | 45 in the plan's order; E20S ids; registry regexes; LightGBM settings; frozen grid only |
| test_pattern_search_search.py | 12 | empty-admissible refusal; the frozen filter; each screen item (pass, t < 2, Sharpe > 4 with alarm, Sharpe < 0.5, PBO raise, degenerate, NaN, >= 0.5, no final); DSR at 528; a small nested run; OOS equals _nested_schedule and 5 x config_daily; the trip-table readings |
| test_pattern_search_leakage.py | 7 | cuts at t1, t2 and every group's t4; perturbation of all 36 features and z (more than 5000 rows compared); planted future bar and centered normalizer caught; fold test on hF with t4 plus a planted overlap; t4 planted-edge canary (median t >= 3, t4 P&L above the t1-t3-only plant's); cross-date shuffle null; noise null |
| test_pattern_search_run.py | 14 | registry refuses before registration, with another sha256, with another N, and under another label; registry path only in test mode; manifest written once and verified (sha, unlisted, changed); required files; harness v12; pinned stages; run and report end to end; report refuses without stages; run refuses before any stage without registration; empty admissible ends with a failed screen; CLI refusal |
| test_pattern_search_backward.py | 17 | tables and overlap; hist then frozen rows; metals map; swap and restore (also on an exception); nesting refused; clock times for every group; member tables inside and outside; release rules and fallback minutes; fallback cost identity and hit; ruling 2 (and CausalityError without it); ruling 3 by hand (ZC 2014-03-04, PR-17) and untouched when the F bar exists; rulings 5, 6, 7; row losses reproduced; feature and leg checks; PR-16 shares |

## 5. Timing probe (synthetic, real window size)

The whole search ran once on a synthetic 17-vehicle world, 2019-05-06..2024-02-29, with ZT cut at 2021-10-01 and ZF at 2020-10-01 as their recorded S_X, warm-up 0, and the frozen sign plant at 3 round trips (the E.11 probe's setting). The run had all 45 configurations and 4 decision times, at nice 10, after a free-memory check (10.6 GB available). Start 16:38:38 PDT, end 16:48:59, 621 s total.

| Stage | Wall s | Peak RSS MB (VmHWM, reset per stage) |
|---|---|---|
| world (synthetic bars) | 3.9 | in panel |
| panel (66,632 rows, 16,658 at t4, 94 feature columns) | 15.1 | 2,133 |
| filter (51 admissible pairs) | 0.1 | 937 |
| cpcv (3,375 units, 1,125 fits) | 567.6 | 1,018 |
| final | 2.3 | 1,018 |
| oos (refits, trips, 1.5 x, shares) | 35.4 | 1,460 |

The planted synthetic screen passed (median t 7.7, PBO 0.0001, Sharpe 3.82). That result is meaningless and is only a functional check. The real panel will be slower: E.12's 28-vehicle real panel took 266 s at 2.9 GB. A guess for the real run is 15 to 30 minutes in total at under 4 GB, because real data may produce more candidates per validation set than the synthetic world. Probe log: ~/.cache/propexp_e20_probe.log. Probe state: ~/.cache/propexp_e20_search_probe/ (not the real state directory).

Dry check: `uv run python -m pattern_search.dry_check` takes 27 s and passes all four verdicts: features, legs, row losses reproduced, and ruling 2 only on LE t1 (296 rows). Report: reports/stage_e20_dry_check_step6.md. No feature failed, so nothing needs dropping before the freeze.

## 6. Files

New: pattern_search/{__init__, __main__, constants, guard, world, rows, features, panel, search, oos, stages, preflight, results, run, freeze_manifest, backward, dry_check}.py; tests/_pattern_search_synth.py; tests/test_pattern_search_{guard, rows, features, panel, grid, search, leakage, run, backward}.py; reports/stage_e20_dry_check_step6.md and .json; this file.

## 7. Review fixes (reports/stage_e20_review_search_code.md; 17:15-17:36 PDT)

SC-1 (SHOULD FIX). Under the original build, `check` never ran world.real_world, so the frozen loader path would first run inside `run`, after the registration. Lead ruling: add `--world` to check.
- `python -m pattern_search check --freeze-sha256 <sha> --harness-sha256 <v12> --world` first runs every existing check. It then calls run.world_check, which:
  - builds the real 17-root world through world.real_world: the frozen phase1.world.load_root per root, with load_confirmation_leg's sha256, L-3 booking, holdout, embargo, store-range and roll-metadata checks, refuse_late, the degraded-day record, closure_counts and compact_bars, followed by the guard's bar check, the coverage check and the training calendar;
  - re-runs guard.check_frames, then pipeline.assert_bars_on_session_grid on the loaded bars;
  - prints and writes a per-root summary to reports/stage_e20_search/world_check.json (schema stage_e20_search_world_check/1): bars, first and last trade date, S_X, splice and roll-blackout dates in the window, and store sha256, plus the training calendar's span.
- It builds no row, feature or panel, computes no statistic or fit, and writes nothing to the state directory. It reads no registry: the registration check stays in `run` only. `--world` with run or report is a usage error.
- The CLI now reports a frozen loader refusal (StageEBarRefusal, Phase1Error) or a BarGridError as REFUSED (rc 2) instead of a traceback.
- To make the loader path testable, world.real_world and world.load_search_root take two keyword arguments used only by tests: `test_stores` (real paths of fixture stores the guard may open; refused if any lies under a store root) and `test_expected_s_x`. The CLI never passes them, so the CLI still opens only the 17 real step 2 files.
- New tests in tests/test_pattern_search_world_check.py (5):
  - check --world on synthetic fixture stores for all 17 roots, written in the real formats by the frozen phase-1 fixture writers: it loads and summarizes every root, while rows, decision_rows, compute_signals, build_panel and build_search_panel are patched to fail if called. It writes nothing to the state directory and needs no registry;
  - check without --world builds no world;
  - a store whose recorded sha256 differs is refused by the frozen loader (ParquetHashMismatch), and no summary is written;
  - fixture stores under a store root are refused;
  - --world is accepted only with check.
- This closes section 3 item 7 in part: the loader composition now runs on fixture stores in the tests. The lead's `check --world` on the real stores, after the freeze manifest, will be its first real run, before any registration. I did not run it on the real stores.

`nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_pattern_search*.py`: **116 passed in 106.67 s** (17:32:36-17:34:23 PDT). After that run, ruff fixed an import order and a docstring line was shortened in the new test file; that file passes again on its own (5 passed). `ruff check` is clean. The freeze manifest's required files pick up the new test file through its glob.

Second fix: the first real check --world (built 17:36-17:43 PDT). The lead's first real `check --world` refused with `BarGridError: NQ: 7 bars outside the open intervals, 0 with another trade date` (reports/stage_e20_briefs/search_check_world.log). Lead ruling, per V2.2b ("On real bars the session-grid check of the synthetic pipeline is replaced by the frozen loader's own L-3 booking check"), E.12's phase-1 practice and harness v9's keep-and-flag rule: on real bars the assertion is not applied, and the closure counts are recorded instead.
- panel.build_search_panel: `check_grid=None` (the default) applies pipeline.assert_bars_on_session_grid on synthetic worlds only. A real world (world.SearchWorld, source "real", tested by panel.is_real) skips it, and an explicit `check_grid=True` still applies it. run.world_check likewise asserts only on a synthetic world. This overrides plan 6's PR-4 item for real bars only. Every other check is unchanged: the frozen loader's sha256, L-3 booking, holdout, embargo, store-range and roll checks, refuse_late, guard.check_frames, the calendar cut, assert_window, the empty refusal and check_panel.
- run.closure_record(world) gives, per root, the frozen phase-1 closure counts the loader recorded (phase1.world.closure_counts): `outside_open_intervals` (bars outside the group calendar's open intervals) and `close_minute` (of those, the close-minute prints booked to the session they close, L-3), plus the store's `bars_in_scheduled_closure`. The counts go into world_check.json (each root's `closure_counts`, and `session_grid_assertion`: "not applied: ...") and into the run's results (`panel.closure_counts` and `panel.session_grid_assertion` in reports/stage_e20_search.json). The bars stay in the world, as in E.12.
- Tests: NQ's fixture store now holds two bars outside the open intervals, labelled as L-3 books them: a close-minute print at the 2023-02-14 session end and a bar 30 minutes into the daily break, booked to 2023-02-15. check --world loads them and records `{"outside_open_intervals": 2, "close_minute": 1, "bars_in_scheduled_closure": 0}` for NQ and 0 for the other roots. The new test test_real_world_closure_bars_are_counted_not_refused shows that the synthetic assertion would refuse those bars (BarGridError "NQ: 2 bars outside the open intervals"), that closure_record counts them, and that build_search_panel on the real fixture world gets past the grid stage. It reaches the empty-panel refusal, because 3 months is shorter than the warm-up; with an explicit check_grid=True it still raises. The synthetic shifted-root test is unchanged and passes.
- `nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_pattern_search*.py`: **117 passed in 110.78 s** (17:40:10-17:42:01 PDT). ruff is clean. Nothing was run on real stores.
