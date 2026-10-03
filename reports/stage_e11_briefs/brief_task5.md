# Brief: CanaryCoder-OpusXHigh (Task 5), leakage canaries, end-to-end wiring, dry runs

You are CanaryCoder-OpusXHigh, Task 5 of Stage E.11 in the PropExperiment repo
(/home/kiros-li/Documents/GitHub/PropExperiment). Tasks 2-4 have built ml_route_v2/ (signals, panel,
targets, models, CPCV, Gate 0, decision layer, sizing, portfolio, simulator, payout simulator). You
prove the pipeline is causal, wire it end to end, and measure it, on synthetic data only.

## Read first (by section, per CLAUDE.md "Context hygiene")
1. CLAUDE.md (invariants, context hygiene, compute limits incl. the overnight profile).
2. reports/stage_e11_interfaces.md (all; sections 0, 8, 9 are yours) and the deviations the lead
   lists at the end of this brief.
3. docs/STAGE_E_ML_V2_DESIGN.md V2.2b (Gate 0 and its canary semantics), V2.9 (leakage controls,
   nested CPCV), V2.11 (compute).
4. The ml_route_v2 modules' docstrings and public signatures (grep "^def \|^class " per module), not
   whole files.

## Objective
Write ml_route_v2/synthetic.py, ml_route_v2/pipeline.py, ml_route_v2/probe.py, tests/ml_v2_fixtures.py,
tests/test_ml_v2_leakage.py, tests/test_ml_v2_e2e.py, and reports/stage_e11_runtime_probe.md.

## Requirements
- synthetic.py: synthetic_universe(roots, first, last, seed, plant=None) -> SyntheticWorld (bars by
  price-path root and by vehicle root in the repo's BAR_COLUMNS, plus MES as a signal-only root;
  a release calendar object; the frozen D8 costs via screening.stage_e_frozen / ml_route.synthetic
  helpers). Calendars from the frozen group calendars over the requested dates (ml_route/synthetic.py
  shows how). plant= lets a test inject: a gross edge of a stated size in vehicle ticks tied to a
  named feature (e.g. the sign of the 60-minute return predicts the next h minutes with mean m), a
  binary edge (E[r | x] = beta x sign(x)), pure noise, a future-leaking column, etc.
- pipeline.py: run_pipeline(world, state_dir, configs=CONFIGS, timing=True) -> PipelineReport:
  panel (Task 2) -> c/sigma filter -> Gate 0 (Task 3; stop if it fails, as V2.2b says, unless a
  test passes force_after_gate0_fail=True) -> nested CPCV with selection_metric.score_split (Task 4)
  -> PBO, DSR at N_total from the ledger -> final selection and refit -> schedule (candidates) ->
  simulate.run_portfolio at 50K -> payout_sim for 50K and 150K, Standard and Consistency, DLL off and
  on. Resumable from state_dir (each stage writes its output and is skipped on restart). Records wall
  time and peak RSS per stage (resource.getrusage / tracemalloc where cheap) and the disk used by
  state_dir.
- tests/test_ml_v2_leakage.py, each canary shown to FAIL on a planted leak (the test asserts the
  guard raises or the edge vanishes), as V2.9 lists:
  1. a planted future bar: a feature computed from a bar that opens at or after t is caught
     (assert_causal / the perturbation test raises);
  2. a planted future release: a release whose timestamp is after t used in a feature at t is caught;
  3. a shuffled target: shuffling y_gross within each date (or across dates) must leave Gate 0 failing
     and the nested OOS Sharpe near zero (t well below 3);
  4. a normalizer that would peek: a z-score using the current or future date's rows is detected (a
     test-only peeking variant must change earlier values under perturbation while zscore_causal does
     not);
  5. a selection step that would see the test block: nested_cpcv raises (or the guard detects) when
     score_fn is handed outer test rows;
  6. a label that overlaps the test fold: the CPCV purge removes the training row whose exit crosses
     into a test date (assert it is absent from the training mask);
  7. a product whose bars are shifted by one minute (its bar timestamps one minute late relative to
     the clock, so a "closed by t" bar is really open): the causality checks catch it (e.g. a bar
     whose close is after t is read) - define the planted shift so that, without the guard, a feature
     at t would use information from after t, and show the guard catches it;
  8. Gate 0 canaries: (a) pure noise fails Gate 0; (b) a planted gross edge (mean on the confident
     quintile well above 2.5 x cost) passes Gate 0 and the cost gate trades it; (c) a planted binary
     edge between 1.5 x cost and 2.5 x cost passes Gate 0 and is then rejected by the cost gate at
     every k (no trades, or zero accepted trades); (d) an edge smaller than the cost fails Gate 0's
     1.5 x cost bar and, bypassing Gate 0, is also rejected by the cost gate. (The design's Gate 0
     bar is 1.5 x cost on the confident quintile and the loosest cost gate needs a predicted gross of
     2.5 x cost; the stage prompt's "an edge smaller than the cost must pass Gate 0 and then be
     rejected by the cost gate" is implemented as (c), and (d) covers the literal reading.)
  Also the window canary: a planted row dated 2024-03-01 or later in a training panel makes
  assert_window / the pipeline refuse.
- tests/test_ml_v2_e2e.py: a small end-to-end run (e.g. 4 products, ~300 dates, a reduced config
  list) that finishes in under about 2 minutes and checks: determinism (two runs, identical model
  sha256 and identical daily P&L), resumability (kill after Gate 0 and restart: no recomputation of
  finished stages), ledger N = N_program + configs + Gate 0 tests.
- probe.py and the dry runs (V2.11, Task 7 needs these figures):
  - Realistic size A: 28 products, the training window's date count (the real CME trade-date
    calendar 2019-05-06..2024-02-29, about 1,200 dates; use the frozen calendars, no bars), 3
    decision times, the full grid of 45 configurations, nested CPCV as designed.
  - Realistic size B: 8 products (the phase-1 subset's likely size), same calendar and grid.
  - The full nested CPCV may be long. FIRST time one complete outer split (all 45 configs over its
    4 inner folds plus the refit) at each size and extrapolate the full run (15 outer splits + the
    final selection over 15 splits + refit + Gate 0 + simulation + payouts). THEN, if the measured
    extrapolation for size B is under 90 minutes, run size B fully end to end (resumable, in the
    background with nice 10, logs to a file) and report the measured total; otherwise report the
    extrapolation only and say so. Size A: extrapolation from the timed split plus a full run of
    every non-CPCV stage (panel build, Gate 0, simulate, payouts).
  - Respect the overnight profile: at most 14 threads in total (LightGBM uses 8), at most two heavy
    jobs at once, combined peak memory under 70% of what `free` shows available just before launch
    (check it, and chunk if needed), nice 10, nothing between 15:30 and 16:00 PT.
  - reports/stage_e11_runtime_probe.md: per stage, wall time, peak RSS, disk, for sizes A and B
    (measured vs extrapolated clearly labelled), the machine (CPU count, RAM, GPU unused), the full
    grid's estimated time on the ThinkPad under the overnight profile, and how it splits into 8 to 10
    hour windows that pause cleanly at checkpoints (V12): which stage boundaries are checkpoints and
    what resumes.

## Boundaries
- Synthetic data only. Never open market data (data/processed*, data/vendor, data/sealed, *.parquet,
  *.dbn*), any Stage E result report, progress.md, docs/STAGES.md or .env.
- Write only the files above. If you find a bug in another worker's module, do NOT fix it: write a
  failing test that shows it (mark it xfail with reason "reported to lead: <id>") and report it.
- Run only the ml_route_v2 tests (`nice -n 10 uv run pytest -q tests/test_ml_v2_*.py` to a file under
  reports/stage_e11_briefs/, read the tail). Not the full suite. No agents, no commits, no network.

## Return
Paths written; the test result line; each canary and what it showed (caught: yes/no); the probe's
measured and extrapolated figures; any bugs found in other modules (with the failing test name); every
deviation from the interfaces file; a summary of at most 200 words; anything unfinished.

## Lead's deviations list (what Tasks 2-4 actually built, beyond reports/stage_e11_interfaces.md)
- Task 2 (signals, panel):
  - SignalContext.cache; Panel.counts; targets add entry_ts_ns; feature_cols drops the constant
    app_ flags; assert_window(mode) accepts "train" and "eval".
  - FAMILY_SIGNALS maps families to signals. The 3 CP ports are being POOLED across products right
    now (one feature per port variable): do not hard-code port signal names. Iterate the REGISTRY.
  - The test generator is ml_route_v2/signals/synthetic_bars.py. Reuse it, or build synthetic.py on
    it.
  - **The roll-blackout union is the caller's job:** pipeline.py must pass clock.exclude_union(...)
    into decision_rows(exclude=...).
  - Excluded families: K5-fomc-01, K6-wasdepost-01, K9-anncday-01.
  - A realistic 28-product panel build took 18 s and 3.3 GiB peak.
- Task 3 (models, CPCV, Gate 0):
  - SplitScore is in configs.py, re-exported by cpcv.py.
  - nested_cpcv and final_selection take admissible= and calendar=; gate0_family_a takes
    admissible=; gate0_family_b takes admissible=, calendar= and rule=.
  - Gate0Test has signal and root fields plus gross_ticks_sign.
  - Blocks are 0-based. cost_gate returns a NaN edge on no-trade rows.
  - Helpers: gate0_b_trades, gate0_b_pooled, holm, horizon_data, assert_fold, sharpe_variance,
    ConfigLedger.require.
  - Fit probe at 250k x 90: ridge 0.19 s; LightGBM depth 3 4.3 s, depth 2 3.1 s.
  - **DSR variance rule (lead):** the per-configuration Sharpe of the PATH-AVERAGED OOS daily
    series, the same matrix as PBO.
- Task 4 (portfolio, simulate, payouts):
  - AccountSpec has extra fields; TradeRecord has cluster and entry/exit times.
  - PortfolioRun has decisions, intents and combined_mll_breaches, plus the breached_combined
    property. Lead rule: any combined breach is an MLL breach in every verdict.
  - run_portfolio accepts the 50K account only.
  - score_split has a candidates_fn kwarg and drops candidates whose targets are missing.
  - accept_trades with d_fixed=None raises.
  - run_path, simulate_payouts and simulate_paths take ks=, keep_d_frac= (default 0.5) and a reset
    delay. simulate_payouts_pair returns ks on and off from one draw.
  - **Lead rule:** the ruin criterion is read with ks=False.
  - Payout sim timing: about 1.9 s per call at 10k x 252.
  - Kill switches act in the payout sim only. The CPI cap applies through the engine member only.
- pipeline.py must also report, for the economics, both account sizes (50K via the engine records,
  150K via payout_sim re-sizing), Standard and Consistency, DLL off and on, ks off (verdict) and on
  (context).
