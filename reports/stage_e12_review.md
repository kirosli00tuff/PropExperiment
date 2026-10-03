# Stage E.12 review

## Part 1: Freeze review

Reviewer: FreezeReviewer-FableXHigh (worker-xhigh, Fable 5.1), 2026-10-03 08:58 to 09:15 PDT, read-only, before the freeze commit.
Brief: reports/stage_e12_briefs/brief_freezereviewer.md. Prompt sections read: SCOPE, GUARDRAILS, Tasks 1, 3, 8.
Manifest reviewed: reports/stage_e12_ml_v2_freeze.json, sha256 45e0faf202f43315c331b3683f352ce6725a78120cd68798b6f93213a6151657 (recomputed; matches the brief). Verifier run: `verify_v2_freeze(p, sha256(p))` printed `ok`. `context_sha256` of docs/DECISIONS.md (75a1c425...) and docs/prompts/STAGE_E.12.md (e3834569...) recomputed and equal to the manifest's. `git_head_at_write` 8b93e98 equals HEAD. No market data read; `uv run python -m data.holdout status`: all_ok true, unlocks_logged 0.
Tests run (nice 10, -p no:cacheprovider, scratch pycache): tests/test_ml_v2_phase1_{freeze,gate0,support,world}.py, test_ml_v2_k9.py, test_ml_v2_gate0.py, test_ml_v2_decide.py, test_ml_v2_portfolio.py: 141 passed in 31.8 s.

Counts: BLOCKING 0, SHOULD FIX 4, NOTE 9. No finding makes Gate 0's verdict wrong or unauditable, implements a decision against V23, or opens a leak. The four SHOULD FIX items are all fixable before the freeze commit, and three of them (F-1, F-3, F-4) concern Tasks 4 to 6 rather than the frozen numbers.

### Findings

| id | grade | what | where | why it matters | suggested fix |
|---|---|---|---|---|---|
| F-1 | SHOULD FIX | The ranking script reserves only the quote, not quote x 1.03, after a take: it tests `q * 1.03 <= rem[acct]` but then does `rem[acct] -= q`. The GUARDRAILS require "the session caps equal the selected subset's fresh quote total plus 3%, never above the combined headroom" and "each exposure's purchase sits on one account, and its fresh quote fits that account's remaining headroom with a 3% margin". With two or more picks on one account the script can select a subset whose 1.03 x total exceeds that account's headroom by up to 3% of the earlier picks. | reports/stage_e12_briefs/rank_phase1.py:100-104; design docs/STAGE_E_ML_V2_DESIGN.md:225-230 (step 5); prompt GUARDRAILS lines 115-128 | At Task 5 the spend gate (or the cap rule) would then refuse the last pick, and the lead would have to drop or re-rank by hand, which is exactly the choice P-4 was written to remove. Not a Gate 0 number. | One line: `rem[acct] -= q * (1 + MARGIN)` (reserve the billing tolerance), or test `(spent_acct + q) * 1.03 <= headroom`. Re-hash the script in the manifest. |
| F-2 | SHOULD FIX | The freeze check, the run-once guard, the list-hash check and the ledger registration are all bound to operator-supplied paths: `--freeze-manifest` (any file, verified against the `--freeze-sha256` the operator also supplies), `--reports-dir` (where the list is written and where `_guard_once` looks for the completed report), `--ledger` (required, any path) and `--state-dir` (where the DONE marker and the pins live). No flag disables a check, but a run with non-canonical paths passes every check against its own files and leaves the tracked tree untouched. ml_route_v2/ is not a harness directory (0 entries in reports/stage_e2b_harness_freeze.json; HARNESS_DIRS at screening/harness_freeze.py:32-33), so the v2 manifest is the only pin on the v2 code. | ml_route_v2/phase1/cli.py:37 (`--freeze-manifest`), :39 (`--reports-dir`), :48 (`--ledger`), :62-67 (`_gates`); gate0_stage.py:259-263 (`_guard_once`), :277-287 | Auditability, not correctness: the canonical run still writes reports/stage_e12_gate0.json once, the gate0 report records freeze_sha256, harness_sha256 and the ledger path, so a deviation is detectable, and the stage prompt binds the operator to the canonical paths. But the design says "Gate 0 then runs once" and the check should not depend on the operator's flags. | Remove `--freeze-manifest` (tests already use `main(freeze_root=...)`); default `--reports-dir` and `--ledger` to REPO_ROOT/reports and ledger/ml_v2_config_ledger.jsonl and accept other values only through `main()` kwargs; make `_guard_once` also refuse when the canonical reports/stage_e12_gate0.json exists whatever `--reports-dir` says. |
| F-3 | SHOULD FIX | `build --vehicles` is a free operator input. Nothing checks it against the P-4 ranking's subset (reports/stage_e12_ranking.json) or the purchase records (reports/step2/purchase_<ROOT>.json). A bought product could be left out, or a vehicle whose purchase failed could be requested (the latter stops on the missing store; the former is silent). The resume check only pins the first request. | ml_route_v2/phase1/cli.py:41-42; ml_route_v2/phase1/build.py:243-256; design V2.2b "Products: the phase-1 exposures the V2.1 subset rule selects" (docs/STAGE_E_ML_V2_DESIGN.md:385) | P-2 says the list is "a function of the bought products, the bars' coverage and the admissible pairs only". This is the one lead choice left at Task 6. The list file records the vehicles, so the omission is auditable after the fact, but it is not refused. | In `phase1_world`/`run_build`, read the ranking output (or the purchase records of the phase-1 session) and refuse unless the requested vehicles equal its taken subset plus NG; record that file's sha256 in the build's input fingerprint. |
| F-4 | SHOULD FIX | data/config.py is imported on the phase-1 path (REPO_ROOT in freeze.py:66, cli.py:63 and :126, signals/k9.py:40; PROCESSED_ROOT, REPO_ROOT, STEP2_ROOT in world.py:457; and through screening/stage_e_start_dates.py:66, data/research_bars.py:27, data/step2_store.py:54, data/build_bars.py:59), and the manifest's own note says harness v8 changes data/config.py. The brief's criterion "v8 must not touch any of them" is therefore not met literally. The v8 brief (reports/stage_e12_briefs/brief_keycapfix.md:18-33) changes only ACCOUNT_2_CAP_USD, require_databento_key, and a new E.12 constants block; none of the imported names (REPO_ROOT, DATA_ROOT, PROCESSED_ROOT, STEP2_ROOT, DATASET, VENDOR_ROOT) is in that list. | reports/stage_e12_ml_v2_freeze.json `harness_at_freeze.note`; the import lines above | The phase-1 path's behaviour depends on a module that changes between the freeze and Gate 0. Low risk (path constants), hashed by the v8 harness manifest, but unrecorded. | Documentary: in the manifest note (rebuilt before the commit) or in the v8 review, list the names the phase-1 path imports from data/config.py and have the v8 reviewer state that v8 leaves each of them byte-identical. |
| F-5 | NOTE | Stale counts after K9 entered: "about 222 tests at 8 products, 282 at 28" assumes 198 family-A tests (66 signals); the library now has 67 signals (201 tests), so 225 and 285. | docs/STAGE_E_ML_V2_DESIGN.md:419 | Arithmetic in explanatory text; the code counts |A| from the panel. | Change to 225 and 285 (or "about 225 / 285"). |
| F-6 | NOTE | tests/ml_v2_fixtures.py (imported by 5 of the hashed test files) is not in the manifest; the glob is `tests/test_ml_v2_*.py`. | reports/stage_e12_briefs/build_v2_freeze.py:72 | The hashed tests depend on an unhashed module; a fixture edit would not be caught. Tests are not on the Gate 0 run path. | Add `tests/ml_v2_fixtures.py` to `code_files()`. |
| F-7 | NOTE | Two decided items have design text but no code yet: the Combine and reset cost figures (design V2.9, docs/STAGE_E_ML_V2_DESIGN.md:961-964: $198 / $348, $95 / $229) appear in no constant, so payout_sim cannot yet "report the expected resets per year and their cost"; and item 9 (the research-window warm-up skips the sealed gap, :574) has no code. Both belong to the phase-2 paths (payout simulation, research-window run), not to Gate 0. | ml_route_v2/constants.py, ml_route_v2/payout_sim.py (grep: no 199/229/149/348 constants) | Phase 2 will need code under the frozen design; the design text is the frozen specification, so this is permitted, but it should be known. | Either add COMBINE_* / RESET_* constants now (the figures are in reports/stage_e12_topstep_150k.md rows 3-5) or state in the design that they are applied at phase 2. |
| F-8 | NOTE | `_entry_problems` uses a strict-subset test (`set(entry) < {...}`): an entry such as `{"path", "sha256", "foo"}` is not a strict subset, so it falls through to `entry["bytes"]` and raises KeyError instead of FreezeError. The run is still refused. | ml_route_v2/phase1/freeze.py:40 | Robustness only. | Use `not {"path", "sha256", "bytes"} <= set(entry)`. |
| F-9 | NOTE | The manifest hashes a forward claim ("v8 ... touches only data/config.py, data/pull_step2.py, docs/ACCESS.md and their tests") about a commit that does not exist yet, and `context_sha256` is informational (verify_v2_freeze does not check it) and will go stale as soon as docs/DECISIONS.md gains another entry this stage. | reports/stage_e12_ml_v2_freeze.json `harness_at_freeze.note`, `context_sha256` | Neither affects Gate 0; both could mislead a later reader. | Phrase the note as a constraint the v8 review verifies; label `context_sha256` "at write, informational". |
| F-10 | NOTE | Inputs Gate 0 reads that no manifest can hash at the freeze because they do not exist yet: the step 2 stores and their summaries reports/step2/bars_<ROOT>.json, the purchase records, the ranking output, the Gate 0 list. The build's input fingerprint records the store sha256s, S_X, the release calendar's sha256 and the frozen tables' hashes (build.py docstring; gate0_stage.py:100-103), and the start rule pins the research parquets to E.2a's recorded sha256 (stage_e_frozen.py:233-235) and MES to D.1f's. | ml_route_v2/phase1/build.py, world.py:28-31, 48-50 | Expected; named here as the brief asks. | Gate0Verifier should reconcile the build fingerprint's store sha256s against the purchase records and the ranking output. |
| F-11 | NOTE | The phase-1 ranking's volatility proxy E|m_1| was measured on research-window bars (a frozen level statistic, reports/stage_e2a_epsilon.json); V23 item 3 accepted this fallback and the design says so (:232-237, :240-243). reports/stage_e12_cme_margins.json carries a ToS flag (`tos_flag`) and 5 vehicles without a figure; its figures are not used and the file is hashed as a record only. | reports/stage_e12_cme_margins.json; design :232-237 | Consistent with V23; recorded so the trail is explicit. | None. |
| F-12 | NOTE | PAYOUT_RESET_DELAY_DATES = 2 is Topstep's stated minimum to pass a Combine ("as few as two days", reports/stage_e12_topstep_150k.md row 7); the design and the constant's comment both call it a lower bound. The payout simulation will understate reset delay. | ml_route_v2/constants.py:153; design :959-960 | Not Gate 0; a known optimistic parameter. | None now; report it beside the payout figures at phase 2. |
| F-13 | NOTE | The EC-K9 builder did not apply the catalog's R-12 exclusion (announcement dates on equity early-close, early-halt or closure sessions); the signal is a flag on decision rows, and V2.2 already drops early-halt and early-close dates from the decision rows, so such dates carry no row. The design (:530-531) describes the flag without saying R-12 is covered this way. | reports/stage_e12_ec_k9_2019_2024.md "Not applied here"; ml_route_v2/signals/k9.py:191-208; design :309-311 | Consistent; a one-line clarification avoids a later question. | Add to V2.3's K9 bullet: "R-12's early-close exclusion is carried by V2.2's decision-row exclusions." |

### Per-check results

#### Check 1: V23 item by item. PASS (with F-1, F-7, F-12 as notes)

Design lines are docs/STAGE_E_ML_V2_DESIGN.md; code lines are as of the reviewed working tree (the manifest's hashes).

| item | design (quote, line) | code (default, line) | result |
|---|---|---|---|
| 1 gross reading, hurdles 1.5c/2c/3c, tau 0.167; Gate 0 at 1.5c on top-20%, t >= 3, Holm 0.05 with family A, >= 30 trades | :322 "admissible iff c(p,h) / sigma(p,h) <= tau = 0.167 (V23 item 1)"; :427-428 "Decided (V23 item 1): the bar as written (1.5c, t >= 3, the top-20% trade set, Holm at 0.05, at least 30 trades), with family A in the Holm family, under the gross reading"; :636 "Trade sign(r_hat) iff \|r_hat_ticks\| > k x c" | constants.py:62 `C_SIGMA_TAU = 0.167`; :71-77 `GATE0_COST_MULTIPLE = 1.5`, `GATE0_T_MIN = 3.0`, `GATE0_FAMILY_ALPHA = 0.05`, `GATE0_TOP_FRACTION = 0.20`, `GATE0_MIN_TRADES = 30`, `GATE0_HOLM_INCLUDES_FAMILY_A = True`, `GATE0_RIDGE_LAMBDA = 0.1`; :91 `COST_GATE_KS = (1.5, 2.0, 3.0)`; :96 `COST_GATE_READING = "gross"`. cost_filter.py:43, 57-58 reads `v2c.C_SIGMA_TAU` at call time. decide.py:9-13 gross is the default branch. gate0.py:93-102 `Gate0Rule` defaults are the constants, `DEFAULT_RULE = Gate0Rule()`; :19-21 Holm across A and B. pipeline.py:324-345 `_gate0` passes no rule override. | PASS |
| 2 phase-1 subset rule as written | :212-230 steps 1-5; :225 "How Stage E.12 applies it (lead rule P-4 ...)" | rank_phase1.py:82-90 (median of the 28, tier, c = rt_wall_ticks x tick_value_usd, sort by tier, c/sigma, vehicle); :109-117 (pass 1 cluster-best, pass 2 rest) | PASS; F-1 on the margin arithmetic |
| 3 CME margin proxy, E|m_1| only if CME blocks | :232-237 "The proxy in force ... the WHOLE ranking uses the frozen E|m_1|"; :240-243 "never mixed" | rank_phase1.py:48-59 (`em1`: e_abs_move_ticks["1"] x tick_value_usd, checked against cost_wall's context), :139 default `em1`; reports/stage_e12_cme_margins.json: 28 vehicle rows, 5 without a figure (M2K, MCL, MNQ, MYM, NG), live 403 | PASS (F-11) |
| 4 phase 1 = training window only | :204 "Decided (V23 item 4)" | constants.py:16-17 `TRAIN_LAST = 2024-02-29`, `FORBIDDEN_FROM = 2024-03-01`; world.py:238-249 `refuse_late`, :493-494 calendar guard | PASS |
| 5 free 2010 quote, bought only after Gate 0 pass with a D4 amendment | :253 "Decided (V23 item 5)" | no code (Task 7 is quote-only) | PASS (text) |
| 6 decision clock and horizons as written | :271 "(decided with the horizons below, V23 item 6)" | constants.py:44 `HORIZONS = ("h60", "h120", "hF")`, :49 `DECISION_TIMES_CT` | PASS |
| 7 roll-blackout rule as written | :309 "Decided (V23 item 7)" | pipeline.py:282-283 `own_blackout(world.blackout, vs)` | PASS |
| 8 signal library as written plus EC-K9 2019-2024 | :521-535 "Added at the freeze (V23 item 8): K9-anncday-01 ... 240 dates, 884 CAL-E12 source rows ... k9_anncday"; :542 "Decided (V23 item 8)" | signals/__init__.py `k9.SPECS` in `_ALL`, K9 removed from EXCLUDED, FAMILY_SIGNALS maps K9-anncday-01 -> k9_anncday; signals/k9.py:53-61 (family, paths, vehicles MNQ/M2K/MYM, 17:59 CT availability), :191-208; live registry: 67 signals (42 member, 20 generic, 5 flag), EXCLUDED = K5-fomc-01, K6-wasdepost-01 | PASS |
| 9 warm-up skips the sealed gap | :574 "Decided (V23 item 9): skip the gap" | not on the Gate 0 path (research-window run); no code yet | PASS (text; F-7) |
| 10 grids as written, 45 configurations | :623 "Decided (V23 item 10): the grids as written, 45 configurations" | constants.py:81-82 `RIDGE_LAMBDAS` (3), `LGBM_DEPTHS` (2); :92 `N_CONFIGURATIONS` = 5 x 3 x 3 = 45 (checked at import) | PASS |
| 11 sizing constants as written plus the release-window rule | :723-731 "Release window (V23 item 11; ...) ... refused if open lot-equivalents, including the entry, would exceed half the XFA scaling tier's maximum position size"; :719 150K tiers 2.9/3.9/4.9/9.9/14.9 | constants.py:123-125 `RELEASE_WINDOW_BEFORE_MIN = 5`, `_AFTER_MIN = 30`, `_TIER_FRACTION = 0.5`; portfolio.py `release_window_mask` (half-open), `release_window_binds` (> 0.5 x tier), `admit` refuses with reason "release_window" when `n >= 1`, `admission_record`/`refusal_counts`; decide.py carries `release_window`; payout_sim.py applies `release_window_binds` in `run_path` and `simulate_paths` | PASS |
| 12 150K MLL, scaling schedule, reset price from Topstep's pages | :58-61 "3 lots below $1,500, 4 from $1,500, 5 above $2,000, 10 above $3,000, 15 above $4,500 (a balance exactly on $2,000, $3,000 or $4,500 is taken in the lower tier ...)"; :959-964 delay 2, costs | account.py ACCOUNT_150K `mll_usd=4_500.0`, `base_lots=3.0`, `scaling_tiers=((1_500.0, True, 4.0), (2_000.0, False, 5.0), (3_000.0, False, 10.0), (4_500.0, False, 15.0))`; constants.py:153 `PAYOUT_RESET_DELAY_DATES = 2`; reports/stage_e12_topstep_150k.md rows 1, 2 (image transcription), 3-5, 7 agree | PASS (F-7: cost constants absent; F-12: lower bound) |
| 13 kill-switch thresholds as written | :733 "with the thresholds as written (decided, V23 item 13)" | constants.py:109-117 unchanged from the draft (diff shows no edit) | PASS |
| 14 success criteria as written; 1.5 x slippage must-survive in the holdout-2 registration | :894-895 "Decided (V23 item 14): surviving the 1.5 x slippage re-pricing is a must-survive condition in the holdout-2 registration"; :916 "t >= 1.0" | constants.py:156 `COST_SENSITIVITY_SLIPPAGE_MULTIPLE = 1.5`; :142 `RESEARCH_T_MIN = 1.0` | PASS |
| 15 payout policy as written | :956 "Decided (V23 item 15)" | constants.py:155 `PAYOUT_KEEP_D_FRAC = 0.5` | PASS |
| 16 deployment (a) frozen model | :992 "## V2.10 Deployment (decided: (a), V23 item 16)"; :1013 | no code (deployment) | PASS (text) |
| 17 ThinkPad | :1018 "## V2.11 Compute (decided: the ThinkPad, V23 item 17)" | n/a | PASS (text) |
| 18 Live Funded call-up | :1077 "18. OPEN: ... decided before the first funded account"; header :6 | n/a | PASS (open by design, the only open item) |
| 19 purchase pre-approval, acct-1 then acct-2 at $249.67 | :1078-1080; :198-201 "Stage E.12 raises the cap to $249.67 in harness v8" | v8 (Task 4, in a worktree; not reviewed here) | PASS (text) |
| research-window Holm slot unused | :906-907 "The route's slot in V21's Holm K = 10 is unused on the research window, as docs/DECISIONS.md V23 records (2026-10-03)"; DECISIONS.md V23 last sentence | constants.py:142 `RESEARCH_T_MIN = 1.0` (a screen, not a Holm bar) | PASS |

#### Check 2: no free parameter left open. PASS (with F-3)

- Grep of the design for `Open`, `open`, `TBD`, `the freeze session`, `later`, `until`: 24 hits; every one is either the header's statement that only item 18 is open (:6, :21, :1049, :1077), ordinary English ("open position", "day-session open", "the open of a later bar"), the V2.9 explanation of how N_program is passed, or the E.11 record section (:1045 onward, labelled "The record: options and recommendations as offered in E.11", :1082). No decision point remains open.
- No Gate 0 number is read from an argument or the environment: the only `os.environ` read in ml_route_v2 is probe.py:246 (OPENBLAS_NUM_THREADS, logged for information). The CLI's flags are paths and the vehicle list only (cli.py:35-50); none names a bar, tau, horizon, block, embargo, fraction, lambda, alpha or trade floor.
- The Gate 0 bar is `gate0.DEFAULT_RULE`, a frozen dataclass whose defaults are the constants (gate0.py:93-102); `pipeline._gate0` (pipeline.py:324-345) calls `gate0_family_a`, `gate0_family_b`, `gate0_verdict`, `gate0_b_trades`, `gate0_b_pooled` without a rule argument; `gate0_stage.run_gate0` calls `pipeline._gate0` unchanged (gate0_stage.py:307) and registers family B with `DEFAULT_RULE` (gate0_stage.py:79). `_register_b` writes `"lambda": GATE0_RIDGE_LAMBDA` into every family-B spec (gate0.py:199), so the ledger pins the lambda.
- `decide.candidates(reading=...)` can override the reading, but Gate 0 does not call decide (the cost gate is the CPCV stage), and the only caller that passes `reading` is a test.
- P-2: `list_doc(build)` (gate0_stage.py:86-104) is a pure function of the saved build (panel signal names, horizons, admissible pairs from the filter, fingerprints); `_verified_list` (:277-287) recomputes it and requires byte equality with the registered file; the register step refuses a second list with other bytes (:150-152). The one input the lead still supplies is `--vehicles` (F-3).
- Constants fingerprint: the manifest records `constants_fingerprint` 013fa5a4...; every stage file and the Gate 0 pin carry it (build.py docstring; gate0_stage.py:266-274), so a constant edit is a stop.

#### Check 3: manifest coverage. PASS (with F-4, F-6, F-9, F-10)

- Verifier: `ok` (above). 90 files: the design, 50 ml_route_v2 files (rglob, no pycache), 25 tests/test_ml_v2_*.py, 14 input files, the ranking script.
- Every ml_route_v2 module on the phase-1 path is listed (phase1/{__init__,__main__,_io,build,cli,freeze,gate0_stage,world}.py, signals/k9.py, gate0.py, pipeline.py, panel.py, cost_filter.py, targets.py, clock.py, normalize.py, configs.py, fingerprint.py, signals/*).
- Harness modules the phase-1 path imports (grep of `from data|rules|screening|sim|compute` in ml_route_v2): data.config, data.group_session, data.calendars.*, data.build_bars, data.step2_store, data.stage_e_bars, data.research_bars, screening.stage_e_frozen, screening.stage_e_start_dates, screening.stage_e_rules, screening.stage_e_engine, screening.stage_e_runner, screening.harness_freeze, rules.{products,sessions,constraints,xfa_rules}, sim.fill_model, compute.platform, ml_route.inputs. All lie under HARNESS_DIRS (rules, sim, screening, funnel, data, ml_route, compute, strategy/stage_e; harness_freeze.py:32-33) and each checked name is listed in reports/stage_e2b_harness_freeze.json (1038 files). v8 changes data/config.py (F-4).
- Data files Gate 0, the filter, the panel and the ranking read, and who hashes them: reports/stage_e2b_release_calendar.json (both manifests); stage_e2a_costs / vehicles / vehicle_sizes / epsilon.json (both, and pinned by sha256 in stage_e_frozen.py:44-53); stage_d1f_step5_start_rule.json (both); stage_e0_topstep_facts.json (both); stage_e0_liquidity.json (both); stage_e10_research/cost_wall.json, stage_e10_catalog_K9.json, stage_e12_ec_k9_2019_2024.json/.md, stage_e12_cme_margins.json, stage_e12_topstep_150k.md (v2 manifest only); the group calendars data/calendars/*.py (harness manifest). The research parquets' sha256s come from stage_e2a_vehicle_sizes.json's `contracts[].parquet_sha256` plus `MES_RESEARCH_SHA256` in code (stage_e_frozen.py:233-235), both hashed.
- Not hashable at the freeze (F-10): the step 2 stores, reports/step2/bars_<ROOT>.json, the purchase records, reports/stage_e12_ranking.json, reports/stage_e12_gate0_list.json. The build fingerprint and the list file record their sha256s at Task 6.
- Not hashed but reachable: tests/ml_v2_fixtures.py (F-6). Nothing else Gate 0 reads was found outside the two manifests.

#### Check 4: leakage and window. PASS (with F-2)

- Window: `refuse_late` refuses any bar whose trade date >= 2024-03-01 or whose ts_event >= 00:00 CT of 2024-03-01 (world.py:238-249); the training calendar must end before FORBIDDEN_FROM (:493-494); the loader cuts each root to [S_X, TRAIN_LAST] and refuses holdout, embargo and out-of-store rows (docstring :28-31; data.stage_e_bars, harness-hashed); `panel.assert_window(out, "train")` runs after the panel (pipeline.py:295).
- S_X reads volume only: `READ_COLUMNS = ("ts_event", "volume", "trade_date")` and `pd.read_parquet(path, columns=list(READ_COLUMNS))` (screening/stage_e_start_dates.py:96, 179-180). The research parquet it opens must hash to E.2a's record (world.py:195-200). No price column is read from any research-window file.
- Sealed stores: the sealed holdout is the MES research parquet (2025-04..2026-06) and the encrypted holdout blobs (data/holdout.py:8-12; docs/HOLDOUT_MANIFEST.json lists only those). MES's confirmation parquet (2019-05-01..2024-02-29), which P-1 reads, is not a sealed file and lies inside the training window. ml_route_v2 imports nothing from data.holdout or data/sealed. Holdout status all_ok, 0 unlocks.
- The ranking's E|m_1| is a frozen research-window level statistic, not a bar read (F-11; V23 item 3).
- Run-once guard: `_guard_once` refuses when state_dir/gate0_DONE.json or reports_dir/stage_e12_gate0.json exists (gate0_stage.py:259-263); `_pin_run` refuses a resume under other constants, inputs or list sha256 (:266-274); `_verified_list` requires the registered list's sha256 to equal `--expected-list-sha256` and its bytes to follow from the saved build (:277-287); `check_registered` requires every test in the ledger with the same spec (:129-139); after the run the executed test ids must equal the list (:309-311). No CLI flag disables any of these; the path flags relocate them (F-2).

#### Check 5: lead rules P-1..P-6, P-1a, the E|m_1| switch, P-4 as applied. PASS (with F-1)

- P-1 / P-1a: design :384-392 states roots = phase-1 price paths + MES, micro stores never read, MES refusal -> coverage exclusion, price-path refusal stops. world.py:133-146 (`available_roots`, coverage reasons), :417-444 (`_starts`, StartDatesRefusal -> MES unavailable), :479-489 (StageEBarRefusal: MES only, else raise). Manifest lead_rules P-1, P-1a match the STATE file text.
- P-2: design :393-396 and :397-404; gate0_stage.py RULE_P2 (:43-48) and `list_doc`. Match.
- P-3: design :397-399; world.py docstring :20-27, `root_start` (:185-204), MES via `mes_from_d1f`. Match.
- P-4: design :225-230 (step 5) and STATE P-4; rank_phase1.py: tier by YTD-2026 ADV >= median of the 28 (:82, :87; the liquidity file has exactly one "YTD 2026 (Jan-Aug 2026)" alternate per product), c/sigma ascending within tier with alphabetical ties (:90), pass 1 = the seven cluster-best in rank order (:109-114), pass 2 = the rest (:115-117), acct-1 first then acct-2 with a 3% margin (:31, :100-105), skip otherwise (:106-107), NG $0 (:30, :89), proxy `em1` by default (:139). The one deviation from the GUARDRAILS' cap rule is F-1.
- P-5: design :723-731; constants.py:123-125; portfolio.py `admit`. Match (half-open window, "including the entry", half the tier in force).
- P-6: design :837-840 (N_program = 198, sources named); constants.py:135; manifest program_n with sources docs/STAGES.md:114 ("N = 198") and reports/E.9_RETURN.md:21 ("Program N = 194 + 4 = 198"), both verified by reading those lines.
- E|m_1| switch (V2.1 step 6): V23 item 3 allows E|m_1| "only if CME's pages block the fetch"; what happened is a live HTTP 403 plus Wayback captures covering 23 of 28 vehicles (5 missing). The lead read "5 of 28" as "more than a few" and switched the whole ranking, never mixing proxies (design :232-237; cme_margins.json confirms the 5). Consistent with V23's intent; recorded as F-11.
- The ranking script reads account headroom through `SpendGate(..., account=a)` (`account_cap_usd - account_spent_usd()`); the constructor resolves the account and ledger paths only (data/spend_gate.py:250-266); no quote or network call is made.

#### Check 6: the EC-K9 2019-2024 calendar. PASS (with F-13)

- Rule: the JSON's `rule` quotes C9 (P-K9C-003-c) "The announcements are the FOMC, Non-farm payroll, GDP (first and last), ISM manufacturing PMI, and the earlier of the CPI and PPI announcements", the same five components as the catalog's `event_dates` keys and k9.py's EVENT_KEYS; the catalog member's condition "trade date d is in the EC-K9 announcement date set" and decision time "known in advance from official schedules, fixed before the 17:59 CT entry intent" are what k9.py implements (:3-6, :61, :207).
- Shape: schema ec_k9/1, window 2019-05-01..2024-02-29, 240 dates = union of the five lists (k9.py checks this at load), `uncovered_spans` empty (no span was guessed; every component has a source row per date), 884 CAL-E12 source rows each with publisher, URL, UTC fetch time, sha256, page file, line numbers and a verbatim quote.
- Counts per year and component (FOMC 6/7/8/8/8/1, NFP 8/12/12/12/12/2, GDP 5/8/8/8/8/1, ISM 8/12/12/12/12/2, inflation 8/12/12/12/12/2) agree with the published schedules; the 2020 FOMC count of 7 reflects the cancelled March meeting.
- Spot checks (5 dates, grep in the saved pages, page sha256 recomputed and equal to the source row's):
  - 2021-09-22 FOMC: fed_fomccalendars.html:2915 `monetary20210922a1.pdf` statement link (CAL-E12-036; ex-ante capture 20201218 CAL-E12-611). OK.
  - 2022-01-07 NFP: bls_empsit_archive.html:470 `empsit_01072022.htm` "December 2021 Employment Situation" (CAL-E12-089; schedule row CAL-E12-090). OK.
  - 2023-04-27 GDP advance Q1 2023: bea_gdp_news_archive_p1.html:550-551 "Gross Domestic Product, First Quarter 2023 (Advance Estimate)" / "April 27, 2023" (CAL-E12-161; ex-ante Wayback 20230214 CAL-E12-738). OK.
  - 2020-01-03 ISM manufacturing: ism_mfgrob_wb_20200115002733.html:420 "FOR RELEASE: January 3, 2020" (CAL-E12-210; next-release notice captured 20191221 CAL-E12-209). OK.
  - 2023-02-14 inflation (CPI Jan 2023, earlier than PPI 02-16): bls_cpi_archive.html:452 `cpi_02142023.htm` (CAL-E12-541; schedule row CAL-E12-542). OK.
- Lead rulings: Q1 (unscheduled FOMC actions 2019-10-11, 2020-03-03, 2020-03-15, the notation votes) and Q2 (2020-03-18, the scheduled meeting cancelled on 2020-03-15) excluded. Both follow the catalog's decision_time_ct ("the date set as known at the entry intent": an unscheduled action is not on a schedule; by the 2020-03-17 evening intent the 03-18 statement day had been cancelled for two days). Consistent with C9. Q3 (scheduled vs actual ISM days) had no cases.
- The .md's "Not applied here" items (R-12, C4, weekly cap) are member-trial rules; as a v2 feature only R-12 is relevant and V2.2's decision-row exclusions carry it (F-13).

### What was not checked

- Harness v8 (Task 4) code: it lives in a worktree and is not part of this freeze; F-4 asks its reviewer to state the data/config.py invariance.
- The full ml_route_v2 and repository suites: the lead's STATE records 795 passed, 2 xfailed (ml_v2) before the freeze; I ran 141 tests of the phase-1, K9, Gate 0, decide and portfolio files only.
- The 150K scaling-plan image itself: I read the worker's transcription (reports/stage_e12_topstep_150k.md section 2) and the page text, not the PNG.
- Wayback capture authenticity beyond the saved pages' sha256s and quotes.
- Any Gate 0 statistic: none exists; the Gate0Verifier covers Task 6.
- The payout-sim and CPCV paths on real data: out of scope for phase 1 (not run in E.12 by SCOPE).

## Part 2: Gate 0 verification (Gate0Verifier-FableXHigh, 2026-10-03 12:20-12:45 PDT)

Verdict line: **VERIFIED WITH NOTES.** Every Gate 0 number recomputed independently agrees with
reports/stage_e12_gate0.json to at most 6.5e-13 relative (tolerance 1e-6 family A, 1e-4 family B);
every count and every Holm decision is exact; the verdict FAIL with no passing pair is reproduced.
No finding is above NOTE.

Method (brief steps 1-7, written to disk before the lead's JSON was opened): own code in
reports/stage_e12_briefs/gate0verifier/ (recompute.py, compare.py, spot_check.py, checks.py,
mes_mbt_check.py; raw outputs my_*.csv/json/npy, compare*.csv/json, checks.json,
mes_mbt_check.json, recompute.log). Inputs: the saved build pickles
~/.cache/propexp_e12_phase1/stages/phase1_panel.pkl (68,138 rows, 27 roots, 150 feature columns,
64 signals, 1,068 trade dates 2019-11-19..2024-02-29; MBT has no row) and the build calendar in
it (1,248 CME dates 2019-05-06..2024-02-29); the registered list; the training-window step 2
parquet files for the spot check. ml_route_v2.gate0 / cpcv / cost_filter / models were read for
definitions and not imported; the panel module was imported only to unpickle the Panel dataclass.
The ridge is my own closed-form solve (centred X and y, alpha = 0.1 x n_train, Cholesky on the
Gram matrix; the lead's uses LU). Blocks, splits, embargo and purge were built from V2.9's text
(6 blocks of floor(1248/6) = 208 dates: 2019-05-06..2020-02-21, 2020-02-24..2020-12-10,
2020-12-11..2021-09-30, 2021-10-01..2022-07-21, 2022-07-22..2023-05-11, 2023-05-12..2024-02-29;
15 splits; one-date embargo each side; the purge removed 0 extra rows, as all holds are intraday).
Every row was out of fold exactly 5 times. nice 10, 6 BLAS threads, 9.5 GB free before loading.

### Comparison table (mine vs the lead's JSON)

| Quantity | Mine | Lead | Agreement |
|---|---|---|---|
| Admissible pairs (tau 0.167) | 81 of 81; max c/sigma 0.1403 | 81 (JSON admissible_pairs; filter.pkl table) | exact; c, sigma, ratio max rel 6.8e-15; n_rows exact |
| Family B pairs recomputed | 81 (3 horizons, CPCV OOF) | 81 | mean g, c, t_B, p: max rel 2.9e-14; n_trades, n_dates, n_obs exact on all 81 |
| Best pair (largest t_B, n >= 30) | gate0B_NG_h60 | gate0B_NG_h60 | same pair |
| NG h60 mean gross per trade (ticks) | 5.5694980694980805 | 5.5694980694980805 | 0 |
| NG h60 c (mean round trip of sides taken) | 1.7128756307018145 | 1.7128756307018143 | 1.3e-16 |
| NG h60 cost multiple vs 1.5c | 3.2515c (bar 1 met) | gross_cost_multiple 3.2515 | 0 |
| NG h60 t_B (date-clustered, 330 dates) | 2.5143449337178385 | 2.5143449337178385 | 0; bar 2 (t >= 3) not met |
| NG h60 one-sided p | 0.0062010357819135 | 0.00620103578191354 | 6.4e-15 |
| NG h60 trades / pair rows | 518 / 2,590 | 518 / 2,590 | exact |
| NG h60 Holm (my p, lead's other 272 p) | rank 1 of 273, threshold 1.8315e-4, not rejected | rank 1, 1.8315e-4, not rejected | exact; bar 3 not met |
| Pairs with t_B >= 3 | 0 | 0 | exact |
| Second pair NG hF | mean 13.921, c 1.766 (7.88c), t 2.330, p 0.0103, 494 trades | same | within 1e-14 |
| Pooled B | mean g -0.71718, cost 2.26000, t 0.28075, 39,997 trades, 1,067 dates | same | rel 0; counts exact |
| Family A, seeded three (seed 0x53e7ef57 = 1407709015 over the 192 A ids in list order) | k5_ovr_pct_h60: m 3.1269e-4, t 0.5985, p 0.5496, 1068 dates, IC -0.00303; k2_auction_mto_h120: m -9.9009e-4, t -1.8619, p 0.06289, IC -0.00984; g01_ret30_h120: m 1.9992e-3, t 0.2661, p 0.7902, IC 0.00623 | same | max rel 3.2e-13 |
| Family A, all 192 (bonus) | computed | 192 | mean, t, p, IC, gross_ticks_sign max rel 6.5e-13; n_dates, n_obs exact |
| Smallest A p | 0.0154, gate0A_g07_range_hF | same | exact |
| Holm family | 273 tests, 0 rejections; the lead's table is internally consistent (ranks follow p, thresholds 0.05/(m - rank + 1)) | 273, 0 | exact |
| Verdict / passing | FAIL / none | FAIL / none | exact |
| N | \|A\| 192 + \|B\| 81 = 273; 198 + 273 = 471 | n_a 192, n_b 81, n_contributed 273, n_holm_family 273 | exact |
| Targets spot check (20 rows, same seed, h60 and h120 both ok, entry and both exits outside [r - 5, r + 30) min of every release) | (open(b_{t+h}) - open(b_t)) x ticks per vendor unit from the step 2 parquet | y_gross_h60, y_gross_h120, entry_price | 20/20 exact for h60, h120 and the entry open (19 roots; per-unit factors e.g. NG 1000, ZN 64, 6J 2e6, M2K 10) |

### Reconciliation (freeze review F-10) and the lead's three added checks

- Store hashes: for all 28 phase-1 roots, reports/stage_e12_phase1_bars.json roots.<R>.store_sha256
  = reports/step2/bars_<R>.json parquet.sha256 = sha256 of the parquet on disk; each bars_<R>.json
  purchase_manifest.sha256 = sha256 of reports/step2/purchase_<R>.json, and its input_files equal
  the purchase record's 58 chunk files and hashes (28/28). Vehicles: the ranking subset (28) =
  phase1_bars vehicles = the list's vehicles = the JSON's vehicles; dropped none; the list's
  ranking_sha256 matches reports/stage_e12_ranking.json. List sha256
  53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea matches STATE line 21 and the
  JSON's list_sha256. Ledger: 273 entries, ids and specs equal the list in order, all stamped
  2026-10-03T12:15:25-07:00, before created_pdt 12:15:54; sha256 aacca512... now = before = after.
  Fingerprints: the JSON's constants (013fa5a4...) and inputs (969d3b7e...) equal the panel
  pickle's; freeze a647cd06... equals STATE; gate0.json sha256 c0af61c2..., .md 363c5676... as in
  STATE line 22.
- Harness v9 (commit 4b1e81e): the diff adds the closure-ruling path to data/step2_store.py
  (load_closure_rulings, _closure_ruling, parameters of build_step2_product / _build_window /
  run_product, the closure_ruling metadata) and one FROZEN_INPUTS line in
  screening/harness_freeze.py. reports/stage_e12_closure_rulings.json (sha256 af7967b5...) holds 24
  entries, all keep_and_flag, for exactly the 12 roots held under v8 (store_builds.log: NQ 6A 6B 6E
  6N YM RTY LE 6C HE 6S 6J; store_builds_v9.log: the same 12 built), and the union of those 12
  summaries' deep closure bars (close_minute false) equals the 24 entries exactly (NQ 6, RTY 5,
  YM 4, one each for the other nine). Each of the 12 summaries records closure_ruling with the
  file's sha256 (equal to the file on disk) and bars_ruled = its deep-bar count. The 15 stores
  built under v8 (harness 452c4a51...) and the pre-existing NG store (harness 9a8ebe73...) carry
  no deep closure bar. Read path: ml_route_v2/phase1/world.py imports only STEP2_REPORTS and
  step2_parquet_path from data.step2_store, neither touched by v9; the v2 freeze manifest (91
  files) does not include data/step2_store.py or screening/harness_freeze.py, and its sha256 is
  unchanged; the build (12:13:59) and Gate 0 (12:15:54) both ran after v9 (12:05:01). See N-4.
- MES (P-1a): booking the confirmation store's 1,695,822 rows by ts_event with the equity group
  calendar (close-minute prints to the session they close) gives exactly 3 rows whose label
  differs from the booking: 2020-03-30 21:59 UTC (label 2020-03-30, booked 2020-03-31), 2020-03-31
  21:59 UTC and 2020-06-30 21:59 UTC (each booked to the next date). The refusal is genuine and the
  recorded "3 rows, first label 2020-03-30 booked 2020-03-31" is exact. The MES-reading signals in
  ml_route_v2/signals are g17_mes (generic.py G17) and k8_flight_ret, k8_flight_tail (k8.py); the
  list's uncovered_signals are exactly those three; 64 covered signals x 3 = 192 A tests.
- MBT: V_ref 48.0 as recorded; thresholds 7.2 / 12.0 / 19.2. On the recorded monthly medians, the
  first month from which every month through 2024-02 stays at or above the threshold is 2023-11
  (0.15), 2024-01 (0.25; 2023-12 = 9 < 12, 2024-01 = 14, 2024-02 = 16) and none (0.40; 2024-02 = 16
  < 19.2), equal to the record's m_star; S_X = the first calendar date of 2024-01 = 2024-01-02.
  The MBT step 2 store holds 41 trade dates from 2024-01-02 (the recorded 41; the union calendar
  has 43, the two early-close holidays). 41 < Z_MIN_DATES 60, so no panel row: consistent.

### Order of events (lead addition, all PDT)

1. 09:25:53 freeze commit 9466f2e "ML route v2 freeze"
2. 10:02:53 v8 commit deccd17
3. 10:03:54 first E.12 "commit" event in ledger/databento_spend.jsonl (17:03:54.03 UTC, acct-1,
   NQ.v.0 2019-05); the session's first row is a quote at 09:26:34
4. 12:05:01 v9 commit 4b1e81e
5. 12:15:25 last (and first) Gate 0 registration in ledger/ml_v2_config_ledger.jsonl (273 entries)
6. 12:15:54 created_pdt in reports/stage_e12_gate0.json (panel built 12:13:59)

Strictly increasing.

### Findings

BLOCKING: none. SHOULD FIX: none.

- N-1 (NOTE, documentation): c(p,h) in cost_filter.py is the mean of max(cost_long, cost_short),
  while V2.2 says "the mean D8 round trip". Under the symmetric reading (mean of the two sides)
  no admissibility changes (0 of 81; max ratio 0.1403 against 0.167), so the Gate 0 list and
  verdict are unaffected. Record the max reading in V2.2 at the next design edit; no rerun.
- N-2 (NOTE, informational): the blocks are cut on the 1,248-date build calendar from
  2019-05-06, while the first panel row is 2019-11-19 (warm-up), so block 1 holds rows on only
  about 68 of its 208 dates. This is V2.9 as written ("from calendars alone").
- N-3 (NOTE, disclosure): STATE lines 21-22, which carry the lead's headline Gate 0 numbers,
  entered my context when I grepped STATE for the list sha256 (the brief's step 6 asks for it).
  My code was written from the design text and the module definitions before it ran, and all
  273 tests were recomputed, not only the headline figures.
- N-4 (NOTE, wording): "no module on the Gate 0 read path changed between v8 and v9" holds for
  the v2 freeze manifest's files and for the two names world.py imports from data.step2_store,
  but data/step2_store.py itself is imported on the read path and did change (build-side
  functions only). State it that way. The harness sha256 therefore differs between the v8
  stores (452c4a51...) and the v9 stores and Gate 0 (7fd757f6...), by design.
- N-5 (NOTE, unverified by rule): V_ref = 48.0 for MBT derives from research-window medians,
  which this review may not read; taken as recorded (research store sha256 78ef1710...).

### Not checked

- The MES refusal path inside the frozen loader itself (I replicated the booking with
  data.group_session; I did not step through world.py's refusal code).
- V_ref inputs (research window, sealed to this review) and the day-session medians' source
  computation; only the arithmetic on the recorded medians.
- The lead's ridge numerics beyond agreement: my solve is a different algorithm (Cholesky vs LU)
  and agrees to 3e-14, which is the check.
