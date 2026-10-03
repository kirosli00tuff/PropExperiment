# Stage E.11 return: ML route v2, design draft and the pipeline built on synthetic data

Lead Opus 5.5 (claude-opus-5-5), effort xhigh; ultracode off. Run 2026-10-03 01:03 PDT to
06:33 PDT, unattended, with one usage-limit pause, 03:58 to 04:10. No market data read,
nothing bought, nothing trained on real bars, no freeze. Two commits: harness v7 (5931e30) and the
stage commit (section 2).

## 1. Verdict summary

**Design.** docs/STAGE_E_ML_V2_DESIGN.md is a DRAFT pre-registration:
- 51 of 54 K1-K9 families as causal features (ports pooled), plus 24 generic signals;
- ridge as the primary model, shallow LightGBM as the only challenger, 45 configurations under
  nested combinatorial purged cross-validation (CPCV);
- a cost gate, drawdown-distance sizing with a daily risk budget, kill switches and a payout
  simulation.

**Gate 0 comes first, on phase-1 data.** It audits gross out-of-fold edges pooled over the
signals. It passes if some product-horizon pair shows a gross mean >= 1.5 x cost with t >= 3,
after Holm 0.05. Otherwise v2 stops.

**Success bar:** median-path t >= 3, DSR > 0.95 at the full N, PBO < 0.5, and ruin <= 10% (a
breach or the halt level). The research window is a screen only.

**Build.** ml_route_v2/ passes 704 tests on synthetic data. Every leakage canary catches its plant,
9 of 9 guard mutations break their canary, and the engine day and the payouts match to the cent.

**Runtime.** One overnight window: 20.4 min measured at 8 products, about 44 min at 28.

**Fable.** Design: 2 blocking, 7 should-fix, 15 notes. Code: 0 blocking, 2 should-fix, 10 notes.
All ruled, and all fixed except C-10, which is deferred.

**Harness v7:** eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4.

**The user owes 19 decisions.** The key ones: the coupled Gate 0 bar, cost-gate reading and tau;
the phase-1 subset and its volatility proxy; the 2010 extension; kill switches; the 150K
parameters; deployment; and the Live Funded risk.

## 2. Guardrail evidence

Start (reports/stage_e11_briefs/start_checks.txt; checks.sh). The first command, at 01:03, showed a
clean tree at 5c28a92, the commit holding the E.11 prompt.

```
$ date
Sat Oct  3 01:04:25 AM PDT 2026
$ git status --short
?? reports/stage_e11_briefs/
$ git log --oneline -3
5c28a92 docs: Stage E.11 prompt revised with research findings and V22
ac7ea2e docs: V22 income path and first-purchase data plan
93ede83 docs: Stage E.11 prompt (ML route v2 design and build) and V21
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
preflight OK: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
```

Start suite (`uv run pytest -q -p no:cacheprovider`, nice 10; reports/stage_e11_briefs/pytest_start.out):
`5582 passed, 2 skipped, 1 xfailed, 54 warnings in 1023.08s (0:17:03)`, exit 0.

End (reports/stage_e11_briefs/end_checks.txt, before the stage commit):

```
$ date
Sat Oct  3 06:32:27 AM PDT 2026
$ git status --short
?? docs/STAGE_E_ML_V2_DESIGN.md
?? ml_route_v2/
?? reports/E.11_RETURN.md
?? reports/stage_e11_STATE.md
?? reports/stage_e11_briefs/
?? reports/stage_e11_interfaces.md
?? reports/stage_e11_keyfix.md
?? reports/stage_e11_review.md
?? reports/stage_e11_rulings.md
?? reports/stage_e11_runtime_probe.md
?? reports/stage_e11_signal_coverage.md
?? tests/ml_v2_fixtures.py
?? tests/test_ml_v2_blackout.py
?? tests/test_ml_v2_clock.py
?? tests/test_ml_v2_configs.py
?? tests/test_ml_v2_cpcv.py
?? tests/test_ml_v2_decide.py
?? tests/test_ml_v2_e2e.py
?? tests/test_ml_v2_engine_stage.py
?? tests/test_ml_v2_gate0.py
?? tests/test_ml_v2_killswitch.py
?? tests/test_ml_v2_leakage.py
?? tests/test_ml_v2_models.py
?? tests/test_ml_v2_normalize.py
?? tests/test_ml_v2_panel.py
?? tests/test_ml_v2_payout.py
?? tests/test_ml_v2_portfolio.py
?? tests/test_ml_v2_probe.py
?? tests/test_ml_v2_signals.py
?? tests/test_ml_v2_simulate.py
?? tests/test_ml_v2_sizing.py
?? tests/test_ml_v2_state_fingerprint.py
?? tests/test_ml_v2_targets.py
$ git log --oneline -3
5931e30 feat: harness v7, per-account Databento keys (sha256 eee8a8b9)
5c28a92 docs: Stage E.11 prompt revised with research findings and V22
ac7ea2e docs: V22 income path and first-purchase data plan
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4
preflight OK: eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
```

End suite (reports/stage_e11_briefs/pytest_end.out): `6320 passed, 2 skipped, 2 xfailed, 54 warnings in 1223.21s (0:20:23)`, exit 0, 06:11 to 06:32 (the second xfail is C-1, documented).

Notes:
- The manifest checks ran against v6 (9a8ebe73...) at the start and v7 (eee8a8b9...) at the end.
- The harness v7 commit 5931e30 holds exactly data/config.py, tests/test_stage_e_config_keys.py and
  reports/stage_e2b_harness_freeze.json. The v6-to-v7 file diff is data/config.py (changed) plus the
  new test (added), with nothing else.
- No key was printed or logged: a no-print scan of the 3 .env values against 18 new files found 0
  hits (01:37).
- REGISTRATION.md stayed 0 bytes. Both holdouts stayed all_ok with 0 unlocks, and the ledger is
  unchanged (17,400 lines, same sha256).
- No Databento call, no quote, no purchase, no push.
- No frozen design document, member module, docs/NULL_CRITERIA* file, live/ or ops/ was edited.
- The stage commit holds exactly what the prompt names: ml_route_v2/, its tests (tests/test_ml_v2_*.py,
  tests/ml_v2_fixtures.py), the design draft, the interfaces, the runtime probe, the review and the
  rulings. It adds this return, progress.md and docs/STAGES.md, which the deliverable requires.
- Left untracked on disk, for the user to commit or discard: reports/stage_e11_STATE.md,
  reports/stage_e11_briefs/ (briefs, logs, checks, cost script), reports/stage_e11_keyfix.md and
  reports/stage_e11_signal_coverage.md. The design cites the last one, which holds each signal
  family's coverage evidence.
- No Stage E screen or confirmation figure was opened. Workers were barred from result reports; the
  lead read only the frozen tables, rules, calendars and code.

## 3. Results per task

### Task 1: the design draft (docs/STAGE_E_ML_V2_DESIGN.md, DRAFT)
Sections V2.0 to V2.12 each carry a stated rule or a bounded grid. In brief:
- **V2.0, economics:**
  - dollar arithmetic at S = 1.0, 1.5 and 2.0 for 50K, 150K and 5 x 150K;
  - ruin views;
  - F1's 3.5 against 6.75 reconciled;
  - the minimum detectable Sharpe per data length: 1.37 on the 4.8-year training window, 0.80 with
    the 2010 extension, 2.75 on the research window.
- **V2.1, universe and purchase:**
  - the 28 exposures, with the full-size price path fixed before Gate 0;
  - windows as v1 M1;
  - phase 1 within the funds already held, by a stated rule (liquidity tier, then c/sigma, with the
    CME margin as the volatility proxy, then a cluster round-robin);
  - phase 2 only after a Gate 0 pass.
- **V2.2, the clock:** 3 decision times by rule; h in {60, 120, F}; one position per product; the
  c/sigma filter at tau 0.10; the product's own roll dates excluded.
- **V2.2b, Gate 0:** as in section 1.
- **V2.3 to V2.5:** signals, causal z-scores (250/60/20, clip 5), gross and net targets.
- **V2.6, models:** ridge lambda {0.01, 0.1, 1.0} and LightGBM depth {2, 3}; 45 configurations
  with k {1.5, 2, 3} and 3 horizons.
- **V2.7, the cost gate:** the literal F7 reading built, with a switch to the gross reading, which
  is recommended.
- **V2.8, sizing and risk:**
  - 0.10 x D, a 0.25 x D loss cap and a daily risk budget;
  - one extra tick per side beyond q_c;
  - at most 3 positions, 1 per cluster;
  - the portfolio at the tier minus 0.1 lot;
  - KS1 to KS5;
  - the simulator on the frozen engine, with three stated differences and a combined-MLL audit.
- **V2.9, evaluation:**
  - nested CPCV, PBO by CSCV, DSR at N_total = N_program + 45 + Gate 0 tests;
  - the training-window verdict, the research-window screen, holdout-2, paper trading;
  - the payout simulation.
- **V2.10 to V2.12:** deployment options, compute, and the decisions.

### Tasks 2 to 5: the build (ml_route_v2/, contracts in reports/stage_e11_interfaces.md)
- **Signal library (reports/stage_e11_signal_coverage.md):**
  - 66 signals: 42 member, from 51 of the 54 families with the 21 CP ports pooled into 4, plus
    24 generic;
  - 154 model columns.
  - Excluded, with reasons: K5-fomc-01 and K6-wasdepost-01 (known after the last decision time)
    and K9-anncday-01 (its EC-K9 calendar does not cover 2019-2024).
  - Every signal passes the availability and perturbation tests.
- **Models and selection:**
  - closed-form ridge and LightGBM, both deterministic by sha256;
  - CPCV with 6 blocks, 15 outer splits, 5 paths and 4 inner folds; purge on timestamps and a
    1-date embargo;
  - per-split risk tables;
  - resumable units, with a constants fingerprint after C-01;
  - PBO through funnel's CSCV (rows = configurations, 16 blocks); DSR through funnel;
  - an append-only configuration and Gate 0 ledger, registered before computation.
  - Fit probe at 250k x 90: ridge 0.19 s, LightGBM at depth 3 4.3 s.
- **Simulator and payout checks:**
  - PortfolioRules differs from the frozen StageERules in exactly three ruled ways: no
    one-position rule, the lot cap per product, the blackout per product. It also adds the extra
    tick beyond q_c, which only raises cost.
  - A single-product run is fill-for-fill identical to the frozen engine.
  - The hand-computed two-product day (2019-06-05, MNQ and MGC) matches to the cent: $137.27 after
    D-08a, and the code reviewer recomputed it from the frozen table.
  - The combined-MLL audit catches a −$2,248.58 combined breach that the frozen per-leg check
    misses.
  - Payouts: hand-computed Standard and Consistency sequences under the keep-D policy, pinned and
    recomputed by the reviewer; agreement with rules/xfa_rules.py under both policies; five
    accounts as one draw.
- **Canaries (tests/test_ml_v2_leakage.py), all caught:**
  - a future bar; a future release; a target shuffled across dates (median-path t −0.40 vs 14.74);
  - a peeking normalizer; selection seeing the test block (3 ways);
  - a label overlapping the test fold; a product shifted by one minute; the window guard;
  - Gate 0: noise fails; a 10x-cost edge passes and trades; a 2x-cost edge passes Gate 0 and the
    gate rejects the planted edge at every k (ridge's linear extrapolation is a documented
    property, C-1, a strict xfail); a 0.5x-cost edge fails both.
- **Runtime probe (reports/stage_e11_runtime_probe.md):**

| | 8 products (phase-1 size) | 28 products |
|---|---|---|
| total, full grid | **20.4 min measured** end to end | **43.9 min** extrapolated from measured stages |
| peak memory | 3.1 GB | 4.8 GB (49% of free at launch, after FIX 3; was 7.2 GB) |
| largest stages | CPCV 5.6 min, engine 5 paths 9.6 min, payouts 4.7 min | CPCV ~12 min, engine 5 x 5.2 min |

  - The ThinkPad, under the overnight profile, fits either size in one 8-to-10-hour window.
  - The checkpoints are each stage, each (configuration, split, fold) CPCV unit, and each engine
    and payout path.
  - The 2010 extension: about 2.5 h, with paths isolated in their own processes for memory.

### Task 6: the account key fix (reports/stage_e11_keyfix.md)
- require_databento_key(env_file, account=None) reads DATABENTO_API_KEY1 for acct-1 and
  DATABENTO_API_KEY2 for acct-2, defaulting to ACTIVE_ACCOUNT.
- It refuses by name (account and variable, never a value) when the variable is missing, empty or
  whitespace-only, and for an unknown account. It has no fallback to the old variable. No caller
  was edited, and the caps are unchanged.
- 34 tests, all with fake values.
- Harness v7, verified; committed as 5931e30.

### Task 7: suite and probe
- Full suite after the design fixes: 6299 passed, 2 skipped, 2 xfailed (the pre-existing one plus
  C-1), exit 0, 21:20 (pytest_task7.out).
- The final suite after the review fixes is in section 2.

### Task 8: reviews (reports/stage_e11_review.md); rulings (reports/stage_e11_rulings.md)
See section 5.

### F1 to F13 in the draft

| Finding | Where in docs/STAGE_E_ML_V2_DESIGN.md | As a rule or open |
|---|---|---|
| F1 MLL binds; realistic band | V2.0: the dollar table at S 1.0, 1.5 and 2.0 for 50K, 150K and 5 x 150K; eps as context; ruin for scale. V2.9: Sharpe reported against the band (not a gate, D-09), alarm above 4.0; verdict 7: ruin (a breach or the KS2b level) <= 10% | rule; the thresholds are open (V2.12 item 14) |
| F2 Gate 0 first | V2.2b: families A and B, a fixed pass bar, fail = stop; V2.1: phase 2 only after a pass | rule; the bar is open (item 1) |
| F3 ridge primary, shallow LightGBM | V2.6: ridge lambda {0.01, 0.1, 1.0}, LightGBM depth {2, 3}, no LSTM or transformer, lstm.py not reused | rule; the grids are open (item 9) |
| F4 nested CPCV, PBO, DSR at full N, t >= 3 | V2.9: 6 blocks, 15 outer and 4 inner splits, purge plus 1-date embargo; PBO by CSCV on 16 blocks; N_total = N_program + 45 + Gate 0 tests; median-path t >= 3 | rule |
| F5 power | V2.0: minimum detectable Sharpe per data length; V2.9: the research-window bar t >= 1.0 with its power | rule; the research bar is open (item 14) |
| F6 horizon, turnover, c/sigma | V2.2: 3 decision times by rule, h in {60, 120, F}, one position per product, at most 3 entries a day, tau = 0.10 | rule; tau and the clock are open (items 6, 7) |
| F7 cost gate | V2.7: net edge > k c, k in {1.5, 2, 3} by nested CPCV | rule; the reading is open (item 10) |
| F8 drawdown-distance sizing | V2.8: 0.10 x D, 0.25 x D loss cap, b = sigma_target / sqrt(3) plus the daily risk budget, the 2b rounding band, size down after a payout through D | rule; the constants are open (item 11) |
| F9 payout mechanics | V2.9 payout simulation: Standard and Consistency, caps by size, the DLL doubling, the MLL path and its post-payout reset, resets, ruin (a breach or D <= 0.25 MLL), keep-D policy | rule; the policy is open (item 15) |
| F10 kill switches | V2.8: KS1 to KS5 with thresholds | rule; the thresholds are open (item 13) |
| F11 five accounts one bet | V2.0 note; V2.8 at most 1 position per cluster; V2.9 payout sim: 5 accounts as one draw | rule |
| F12 Live Funded bans the API | V2.12 item 18, D9.10 / facts F12.2g | open (deployment risk) |
| F13 no tick or order-book data | V2.1: one-minute OHLCV only, in every phase | rule |

## 4. Delegation record

Times are PDT. The subagent windows come from each transcript's first and last message
(reports/stage_e11_briefs/cost_final.txt).

| # | Agent (role) | Agent file | Model | Effort | Start | End | Tokens | Result |
|---|---|---|---|---|---|---|---|---|
| 0a | ApiSurvey-SonnetMed | worker-medium | sonnet | medium | 01:08 | 01:13 | 4,299,880 | API inventory (reports/stage_e11_briefs/api_inventory.md) |
| 0b | MemberInventory-SonnetMed | worker-medium | sonnet | medium | 01:08 | 01:14 | 3,062,821 | 54-family decision-variable inventory |
| 6 | KeyFix-OpusXHigh | worker-xhigh | opus | xhigh | 01:23 | 01:36 | 2,940,396 | key fix, v7 built and verified; lead committed 5931e30 |
| 2 | SignalCoder-OpusXHigh | worker-xhigh | opus | xhigh | 01:28 | 02:23 | 54,451,906 | clock, 66 signals, normalizer, targets, panel; port pooling as a resumed follow-up |
| 3 | ModelCoder-OpusXHigh | worker-xhigh | opus | xhigh | 01:29 | 01:50 | 8,031,198 | configs, models, nested CPCV, Gate 0, cost gate |
| 4 | PortfolioCoder-OpusXHigh | worker-xhigh | opus | xhigh | 01:29 | 02:07 | 23,190,941 | sizing, portfolio, kill switches, simulator, payouts; MLL-audit and payout-policy follow-up |
| 5 | CanaryCoder-OpusXHigh | worker-xhigh | opus | xhigh | 02:21 | 03:36 | 35,622,844 | synthetic world, pipeline, probe, canaries |
| 5b | FixCoder-OpusXHigh | worker-xhigh | opus | xhigh | 03:38 | 04:45 (last message 05:10) | 24,243,760 | G0-1, roll-blackout rule, memory and checkpoints; cut by the usage limit at 03:58, resumed at 04:12 |
| 8a | DesignReviewer-FableMax | worker-max | fable | max | 03:38 | 03:58 | 1,090,125 | Part 1 complete on disk; the return message was lost to the usage limit |
| 5c | DesignFixCoder-OpusXHigh | worker-xhigh | opus | xhigh | 04:42 | 05:18 | 30,012,855 | code side of the Part 1 rulings plus 2 lead items |
| 8b | CodeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 05:19 | 05:45 | 6,098,127 | Part 2: 0 blocking, 2 should-fix, 10 notes; 9 of 9 mutations caught |
| 9b | ReviewFixCoder-OpusXHigh | worker-xhigh | opus | xhigh | 05:46 | 06:11 | 23,958,306 | code side of the Part 2 rulings |

There were 12 spawns, at most 4 at once (Tasks 2, 3 and 4 plus KeyFix, 01:29 to 01:36). No worker
spawned another.

## 5. Verification

Fable reviewed both the design (max) and the code (xhigh). Neither reviewer wrote what it reviewed.
Every finding has a written ruling in reports/stage_e11_rulings.md.

**Design (DesignReviewer-FableMax).**
- The reviewer recomputed every figure in V2.0 and V2.9. One lead error was caught before the
  review, the research-window power figures, and corrected.
- BLOCKING:
  - **D-01:** ruin = "MLL breached" is near-vacuous under D-proportional sizing. Fixed: ruin = a
    breach OR D <= 0.25 MLL, with switches off, plus the analytic figures in V2.0.
  - **D-02:** the research-window Holm sentence contradicted its t >= 1.0 bar. Fixed: the research
    window is a screen; confirmation rests on the DSR at N_total and the holdout-2 read; the Holm
    level is an open alternative.
- SHOULD FIX, all fixed:
  - D-03: a daily risk budget;
  - D-04: per-split risk tables, in the CPCV and in the engine schedule;
  - D-05: the Gate 0, gate and tau decisions coupled into one;
  - D-06: the price path fixed before Gate 0, and Gate 0 runs once;
  - D-07: aggregation and eligibility written into the draft;
  - D-08: the extra tick beyond q_c, and a 1.5 x slippage sensitivity;
  - D-09: a power paragraph; Sharpe >= 1.5 dropped as a gate.
- NOTES D-10 to D-24 are all applied in the draft.

**Code (CodeReviewer-FableXHigh).**
- Its own test run: 717 passed, 1 xfailed.
- Mutation checks: 9 of 9 guard removals made their canary fail; the control passed 11 of 11.
- The hand-computed day and the four payout sequences were recomputed from the frozen tables.
- SHOULD FIX, both fixed:
  - **C-01:** resumable state ignored constants. Fixed: a constants fingerprint.
  - **C-02:** a sparse pair crashed the nested run. Fixed: a risk_unknown skip.
- NOTES:
  - fixed: C-03, C-04, C-05, C-06, C-07, C-09, C-11, C-12;
  - C-08: a design rule on N across runs;
  - C-10, deferred to the next purchase session: docs/ACCESS.md:9 still names the old key
    variable, and data/config.py returns the unstripped value (a frozen file, so it needs v8).
- The review-fix result: 704 passed, 1 xfailed across tests/test_ml_v2_*.py (21 new tests); full suite 6320 passed at the end.

## 6. Open choices (decisions the lead made on its own, with the reason)

Every decision the lead made without the user, with the reason. Design choices the user can
override are also in V2.12; this list adds the process choices.

**Design (Task 1 and the rulings).**
1. **The cost gate is read literally** (net edge > k c, so gross > (1+k)c). That is F7's wording. A
   one-line switch to the gross reading is built, and the lead recommends the gross reading
   (review D-05).
2. **The Gate 0 canary "an edge smaller than the cost passes Gate 0, then the cost gate rejects it"**
   cannot hold literally under the proposed 1.5c Gate 0 bar. It is implemented as a binary edge in
   [1.5c, 2.5c), which passes Gate 0 and is rejected by the gate, plus an edge below c, which
   fails both. The pre-cost alternative, under which the sentence holds literally, is open
   (V2.12 item 1).
3. **The model is fit on the gross normalized target**, with the cost gate after it. "The net model"
   is the pipeline of model, gate, sizing and net P&L, selected on net P&L. The reason: the cost is
   known exactly at decision time, and Gate 0 shares the fit.
4. **Ridge without elastic net** (154 columns against about 10^5 rows). The grid is 3 ridge values
   plus 2 LightGBM depths, times 3 values of k and 3 horizons: 45 configurations, at MinBTL's bound
   of about 45.
5. **Decision clock by rule** (t1 = O + 30; t3 the latest with t3 + 120 <= F; t2 the midpoint), and
   h in {60, 120, F}.
6. **tau = 0.10**, derived from IC 0.10 x z 2.5 against the loosest literal hurdle of 2.5c.
7. **The Gate 0 statistics.** Family A is the date-clustered IC t per signal and horizon
   (two-sided). Family B is the top 20% of |r_hat| from ridge at lambda 0.1 under CPCV, per pair.
   Holm runs at 0.05 over A and B together, with a 30-trade floor.
8. **The research window is a screen** (t >= 1.0), because 1.19 years cannot confirm a Sharpe near
   1.5 (F5). Confirmation rests on the nested OOS t >= 3, the DSR and the holdout-2 read (review
   D-02, option (a)).
9. **The selection metric** is the fixed-D (the 50K MLL) daily Sharpe with zeros on no-trade dates.
   It is the mean over folds, and eligibility needs at least 30 trades and a finite score on every
   fold.
10. **The simulator subclasses StageERules** with three stated differences: no one-position rule,
    the lot cap per product, the blackout per product. It adds a cost-only override and a
    combined-MLL audit. The 150K figures come from the payout simulator's re-sizing, a lower bound,
    because the frozen account model encodes 50K only; the 150K tiers are taken as the 50K tiers.
11. **Phase-1 scope is the training window only**, with holdout-2 deferred to phase 2. This departs
    from V1 so that more products fit the budget; it is open.
12. **The sizing rounding band**: one contract up to 2b, D2's band, so that full-size vehicles stay
    tradeable at 50K. The daily risk budget caps it at sigma_target.
13. **Payout policy**: on the first eligible date, request the largest amount that leaves
    D >= 0.5 x MLL. The plain maximum halted accounts after small early payouts. Ruin is read with
    the kill switches off.
14. **The ports are pooled** across products, one feature per port variable, because D6 defines
    each port as one rule ported to every product. G9's 120-date median is kept, along with its
    140-date training warm-up.
15. **The roll-blackout rule**: the product's own roll dates exclude its rows. A signal leg's roll
    date makes only the features reading that leg not applicable. D4's union over 8 leads would
    have dropped a large share of all dates.
16. **The research-window warm-up skips the sealed gap** (training dates, then research dates).
    Proposed and open; research-only warm-up would lose 80 to 140 of 299 dates.
17. **The engine and payout figures come from the nested OOS schedule** (5 paths), not the in-sample
    final refit. Each engine path runs in its own process for memory.

**Process.**
18. **Harness v7 was committed first** (01:37), before any ml_route_v2 test file existed. New tests
    are named test_ml_v2_* so they fall outside the manifest's patterns, and ml_route_v2/ is
    outside the harness directories. So v7 differs from v6 only by data/config.py and its test.
19. **The key-fix test is named test_stage_e_config_keys.py**, so the manifest freezes it together
    with data/config.py.
20. **The suites ran as `uv run pytest -q -p no:cacheprovider`** (nice 10), which keeps .pytest_cache
    out of the tree. That is one flag beyond the prompt's `uv run pytest -q`.
21. **The design reviewer's Part 1 was complete on disk** when the usage limit cut the agent off. It
    was used as written, with no rerun. Only its return message was lost.
22. **FixCoder was resumed after the limit** through SendMessage, with its partial work on disk.
23. **The lead deleted 1.9 GB of synthetic probe frames** (~/.cache/propexp_e11_probe/A_fix3) that
    this session had created. The A and B probe states can no longer resume after the fingerprint
    changes, and are deleted at the end.
24. **C-10 is deferred** (docs/ACCESS.md:9 names the old variable; data/config.py does not strip the
    key). The prompt allows exactly two commits, and data/config.py is frozen in v7. The next
    purchasing session fixes both when it writes its own manifest.
25. **The lead fixed one of its own arithmetic errors before the review**: the research-window power
    at t >= 1.0 is 0.74 and 0.88, not 0.70 and 0.83.
26. **The lead corrected guessed times in the STATE file** at 01:23, using file timestamps.
27. **Mid-stage, a full suite ran with the two in-flux canary files excluded** (6130 passed, 02:40).
    It was an early check, not a gate.

## 7. Decisions for the user (V2.12, each with the lead's recommendation)

The full text is V2.12 of docs/STAGE_E_ML_V2_DESIGN.md. Here each decision comes with the lead's
recommendation first.

1. **The Gate 0 bar, the cost-gate reading and tau (one coupled decision).** Recommended:
   - the gross reading (hurdles 1.5c / 2c / 3c, tau 0.167);
   - Gate 0 at 1.5c on the top-20% confident trades, t >= 3, Holm 0.05 with family A included
     (operative z about 3.57), >= 30 trades.
   Alternatives: the literal F7 reading as built (2.5c / 3c / 4c, tau 0.10), or a pre-cost Gate 0
   with no cost multiple.
2. **The phase-1 subset rule.** Recommended as written: the liquidity tier (median ADV), then
   c / sigma_proxy, then a cluster round-robin, greedy to the budget.
3. **The volatility proxy.** Recommended: the CME maintenance margin (it reads no window of ours).
   Use the frozen E|m_1| only if CME's pages block the fetch.
4. **Phase-1 scope.** Recommended: the training window only (more products for Gate 0), with the
   holdout-2 chunks bought in phase 2 for the traded products. This departs from V1.
5. **The 2010 extension.** Recommended: take the free quote at the freeze, and buy only after a
   Gate 0 pass, with a D4 start-rule amendment. It is the only lever that makes a Sharpe near 1
   detectable (minimum detectable Sharpe 0.80 vs 1.37).
6. **The decision clock.** Recommended as written: three times by rule, holds of 60 min, 120 min
   or to the flatten.
7. **The roll-blackout rule.** Recommended as written: the own roll date excludes rows; a signal
   leg's roll date makes its features not applicable.
8. **The signal library.** Recommended: all 54 families and G1-G19, with the ports pooled. Also
   build the EC-K9 announcement calendar for 2019-2024 from official pages in the freeze session,
   so K9-anncday-01 can enter.
9. **The research-window warm-up.** Recommended: skip the sealed gap.
10. **The grid sizes.** Recommended as written: 3 ridge, 2 LightGBM, 3 k and 3 horizons, 45 in all.
11. **Sizing constants.** Recommended as written: 0.10 x D, 0.25 x D, the daily budget, the 2b band
    and one extra tick per side beyond q_c. Also add the release-window rule: no new entry near a
    release while open lot-equivalents exceed half the tier.
12. **The 150K parameters.** Recommended: the freeze session reads Topstep's 150K MLL (V22 says
    $4,500) and the XFA scaling schedule. Until then every 150K figure is a lower bound.
13. **Kill-switch thresholds.** Recommended as written:
    - KS1: -0.30 x D_open;
    - KS2: 0.50 x MLL, half size;
    - KS2b: 0.25 x MLL, halt;
    - KS3: 5 losing dates;
    - KS4: 3 standard errors over 40 dates;
    - KS5: 2 and 5 minutes.
14. **The success criteria.** Recommended:
    - training window: median-path t >= 3, DSR > 0.95 at N_total, PBO < 0.5, ruin <= 10%
      (breach or the KS2b level), >= 30 trades per product, with the Sharpe reported against the
      band;
    - research window: a screen (mean > 0, t >= 1.0, >= 30 trips);
    - the 1.5 x slippage sensitivity as a must-survive condition in the holdout-2 registration;
    - paper trading: 40 dates, costs within 1.25 x D8.
    Alternatives: keep Sharpe >= 1.5 as a gate; a Holm-level research bar (t >= 2.58); eligibility
    on a majority of splits instead of all.
15. **The payout policy.** Recommended: request at the first eligibility the largest amount that
    leaves D >= 0.5 MLL. Choose Standard or Consistency, and DLL on or off, from the payout
    simulation once real data exist.
16. **Deployment.** Recommended: (a), a frozen ridge model with weights hashed and never retrained
    live. In effect it is a plain linear rule. It replaces the 2026-09-24 "plain rules" decision;
    Topstep's AI clause (D9.9) may need a support answer.
17. **The compute host.** Recommended: the ThinkPad. The full grid takes under 1 hour at 28
    products, and about 2.5 h with the 2010 extension.
18. **The Live Funded risk (F12).** The API is banned on Live Funded, so the bot runs on XFAs only,
    and a call-up ends automated trading on that account. Recommended: plan as V22 does (XFA
    payouts fund a personal account) and decide before the first funded account whether to accept
    a call-up.
19. **The purchase plan and the cap raise.** Recommended:
    - phase 1 spends acct-1's headroom (about $28.41) first, then acct-2's $125;
    - the purchasing session raises ACCOUNT_2_CAP_USD to about $249.67 (V19) in its own manifest,
      and logs a fresh quote before buying;
    - the same session fixes C-10 (docs/ACCESS.md:9 and key.strip() in data/config.py) in that
      manifest.

**What the freeze session needs:**
- the decisions above;
- the CME margin table, or the E|m_1| choice;
- Topstep's 150K MLL, scaling schedule and reset price;
- a fresh phase-1 quote under the subset rule;
- the EC-K9 calendar for 2019-2024 (if item 8 is accepted);
- the design and the ml_route_v2/ build hashed into a v2 freeze manifest;
- the program N read from the ledger;
- a DECISIONS entry for the route's unused research-window Holm slot.

## 8. Session cost

Computed at 06:33 PDT from this session's transcripts (lead 92aec2d7....jsonl plus 12 subagent files;
reports/stage_e11_briefs/cost.py, E.10's corrected script; output in cost_final.txt). The lead's
tokens after 06:32 (filling in this return, progress.md, docs/STAGES.md and the commit) are not
included.

**Final ETA table**

| # | Task | Owner | Model / effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 | Startup checks, baseline suite | lead | opus xhigh | 01:03 | 01:22 | 19 min | (lead) | done; 5582 passed |
| 0a | API inventory | ApiSurvey-SonnetMed | sonnet medium | 01:08 | 01:13 | 5 min | 4,299,880 | done |
| 0b | Member inventory | MemberInventory-SonnetMed | sonnet medium | 01:08 | 01:14 | 6 min | 3,062,821 | done |
| 1 | Design draft | lead | opus xhigh | 01:08 | 01:21 | 13 min, revised through 06:00 | (lead) | done |
| 6 | Key fix, harness v7 | KeyFix-OpusXHigh, then the lead's commit | opus xhigh | 01:23 | 01:37 | 14 min | 2,940,396 | done; 5931e30 |
| I | Interfaces and constants | lead | opus xhigh | 01:23 | 01:28 | 5 min | (lead) | done |
| 2 | Signals, normalizer, targets | SignalCoder-OpusXHigh | opus xhigh | 01:28 | 02:23 | 55 min | 54,451,906 | done; ports pooled on a ruling |
| 3 | Models, CPCV, Gate 0, gate | ModelCoder-OpusXHigh | opus xhigh | 01:29 | 01:50 | 21 min | 8,031,198 | done |
| 4 | Sizing, portfolio, simulator, payouts | PortfolioCoder-OpusXHigh | opus xhigh | 01:29 | 02:07 | 38 min | 23,190,941 | done; one follow-up |
| — | Mid-stage suite (early check) | lead | — | 02:23 | 02:40 | 17 min | — | 6130 passed |
| 5 | Canaries, pipeline, probe | CanaryCoder-OpusXHigh | opus xhigh | 02:21 | 03:36 | 75 min | 35,622,844 | done |
| 5b | Fix round 1 | FixCoder-OpusXHigh | opus xhigh | 03:38 | 04:45 | 55 min of work | 24,243,760 | done after the pause |
| 8a | Design review | DesignReviewer-FableMax | fable max | 03:38 | 03:58 | 20 min | 1,090,125 | Part 1 complete |
| — | **Pause: usage limit** | — | — | 03:58 | 04:10 | 12 min | — | not work |
| 8a' | Part 1 rulings and design fixes | lead | opus xhigh | 04:11 | 04:41 | 30 min | (lead) | done |
| 5c | Fix round 2 (design rulings) | DesignFixCoder-OpusXHigh | opus xhigh | 04:42 | 05:18 | 36 min | 30,012,855 | done |
| 7 | Full suite and probe review | lead | opus xhigh | 05:19 | 05:40 | 21 min | (lead) | 6299 passed |
| 8b | Code review | CodeReviewer-FableXHigh | fable xhigh | 05:19 | 05:45 | 26 min | 6,098,127 | done |
| 9a | Part 2 rulings | lead | opus xhigh | 05:45 | 05:55 | 10 min | (lead) | done |
| 9b | Fix round 3 (code rulings) | ReviewFixCoder-OpusXHigh | opus xhigh | 05:46 | 06:11 | 25 min | 23,958,306 | done |
| 9c | End suite, end checks, cost, return, commit | lead | opus xhigh | 06:11 | 06:33 | about 40 min | (lead) | end suite 6320 passed |
| **Stage** | | | | 01:03 | 06:33 | **about 5 h 40 min of work** (5 h 52 min wall less the 12-minute pause), against an initial estimate of 9 h 55 min | **280,315,617** | lead 63,312,458 (22.6%); workers 217,003,159 (77.4%) |

**Tokens per model**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 872 | 181,259 | 6,169,223 | 836,898 | 7,188,252 |
| claude-opus-5-5 | 1,960 | 1,630,596 | 257,546,254 | 6,585,854 | 265,764,664 |
| claude-sonnet-5-5 | 114 | 86,359 | 6,915,582 | 360,646 | 7,362,701 |
| all | 2,946 | 1,898,214 | 270,631,059 | 7,783,398 | 280,315,617 |

**Per worker spawn:**
- ApiSurvey-SonnetMed: worker-medium, sonnet, medium, 4,299,880.
- MemberInventory-SonnetMed: worker-medium, sonnet, medium, 3,062,821.
- KeyFix-OpusXHigh: worker-xhigh, opus, xhigh, 2,940,396.
- SignalCoder-OpusXHigh: worker-xhigh, opus, xhigh, 54,451,906.
- ModelCoder-OpusXHigh: worker-xhigh, opus, xhigh, 8,031,198.
- PortfolioCoder-OpusXHigh: worker-xhigh, opus, xhigh, 23,190,941.
- CanaryCoder-OpusXHigh: worker-xhigh, opus, xhigh, 35,622,844.
- FixCoder-OpusXHigh: worker-xhigh, opus, xhigh, 24,243,760.
- DesignReviewer-FableMax: worker-max, fable, max, 1,090,125.
- DesignFixCoder-OpusXHigh: worker-xhigh, opus, xhigh, 30,012,855.
- CodeReviewer-FableXHigh: worker-xhigh, fable, xhigh, 6,098,127.
- ReviewFixCoder-OpusXHigh: worker-xhigh, opus, xhigh, 23,958,306.

**Delegation share:**
- The lead took 22.6% of tokens and the workers 77.4%.
- By tier: Opus lead 22.6%, Opus workers 72.2%, Fable 2.6%, Sonnet 2.6%.
- Cache reads are 96.5% of all tokens.
- SignalCoder alone used 19.4%: 66 signals, each read from its member module.
