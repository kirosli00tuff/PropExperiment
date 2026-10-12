# Brief: SearchCoder-OpusXHigh (Stage E.20 Step 6, the pattern_search package)

One objective: build a new package `pattern_search/` and its tests that implement
reports/stage_e20_plan.md (as fixed after PlanReviewer's review; the review is
reports/stage_e20_review_plan.md and the lead's rulings are in reports/stage_e20_rulings.md) by
configuring and calling the frozen ml_route_v2 code WITHOUT EDITING IT, on synthetic data only.
Where the plan cannot be implemented as written without editing a hashed file, or leaves a choice
open, STOP that item and report it with options; do not decide a rule yourself.

## Inputs

- The plan (every section), the product summary's feature lists (reports/stage_e20_product_summary.md
  section 1.3), docs/prompts/STAGE_E.20.md F2, F3, F6, F7, F9.
- The frozen code maps: reports/stage_e20_briefs/codemap_clock_panel_signals.md,
  codemap_models_cpcv_selection.md, codemap_sizing_sim_engine.md, codemap_phase1_world.md,
  codemap_leakage_tests.md (read them first; they give signatures and file:line references).
- Frozen code (read by section, never edited): ml_route_v2/ (clock, panel, normalize, targets,
  signals/, cpcv, selection_metric, portfolio, decide, cost_filter, configs, models, pipeline,
  fingerprint, phase1/world.py, synthetic.py), data/stage_e_bars.py, screening/stage_e_rules.py,
  screening/trial_registry.py, screening/harness_freeze.py, ml_route_v2/phase1/freeze.py.
- Patterns for the guard, freeze-manifest check, registration check and run-once discipline:
  h6_rod/ (guard.py, preflight, run.py), base_rules/guards.py, c1_replication/guards.py.

## Package (suggested layout; small focused modules)

- `guard.py`: plan section 3, the F3 read guard (path classes, the 2024-03-01 bar bound, the audit
  hook, the B1-only exception left as a refusal for now: the B1 code is not built in this step).
- `world.py`: the 17-vehicle real-data world from the frozen loaders, with E.12's recorded S_X
  (reports/stage_e12_phase1_bars.json "roots" -> "s_x"), never calling the D4 rule, never opening a
  research store or MES; the frozen release calendar and D8 costs; roll blackouts. Plus a synthetic
  17-vehicle world for tests (from ml_route_v2/synthetic.py).
- `rows.py`: the frozen decision rows plus t4 rows (plan section 4).
- `features.py`: rod_ret and rod_absratio (plan 5.2), zscore_causal, masks, flags, availability
  asserts, attached to the frozen Panel via dataclasses.replace.
- `backward.py`: the 2010-2019 swap context of plan section 10.1 (every listed module attribute or
  factory swapped by setattr and restored on exit, as c1_replication/context.hist_tables does, for all
  seven groups and the KEPT members' tables), used only by the Step 6 sentinel dry check now and by
  the B1 evaluation later. It opens no store.
- `dry_check.py`: the Step 6 sentinel dry check (plan section 13): synthetic sentinel frames for every
  leg in its 2010-2019 listing and calendar state, the swaps applied, every KEPT feature computed and
  shown applicable on its event rows; removing one leg's frames stops the build; the declared row-loss
  shares of section 10.1 reproduced. Its report goes to reports/stage_e20_dry_check_step6.md; any
  feature that fails is reported to the lead (the lead drops it before the freeze).
- `panel.py` (also re-applies every frozen check plan section 6 names): rows -> SignalContext -> build_targets -> build_panel(signals = the plan's 34 KEPT
  names, exactly) -> the r_ROD features -> checks (every feature finite on every ok row; t4 rows
  have ok_h120 False; the feature list equals the plan's).
- `search.py`: the admissibility filter with the empty-set refusal; the ConfigLedger in the state
  directory; nested_cpcv and final_selection with the frozen arguments (plan section 8); the screen
  (plan section 9 items 1-3) and every reported item of section 9 (DSR with N_total passed
  explicitly, per-configuration table, the final configuration's own CPCV OOS t and Sharpe,
  per-product OOS round trips with the under-30 flag, the 1.5 x slippage re-pricing, the t4 share
  and the r_ROD share). The ruin probability is NOT built in this step (plan section 9: only after a
  passed screen).
- `run.py`, `__main__.py`: `python -m pattern_search check | run | report`, each running the
  harness preflight (v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32), the v2
  freeze verification (reports/stage_e12_ml_v2_freeze.json, a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b),
  the search freeze manifest check (sha256 on the command line), the store sha256s (E.17 manifest),
  and, for `run`, the registry check: label E20S with ids E20S-01..E20S-45 (the prompt's
  E20-S01..S45; E20S-nn = configs.CONFIGS[nn - 1]) registered with the search freeze manifest's
  sha256, before any fit. Stages checkpointed in the state directory (~/.cache/propexp_e20_search;
  a test-mode path in tests), resumable by configuration and split (the frozen cpcv_units.jsonl),
  results to reports/stage_e20_search/ and reports/stage_e20_search.json and .md.
- `freeze_manifest.py`: builds reports/stage_e20_search_freeze.json (schema
  "stage_e20_search_freeze/1": the plan, every pattern_search file, every pattern_search test, and
  every input the search reads, each with path, sha256 and bytes) and verifies it; the lead runs it.

## Tests (new files tests/test_pattern_search_*.py; frozen tests untouched; synthetic data only)

Plan section 13: the guard's planted cases; V2.9's perturbation, fold and canary tests rerun on a
synthetic 17-vehicle world with t4 rows and the r_ROD features, calling the frozen helpers (the
codemap_leakage_tests map lists them); the grid count is 45 and its order and ids match the plan;
the feature list equals the plan's exactly; t4 rows and both r_ROD features on synthetic bars
(hand-computed values; the early-halt, missing-bar and warm-up cases; availability at or before t);
the empty-admissible refusal; the registry check refuses before registration and with another
freeze sha256.

## Timing probe

Run the whole search (panel, filter, nested CPCV, final selection, screen) once on a synthetic
17-vehicle world at the real window size (2019-05-06..2024-02-29, four decision times), at nice 10,
after checking free memory, and record wall time per stage and peak RSS. If a full run would take
over 45 minutes, run one outer split and extrapolate, saying so.

## Output

The package and tests, plus reports/stage_e20_briefs/search_build.md: a table from every plan
clause to the function that implements it, your choices with reasons, the test list and result
(`uv run pytest -q -p no:cacheprovider tests/test_pattern_search*.py`), the timing probe, and every
item you stopped on. Reply to the lead: the path, a summary of at most 200 words, anything unfinished.

## Boundaries

- No real data: do not open any store (data/processed*, data/sealed, data/raw, data/vendor, any
  parquet or dbn), the GEX CSV, or any result of E.12 Gate 0, E.15, E.17, E.18 or the H6 run.
- Do not edit any existing file (ml_route_v2/, screening/, rules/, sim/, data/, base_rules/,
  c1_replication/, h6_rod/, strategy/, frozen tests, the plan). No ledger writes (registry, spend or
  the E.12 config ledger); tests use temporary paths. No commits, no Databento, no TopstepX.
- Do not start the full test suite; run only your tests and the timing probe, at nice 10, one heavy
  job at a time. Do not spawn agents.
