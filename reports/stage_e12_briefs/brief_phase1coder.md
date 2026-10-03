# Brief: Phase1Coder-OpusXHigh (worker-xhigh, opus). Stage E.12 Task 1b

You are a worker in Stage E.12 (prompt: docs/prompts/STAGE_E.12.md; read its SCOPE, GUARDRAILS and
Task 6 only). The lead owns every design decision; anything not settled below that needs judgment
on a rule: stop and report it, do not decide it.

## Objective
Build the REAL-DATA entry point of ML route v2 for phase 1, so the lead can run, after the freeze
and the purchase: (1) build the phase-1 world and training panel from the frozen stores, (2) apply
the c/sigma filter, (3) generate and register the Gate 0 test list, (4) run Gate 0 once. Today the
pipeline only runs on ml_route_v2.synthetic.SyntheticWorld (ml_route_v2/pipeline.py:269
build_world_panel, :298 _filter, :321 _gate0). Everything you write is frozen and hashed by the
lead at Task 3 BEFORE any phase-1 data exists, so it must be right blind.

## HARD BOUNDARIES (a breach fails the stage)
- Read NO bar rows of any real store: no step 2 parquet row, no research parquet row, no MES row,
  no raw .dbn file. You MAY read parquet schema and file-level metadata only (pyarrow.parquet
  read_schema / read_metadata, and the JSON summaries reports/step2/bars_NG.json,
  reports/step2/purchase_NG.json) of data/processed_step2/NG/ and
  data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet, to match formats.
  Tests use synthetic fixture stores written in pytest tmp dirs (/tmp is a RAM tmpfs: keep
  fixtures small).
- Never open anything under data/sealed, data/vendor, any holdout or research store for rows.
- No Databento client, no key, no network.
- New code goes under ml_route_v2/ only (a new *.py under data/, screening/, rules/, sim/, funnel/,
  compute/, ml_route/ breaks the harness manifest). Do not edit any file under those dirs.
- Files you own: new ml_route_v2/phase1.py (or a small package ml_route_v2/phase1/), new tests
  tests/test_ml_v2_phase1*.py, and minimal edits to ml_route_v2/panel.py, ml_route_v2/pipeline.py
  and ml_route_v2/clock.py if needed (e.g. a `signals=` parameter). V23Coder owns constants.py,
  decide.py, cost_filter.py, portfolio.py, signals/ (including a new K9 signal) and gate0.py; do not
  edit them. If you need a constant, define it in your module with a comment citing the design
  section, or report it.
- No commits. Compute: nice -n 10, at most 6 BLAS/OMP threads, tests with
  `PYTHONPYCACHEPREFIX=<a fresh dir under /tmp/claude-1000/> nice -n 10 uv run pytest -q
  -p no:cacheprovider tests/test_ml_v2_*.py` (another coder runs tests at the same time).

## The rules to implement (lead decisions, frozen; cite them as "E.12 lead rule P-n")
- P-1 Roots available: the phase-1 price paths (the lead passes the vehicle list; each vehicle's
  price path is ml_route_v2.constants.UNIVERSE[v][1]) plus MES. MES bars come from its frozen
  confirmation store (path above; find how screening/stage_e_runner.py or data/stage_e_bars.py
  loads MES's confirmation leg and reuse that). The owned micro step 2 stores MCL, MGC, MHG are
  NOT price paths and are never read. A signal (signals.REGISTRY) is covered iff
  spec.own_path_only, or every root in spec.roots_read is available. Uncovered signals are left
  out of the panel and listed by name with their missing roots in the build report.
- P-2 Gate 0 list: family A = every panel signal (the covered signals, as gate0 uses
  panel.signal_names) x HORIZONS; family B = every admissible (vehicle, horizon) pair. Rows of
  family A at h are the ok rows of admissible pairs at h (gate0._family_a_horizon already does
  this). A test with < 2 dates keeps t NaN, p 1 and is counted. The list file
  reports/stage_e12_gate0_list.json holds: the rule text, the vehicles, the covered and uncovered
  signals, the admissible pairs, the ordered test ids with their ledger specs, |A|, |B|, and the
  inputs' fingerprints. Its sha256 is printed.
- P-3 S_X per price path: D4's frozen start rule. Reuse screening/stage_e_start_dates.py
  (product_start_rule / start_rule; read its docstring): it reads ts_event, volume and trade_date
  only (never a price) of the root's research store (sha256 must equal E.2a's recorded value,
  screening.stage_e_frozen) and step 2 store. MES: D4's fixed 2020-02-03 (stage_e_start_dates
  mes_from_d1f). If the set-file machinery cannot take a partial set, call the per-root function and
  record S_X, V_ref, the monthly medians' source and both store sha256s in the build report; do
  not write reports/stage_e_start_rule_*.json. A root whose window is empty is dropped by name.
  Each root's bars are cut to trade dates [S_X, 2024-02-29] (data.stage_e_bars.load_confirmation_leg
  takes the start and the store sha256; use it, it also enforces the trade-date refusals and gives
  the roll blackout, L-8).

## What to build
1. `phase1_world(vehicles, *, step2_root, research_root, mes_path, ...)` returning an object with
   the fields build_world_panel and the Gate 0 stage read (mirror SyntheticWorld: vehicles, first,
   last, bars_first, calendar, bars, releases, costs, blackout, legs; frames may be empty: no engine
   in this stage). Sources, all frozen:
   - bars and blackout per root: data.stage_e_bars (above);
   - training calendar (V2.9): every CME trade date from the earliest phase-1 S_X to 2024-02-29 of
     at least one phase-1 group calendar (data.group_session.load_group_calendar);
   - decision rows: V2.2 exclusions (own roll blackout; early-halt and early-close dates of the
     group calendar; CPI-window entries are the engine's). Check that ml_route_v2/clock.py applies
     the group calendar's early-halt/early-close exclusion with real calendars; if it does so only
     for synthetic ones, fix it with a pure real-calendar adapter and a test, and say so;
   - releases: screening.stage_e_rules.load_release_calendar (reports/stage_e2b_release_calendar.json);
   - costs: the same frozen D8 inputs the synthetic world uses (see synthetic.py: how `costs` is
     built), for the real vehicles;
   - vendor-degraded dates: from each store's summary (reports/step2/bars_<ROOT>.json), reported
     and kept (V2.2, NULL_CRITERIA_E 4).
   Window guard: refuse any bar or row dated on or after 2024-03-01 (constants.FORBIDDEN_FROM),
   run panel.assert_window(train).
2. CLI `python -m ml_route_v2.phase1 <step>` (each step resumable, each refusing to run unless
   `--harness-sha256 <sha>` passes screening.harness_freeze.preflight AND `--freeze-sha256 <sha>`
   verifies the v2 freeze manifest reports/stage_e12_ml_v2_freeze.json: the file's own sha256
   equals the argument and every listed file's sha256 matches on disk. Manifest format:
   {"schema": "ml_v2_freeze/1", "files": [{"path": "...", "sha256": "...", "bytes": n}], ...};
   write `verify_v2_freeze(path, expected_sha256)` and test it):
   - `build --vehicles V1,V2,... --state-dir DIR`: world, panel (build_world_panel's logic on the
     real world), c/sigma table at the frozen tau (cost_filter.c_sigma_table reads tau from
     constants), risk table. Writes reports/stage_e12_phase1_bars.json (per root: S_X, store sha256,
     trade dates, rows per vehicle and horizon, warm-up rows dropped, degraded dates, roll blackout
     dates count; uncovered signals) and reports/stage_e12_c_sigma.json (every (vehicle, h): c, sigma,
     ratio, admissible; dropped pairs listed with ratio). Saves the panel + filter to DIR with the
     constants fingerprint (fingerprint.constants_fingerprint) and an input fingerprint. Prints counts
     only, never a return, mean or t.
   - `register --state-dir DIR --ledger ledger/ml_v2_config_ledger.jsonl`: builds the P-2 list from
     the saved panel and filter, writes reports/stage_e12_gate0_list.json, registers every test in
     configs.ConfigLedger (the same ids/specs gate0._register_a/_register_b would write, so the
     later run's registration is a no-op), prints the list sha256, |A|, |B|. Computes no statistic.
   - `run --state-dir DIR --ledger ... --expected-list-sha256 SHA`: verifies the list file's sha256
     and that every test is registered, then runs gate0_family_a, gate0_family_b, gate0_verdict,
     gate0_b_trades/gate0_b_pooled exactly as pipeline._gate0 does (no rule of yours). Run-once
     guard: if DIR holds a completed result marker, refuse; a partial run resumes from gate0's B
     state (same inputs and constants fingerprint, else refuse). Writes reports/stage_e12_gate0.json
     (every test: id, family, signal or root, horizon, n_dates, n_obs, mean, t, p, Holm rank,
     threshold and decision; B: mean gross ticks vs cost ticks and the multiple, t_B, n_trades;
     A: Spearman IC and sign-gross; pooled B; verdict PASS/FAIL and passing pairs; N contributed
     |A|+|B|; fingerprints) and reports/stage_e12_gate0.md (the same, readable).
3. Tests (tests/test_ml_v2_phase1*.py): fixture stores in the real formats (schema and metadata
   as read above) for 2-3 synthetic roots + MES; the coverage rule; S_X cut; the window guard
   refusing a 2024-03-01 row; the list rule and its registration being a no-op for the later run;
   the list-hash refusal; the run-once refusal; a resume after an interrupted family B; the freeze
   verification (good, tampered file, wrong sha); and an end-to-end build->register->run on the
   fixture world where a planted gross edge passes and noise fails (reuse synthetic.py plants if
   you can feed them through the fixture stores; otherwise state why not).

## Memory
The real phase 1 may hold 10-25 products x ~1,150 training dates. Keep peak memory well under
4 GB for 25 products (float32 where gate0/cpcv allow; free bars after the panel). Measure the
fixture run's peak and extrapolate in your report.

## Return (at most 200 words) + files
Write reports/stage_e12_briefs/phase1coder_report.md: files changed with line counts, how each rule
P-1..P-3 is implemented (file:line), every assumption, test count and result (the exact pytest
summary line), memory estimate, and anything you could not finish or that needs a lead ruling.
Return its path, a summary, and open items.
