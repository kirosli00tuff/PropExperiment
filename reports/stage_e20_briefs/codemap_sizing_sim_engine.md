# Stage E.20 code map: sizing, simulator, engine stage, payouts (read-only)

Area: sizing-sim-engine. Mapper: read-only, code read by section; no data store opened; no E.12
Gate 0, E.15, E.17 or E.18 result read. Repo HEAD abfdeb8 (2026-10-11).
Files read: ml_route_v2/{sizing,simulate,engine_stage,payout_sim,account,killswitch}.py in full by
section; ml_route_v2/portfolio.py, constants.py, pipeline.py (stages 5, 7-9), selection_metric.py,
cpcv.py (NestedResult only), phase1/world.py (Phase1World fields), synthetic.py (engine_frames);
screening/stage_e_rules.py (StageERules fields, costs, _opening_refusal, gate);
screening/stage_e_engine.py (run_engine, MAX_ENTRIES_PER_DAY); rules/products.py and
rules/constraints.py (member caps).

Hash status. Every ml_route_v2/*.py named below is in reports/stage_e12_ml_v2_freeze.json
`files` (91 entries, including constants.py, portfolio.py, pipeline.py, cpcv.py, synthetic.py,
phase1/*). screening/stage_e_rules.py and stage_e_engine.py are not in that list. They are in the
Stage E harness freeze (reports/stage_e2b_harness_freeze.json, and reports/stage_e16_freeze.json
lists stage_e_rules.py), and the parent-method sha256 pins are in the v2 tests
(simulate.py:3-4).

---------------------------------------------------------------------------------------------
## Q1. Sizing at 50K (V2.8)

Constants (constants.py:99-125): DAILY_SIGMA_FRACTION 0.10, TRADE_LOSS_FRACTION 0.25,
RISK_SPLIT_M 3, RISK_ROUND_UP_RATIO 2.0, MAX_OPEN_POSITIONS 3, MAX_OPEN_PER_CLUSTER 1,
PER_PRODUCT_LOT_EQUIVALENTS 1.0, PORTFOLIO_TIER_MARGIN_LOTS 0.1, BEYOND_QC_EXTRA_TICKS_PER_SIDE 1.0,
RELEASE_WINDOW_BEFORE_MIN 5, RELEASE_WINDOW_AFTER_MIN 30, RELEASE_WINDOW_TIER_FRACTION 0.5.
KS constants are at constants.py:109-118 (KS1 0.30, KS2 0.50 / x0.5, KS2b 0.25, KS3 5 dates).

sizing.py (FLOOR_GUARD 1e-9 on every floor, sizing.py:42-46):
- `risk_budget_usd(d_open: float) -> float` (55): b = 0.10 x D_open / sqrt(3).
- `daily_variance_budget(d_open: float) -> float` (60): (0.10 x D_open)^2, in $^2 (D-03).
- `budget_use(n: int, sigma_ticks: float, tick_value_usd: float) -> float` (65): (n x sigma$)^2.
- `budget_contracts(remaining_var: float, sigma_ticks: float, tick_value_usd: float) -> int` (70).
- `excess_cost_ticks(n: int, q_c: int | None) -> float` (77): 2 x 1.0 x (n - q_c)^+ / n (D-08a).
- `contracts(*, d_open, d_now, sigma_ticks, loss_ticks, cost_ticks, tick_value_usd, product_cap:
  int, capacity_contracts: int, multiplier: float = 1.0, budget_var: float | None = None) -> int`
  (85-111). n_risk = floor(b x mult / sigma$); rounding band at 105-106: n_risk 0 -> 1 if
  sigma$ <= 2.0 x b x mult; loss cap n_loss = floor(0.25 x D_now / ((L + c) x tick value)) (107);
  n = min(n_risk, n_loss, product_cap, capacity), then min with budget_contracts when budget_var
  is given. The budget is not scaled by KS2 (docstring 11-18).

portfolio.py (caps; one admission rule shared by the fixed-D metric and the engine member):
- `admit(*, root, cluster, sigma_ticks, loss_ticks, cost_ticks, d_open, d_now, book:
  Sequence[OpenPosition], tier_tenths: int, release_window: bool, multiplier: float = 1.0,
  extra_cap: int | None = None, budget_var: float | None = None) -> Admission` (162-195). The order
  is: risk_unknown, then product_open (one open position per product), then max_open_positions (3),
  then cluster_open (1 per cluster), then capacity = (tier - MARGIN_TENTHS - open tenths) //
  lot_tenths, then cap = product_cap (or min with extra_cap = the CPI cap), then sizing.contracts,
  then the release window: refused, not re-sized, if `release_window_binds(open_tenths + n x
  lot_tenths, tier_tenths)`. Reasons: "release_window", "risk_budget_spent", "size_zero".
- `release_window_mask(fill_ns: np.ndarray, release_ns: np.ndarray) -> np.ndarray` (91):
  [r - 5, r + 30) min, half-open.
- `release_window_binds(open_tenths_with_entry, tier_tenths) -> np.bool_ | np.ndarray` (108):
  open > 0.5 x tier (50K: 1.0 / 1.5 / 2.5 lots).
- `vehicle_facts(root: str) -> VehicleFacts` (132, @cache): tick value, lot_tenths, product_cap =
  min(rules.products.member_cap_contracts(root), floor(1.0 lot / weight)), q_c and commission from
  screening.stage_e_frozen.leg_inputs(root, traded=True).
- `base_tier_tenths(account) -> int` (198, fixed D), `live_tier_tenths(account,
  prior_close_balance_usd) -> int` (204, engine). MARGIN_TENTHS = round(0.1 x 10) = 1 (82).
- Fixed-D path: `admission_record(cands, risk, account, *, d_fixed)` (264) and
  `accept_trades(..., d_fixed)` (310). Per-date variance budget dict, base tier.
- D9.11 caps: rules/products.py:207 VOLATILITY_CAP_50K {"MCL": 10, "MGC": 10, "CL": 1, "GC": 1,
  ...}; member_cap_contracts (products.py:225) = min(MEMBER_CAP_TENTHS 10 // weight, vol cap).
- D9.12 CPI cap: simulate.PortfolioMember._cpi_cap (simulate.py:316): 0 inside the CPI window,
  else CPI_MICRO_MAX_50K = 3 (rules/constraints.py:26). Engine member only. Not in the fixed-D
  metric or payout_sim.
- Per-vehicle facts for the 17 E.20 vehicles (from vehicle_facts at run time; no data read):
  product_cap 1 for every mini, 10 for MNQ, M2K, MGC and MCL; q_c 1 for all except MCL 4 and M2K 3.
- account.py: `tier_max_lots(account, prior_close_balance_usd) -> float` (130),
  `tier_max_tenths(...) -> int` (142), `payout_cap_usd(account, path_type, dll) -> float` (147),
  `trail_floor(account, prev_floor_usd, eod_balance_usd) -> float` (155). ACCOUNT_50K (74-92):
  MLL $2,000, DLL $1,000, base 2 lots, then 3 lots at >= $1,500 and 5 above $2,000.
  ACCOUNT_150K (94-127).
- killswitch.py: `KillSwitches` frozen dataclass (41-95): start_day, end_day, ks1_threshold,
  on_day_pnl, on_entry, size_multiplier. Also `ks4_fires` (98), `ks5_blocks_entry` (108),
  `ks5_flatten_due` (117). KS1 to KS4 are used only in payout_sim; the engine member uses none of
  them (C-11).

---------------------------------------------------------------------------------------------
## Q2. Which series feeds the training-window verdict

- The nested OOS daily series comes from the fixed-D fast path, NOT from the engine. The chain:
  cpcv.nested_cpcv (cpcv.py:669-704) builds `path_daily` (dates x 5 paths, 644, 691) from each
  unit's `score.daily`, and score_fn = pipeline.score_fn_for(risk) = selection_metric.score_split
  (pipeline.py:350). score_split (selection_metric.py:75-96) calls accept_trades with
  d_fixed = account.mll_usd ($2,000), then fixed_d_daily_pnl (portfolio.py:336) over every
  validation date, with zeros on no-trade dates.
- pipeline._stats (pipeline.py:391-416) is the "stats" stage:
  - criterion 2: `median_path_t` = median of `_daily_t` (mean / (sd ddof 1 / sqrt n), 367) over
    path_daily's 5 columns;
  - annualized Sharpe: mean / sd (ddof 1) of `avg` = path_daily.mean(axis=1), x
    sqrt(TRADE_DATES_PER_YEAR);
  - DSR: `cpcv.dsr_at_n(avg, n_total, sharpe_variance(finite config_sharpes))` (cpcv.py:769, 761),
    with n_total = ledger.n_total(n_program);
  - PBO: `cpcv.pbo_cscv(nested.config_daily)` (cpcv.py:735). config_daily is the 45 configs'
    CPCV OOS daily, each averaged over the 5 paths (cpcv.py:650-666). config_sharpes uses the
    population sd (cpcv.py:646, 703).
- Engine series: run_engine_path returns `daily` = PortfolioRun.daily (simulate.py:614-620,
  path-dependent D, kill switches off). It is stored in engine/path_<j>.pkl but no code feeds it
  into _stats, PBO or DSR (grep: no consumer outside engine_stage).
- Criterion 7 reads the engine record: run_payout_paths uses each path's `days` (DayRecords of
  engine TradeRecords, simulate.py:574-611), re-sized in payout_sim.
- Criterion 6 (30 round trips per product): the engine summary carries `trips_by_root`
  (engine_stage.py:189). No code computes criterion 6, or the combination of combined-MLL breaches
  into a verdict. Which record criterion 6 should read: UNKNOWN in code.
- Gate 0 waiver: run_pipeline always runs the "gate0" stage and stops on a fail unless
  `force_after_gate0_fail=True` (pipeline.py:535-608). The stage functions (nested_cpcv, _stats,
  _nested_schedule, _simulate_stage, _payouts_stage) are module-level and callable directly.
  That is composition, with no edit.

---------------------------------------------------------------------------------------------
## Q3. Engine path

PortfolioRules(StageERules) (simulate.py:152-196, frozen dataclass), the differences from
StageERules (stage_e_rules.py:277-290: fields legs, window_dates, blackout, releases,
restart_on_terminal, mask_hindsight_fields, phase):
1. `_opening_refusal` runs the parent on `_PerProductRun` (simulate.py:134-149, read-only view
   with traded = (root,)). The parent's `others` check (stage_e_rules.py:524-526,
   engine_second_leg_position) is therefore always empty, so several products can be open. The
   `check_member_size` check (527-531) then applies D9.5 and D9.11 per product only.
2. New field `product_blackout: Mapping[str, frozenset[date]] | None`. When set, the parent runs on
   `replace(self, blackout=own set)`, so each product gets its own roll blackout.
   `__post_init__` raises if any leg lacks a set.
3. `fill_cost` / `close_cost` add the beyond-q_c cost (`_beyond_q_c`, 178-186) for market fills.
   Everything else is inherited: `gate` (scaling plan over ALL products, stage_e_rules.py:557-569),
   MAX_ENTRIES_PER_DAY = 20 per root (stage_e_engine.py:70; constants.MAX_ENTRIES_PER_PRODUCT_DAY
   = 3 is not referenced by any v2 module except constants.py), the real-time and EOD MLL, the
   forced flatten and the D9.5a guard.

`build_rules(roots, frames, rules_kwargs) -> PortfolioRules` (simulate.py:623-638): it accepts the
keys window_dates, releases, legs (override of leg_inputs), product_blackout, blackout, plus any
other StageERules field.
`run_portfolio(frames, schedule, risk, *, account=ACCOUNT_50K, rules_kwargs=None) -> PortfolioRun`
(641-662): 50K only (it raises otherwise). roots = the schedule's roots.
PortfolioMember(schedule, risk, account, *, cpi=()) (230-397): plans keyed by (root,
decision_ts_ns); duplicates raise (237). D_now = balance + unrealized - floor; D_open and the
variance budget reset at each trade date's first minute (290-296); the budget is spent at intent
issue (377). Exits are market at exit_ts. hF, or an exit inside the flatten window, is left to the
engine's forced flatten (331-343). horizon must be literally "hF" for the hold-to-flatten branch.

Combined MLL audit: `combined_mll_audit(result: EngineResult, frames: Mapping[str, pd.DataFrame],
rules: StageERules) -> tuple[CombinedMllBreach, ...]` (simulate.py:505-543). It replays the
engine's Fill ledger with FIFO. At grid minutes with >= 2 open legs it computes realized balance +
each leg's adverse-extreme unrealized and compares it with the floor in force, before the engine's
own first breach. TIE_CENTS 1e-6. `PortfolioRun.breached_combined` (416). Docstring rule: any
combined breach counts as an MLL breach in every verdict. engine_stage stores only the count
(`combined_breaches`, 190). payout_sim does not read it.

engine_stage.py (docstring 1-39):
- `prepare_engine(world: Any, schedules: Mapping[int, pd.DataFrame], paths: Sequence[int],
  engine_dir: Path) -> EngineInputs` (143-165). It writes `<engine_dir>/frames/<root>.pkl` once
  per traded vehicle via `world.engine_frames([root], calendar)[root]`, plus frames/meta.pkl (a
  world mismatch raises). It reads `world.vehicles, .calendar, .seed, .plant, .blackout,
  .releases, .engine_blackout()`, and own_blackout uses UNIVERSE[v][1] (pipeline.py:260-266).
  - FACT: `Phase1World` (phase1/world.py:466-486) has no `engine_frames` or `engine_blackout`
    method and `frames` is empty ("No engine runs in this stage", world.py:7). Only SyntheticWorld
    implements them (synthetic.py:111-128, using the module function
    `synthetic.engine_frame(vehicle, path_bars, dates)` at 373).
  - No real-data engine run exists in the repo: grep finds no caller of prepare_engine,
    run_portfolio or engine_frames outside ml_route_v2/ and tests/.
  - A real-data world object with these two methods is composition (prepare_engine takes
    `world: Any`), with no edit.
- `run_engine_path(engine, sched, risk) -> dict` (174-194): it loads only that path's vehicles'
  frames and returns days, daily, n_trips, trips_by_root, combined_breaches, engine_breaches,
  minutes_processed, and kill_switches "off".
- `run_engine_paths(engine, schedules, risk, paths, ckpt_dir, *, isolate: bool) -> dict[int,
  dict]` (218-234): one checkpoint `path_<j>.pkl` per path, with fingerprint = constants
  fingerprint + frame hashes of sched and risk + world_fp + blackouts (110-119). A mismatch raises
  PipelineError and a restart skips finished paths. With `isolate`, each path runs in its own
  spawned process, one at a time (205-215), and engine_peak_rss_mb is kept. The pipeline default
  is ISOLATE_ENGINE_PATHS = True (pipeline.py:115).
- `_simulate_stage` (pipeline.py:514-524) clears `held` (the world) and gc's before the engine.
- Memory (reports/stage_e11_runtime_probe.md:90-99, synthetic size A, 28 vehicles):
  - before FIX 3: simulate, one path, 341 s, 7,198 MB peak;
  - after FIX 3: frames to disk 32.2 s, +1,841 MB disk; one path inline 310.6 s, 4,778 MB;
    isolated, 802 MB parent + 4,669 MB child (22,084 candidates, 6,597 trips);
  - total grid 43.9 min, 4.8 GB.
  No real-data figure was found (stage_e12_STATE.md has no simulate or payout line).

---------------------------------------------------------------------------------------------
## Q4. Payout simulation (criterion 7)

- Inputs: `Sequence[DayRecord]` (payout_sim.py:164) of `TradeRecord` (111-161), from the engine
  path via simulate.trade_records / day_records. Each record has per-contract net P&L and worst
  excursion in $, sigma/loss/cost ticks, tick value, lot_equiv, cluster, entry/exit ns, q_c and
  release_window.
- `bootstrap_indices(n_days, n_paths, horizon, block_mean, seed) -> np.ndarray` (508): a
  stationary block bootstrap with mean block PAYOUT_BLOCK_MEAN 10, seed constants.SEED.
- `simulate_paths(days, account, idx, *, path_type, dll, ks=True, restart=True,
  reset_delay_dates=2, keep_d_frac=0.5, ks2_sizing=None) -> PathArrays` (524). It is vectorized,
  and a test pins it to `run_path(days, account, *, path_type, dll, ks=True, restart=False, ...)
  -> PathResult` (273).
- Re-sizing per trade (run_path 354-361; `_contracts_vec` 463):
  - D comes from the path; capacity = tier at the prior close - MARGIN - open tenths; product_cap
    from vehicle_facts;
  - KS2's multiplier, the variance budget and the release-window refusal apply;
  - no MAX_OPEN, cluster or CPI checks are applied (they bound the engine trades already taken);
  - P&L scales linearly with n', plus the D-08a re-pricing (`resize_adjustment_usd`, 155).
- `simulate_payouts_pair(days, account, *, path_type, dll, n_paths=PAYOUT_PATHS (10_000),
  horizon=252, block_mean=10, seed=SEED, n_accounts=5, ks_values=(True, False),
  reset_delay_dates=2, keep_d_frac=0.5, ks2_sizing=True) -> dict[bool, PayoutSummary]` (737).
  It uses one draw for both ks values. The verdict entry is `False` (KS1, KS3, KS4 off; KS2
  sizing on). `simulate_payouts(...)` (721) is the single-ks wrapper.
- `summarize(...) -> PayoutSummary` (703). PayoutSummary fields (680-700): ruin_prob (D <= 0.25 x
  MLL at a close, or a breach), breach_only_prob, halt_prob, monthly net mean / median / p10 / p90
  (x5 accounts), p_any_payout, expected_resets, and others.
- engine_stage `run_payout_paths(sim, n_paths, ckpt_dir) -> pd.DataFrame` (271-288) loops per
  nested path j over 50K and 150K x Standard and Consistency x DLL off/on. That is 8 pair calls
  and 16 simulate_paths calls per path. Rows carry `verdict_reading = not ks`, n_trips and
  empty_schedule (C-03 NaN rows for an empty path). There is one checkpoint per path (fingerprint:
  days, n_paths, constants fingerprint).
- How the 5 per-path ruin_prob values combine into one criterion-7 figure: UNKNOWN. No code does
  it; the engine_stage docstring (35-39) only mentions an "average over the path column".
- Runtime (synthetic, 28 vehicles): payouts for one path took 54.3 s / 4,630 MB before FIX 3, and
  51.7 s after it (2,414 MB inline, 802 MB isolated); 5 paths take about 4.5 min
  (runtime_probe:92-98).
- n_days = the path's number of closed engine dates (every DayClose date, zero-trade dates
  included, simulate.py:603-611).

---------------------------------------------------------------------------------------------
## Q5. Dependence on the 28-exposure universe; 17-root subset

- UNIVERSE (constants.py:22-33) holds all 17 E.20 vehicles: NG, MNQ, ZN, 6E, MGC, ZC, ZT, ZF, ZB,
  UB, TN, MCL, ZL, ZS, M2K, HE, LE. In my area it is read only in these places:
  - simulate.py:310, as a fallback cluster when a held root has no plan;
  - pipeline.own_blackout (266), which needs every world vehicle in UNIVERSE;
  - synthetic.engine_frames (UNIVERSE[v][1] = price path).
- Clusters: the member and accept_trades take `cluster` from the schedule or candidate row. The
  per-cluster cap (1) and MAX_OPEN (3) are absolute counts that do not depend on the universe size.
  With 17 roots, K7 (MBT) is absent and K3 and K5 have a single vehicle each (6E, MGC).
- Per-product and D9.11 caps: per root from rules.products / leg_inputs, with no universe list.
  All 17 resolve in vehicle_facts (run at map time). leg_inputs raises for a root that is not an
  E.2a traded vehicle (stage_e_frozen.py:268-273).
- run_portfolio, build_rules, PortfolioRules and run_engine_path use the schedule's roots only, and
  product_blackout is subset to them (engine_stage.py:184-185). So a 17-root subset passes with no
  edit, provided the world object exposes vehicles = the 17 and the methods listed in Q3.
- Outside my area but observed: panel.py:102-103 one-hots `id_root_<v>` over all 28 UNIVERSE
  vehicles and all 7 CLUSTERS. Absent vehicles give constant-zero columns. probe.py:114-118
  accepts only 28 or 8 products (the CLI only).
- Any change to constants.py (for example N_DECISION_TIMES = 3, MAX_ENTRIES_PER_PRODUCT_DAY = 3,
  UNIVERSE) is an edit to a hashed file. It also changes constants_fingerprint, which
  invalidates every engine and payout checkpoint (engine_stage.py:112, 276).

t4 in this area: the member and the engine key entries by (root, decision_ts_ns) and impose no
count of decision times. PortfolioMember._windows (264-272) derives each root's trading interval
from its plans, so t4 rows are covered with no edit. A t4 h60 exit at F_X falls to the engine's
forced flatten (343). A t4 row while that root's t3 h120 trade is still open is skipped as
"product_open" (admit 172-173). The engine per-root entry cap is 20 (not binding at 4 times).
Risk is joined by (root, horizon), or by row-level sigma_ticks / loss_ticks when the row carries
them (portfolio.join_risk 227), so t4 rows use the same (root, h) risk unless the caller attaches
row values (cost_filter: outside this area).

---------------------------------------------------------------------------------------------
## Q6. The 1.5 x slippage re-pricing

- Constant COST_SENSITIVITY_SLIPPAGE_MULTIPLE = 1.5 (constants.py:156).
- Implemented in `portfolio._trade_cost_ticks(base, n, roots, slippage_multiple)` (322-333): cost =
  commission + m x (D8 cost + beyond-q_c surcharge - commission), in ticks. It is called by
  `fixed_d_daily_pnl(accepted, targets, *, slippage_multiple=1.0)` (336-372), which is called by
  `selection_metric.score_split(..., slippage_multiple=1.0)` (75).
- Driven by `pipeline._nested_schedule(panel, nested, configs, admissible, risk=None,
  risk_fn=None, multiples=(1.0, 1.5)) -> dict` (438-511). It re-scores each outer split's selected
  refit at each multiple with the split's own risk table and assembles the 5 paths
  (`assemble_record`, 419). The 1.0 x record must match nested.path_daily within $1e-6 or it raises
  (497-503). Outputs: `path_daily_by_multiple` and `cost_sensitivity` = record_figures (median-path
  t, Sharpe, daily mean) per multiple (380-388).
- Not implemented: the engine (PortfolioRules / StageERules._market_cost use leg.costs at 1.0x)
  and payout_sim have no slippage multiple. PBO and DSR are not re-computed at 1.5x.
- Interface fact: build_rules accepts a `legs` override in rules_kwargs (simulate.py:633), but
  engine_stage.run_engine_path does not pass one (180-186).

## UNKNOWN / not established
- How criterion 7 aggregates the 5 per-path ruin_prob values, and which record (engine or fixed-D)
  criterion 6 counts: no code computes either.
- Real-data runtime or memory of the simulate and payouts stages: no measurement on disk.
  Synthetic figures only.
