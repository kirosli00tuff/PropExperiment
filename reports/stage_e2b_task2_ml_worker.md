# Stage E.2b Task 2: ML route pipeline (MLPipelineCoder-OpusXHigh)

Worker: MLPipelineCoder-OpusXHigh (worker-xhigh, opus). 2026-09-26, 12:43 to 13:40 PDT.
Synthetic data only. No bar parquet of any Stage E product was opened; no holdout, TopstepX,
Databento or git state was touched. Frozen files read (read-only): docs/STAGE_E_ML_DESIGN.md,
reports/stage_e2a_costs.json and reports/stage_e2a_vehicles.json (both sha256-checked against
the recorded hashes), and the calendar and rules modules.

## 1. Interfaces

**Job entry (E.ML-train), `ml_route/train.py`**
```
python -m ml_route.train fit --challenger {lgbm,lstm} --horizon {h30,h120,hF} \
    --store-root <STEP2_ROOT or a copy> --out-dir <dir> --harness-sha256 <sha256>
python -m ml_route.train finalize --out-dir <dir> --harness-sha256 <sha256>
```
- Both commands call `screening.harness_freeze.preflight(expected)` before anything else. That
  follows the lead's relayed change: the hash is a required flag, and preflight's return value is
  written into every ledger record, every candidates file, every rule's provenance and the route
  manifest. No flag or environment variable skips the call.
- `fit` runs these steps for one challenger and one horizon:
  - `load_route_inputs()` (frozen tables);
  - `frozen_block_cut()` (M7.3);
  - `build_dataset(store_root, inputs)`, which reads only the store;
  - saves the row index (`row_index_<ch>_<h>.npz`, sha256 in the candidates file);
  - 10 CPCV splits x every configuration, resumable from the JSONL ledger;
  - ML-A01 scores, selection with the ML-A10 tie-breaks, and a refit on blocks 1-5 (model file
    saved; its sha256 is the model hash);
  - per cluster: the surrogate, its candidate leaves, and the block-6 pre-test. Output:
    `candidates/<ch>_<h>.json`.
- `finalize` applies M5 step 4 across the six candidates files. It writes
  `rules/<rule_sha256>.json`, `rules/RULES.md` and `route_manifest.json`, and returns the
  manifest's sha256.
- **Today it refuses by name.** `load_route_inputs()` raises `RouteInputMissing` because two
  frozen inputs are not wired: the S_X table and the scheduled-release calendar. See Q1 and Q2.

**Store reader, `ml_route/store.py`**
- `assert_store_root(store_root, forbidden_root=PROCESSED_ROOT) -> {root: path}` is the path
  allowlist (ML-A23). It refuses:
  - a store root that is data/processed/, lies inside it, or contains it;
  - any file other than `<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet`;
  - a symlink whose target is not a step 2 file name or lies under data/processed/.
- `read_product_bars(store_root, root, s_x) -> ProductBars` also refuses:
  - metadata that does not say `store: "step2"`;
  - any row dated on or after 2024-03-01, or before 2019-05-06.

  It then cuts the rows before S_X, asserts the cut, and returns the roll-blackout dates from the
  metadata.
- `assert_window(root, s_x, days, step)` is M7.4's test on a saved row index. `fit` runs it on the
  training, refit, distillation and pre-test rows.
- The file name template matches `data.step2_store.step2_parquet_path` (a test checks this). The
  training root is `STEP2_ROOT = data/processed_step2`, relayed by the lead, and is passed
  explicitly.

**Rule wrapper, `ml_route/rule_wrapper.py`** (the full interface is in its module docstring, for
CanaryCoder)
```
spec  = rule_spec_from_json(rule_json)           # refuses a rule whose rule_sha256 no longer matches
strat = DistilledRuleStrategy(spec, product, cost, times, blackout, releases, cpi,
                              lead=LeadSpec(root, per_unit, product, times) | None,
                              quantity_micros=1)  # a strategy.interface.Strategy (one leg)
strat.observe_lead(bar)                          # the cluster lead's bars, any order, any time
strat.on_bar(bar, account); strat.decisions      # audit trail: t, features complete, fired, acted
```
- **Timing matches the training rows exactly.** The decision at t acts on the bar opening at t and
  reads only earlier bars. Its intent fills at the open of t + 1 min. The exit is emitted so it
  fills at the open of t + h or at F_X.
- **Lead history is filtered before anything reads it.** Only lead bars closed by t are kept, so
  lead bars handed over early cannot matter.
- **Features come from the training code.** ml_route.rows and ml_route.features compute them, and
  M7.1's validator checks them.
- A non-lead leg built without its lead is refused.

## 2. Files

- **Created:**
  - `ml_route/`: `__init__`, constants, inputs, store, blocks, features, rows, dataset, selection,
    lgbm, lstm, lstm_data, adapters, ledger, surrogate, rule_wrapper, manifest, train, probes,
    synthetic.
  - Tests: `tests/test_ml_route_blocks_selection.py`, `_store.py`, `_features.py`, `_models.py`,
    `_distil_entry.py`, `_wrapper.py`, `_e2e.py`, `_probes.py`.
  - `reports/stage_e2b_ml_probes.json` and this report.
- **Modified:** `pyproject.toml` and `uv.lock` (dependencies only).
- **Not touched:** other workers' files, sim/, strategy/, screening/, data/, and anything frozen.

## 3. Dependencies (step 1, done 12:44-12:52 PDT, before any other work)

- **Added to pyproject.toml (pinned):**
  - lightgbm==4.7.0 and torch==2.14.0, as the brief asks;
  - scikit-learn==1.9.1, which the brief did not name. The frozen M5 ruling ML-A11 requires
    scikit-learn's DecisionTreeRegressor, "its version pinned in uv.lock". This is a deviation
    from the brief's list and is flagged here.
- **torch source.** torch comes from `[[tool.uv.index]] pytorch-cu130`
  (https://download.pytorch.org/whl/cu130, `explicit = true`). `[tool.uv.sources]` sends torch
  there for `sys_platform == 'linux' or 'win32'`.
  - The lock holds `torch 2.14.0+cu130` wheels for manylinux_2_28_x86_64 and win_amd64 (and
    aarch64). Other platforms fall back to PyPI's torch 2.14.0.
  - `torch.cuda.get_arch_list()` = sm_75, sm_80, sm_86, sm_90, sm_100, sm_120, so both sm_75 and
    sm_86 are present.
- **Lock diff: no existing package changed.** All 35 existing entries are byte-identical: numpy
  2.5.3, pandas 3.0.5 and pyarrow 25.0.1 are unchanged. The only changed entry is propexperiment
  itself (its dependency list). 35 packages were added (torch and its nvidia-*/triton
  dependencies, lightgbm, scipy 1.18.1, narwhals, scikit-learn, joblib, threadpoolctl,
  cloudpickle and others).
- **Sync.** `uv sync` was run only after the diff was checked; its dry run showed installs only,
  with no removals or version changes.
- **Versions:**
  - lightgbm 4.7.0; torch 2.14.0+cu130; CUDA runtime 13.0; cuDNN 9.24.0 (92400);
    scikit-learn 1.9.1; Python 3.12.13;
  - NVIDIA driver 595.91.07 (supports CUDA 13.2), RTX 3050 4GB Laptop GPU, sm_86.

  These are also recorded under `probes.versions` and `probes.lstm` in
  reports/stage_e2b_ml_probes.json.

## 4. M7 tests and what each proves (80 tests, all passing; 90% line coverage of ml_route)

| M7 item | Test (file::name) | Proves |
|---|---|---|
| 7.1 validator | features::TestValidatorCanaries::test_honest_table_passes | every value of the real pipeline is available at or before its t |
| 7.1 canary: feature = y | features::...::test_feature_equal_to_the_target_is_rejected | two cases, both rejected with FeatureLeak: (a) a column built mechanically from the exit bar (availability = that bar's close) and (b) a column set to y with y's availability |
| 7.1 canary: next bar's close | features::...::test_feature_equal_to_the_next_bars_close_is_rejected | the close of the bar opening at t (available t + 1 min) is rejected |
| 7.2 single product | features::TestPerturbation::test_single_product_features_and_prediction_unchanged | after every bar closing after t is randomized, every row at or before t has identical features and an identical LightGBM prediction; later rows do change |
| 7.2 cross product (F16) | features::TestPerturbation::test_cross_product_lead_feature_unchanged | randomizing only the lead's (NQ) future leaves RTY's rows at or before t identical; later F16 values change |
| 7.3 cut | blocks_selection::TestBlockCut (3) | the frozen calendar has n = 1248 dates, 2019-05-06..2024-02-29, and six blocks of 208; the sixth takes the remainder; a bad calendar is refused |
| 7.3 CPCV | blocks_selection::TestCpcv (4) | 10 splits in combination order; the validation, embargo and training dates are right (known answer); adjacent blocks are embargoed on their outer sides only; a planted row whose target reaches a validation date is purged; assert_fold raises on a validation or embargo date on the training side |
| 7.4 window | store (13 cases), e2e::test_fit_entry_refuses_the_research_store_root | refused: a planted research-window bar (2025-05-01), an embargo bar (2024-03-01), a holdout-2 bar, a planted research-window parquet path, stray and misplaced files, a symlink into the research root, data/processed/ itself (also through the real entry), metadata other than step2, and S_X outside the window. Also: the S_X cut is asserted and the saved-row-index assertion works |
| 7.5 normalization | models::test_perturbing_every_row_after_the_training_window_leaves_the_model_hash | randomizing every bar after 2024-02-29 leaves the fitted model's sha256 unchanged |
| 7.5 control | models::test_the_normalization_test_has_teeth | the same perturbation does change the hash when post-window rows are admitted, so the test can fail |
| 7.6 hash chain | models: ledger chain, refit, model file, determinism (7) | the ledger is a sha256 chain (an edit or a reorder raises; a duplicate key raises). A same-machine refit with another hash raises; another machine's hash is only recorded. A saved model with other bytes is refused. LightGBM and the LSTM (CPU and GPU) reproduce their hashes. A re-run skips every ledger key and reproduces the refit hash |
| 7.7 wrapper | wrapper (6) | see the list below |
| entry discipline | distil_entry::TestEntryPreflight (4) | `fit` and `finalize` refuse when preflight raises, and no input is read first; `--harness-sha256` is required; the real preflight refuses a wrong hash |

M7.7 in detail. All six run through the real MES engine (sim/engine.py via sim.leakage_canaries'
machinery, unchanged):
- the tripwire: the engine never hands the wrapper a later bar;
- the wrapper's complete feature set and fired decisions equal the training table's at every
  decision time (train/test parity);
- entries fill at t + 1 min and exits at t + 30 min;
- a planted future changes no earlier decision (and does change later ones);
- the cross-product canary: all NQ lead bars, future ones included, are handed over before the
  run; parity with training holds, and randomizing the lead's future changes no decision at or
  before the cutoff;
- a non-lead leg built without its lead is refused, and so is a leg without a vehicle.

The other tests carry known answers:
- sigma_X,d, F1, F5, F16 and the net target y and cost are recomputed by hand from the synthetic
  frame and the raw cost JSON, and match to 1e-12;
- the to-F exit is at the flatten bar;
- decision counts are 12 for equity and 13 for rates, with the early-halt date 2019-07-03
  excluded;
- the event-guard and CPI exclusions, and the roll-blackout exclusion;
- the T12-4 event cost (largest s_b plus the fill bucket's own depth);
- ML-A01: the position thresholds, P&L at 1.0 and 1.5x, one open position, the portfolio day
  mean, a split score by hand, and the configuration score needing 10 splits;
- ML-A10 tie-breaks for both challengers;
- ML-A02 thresholds (0.5 c_bar and -2.5 c_bar);
- the surrogate's depth-2 leaves: order, conditions and unrounded cuts;
- the pre-test's reasons, and step 4's ranking and tie order;
- rule JSON hashing, and a catalog rendering that keeps the float repr;
- the frozen inputs: 31 products, and RB, HO and SI with no vehicle;
- the manifest's trial counts (36 configurations) and its refusals;
- end to end: the real `fit` entry on a synthetic step 2 store for LightGBM (81 chained ledger
  records) and for the LSTM (41).

Test files and counts:

| File | Tests |
|---|---|
| test_ml_route_blocks_selection.py | 13 |
| test_ml_route_store.py | 13 (11 functions) |
| test_ml_route_features.py | 14 |
| test_ml_route_models.py | 11 |
| test_ml_route_distil_entry.py | 16 |
| test_ml_route_wrapper.py | 6 (about 18 s) |
| test_ml_route_e2e.py | 3 (about 23 s) |
| test_ml_route_probes.py | 4 |

Existing file run: tests/test_leakage_canaries.py passed 15 of 15, unchanged.

## 5. Probes (ThinkPad, synthetic data of the real size; reports/stage_e2b_ml_probes.json)

| Probe | Setup | Measured | Peak RAM | Peak VRAM | Projection (full run) |
|---|---|---|---|---|---|
| LightGBM, one CPCV split (blocks 1+2 validation) | 450,000 rows, 31 products, 55 columns (F1-F17 plus one-hot F18 and F19); 224,928 train and 149,695 validation rows; 8 threads; via heavy.sh | largest config (31 leaves, min_data 500): fit 3.89 s, with prediction and score 4.86 s. Smallest (7, 2000, 10): 1.94 s / 2.56 s | 774 MiB | none | 24 x 11 fits: about 0.29 h (upper bound 0.38 h if every fit is the largest) |
| LSTM batch size (M8 A-1) | 32 hidden, lookback 72, one forward and backward pass at 512 | max_memory_reserved 138 MiB; CUDA context 164 MiB (nvidia-smi per-process 302 minus reserved 138); peak 302 MiB; 3,794 MiB of 4 GB free, so 512 is kept (no halving) | none | 302 MiB | batch size 512 for all four LSTM configurations |
| LSTM one epoch | largest config, batch 512, 224,928 rows, on the RTX 3050 | 3.40 s per epoch | 1,528 MiB | 138 MiB reserved | 12 configs x 11 fits x 8 epochs: about 0.70 h (upper bound 1.06 h); lookback 24 scaled by 24/72, a guess |

Probe caveats. Both challengers project far below M8's guesses (7-14 h for the trees, 18-35 h
for the LSTM). The E.ML-train session should re-time its first real fit:
- **Not timed:** building the row table from about 28 x 1.6M one-minute bars, and the real
  per-batch sequence gather. The gather groups a batch by product (up to 28 groups) where the
  probe's synthetic gather used one array.
- **Real sizes differ slightly:** 28 products with rows, and 52 design columns.

## 6. Commands run (results)

- Dependency step: `uv lock` (+31 packages, then +4 with scikit-learn), a lock diff script (0
  existing changed), `uv sync --dry-run` (installs only), `uv sync` (twice).
- Torch check: the CUDA check printed available True and the arch list above.
- Probes: `reports/stage_e2b_briefs/heavy.sh /usr/bin/time -v uv run --no-sync python -m
  ml_route.probes lgbm|lstm --out reports/stage_e2b_ml_probes.json`, both exit 0. Wall times:
  lgbm 8.5 s, lstm 11.4 s.
- Tests: `uv run --no-sync pytest -q tests/test_ml_route_*.py --cov=ml_route`: 80 passed,
  90% coverage (probes.py 26%, since the probes themselves ran as a script).
- Existing canaries: `uv run --no-sync pytest -q tests/test_leakage_canaries.py`: 15 passed.
- Lint: `uv run --no-sync ruff check ml_route/ tests/test_ml_route_*.py`: all checks passed.

## 7. Readings taken, and open questions for the lead

Readings (the frozen text left a detail open; each is chosen literally and written in the module
docstrings):

- **R1 (bar-exact lookbacks).** F1-F5 read the bars closing exactly at t and at t - k, both on
  trade date d; either one absent makes the value missing.
- **R2 (F6 and F9).** Both start from the trade date's first bar.
- **R3 (F7 and F8).** Both use the group calendar's previous trade date (CP3's d - 1); F8 needs
  that date to be complete.
- **R4 (F10).** F10 compares the volume of bars closing in (t - 30, t] with the median of the same
  CT clock window over the product's 20 previous trade dates. Fewer than 20 previous dates, or a
  zero volume or median, makes it missing.
- **R5 (F13-F15).** F13 counts minutes to the first release at or after t; F14 counts minutes since
  the last release before t; F15 flags a release on t's CT calendar date.
- **R6 (F16).** F16 is the lead's 30-minute return ending at the lead's latest bar closing at or
  before t on the same trade date, divided by the lead's sigma.
- **R7 (F17).** The median runs over sigma on the 120 trade dates ending at d, inclusive.
- **R8 (LSTM volume steps).** An LSTM step's log volume ratio is F10's construction per 5-minute
  clock slot; a date with no bar in the slot counts as zero volume. An undefined step makes the row
  missing for the LSTM.
- **R9 (LSTM row set).** The LSTM's rows are the complete rows whose 72-step sequence is fully
  defined, so all four configurations score the same rows.
- **R10 (LSTM dropout).** Dropout 0.2 is applied to the final hidden state. nn.LSTM's own dropout
  does nothing with one layer.
- **R11 (LSTM padding).** Sequences are padded and masked by packing. This is the same computation
  as left padding with a mask, and a test proves padded steps never reach the output.
- **R12 (pre-test floors).** "D9's floors" in the pre-test means D9.3's trade-rate floor: at most 20
  entries per product per date, holds of at least 2 minutes, and a mean hold of at least 10 minutes.
  "Net P&L" is the sum over the rule's trades. The ranking's "per trade date" divides by the dates
  with the cluster's rows in block 6.
- **R13 (session cap).** A D6 session that would give more than 13 decision times raises. No real
  product does.
- **R14 (thread constant).** `TORCH_CPU_THREADS = 4` is a harness constant, not a design value.

Open questions (the code refuses each case by name):

- **Q1. S_X per price-path contract has no frozen table.** `load_start_dates()` raises. The lead
  needs to name the file that ScreenStatsCoder's start rule writes (from V_ref,X, research-window
  volume, which M7.9 allows).
- **Q2. The scheduled-release calendar per product and the CPI instants for 2019-05..2024-02 are
  not built.** These are D8's release list, D9.5a and D9.12. `load_event_calendar()` raises. They
  feed F13-F15, the event-window cost, the entry guard and the CPI exclusion.
- **Q3. An exit fill that lands in [release, release + 2 min) has no training target.** D9.5a
  defers such a fill, but M4 does not say how the target treats it. The target is set missing and
  counted (`target_<h>_exit_in_event_guard`).
- **Q4. The Stage E runner's member protocol differs from the one the wrapper implements.**
  RunnerCoder's protocol is `strategy/stage_e/interface.py` `StageEMember.on_minute(view,
  account)`; the wrapper implements `strategy.interface.Strategy`, which the existing canaries use.
  A multi-leg adapter is needed before E.ML-test and before CanaryCoder's cross-product canary on
  the Stage E engine. It would hold one DistilledRuleStrategy per traded exposure of the cluster
  (ML-A15), with the lead's bars fed through `observe_lead`. It is not built here.
- **Q5. ML-A15's primary-leg fallback is not wired.** The fallback is "highest 2026 Jan-Aug ADV
  in D1's table". It is not reachable today, since every F16 lead exposure has a vehicle, and the
  code raises `RouteInputMissing` if it ever is.
- **Q6. The training-window DSR and PBO that M6 reports are not computed.** The ledger keeps every
  fit's validation daily P&L series for them. The statistics code belongs to the stats worker.
- **Q7. Windows needs a new enough driver for CUDA 13.0 wheels.** The cu130 wheels need an NVIDIA
  driver of about 580 or later on the Windows PC. sm_75 is in the arch list, so an older driver
  means updating the driver, not changing the wheel. E.2c should repeat the probes there
  (`python -m ml_route.probes versions|lgbm|lstm`).

## 8. Not finished

- **E.ML-test entry.** Not in the brief and not built. The refusal primitives it needs exist:
  `verify_model_file`, `verify_chain`, and `rule_spec_from_json`'s hash check.
- **The Stage E engine adapter for the wrapper.** See Q4.
- **Real-data wiring of S_X and the release calendar.** See Q1 and Q2. Until both exist, the real
  `fit` entry refuses.
