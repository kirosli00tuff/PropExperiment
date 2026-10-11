# Stage E.20 code map: models, CPCV, selection (read-only)

Scope: ml_route_v2/{configs,models,cpcv,selection_metric,pipeline,portfolio,cost_filter,decide,
fingerprint,constants}.py, screening/stage_e_verdict.py, funnel/multiple_comparisons.py. No data
store, gate0 report or E.15/E.17/E.18 result was opened.

Freeze status. reports/stage_e12_ml_v2_freeze.json (91 files) hashes every ml_route_v2 file named
above, plus account.py, sizing.py, panel.py, clock.py, phase1/*, and their tests. The harness
manifest reports/stage_e2b_harness_freeze.json (1062 files) hashes funnel/multiple_comparisons.py,
ml_route/accounting.py, screening/stage_e_verdict.py, rules/products.py and
screening/stage_e_frozen.py. In this map, "edit" means a change to one of those hashed files.

## Q1. The 45-configuration grid and the ConfigLedger

- The literals are in constants.py: `RIDGE_LAMBDAS = (0.01, 0.1, 1.0)` (alpha = lambda x n_train),
  `LGBM_DEPTHS = (2, 3)`, `COST_GATE_KS = (1.5, 2.0, 3.0)`, `HORIZONS = ("h60", "h120", "hF")`,
  `N_CONFIGURATIONS = 45`. The horizon id is "hF", not "F".
- configs.py:56 `ModelSpec(kind, param, model_id)` and configs.py:66
  `Config(config_id, model, k, horizon)`. Both are frozen dataclasses.
- configs.py:87 `ridge_spec(lam: float) -> ModelSpec` gives the id "ridge_l<lam:g>".
  configs.py:93 `lgbm_spec(depth: int) -> ModelSpec` gives the id "lgbm_d<depth>".
- configs.py:99 `config_id(model: ModelSpec, k: float, horizon: str) -> str` returns
  "<model_id>_k<k:g>_<horizon>", for example `ridge_l0.01_k1.5_h60` and `lgbm_d3_k3_hF`.
- configs.py:103-115 build `CONFIGS: tuple[Config, ...]` at import time. The order is: models
  outermost (ridge 0.01, 0.1, 1.0, then lgbm d2, d3), then k, then horizon. CONFIGS[0] is
  ridge_l0.01_k1.5_h60 and CONFIGS[44] is lgbm_d3_k3_hF. configs.py:116 builds `CONFIGS_BY_ID`.
- configs.py:119 `tie_break_key(config) -> tuple`. A smaller key wins. The order is ridge before
  lgbm, then the larger lambda, then the smaller depth, then the larger k, then the shorter
  horizon. It raises unless kind is in `MODEL_KINDS` and horizon is in the constant `HORIZONS`.
- configs.py:78 `SplitScore(sharpe: float, n_trades: int, daily: pd.Series, n_risk_unknown: int = 0)`.
- configs.py:138 `ConfigLedger(path: Path)` is an append-only JSONL file. Each line holds entry_id,
  kind, spec and time (America/Vancouver).
  - `register(entry_id: str, kind: str, spec: Mapping) -> None` (167). kind must be one of
    `("config", "gate0_A", "gate0_B")`. Registering the same id with the same spec does nothing.
    The same id with a different spec raises LedgerError.
  - `is_registered(entry_id)` (186). `require(entry_ids)` (189) raises "computation before
    registration".
  - `n_registered(kind: str | None = None) -> int` (196).
  - `n_total(n_program: int = N_PROGRAM_AT_FREEZE) -> int` (201) returns n_program plus ALL
    registered entries, of every kind.
- configs.py:209 `register_configs(ledger, configs) -> None`. cpcv._prepare calls it before the
  first fit (cpcv.py:533).
- In the pipeline the ledger path is `state_dir/ledger.jsonl` (pipeline.py:112, 552).
  Config ids carry no root. Registering the same 45 ids into one ledger counts 45 once; separate
  state dirs each count their own entries.
- The grid can be supplied by composition. `nested_cpcv`, `final_selection` and `run_pipeline`
  take `configs: Sequence[Config]`, and Config objects can be built directly. Two limits: a new
  horizon id outside HORIZONS breaks tie_break_key, and a new model kind breaks fit_model and
  tie_break_key. Either would need an edit to constants.py, configs.py or models.py.

## Q2. Nested CPCV (cpcv.py)

- cpcv.py:153 `calendar_blocks(dates: Sequence[date], n_blocks: int = N_BLOCKS) -> tuple[tuple[date, ...], ...]`.
  It sorts the unique dates and cuts 6 contiguous blocks of floor(n/6) dates; the last block
  takes the remainder.
- cpcv.py:116 `Split(index, test_blocks, train_dates, test_dates, embargo_dates)`.
- cpcv.py:175 `outer_splits(blocks, n_test_blocks: int = N_TEST_BLOCKS, embargo: int = EMBARGO_DATES) -> tuple[Split, ...]`.
  It builds C(6,2) = 15 splits in itertools.combinations order. The embargo drops
  `EMBARGO_DATES = 1` calendar date on each side of each test block from training.
- cpcv.py:203 `inner_splits(outer: Split, blocks, embargo: int = EMBARGO_DATES) -> tuple[Split, ...]`.
  It builds 4 leave-one-block-out folds over the outer training blocks, with the same embargo.
  It asserts isolation from outer test and embargo dates (LeakageError).
- cpcv.py:219 `assemble_paths(splits, n_blocks: int = N_BLOCKS) -> tuple[dict[int, int], ...]`
  returns 5 paths. In path j, block b goes to the j-th split (in index order) that tests b.
- cpcv.py:269 `split_masks(split, trade_date, decision_ts_ns, exit_ts_ns) -> (train_mask, test_mask)`.
  The purge removes a training row whose [decision_ts, exit_ts] interval meets the merged span
  [earliest decision, latest exit] of any test date's rows. It raises if any exit precedes its
  decision.
- cpcv.py:285 `assert_fold(...)` is the fold test. cpcv.py:498 `_assert_rows_isolated` checks the
  inner rows against the outer test.
- cpcv.py:324 `horizon_data(panel, horizon, admissible=None) -> HorizonData` (rows, X, y, days,
  t_ns, x_ns, sigma).
  - Panel duck type: `panel.frame` (DataFrame) and `panel.feature_cols`.
  - Required columns: root, trade_date, decision_ts_ns, sigma_d, `ok_<h>`, `y_norm_<h>`,
    `exit_ts_ns_<h>`, plus the feature columns.
  - Rows used: `ok_<h>` True and, if `admissible` is given, root in that horizon's admissible
    roots.
  - It RAISES CPCVError when any feature or y is non-finite on a used row, or when sigma_d <= 0
    (cpcv.py:340-345).
- The score function also needs these columns: cluster, `cost_long_<h>`, `cost_short_<h>`,
  `y_gross_<h>`, `release_window` (bool dtype), and flatten_ts_ns where an exit is missing.
  risk_table needs `ok_/y_gross_/cost_long_/cost_short_` for ALL three HORIZONS (Q4).
- Predictions: r_hat = predict(model, X_test) x sigma_d, in vehicle ticks (cpcv.py:490).
- Fits: one fit per (model_id, horizon, split or fold), shared by the 3 k values
  (cpcv.py:476 `_fit_and_score`, cpcv.py:511 `_groups`).
  - Nested total: 15 x (4 + 1) x 5 models x 3 horizons = 1,125 fits.
  - final_selection reuses the outer units and adds 1 refit. The schedule stage refits each
    split's selected model, up to 15 times, and checks its sha256.
- models.py:125 `fit_model(spec: ModelSpec, X, y, *, seed: int = SEED) -> FittedModel` and
  models.py:141 `predict(model, X) -> np.ndarray`.
  - Ridge is closed form under 1 BLAS thread (`RIDGE_BLAS_THREADS`, models.py:76).
  - LightGBM uses `LGBM_FIXED` (constants.py; 300 rounds, `num_threads: 8`, deterministic,
    min_data_in_leaf 2000, lambda_l2 100) with max_depth d and num_leaves 2**d.

## Q3. Selection metric (selection_metric.py)

- selection_metric.py:75 `score_split(test_rows: pd.DataFrame, r_hat_ticks: np.ndarray, config, *, risk: pd.DataFrame, account: AccountSpec = ACCOUNT_50K, candidates_fn: CandidatesFn | None = None, slippage_multiple: float = 1.0) -> SplitScore`.
- It is a fast fixed-D portfolio pass in pandas. It does NOT call the engine (simulate.py); the
  engine runs only in pipeline stage 8. The steps:
  1. `decide.candidates` (decide.py:110) applies the cost gate at the config's k and horizon.
  2. `_scorable` drops candidates with a missing `y_gross_<h>`.
  3. `portfolio.join_risk` (portfolio.py:227) attaches sigma_ticks and loss_ticks. A pair absent
     from the risk table raises; NaN figures are counted as risk_unknown.
  4. `portfolio.accept_trades(joined, risk, account, d_fixed=account.mll_usd)` (portfolio.py:310,
     called at selection_metric.py:90). D is held at the 50K MLL, $2,000 (account.py:76).
  5. `portfolio.fixed_d_daily_pnl(accepted, test_rows, slippage_multiple=)` (portfolio.py:336)
     gives the net $ per trade date: n x (side x y_gross - cost) x tick value. The cost is the
     D8 cost plus the beyond-q_c surcharge.
  6. The daily series is reindexed to ALL trade dates of the validation rows, with 0 on no-trade
     dates.
  7. The score is `daily_sharpe` (selection_metric.py:64): mean / sd with ddof 1, and 0.0 when
     the sd is 0 or there are fewer than 2 dates.
- Caps (portfolio.py:162 `admit(...)`, applied by `admission_record`, portfolio.py:264):
  - one open position per product, an open position being [decision_ts, exit_ts);
  - at most 3 open positions and at most 1 per cluster;
  - at most 1 lot-equivalent per product and at most the D9.11 50K member cap;
  - the base tier minus 0.1 lot (D fixed means the base tier);
  - `sizing.contracts`, where 0 means skipped;
  - the daily variance budget (0.10 x 2000)^2, consumed per accepted trade ("risk_budget_spent").
- Release-window rule (portfolio.py:91 `release_window_mask` and :108 `release_window_binds`): a
  candidate with `release_window` True is REFUSED, not resized, when open lot-equivalents
  including its own n exceed 0.5 x the tier in tenths. The flag comes from targets.py through the
  `release_window` column, which decide.candidates carries.
- Ranking at one decision time: edge_over_cost descending, then root (portfolio.py:257,
  decide.py:136-138).
- Vehicle facts (`portfolio.vehicle_facts`, portfolio.py:132) come from `rules.products.product`
  and `screening.stage_e_frozen.leg_inputs(root, traded=True)`. Whether these resolve for all 17
  E.20 vehicles was not checked: UNKNOWN. All 17 are keys of `constants.UNIVERSE`.
- Eligibility and ties are applied in cpcv.py, not in selection_metric:
  - cpcv.py:462: a unit is eligible when sharpe is finite (not None) and `n_trades >= MIN_TRADES`
    (30). Since daily_sharpe returns 0.0 when undefined, sharpe is None only when n_train or
    n_test is 0.
  - cpcv.py:595 `_select(configs, records, n_required)`: a config qualifies only if it has a
    record on all n_required sets and every one is eligible. The best mean score wins, with the
    key `(-mean, tie_break_key(c))` (cpcv.py:607); a tie needs exact float equality. If no config
    is eligible, the split selects None and trades nothing (zeros).

## Q4. Risk table and the c/sigma filter (cost_filter.py)

- cost_filter.py:41 `_table` builds one row per (root, h in constants.HORIZONS) over rows with
  `ok_<h>`. Columns:
  - c_ticks = mean of max(cost_long, cost_short);
  - sigma_ticks = sd (ddof 1) of y_gross;
  - ratio = c / sigma;
  - admissible = ratio <= `v2c.C_SIGMA_TAU` (0.167, looked up at call time);
  - loss_ticks = the 0.99 quantile of |y_gross| (`LOSS_QUANTILE`);
  - n_rows.

  All decision times of a root are pooled per (root, h). It refuses dates >= 2024-03-01
  (`panel.assert_window`).
- cost_filter.py:62 `c_sigma_table(panel) -> DataFrame`.
  cost_filter.py:67 `risk_table(panel, *, roots: Sequence[str] = ()) -> DataFrame` gives NaN rows
  for listed roots that have no rows.
  cost_filter.py:73 `admissible_roots(table) -> tuple[str, ...]`.
- The admissibility filter runs as a single pass over the whole training panel (all 6 blocks):
  `pipeline._filter(panel) -> {"c_sigma", "risk", "admissible"}` (pipeline.py:301). The
  admissible (root, h) tuple then restricts rows through `horizon_data`'s admissible mask.
- Per-split risk: `pipeline.split_risk_fn(panel)` (pipeline.py:356) is
  `functools.partial(risk_table, roots=<every panel root>)`. It is passed as `risk_fn` to
  nested_cpcv and evaluated on each outer split's purged and embargoed training rows, and on each
  inner fold's training rows. It is cached per (fold, horizon) within one outer split
  (cpcv.py:552 `split_risk`, cpcv.py:566 `_compute_units`).
- The whole-window `filt["risk"]` is bound into `score_fn_for(risk)` (pipeline.py:350). Under
  risk_fn, cpcv's `risk=` keyword overrides it (cpcv.py:442). The bound table still enters the
  CPCV fingerprint through `_callable_name`.
- pipeline.py:581 passes `admissible=adm or None`. An EMPTY admissible tuple becomes None, which
  means no admissibility filter at all.
- t4 rows added to the panel would enter the h60 and hF c, sigma and L estimates, because rows are
  pooled per (root, h) through `ok_<h>`. Setting `ok_h120` False on t4 rows keeps them out of
  h120 in both the filter and horizon_data. This is a panel-side change; no CPCV or filter edit
  is needed.

## Q5. Pipeline end to end (pipeline.py)

- pipeline.py:535 `run_pipeline(world, *, state_dir: Path, configs: Sequence[Config] = CONFIGS, timing: bool = True, force_after_gate0_fail: bool = False, stop_after: str | None = None, paths: Sequence[int] | None = None, payout_paths: int = PAYOUT_PATHS, n_program: int = N_PROGRAM_AT_FREEZE, isolate_paths: bool = ISOLATE_ENGINE_PATHS) -> PipelineReport`.
- Stages (pipeline.py:110):
  1. panel: `build_world_panel(world)` (269) uses clock.decision_rows with 3 decision times.
     run_pipeline has NO panel argument; it builds the panel from `world`.
  2. filter
  3. gate0: always computed. It registers gate0_A and gate0_B ledger entries, which raises
     N_total. A failure stops the run unless `force_after_gate0_fail=True`.
  4. cpcv: `nested_cpcv(panel, configs, score, ledger=, state_dir=state_dir/"cpcv", admissible=adm or None, calendar=world.calendar, risk_fn=split_risk_table)` (pipeline.py:579-581).
  5. stats: `_stats(nested, ledger, n_program)` (391).
  6. final: `final_selection(...)` with the same arguments (587-589), then `_final` (610).
  7. schedule: `_nested_schedule` (438) does the refits, the candidates per path, and the
     re-score at 1.0x and 1.5x slippage. The 1.0x re-score must equal nested.path_daily within
     1e-6 $.
  8. simulate: the engine, per path.
  9. payouts: `run_payout_paths`. ruin_prob for criterion 7 comes from here (docstring
     pipeline.py:77-87).
- Checkpointing:
  - Each stage is saved to `state_dir/stages/<name>.pkl` as `{"constants": fp, "out": ...}`.
    `_Stages.run` (pipeline.py:218) LOADS an existing file instead of computing, after checking
    the constants fingerprint.
  - Inside CPCV, `state_dir/cpcv/cpcv_units.jsonl` holds one line per unit, keyed
    `(unit "inner"|"outer", config_id, outer, inner)` with inner = -1 for an outer unit
    (cpcv.py:374 `JsonlStore`). Line 1 pins `input_fingerprint`, built from the panel frame hash,
    the feature list, the blocks, the admissible pairs, the score_fn and risk_fn names (with a
    digest of each partial's bound arguments), the embargo, min_trades and
    `constants_fingerprint()` (cpcv.py:528-549). A mismatch raises StateMismatchError.
  - Finished units are skipped on restart (cpcv.py:579, 590). Outer units keep the daily
    series; inner units do not.
- Threads and processes:
  - CPCV is a single-process sequential loop over outer splits, then over (model, horizon)
    groups, then over folds.
  - LightGBM uses `num_threads` 8 from `LGBM_FIXED` for both fit and predict. It is a constant in
    hashed constants.py; there is no parameter.
  - Ridge uses 1 BLAS thread.
  - `isolate_paths` affects only the engine stage.
  - `fingerprint.constants_fingerprint()` (fingerprint.py:31) hashes the file bytes AND the live
    values, so a runtime override of any constant changes the fingerprint of all state.
- `nested_cpcv(panel, configs, score_fn, *, ledger: ConfigLedger, state_dir: Path, admissible=None, calendar: Sequence[date] | None = None, risk_fn: RiskFn | None = None) -> NestedResult`
  (cpcv.py:669). With calendar None, the blocks come from the panel's unique trade dates.
- `NestedResult` (cpcv.py:636) holds:
  - blocks, splits, paths;
  - `selected` (config_id or None per outer split) and `selected_sha256`;
  - inner_table and outer_table;
  - `path_daily`: calendar dates x 5 paths, the nested OOS daily net $. It is assembled at
    cpcv.py:695-697 through `_path_series` (cpcv.py:621);
  - `config_daily`: dates x configs, each date the mean over the 5 splits that test its block
    (cpcv.py:650);
  - config_sharpes (population sd) and config_path_sharpes.
- `final_selection(...same signature...) -> FinalResult(config, table, model, n_train_rows)`
  (cpcv.py:716). It runs `_select` over the 15 outer units, then refits the winner on all rows.
- Public helpers: `pipeline.assemble_record(nested, daily_by_split) -> DataFrame` (419) and
  `record_figures(path_daily) -> dict` (380).
- Composition: pattern_search can build its own Panel (`panel.Panel(frame, feature_cols,
  signal_names, horizons, avail_max_ts_ns, counts)`, a frozen dataclass, panel.py:43). It can
  then call `nested_cpcv` and `final_selection` directly, with `score_fn_for(risk)`,
  `split_risk_fn(panel)`, `_filter(panel)`, and `_stats` or the public pbo/dsr functions. This
  needs no edit; `_filter` and `_stats` are private but importable.
- Facts only, as status rather than advice:
  - `run_pipeline` itself cannot take a custom panel or 4 decision times. clock.decision_rows
    uses `N_DECISION_TIMES = 3` and `LONGEST_FIXED_HORIZON_MIN = 120` (clock.py:40-76), so t4
    through the pipeline's own panel stage would need an edit to clock.py or constants.py.
  - A pre-existing `stages/panel.pkl` with the right constants fingerprint would be loaded by
    `_Stages.run`.
  - Stages 7-9 need `world` (bars, calendar) and the engine.

## Q6. PBO and DSR at N_total

- PBO: cpcv.py:735 `pbo_cscv(perf: np.ndarray, n_blocks: int = PBO_BLOCKS) -> dict`, with
  `PBO_BLOCKS = 16`.
  - perf is dates x configurations; the pipeline passes `nested.config_daily.to_numpy()`, all
    45 configs.
  - It cuts 16 contiguous blocks of floor(n/16) dates (the last takes the remainder) and sums
    P&L per block.
  - It calls `funnel.multiple_comparisons.probability_of_backtest_overfitting(performance: list[list[float]], n_blocks: int = 8) -> PBOResult`
    (multiple_comparisons.py:143). That function enumerates all C(16,8) = 12,870 balanced splits,
    picks the in-sample best, and returns the fraction with OOS logit <= 0. n_blocks must be
    even.
  - It returns pbo, n_splits, n_strategies, n_blocks, n_dates, block_dates, degenerate and note.
  - It raises on non-finite input; _stats catches the error and records pbo NaN.
- DSR: cpcv.py:769 `dsr_at_n(daily: np.ndarray, n_trials: int, sharpe_variance: float) -> dict`.
  - It takes moments from `ml_route.accounting.moments` (population sd, raw kurtosis, daily,
    unannualized).
  - It calls `deflated_sharpe_ratio(observed_sharpe, n_observations, n_trials, sharpe_variance, skewness=0.0, kurtosis=3.0) -> dict`
    (multiple_comparisons.py:81).
  - It returns status "undefined" for fewer than 2 dates, sd 0, or degenerate moments.
- cpcv.py:761 `sharpe_variance(sharpes) -> float` is the population variance.
- How `_stats` (pipeline.py:391) applies them:
  - DSR is computed on the PATH-AVERAGED nested daily series (`path_daily.mean(axis=1)`), not on
    the median path.
  - Its sharpe_variance is taken over the finite `nested.config_sharpes`, the 45 configs'
    path-averaged OOS daily Sharpes.
  - `n_total = ledger.n_total(n_program)`.
- `N_PROGRAM_AT_FREEZE = 198` (constants.py). N_total = n_program + every ledger entry (configs,
  gate0_A, gate0_B).
- N_total CAN be passed explicitly in either of two ways:
  - `run_pipeline(n_program=...)` and `_stats(nested, ledger, n_program)` set the base, and the
    ledger adds its entries;
  - `dsr_at_n(daily, n_trials, variance)` takes the trial count directly.
- Another implementation exists: screening/stage_e_verdict.py:181
  `dsr(mom, n_trials: int, variance: float) -> tuple[float | None, str | None]`, :200
  `dsr_table(moms, variance_over, n_trials, members) -> dict`, and :215
  `pbo(series: Mapping[str, np.ndarray]) -> dict`. That `pbo` uses `N_PBO_BLOCKS = 8`, not 16,
  so it is not the v2 contract.

## Q7. Median-path daily t (criterion 2)

- pipeline.py:367 `_daily_t(xs) -> float` computes mean / (sd ddof 1 / sqrt(n)). It returns NaN
  for fewer than 2 values and 0.0 when sd = 0.
- `_stats` (pipeline.py:396-397) and `record_figures` (pipeline.py:380) compute
  `path_t = [_daily_t(path_daily[j]) for j in 5 paths]` and
  `median_path_t = np.median(path_t)`, the 3rd of 5.
- Each path column runs over EVERY date of the 6 calendar blocks (the training calendar passed as
  `calendar`). Zeros fill:
  - no-trade dates (score_split reindex);
  - calendar dates with no rows (`.get(d, 0.0)`, cpcv.py:627);
  - every date of a split whose `selected` is None.
- The t is computed over dates, with zeros included.
- Annualized net Sharpe at 50K is `mean/sd(ddof 1) x sqrt(252)` of the path-averaged series
  (`_stats` "sharpe_annual"; `TRADE_DATES_PER_YEAR = 252`). This is the fixed-D record (D =
  $2,000). The engine and payout figures (ruin) come from stages 8-9.

## Q8. COST_GATE_READING and the k grid

- `COST_GATE_READING = "gross"` is a constant in hashed constants.py.
  `decide.gate_reading(reading: str | None = None)` (decide.py:56) reads `v2c.COST_GATE_READING`
  at call time.
- `decide.cost_gate(r_hat_ticks, cost_long, cost_short, k, *, reading=None)` (decide.py:64) and
  `decide.candidates(rows, r_hat_ticks, config, *, reading=None)` (decide.py:110) both take a
  `reading=` parameter.
- `score_split` calls `cand_fn(test_rows, r_hat, config)` without `reading`. A different reading
  therefore needs `candidates_fn=functools.partial(candidates, reading=...)`, which is
  composition, or a runtime constant change, which changes the constants fingerprint.
  E.20 keeps "gross".
- Gross gate: long iff r_hat > k x c_long; short iff -r_hat > k x c_short (decide.py:84-86).
- The k grid `COST_GATE_KS` is a constant used only to build `CONFIGS` at import time. Each
  Config carries its own `k`, which `candidates` reads (`config.k`). A different grid can be
  passed as a custom `configs` sequence without an edit.
- `C_SIGMA_TAU`, `MIN_TRADES`, `N_BLOCKS`, `EMBARGO_DATES` and `PBO_BLOCKS` are constants:
  - N_BLOCKS, N_TEST_BLOCKS and EMBARGO_DATES are default arguments of calendar_blocks,
    outer_splits and inner_splits, but nested_cpcv calls them with the defaults;
  - pbo_cscv takes `n_blocks=`;
  - MIN_TRADES is hard-wired in `_unit_record`.

## Additions vs the frozen code (configuration/composition or edit)

- t4 rows that enter only h60 and hF: panel-side. Set `ok_h120=False` on t4 rows. This works by
  composition only if pattern_search builds the Panel itself; the frozen clock/panel stage
  (clock.py, constants `N_DECISION_TIMES`) emits 3 times. Whether panel/targets can produce t4
  rows without an edit belongs to the panel area: UNKNOWN here.
- New features (r_ROD and its ratio to the 60-date median, plus literature features): composition
  through `Panel.feature_cols` and frame columns. They must be finite on every `ok_<h>` row used,
  or horizon_data raises (cpcv.py:340-341).
- Gate 0 waived: composition, by calling nested_cpcv and final_selection directly.
  `run_pipeline` would run gate0 (registering its entries) unless stopped; it has no skip flag,
  only `force_after_gate0_fail`.
- 45 configs, nested CPCV, the selection metric, PBO, DSR at an explicit N and the median-path t:
  all by calling the frozen functions. No edit is needed.
- Per-root runs versus one pooled 17-root portfolio: the code pools every root in the panel into
  one portfolio per validation set (score_split). How E.20 partitions the roots is not settled in
  this code: UNKNOWN.
