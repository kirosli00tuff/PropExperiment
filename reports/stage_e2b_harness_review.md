# Stage E.2b Task 7: adversarial harness review (HarnessAuditor-FableMax)

Reviewer: worker-max on Fable 5.1, spawned 17:58 PDT 2026-09-26, written 18:20-18:35 PDT. I wrote none of
the code reviewed. Manifest under review: reports/stage_e2b_harness_freeze.json, sha256
eb78185a36e4c5a31e864aa4bdc2eb4d425e5705b67029af4ceb6a438de44662 (1,028 files: harness_code 134,
frozen_input 807, earlier_freeze 38, import_closure 11, stage_e_test 38; verified by
`python -m screening.harness_freeze verify --expected <sha>` in the scratch copy: "preflight OK").

Grades, as the brief defines them: BLOCKING = a leak, a look-ahead, a way to change a frozen value, a canary
that cannot fail, a holdout exposure; SHOULD FIX = a defect that could produce a wrong result or a silent
failure; NOTE = everything else worth the lead's eye.

**Counts: BLOCKING 1, SHOULD FIX 3, NOTE 11.**

## What I read

Whole files: screening/harness_freeze.py, stage_e_engine.py, stage_e_rules.py, stage_e_align.py,
stage_e_runner.py, stage_e_frozen.py, stage_e_freeze.py, stage_e_start_dates.py, stage_e_stats.py,
stage_e_stats_power.py, stage_e_stats_start.py; data/stage_e_bars.py, step2_seal.py, trade_date_guard.py,
step2_store.py; ml_route/constants.py, freeze_scope.py, features.py, rows.py, inputs.py, blocks.py,
dataset.py, store.py, train.py, test.py, manifest.py, selection.py, surrogate.py, stage_e_adapter.py,
rule_wrapper.py, adapters.py, lstm_data.py, ledger.py; compute/datarules.py, gitbundle.py, jobspec.py
(to line 120); strategy/stage_e/interface.py, _template.py, __init__.py; tests/_stage_e_synthetic.py.
By section: data/pull_step2.py (docstring, check_chunk, the buy flow lines 531-706), data/holdout.py
(function outline, next_holdout2_chunk, status wiring), data/pull_universe.py (guard call sites),
compute/remote.py (lines 106-455), compute/agent.py (77-145, 183-260, 290-366), compute/files.py
(36-95), compute/machine.py (outline), screening/build_release_calendar.py (outline and the F6.4
mapping code), tests/_stage_e_canary_kit.py (outline, mutants 492-640), tests/test_stage_e_canaries.py
(test list), tests/test_leakage_canaries.py (header and test list), the ML test files (test lists),
rules/price_limits.py and rules/constraints.py (outlines), strategy/interface.py (Bar timing fields).
Frozen text: docs/STAGE_E_DESIGN.md D4, D5, D6, D8, D9, D11; docs/NULL_CRITERIA_E.md whole;
docs/STAGE_E_ML_DESIGN.md M1-M8; reports/stage_e2b_v10_amendment.md whole; docs/DECISIONS.md lines
124 and 149-150 (V6); reports/stage_e2b_STATE.md whole (OC-A..OC-T and the per-worker rulings).

## What I ran (scratch copy only; the repository was read-only throughout)

Scratch copy: rules, sim, screening, funnel, data/*.py, data/calendars, ml_route, compute, strategy,
tests, pyproject.toml, uv.lock, reports/*.json|md, reports/stage_e2a_funnel, docs/*.json|md copied to
<scratchpad>/review (109 MB; no data/processed, data/vendor, data/sealed, ledger or .env). Imports resolve
to the scratch tree (checked: screening.__file__ and data.config.REPO_ROOT point into it).

- Baseline: `pytest tests/test_stage_e_canaries.py tests/test_leakage_canaries.py` in the scratch copy:
  222 passed, 1 skipped (the real-research-month canary, no data) in 119 s, under heavy.sh.
- E1 (item 3, 6): a hand-written start-rule file whose `s_x` contradicts its own recorded medians, fed to
  `screening.stage_e_start_dates.write_start_rule` and `start_dates_for`.
- E2 (items 3, 8): a `strategy/members/__init__.py` that changes a frozen runner constant at import, under
  `write_cluster_freeze`, `verify_cluster_code`, `harness_freeze.check` and `resolve_member`.
- E3 (item 8): a bytecode file compiled from altered source with PEP 552 unchecked-hash invalidation, placed
  in `screening/__pycache__/` beside the byte-identical listed source, then `harness_freeze.check` and an
  import in a fresh process.
- E4 (item 4): nine leaks planted one at a time in the scratch code the canaries guard (driver
  <scratchpad>/plant.py), the guarding tests run, every file restored to the repository's bytes (hash-checked).
- Release calendar (item 8): 25 random entries (seed 20260926) checked quote-in-saved-page,
  date+time_local+tz == instant_utc, and source-file agreement; the F6.4 product mapping re-derived
  independently from the quoted F6.4 text and rules/products.py.
- Export dry run (item 7): `compute.gitbundle.tree_entries` + `export_problems` on HEAD's tree (read-only
  git plumbing; key scan skipped by passing an empty key): 1,204 entries, 1 excluded (ledger/), 0 problems.
- Verifications: `holm_alpha_k(9)` raises `ValueError: K must be in 1..8`; the pinned daily t equals
  mean / (sd / sqrt(n)) (5.0 for mean 1, sd 2, n 100).

Not done: nothing was run on real bars (the MES regressions and the real-month canary need data/processed);
no Windows machine or SSH end was exercised; ml_route/accounting.py (training-window DSR and PBO,
informational only) was not re-derived; the D.1f-frozen modules (sim/, rules/, funnel/) were read only where
the Stage E code calls them.

---

## 1. Look-ahead in the runner

**Result: no look-ahead found.** Findings are NOTEs on fidelity conventions.

What I checked, with the lines:
- Fills happen at the open of a later bar of the order's own leg: `_Run.fill` refuses a fill bar opening
  before the order's decision time (stage_e_engine.py 308-311); orders are stamped `ts + NS_PER_BAR`
  (611-615) and filled only in the next minute's `fill_pending_at_open` (494-517); the loop order is
  session change, fills, MLL, forced orders, then the member (618-656). The member's intent must carry
  exactly this minute's decision time (stage_e_rules.py 476-481).
- The member sees each leg's bar of the current minute only, with the hindsight field masked (`visible`,
  584-587; `call_member`, stage_e_rules.py 443-445; `HINDSIGHT_FIELDS` = vendor_degraded_day,
  strategy/interface.py 127-131); no forward fill (`iter_minutes` 239-263; `engine_leg_missing_bar`
  486-490).
- D9.7 reads the PRIOR trade date's settlement proxy: proxies are finalized when the first bar of the next
  date arrives (`_Settlement.add` 258-274) and looked up by `previous_trade_date` (329-334); the
  same-day variant is a positive control in the kit and my planting P4 (item 4) proves the canary fires.
- Release instants are looked up at or before the fill bar's open (`_latest_at_or_before` 129-132, used by
  the event window 134-136 and the fill guard 138-140), on the fill bar's time (347-358, 375-380); the
  CPI window and the flatten probes read calendars only (391-399).
- Limit orders: marketability is judged against the decision bar's close, a price known at the decision
  (519-523); fills need trade-through on a later bar's range (engine 519-541).
- Costs: bucket by the fill bar's open time (stage_e_frozen.py 113-127), event window by the fill bar
  (stage_e_rules.py 337-345).
- Alignment: the member window is the intersection of the legs' dates minus the union of their roll
  blackouts and UR-1 (stage_e_align.py 57-77); coverage over the member's declared intervals (100-131).
- Bars: booked to trade dates by the group calendar, holdout-1, holdout-2, embargo and out-of-store rows
  refuse the whole file, label mismatches refuse (data/stage_e_bars.py 121-174, 253-273); the research
  parquet's sha256 must equal E.2a's record (261-264); the step 2 store is cut at S_X after the whole
  file is checked (281-293).
- The template member reads `view.bar(root)` only and returns intents stamped with the view's decision
  time (strategy/stage_e/_template.py 105-145).

**NOTE-1. Closure-gap and session-end exits fill at the decision bar's close.** stage_e_engine.py
339-357 (`fill_at_close`), 443-471 (`close_on_closure_bar`), 402-418 (`roll_session`). When the next bar
of a leg is a scheduled-closure print (OC-T) or the session ends with a position open, the exit fills at the
close of the last tradable bar, i.e. the last price the member saw at its decision time. Not future
information (the fill instant equals the decision instant), but a more favourable convention than the
next-open rule used everywhere else; the engine flags and counts it (`fill_at_prior_close_closure_gap`,
470; the runner records `closure_gap_fills`, stage_e_runner.py 394-395). No fix needed; the count belongs
beside any result where it is non-zero.

**NOTE-2. The locked-market test reads the fill bar's whole range.** stage_e_rules.py 361-373
(`_locked`): a lock is declared from the fill bar's high/low, information that is complete only at that
bar's close. The direction is conservative (an exit is deferred, never advanced; R-08 flags and counts
`locked_bars_waited`), so it cannot manufacture an edge. No fix needed.

**NOTE-3. The release calendar records what happened, not what was scheduled.** The calendar's `moves`
lists 15 releases published on a date other than the one first scheduled (macro 6, commodity 4, named 5,
all 2020-2026, most from the 2025 lapse in appropriations) and 14 cancellations. The engine uses the
published instants for costs and the fill guard only (cost side, conservative), and the ML route uses them
for F13-F15 on the training window 2019-2024 where the only recorded moves are two WPSR delays (2022-06,
2023-11) and one API schedule revision (2020-11). Calendar knowledge a day ahead is realistic in every
case; no fix, but the summary of a run should say the instants are as published.

## 2. Leakage in the ML pipeline

**Result: no path found by which a research-window, embargo or holdout date, or a statistic computed from
one, reaches training, tuning, normalization or distillation.** Two NOTEs.

What I checked:
- Windows: the store allowlist admits only `<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet`
  under a root that is not, and does not contain or lie inside, data/processed (ml_route/store.py 47-73);
  every row on or after 2024-03-01 or before 2019-05-06 refuses the product (118-131); the S_X cut is
  asserted on the returned rows (129-131) and again on the saved row index, per split, per refit and per
  distillation step (train.py 106-108, 141-143, 188-191; store.py 152-162). The training calendar is
  cut from the group calendars alone (blocks.py 76-103).
- Features carry availability times derived from the bars they read: F1-F6, F9 from the bar closing at t
  (rows.py 112-132), F7 from the O_X bar's close (features.py 150-152), F8 from the previous complete
  date's C-1 close (153-158), F10 from a `shift(1)` rolling median and the (t-30, t] volume (rows.py
  153-166), F11-F15 calendar values (134-139, 169-181), F16 from the lead's latest bar closing at or
  before t on the same date (183-201), F17 from sigma values that each read the 20 complete dates strictly
  before their date (features.py 126-142); the validator refuses any present value with availability
  after t (rows.py 296-306) and my planting P8 shows it fires.
- Targets: entry at the open of t + 1 min, exit at t + h or the flatten bar, the OC-M deferral mirrors the
  engine's guard (rows.py 204-272); the target is the row's own future and never a feature; the row's
  sigma is its date's (109, 144).
- CPCV: blocks 1-5 only, two validation blocks per split, one full trade date embargoed on each side,
  purge by target-window overlap, `assert_fold` on every split (blocks.py 129-178, train.py 100-104);
  block 6 is read only in the pre-test (train.py 185-191); selection scores use validation rows only
  (selection.py, train.py 110-125).
- Normalization: neither adapter estimates a dataset-level statistic. LightGBM gets F1-F17 plus one-hot
  indicators (adapters.py 34-48); the LSTM's sequences are divided by the row's own sigma and use the
  `shift(1)` 20-date volume median (lstm_data.py 43-66, 100-119); the static inputs are the row's
  features and the cluster one-hot (adapters.py 100-103).
- Distillation and the hash chain: surrogates on blocks 1-5 rows only (train.py 185-193), candidate
  thresholds at 1.5x cost per ML-A02, the pre-test on block 6, ranking per ML-A10 (surrogate.py 59-186);
  ledgers are hash chains with the harness sha256 and machine per fit (ledger.py); E.ML-test re-verifies
  the route manifest's sha256 and body hash, the harness, every ledger, model file, surrogate tree, rule
  file, the RULES.md rendering, the frozen tables and the calendar hash, then reads research bars only
  through `load_research_leg` with E.2a's parquet hash (test.py 114-231, 398-402).
- At the test the wrapper's own history excludes the current bar until after the decision (rule_wrapper.py
  250), the lead history is filtered to bars closed by t (203), features come from the training code with
  `only_date_pos` and pass the validator (191-197). The stage_e adapter runs one traded leg per exposure
  with the price path and lead as signal legs (stage_e_adapter.py 143-151).

**NOTE-4. The training store trusts the parquet's trade_date label.** ml_route/store.py 118-131 reads
`trade_date` and refuses labels on or after 2024-03-01; it never re-books `ts_event` on the group calendar,
as the runner does for the same files (data/stage_e_bars.py 152-174) and as compute/datarules.py does
on both ends of a PC job (261-291). Scenario: a row whose timestamp is in the research window but whose
label was rewritten to 2023 passes the M7.4 window test; its features are inert (every lookup is by exact
timestamp), so this is defense in depth against a tampered file rather than a leak the pipeline could
produce. Fix (one call): after reading, run `data.stage_e_bars.check_bookings(root, calendar, frame,
"step2", where)` and refuse on any exception.

**NOTE-5. Silent CPU fallback for the LSTM.** ml_route/adapters.py 151-160 (`_gpu_or_cpu`): when CUDA is
unavailable the device becomes "cpu" without a named refusal, although V7 plans no CPU fallback and V10-2
turns on the machine the fit runs on. The ledger's machine record would show no `gpu` key, so it is
detectable afterwards, but the job should refuse by name (RouteInputMissing) when `torch.cuda.is_available()`
is False, and the route manifest should carry the device.

## 3. Frozen values a session could change

Inventory of arguments, environment variables and out-of-manifest files (grep over the harness dirs):
command-line inputs are only WHICH member, cluster, set, challenger, horizon and WHERE data and outputs
live (`--research-root`, `--step2-root`, `--store-root`, `--out-dir`, `--route-dir`) plus the expected
harness sha256; the only environment reads are the Databento key (data/config.py 137), the CUDA workspace
setting written by lstm.py 51, and the thread limits compute/platform.py writes. Data roots are checked
by content: research parquets by E.2a's sha256 (stage_e_frozen.py 233-235, stage_e_bars.py 261-264),
step 2 stores by name allowlist, metadata and row dates (ml_route/store.py) and by calendar booking
(stage_e_bars.py). Files outside the manifest that a run reads: reports/stage_e_<k#>_member_freeze.json,
reports/stage_e_start_rule_<SET>.json, reports/step2/purchase_<ROOT>.json (the store builder), the
per-product holdout-2 manifests, the route directory of E.ML-test, and the bar stores; all excluded from
the manifest by design (harness_freeze.py 142-159, notes 285-288).

**F-1 BLOCKING. `strategy/members/__init__.py` runs on every screening run and is hashed by nothing.**
screening/stage_e_freeze.py 87-96 (`_cluster_files` hashes `strategy/members/<k#>/**/*.py` only),
190-192 (`resolve_member` imports `strategy.members.<k#>.<module>`, which executes
`strategy/members/__init__.py`); screening/harness_freeze.py 28-29 (harness dirs include
`strategy/stage_e`, not `strategy/members`), 67-78 (the unlisted-.py scan covers harness dirs only),
135-140 (the import closure starts from the entry modules and cannot reach members, which are named at
run time in the freeze file); strategy/stage_e/_template.py 5-6 tells the cluster session to create that
file. Scenario: a cluster session, following the template, creates the package init; anything written into
it (a monkeypatch of the cost table, the release calendar, a D9 constant, the engine's fill rule) changes
every member's result while the cluster freeze verifies, the harness preflight passes with no problem, and
every record carries the expected hashes. Evidence (E2, scratch copy): with an init that sets
`screening.stage_e_runner.MEAN_HOLD_MIN_MINUTES = 0.0`, `write_cluster_freeze` hashed only
`strategy/members/k1/__init__.py` and `strategy/members/k1/synth.py`, `verify_cluster_code` passed,
`harness_freeze.check` returned no problems, `unlisted_python_files` returned [], and after
`resolve_member` the constant read 0.0 (10.0 before). This re-opens, one directory over, the gap the D.1f
review's F3 rule closed ("an unlisted module cannot be imported into a run"). Fix: (a) `_cluster_files`
also hashes `strategy/members/__init__.py` (and refuses it unless empty), and (b) `unlisted_python_files`
scans `strategy/members` and refuses any *.py there that is neither `strategy/members/__init__.py` nor
under a cluster directory; and (c) the same static allowlist the review of member code needs anyway: refuse
a member module whose imports go beyond datetime, math, decimal, zoneinfo, dataclasses, rules.products,
rules.xfa_rules, screening.stage_e_frozen.load_frozen_tables and strategy.stage_e.interface, since an
in-process member can otherwise read any file or patch any module. (a) and (b) touch harness code, so
the manifest is rebuilt (v2) with the new sha256.

**F-2 SHOULD FIX. A bytecode or extension file beside a listed source passes the preflight and is what
runs.** screening/harness_freeze.py 67-78, 93-101: the check hashes the listed sources and scans for
unlisted *.py; `__pycache__` and non-.py files are excluded (76, 177). Python imports
`__pycache__/<name>.cpython-312.pyc` without consulting the source when the pyc's flags say unchecked
hash (PEP 552), and an extension module `<name>.cpython-312-x86_64-linux-gnu.so` in the same directory
takes precedence over `<name>.py`. Evidence (E3, scratch copy): `stage_e_stats.py` unchanged
(`SCREEN_T_MIN = 1.0`), an unchecked-hash pyc compiled from a copy with `SCREEN_T_MIN = 0.0` written to
`screening/__pycache__/`; a fresh process reported `preflight problems: []` and `SCREEN_T_MIN` = 0.0.
Unlike F-1 this needs a step no documented workflow produces, hence SHOULD FIX. Fix: the preflight refuses
(1) any file under a harness directory whose suffix is in `importlib.machinery.EXTENSION_SUFFIXES` or is
`.pyc` outside `__pycache__` and is not listed, and (2) any `__pycache__/*.pyc` whose flags word has bit 0
set and bit 1 clear (hash-based, unchecked); and every entry point is launched with a fresh
`PYTHONPYCACHEPREFIX` (documented in the stage prompts), which makes pre-planted caches unreachable.

**F-3 SHOULD FIX. The start-rule files carry S_X, a frozen value, with no check that S_X follows from the
file's own data, and the step 2 store they read is not pinned.** screening/stage_e_start_dates.py
428-445 (`_root_values` validates the form of `s_x`, `v_ref` and `monthly_medians` only), 482-500
(cross-file agreement is the only consistency check), 361-375 (`write_start_rule` runs the same parse and
nothing else), 183-200 (`read_volume_bars` takes `expected_sha256=None` for the step 2 store); the
runner cuts the confirmation window at that S_X (stage_e_runner.py 247-251) and the ML route trains from
it (ml_route/inputs.py 331-355). Scenario: a file edited by hand (chmod 444 is the only guard and the
session owns the file), or built with `--step2-root` pointing at a doctored store (volumes changed, the
research side stays pinned but the step 2 side records whatever it read), shifts a product's confirmation
window; every later output records the file's sha256 and passes. Evidence (E1, scratch root): an entry with
`monthly_medians` giving S_X = 2019-05-06 (the rule re-run on them) but `s_x` = 2023-06-15 was accepted
by `write_start_rule`, and `start_dates_for(("ZN",))` returned 2023-06-15; only a second file
disagreeing raised `StartRuleConflict`. Fix: (a) the loader re-runs
`screening.stage_e_stats_start.start_rule` on each entry's recorded `monthly_medians` and
`first_trade_dates` and refuses when `s_x`, `v_ref`, the sensitivity dates or `m_star` differ; (b) each
entry keeps the step 2 parquet's sha256 it was computed from (the builder already lists it under
`inputs`) and `load_confirmation_leg`/`read_leg_dates` refuse when the store they read hashes
differently; (c) the cluster prompt states the start-rule file's sha256 as it states the harness sha256.

**NOTE-6. Freeze files, records and start-rule files are protected by chmod 444 and write-once only.**
screening/stage_e_freeze.py 150-165 and stage_e_start_dates.py 361-375 write once and chmod 444; the
runner writes records once per `--out-dir` (stage_e_runner.py 291-300) but `--out-dir` is free, and no
code compares a freeze file with its git blob at HEAD. A session that removes and re-creates a freeze file
after changing member code is caught only by the commit discipline (the record carries
`cluster_freeze_sha256`, 356). Suggested cheap addition: the runner records `git rev-parse HEAD` and
whether `git status --porcelain` is empty for strategy/members and reports/, so the lead's end check can
see a re-freeze; and the cluster prompt states the freeze file's sha256.

## 4. Canaries that cannot fail, and tests that pass for the wrong reason

**Result: no canary found that cannot fail.** Every leak I planted in the real scratch code was caught by
the test that guards it (E4; each file restored to the repository's bytes, hash-checked):

| Planting (scratch copy) | Guarding tests | Result |
|---|---|---|
| P1 engine: `visible` returns the bar unmasked (hindsight field reaches the member) | test_stage_e_canaries -k hindsight | 8 failed: `test_a_hindsight_flag_never_reaches_the_member` on every group |
| P2 rules: release lookup takes the first release at or after the fill (off by one) | -k release | 8 failed: `test_a_release_never_reaches_a_fill_before_its_instant` on every group |
| P3 engine: member asked before the minute's fills, orders back-stamped and filled at the bar it saw | -k "jump or latency or pulls" | 21 failed: the jump canary, the latency control and the tripwire, every group |
| P4 rules: D9.7 reads the current date's settlement as it prints | -k settlement | 3 failed: the planted-settlement canary on equity, grains, livestock (the hard-limit groups; the others have no D9.7) |
| P5 ml_route/rows: F16 reads the lead bar closing at t + 1 min | test_ml_route_features + canaries -k "lead or honest or ml_" | 6 failed (every ML wrapper canary) and 12 fixture errors from the availability validator raising on the "honest" table |
| P6 ml_route/store: the >= 2024-03-01 row refusal removed | test_ml_route_store | 3 failed: `test_planted_out_of_window_bar_makes_the_job_refuse` for 2024-03-01, 2024-04-02, 2025-05-01 |
| P7 ml_route/blocks: CPCV embargo dates never added | test_ml_route_blocks_selection | 3 failed: membership-and-embargo, outer-sides, leaked-dates |
| P8 ml_route/rows: validator tolerates values one bar after t | test_ml_route_features -k rejected | 1 failed: `test_feature_equal_to_the_next_bars_close_is_rejected` |
| P9 data/stage_e_bars: the holdout/embargo/out-of-store refusal disabled | test_stage_e_loader, test_compute_datarules -k holdout... | 4 failed: MBT rows booked and labelled 2026-06-22, holdout-2/embargo rows in the step 2 store, out-of-range research rows |

Reading of the suites: the Stage E canaries pair each real-engine test with a deliberately broken positive
control from the kit (`SameBarFillRun`, `LookaheadViewRules`, `SameDaySettlementRules`,
`ClosureBlindRules`, `LookaheadReleaseCalendar`, tests/_stage_e_canary_kit.py 492-640), which proves the
statistic can move; my plantings prove the real code paths are what the statistic reads. The MES canaries
(tests/test_leakage_canaries.py) keep the D.1 engine's planted-future, mutant, latency, tripwire and
frozen-primitive checks. The M7 set covers M7.1 (target and next-close canaries), M7.2 (single and
cross-product perturbation), M7.3 (block cut, splits, purge, fold test), M7.4 (planted bar and path,
window assertion), M7.5 (post-window perturbation leaves the model hash; the test's own teeth), M7.6
(ledger chain, model bytes, refit on the same machine), M7.7 (wrapper canaries) and M7.8
(`check_harness_scope`). Observation, no finding: in P5 the "honest table" fixture errors instead of a
named test failing, because the validator raises while the fixture builds; the outcome (the run cannot
proceed) is right, and the wrapper canaries in test_stage_e_canaries fail by name.

## 5. Holdout handling in the step 2 path

**Result: no holdout exposure found.** Two NOTEs.

What I checked:
- Order per chunk (data/pull_step2.py 578-643): quote, authorize, commit, download to `.partial`, link,
  read-only, record-byte check and settle, then `seal_chunk`; any exception after the download purges the
  plaintext and its `.partial` before it propagates (`_purge` 531-536; `_acquire_sealed` 626-636 and the
  resume branch 618-625). Sealing (data/step2_seal.py 118-160) follows data.holdout step for step:
  refusals before any byte is read (84-115: the 13 chunk names only, the product's own path, sealed once,
  oldest first via `next_holdout2_chunk`, intact unlock log, no orphan blob), round trip proved in memory,
  blob written with "xb" and fsync, proved again from disk, manifest appended, SEALED logged, log pinned,
  only then the plaintext removed.
- Trade-date refusal before any vendor call (data/trade_date_guard.py 110-171): every minute of a request
  is booked on the group calendar with the L-3 close-minute rule; unbookable minutes past the calendar's
  coverage refuse (`CalendarCoverageRefused`); holdout-1 dates refuse on every path; holdout-2 dates refuse
  unless the chunk is one of the 13 sealing chunks, and `check_chunk` ties the sealing flag to exactly
  those names (pull_step2.py 287-306). Step 1 (data/pull_universe.py 296-321) refuses both holdouts and
  data.holdout's own sealed-range and sealed-target checks stay.
- Resume states (pull_step2.py 608-625, 650-668): sealed and no plaintext -> skipped; sealed with plaintext
  left -> `complete_interrupted_seal` (removal only under the round-trip proof); unsealed on disk ->
  byte-checked and sealed, never re-bought; a kept chunk with a file but no settle line or the reverse ->
  `ResumeStateError`, nothing deleted.
- The store builder (data/step2_store.py 138-163) refuses, before opening anything, any input that is a
  sealed chunk name, lies under a sealed root, is listed in a holdout manifest or is outside the product's
  own `<ROOT>_v_0` directory, and requires exactly the product's unsealed chunk names (OC-R months);
  `drop_outside_window` (180-202) books every decoded row by `ts_event` alone and drops rows outside
  2019-05-06..2024-02-29 before any price column is used, raising `HoldoutLeakError` on any row booked to
  holdout-2 or later or unbookable; the written frame is checked again (332-336).
- Status: per-product reports fold into `holdout_2.products` and `all_ok` (data/holdout.py 782-795;
  step2_seal.py 177-235), a manifest with a non-product name reported not ok.

**NOTE-7. The first hour of the embargo's first trade date sits in an unsealed chunk.** The February 2024
chunk (range=2024-02-01_2024-03-01) ends at 00:00 UTC on 2024-03-01, so the Globex evening of 2024-02-29
from 17:00 CT (23:00 UTC) books to trade date 2024-03-01, the embargo (trade_date_guard.py 30-32 says so;
step2_store.py 189-202 drops those rows unread and counts them as `embargo_rows_dropped_unread`). D4's
"inside the first sealed chunk, never built into bars" holds for the bars; the raw plaintext of that hour
stays in the unsealed vendor file, as it did for MES in D.1f. No holdout-2 byte is involved. If the lead
wants the letter of D4, the seal could take the last hour of the February chunk too, but that is a design
question, not a defect.

**NOTE-8. A failed seal on the resume path deletes a paid-for chunk.** pull_step2.py 618-625: a chunk
downloaded and settled but not yet sealed is byte-checked and sealed on resume; any exception there (a
disk-full while writing the blob, for example) purges the plaintext, and the chunk must be bought again. This
is the intended trade (no plaintext holdout byte persists after a failure) and costs money, not integrity.

## 6. The D4 power check, the D5 screen and tiers, Holm, and the start rule

**Result: one SHOULD FIX (the Holm family cap), the rest matches the frozen text and the rulings.**

Verified against the text:
- D5 screen: `passes = mean > 0 and t >= 1.0` over every window date with zeros on no-trade days,
  t = mean / (population sd / sqrt(n)) from the pinned `harvey_liu_zhu_verdict` (stage_e_stats.py
  135-162; formula checked numerically); mean <= 0 with zero variance fails without a t (148-149, runner
  Q10 ruling); mean > 0 with zero variance is a named `ScreenUndefined` (151-153).
- Tiers per OC-H (209-244): coverage label -> excluded before screening with no screen; any other D9
  label -> excluded before confirmation, screen kept; unlabelled -> A on pass, B otherwise. The runner
  builds labels from the engine's refusal counters and the trip statistics (stage_e_runner.py 181-206),
  and the coverage exclusion happens before the engine runs (368-372).
- Holm: step-down over one cluster's Tier A at 0.05 / K (270-312), K = clusters with a non-empty Tier A
  (247-256).
- D4 power check (stage_e_stats_power.py): n_b analytic with ddof-1 sd, the stationary-bootstrap VIF
  (p = 1/5, lags 1..20, floor 0.2 gamma_0), 2,000 replicates on the D.1e grid plus n_a and n_b, the 15 %
  switch rule, the censored case, the label from n_b alone against `supply_days` (label_power 251-266);
  n_a at 0.05 / (9 x m_c) per OC-I, descriptive (272-283, 514-519); seed base 20260922 plus the ordinal
  (D.1e's seed base; NULL_CRITERIA_E 3's 20260923 is the confirmation UCB bootstrap, a different
  statistic, no conflict); eps from the epsilon table by vehicle (517). Supply = the step 2 store's dates
  from S_X, intersected over legs, minus the union of roll blackouts, no price read (stage_e_runner.py
  254-268); an empty window supplies 0 days per Q-3 (259-261).
- Start rule (stage_e_stats_start.py): V_ref = median of exactly the 14 reference monthly medians
  (94-107), M* = the earliest month from which every month through 2024-02 has a median >= 0.25 V_ref
  (128-137), 0.15 and 0.40 descriptive, earliest S_X 2019-05-06, first trade date with bars of M*; the
  builder's day session is D6's (O_X, C_X) per contract from the hashed sizes table for every root per
  OC-S (stage_e_start_dates.py 144-159), medians over bars present by CT clock minute keyed by trade
  date month (162-175), volume and dates only (READ_COLUMNS 96), every row booked (183-200); MES from
  D.1f's pinned record re-run to itself and to 2020-02-03 (257-277).

**F-4 SHOULD FIX. The Holm family cap is 8, but V6 makes the route a ninth family.**
screening/stage_e_stats.py 102 (`MAX_CLUSTERS = 8`), 262-267 (`_checked_k` refuses K outside 1..8),
270-272 (`holm_alpha_k`), 247-256 (`k_from_tiers` counts clusters only); docs/DECISIONS.md 149-150
records V6: "D5's K counts every family with a non-empty tested set, the route included ... D5's 'at most
8' reads 'at most 9'". Scenario: eight clusters with a non-empty Tier A plus a tested route rule ->
`holm_alpha_k(9)` raises `ValueError: K must be in 1..8, got 9` (verified), and any session that works
around it by hand risks the wrong alpha; with fewer active clusters the route family is silently not counted
by `k_from_tiers`, giving 0.05 / K instead of 0.05 / (K + 1), an alpha too large by one family. Fix: rename
to families, `MAX_FAMILIES = 9`, `k_from_tiers(tiers, route_tested: bool)` adds one when the route has a
tested rule, and the ML test summary's "Holm: not computed" entry names the same function.

## 7. The Windows backend and the V10 amendment

**Result: no path found by which a holdout bar, an embargo bar, a secret or the ledger reaches the PC;
results are refused without their hashes; V10 leaves A-1 and every statistical choice intact.** Three NOTEs.

Verified:
- Export (compute/gitbundle.py 143-180): a parentless commit of the frozen commit's tree minus `ledger/`
  (29, 150-151), every blob checked (102-119: regular modes only, no `.env*`, no `.parquet`/`.dbn`/
  `.zst`/`.sealed` or a `sealed` path part, no sealing magic, no Databento key bytes), bundled from a scratch
  repository borrowing objects read-only; `RemoteRunner.export` materializes the export and runs the
  harness preflight on that tree before anything leaves (remote.py 150-157). Dry run on HEAD: 1,204
  entries, 1 excluded, 0 problems (key scan skipped). The far side re-hashes every tracked file as a git
  blob after pinning autocrlf and `* -text` (gitbundle.py 198-228), checks the six package versions against
  uv.lock (agent.py 101-110, machine.py 93-106) and runs the preflight there.
- Data (compute/datarules.py): only the two store file names are allowlisted (46-51); a training root takes
  step 2 files only, a backtest root both, at fixed layout paths (57-58, 125-131, 319-345); every file is
  refused by location (sealed roots and names, `.env`, ledger paths and `*spend*.jsonl`, 147-171), by
  sealing magic (188-192), by key bytes on the send side (303-304), by trade dates and metadata range
  (239-258) and by calendar booking through the runner's own `check_bookings` (261-291); the far side
  repeats every content check and hash-binds each file to the sent sha256 (agent.py 123-142) and refuses
  a root holding anything else. Raw vendor chunks cannot travel as data (not allowlisted) or as code
  (forbidden suffix).
- Jobs: kinds are a fixed registry with the backend's own options reserved and user arguments restricted
  to a character allowlist (jobspec.py 39-82); a training kind takes a training root only (105-107); a
  screening job gets the backtest root's research and step 2 sub-roots (agent.py 89-98).
- Results: `verify_results` refuses when the pulled directory has no manifest, when the far ledger recorded
  no manifest sha256, on a manifest hash mismatch, on any file missing, extra, unlisted or differing, and
  when the record's job id, export commit, spec hash or harness sha256 differ (remote.py 397-425;
  files.py 66-93).
- Limits: `Busy` refuses a second running job on the PC (agent.py 240-243), threads 1..14 (jobspec.py 30),
  below-normal priority (agent.py 328, platform.py).
- V10 against the frozen ML design: V10-2 keeps A-1 one value: the batch size comes from the frozen probe
  file (reports/stage_e2b_ml_probes.json is a frozen_input of the manifest; batch 512, peak 302 MiB
  recorded), read by `lstm_batch_size` (adapters.py 59-68) for every fit on either machine; there is no
  re-planning path in code; the GPU check refuses when free VRAM is below the probe's peak plus 0.5 GB
  instead of lowering the batch (151-160); the route manifest records the batch size and the probe
  (manifest.py 110-113). V10-3: every fit's machine is in the hash-chained ledger and the refit hash is
  compared on the same machine only (ledger.py 108-115; train.py 126-134, 146-148). V10-4/5/6/7 are
  what the code does (above). No grid, seed, thread constant, window, block, cost or threshold differs from
  ml_route/constants.py and the frozen text; `LGBM_THREADS = 8` stays a constant, the 14-thread limit is
  the job process's environment.

**NOTE-9. Isolation of the training root from the research store on the PC is by allowlist and code,
not by the operating system.** datarules.py 56-58 and the agent's layout put the training and backtest roots
in sibling directories of one agent root, readable by the same user; a training job "cannot read" the
research store only because ml_route.store's allowlist and the far side's root check are what its code
uses. Same trust model as in-process member code (F-1's item c). If the lead wants a structural guarantee,
run training jobs with a backtest root absent from the PC (delete it before an ML job) or under a separate
OS account.

**NOTE-10. Tracked files that travel in the export and were checked for secrets.** `.claude/settings.json`
(7 lines, no key-like content), `.claude/agents/*.md`, `docs/ACCESS.md` and `docs/HOLDOUT_UNLOCK_LOG.md`
would be exported with the tree; none holds a secret (the key scan covers the Databento key only, and no
other credential exists in the repository by CLAUDE.md's invariants). Also procedural: the export is of a
commit, so the E.2b harness travels only once it is committed (63 harness files are untracked at the time
of this review).

**NOTE-11. V10-2's "machine chosen ... recorded before the first fit" has no explicit field.** The
frozen probe records the GPU it ran on (reports/stage_e2b_ml_probes.json, `probes.lstm.gpu`) and every
fit records its machine, but nothing writes "the LSTM challenger runs on <machine>" before the first fit,
and the LSTM adapter picks cuda or cpu per process (NOTE-5). A one-line record in the route directory before
the first `fit`, checked by later fits, would match the amendment's letter.

## 8. The lead's added inputs: the release calendar and the preflight

**Release calendar: no finding.** Spot check of 25 random entries (seed 20260926): 25/25 OK, each quote
found verbatim (whitespace-normalized) in its saved page under data/vendor/release_pages/, each
`date` + `time_local` in `tz` equal to `instant_utc`, each source entry agreeing with the calendar entry.
Ids: TREASURY_AUCTION 2020-02-26-5Y, 2025-11-24-2Y, 2020-08-13-30Y, 2024-11-05-10Y, 2020-10-07-10Y,
2025-05-28-5Y, 2026-03-11-10Y; NFP 2019-11-01, 2021-11-05; ISM_SERVICES 2019-07-03, 2022-02-03;
API_WSB 2021-11-16 (announced_schedule); G17 2024-12-17; CROP_PROGRESS 2021-06-01, 2023-06-26,
2021-08-02; PPI 2026-05-13; NGS 2019-09-19, 2023-11-16, 2022-10-13 (all three [unverified] by the standing
rule, as the lead ruled); WPSR 2019-11-27, 2026-01-28, 2021-03-03; CPI 2025-10-24 (the shutdown move),
2024-05-15. The F6.4 mapping re-derived from the quoted text agrees with the calendar's
`release_products`: Unemployment Rate -> the 24 listed roots in the product table, 6M/GE/MET/NKD not in
the table, micro siblings M2K, M6B, MGC, MHG, MNQ, MYM, SIL plus MES as ES's micro (the accepted reading);
FOMC -> all 46 universe roots plus MES (47); Crude Oil Inventories -> CL, QM, MCL, RB; Natural Gas
Inventories -> NG, QG plus MNG; Crop Production -> ZC, ZS, ZW, ZM, ZL; member-named additions per OC-N
(for example NFP on 6A..6S, GC, HG, MBT, SI, ZN; WPSR on 6C, HO, NG) are recorded per release with the
naming members. Every entry's product list equals its release's `products`. Coverage 2019-05-01..
2026-06-21 is checked by both consumers (stage_e_runner.py 347-349, ml_route/inputs.py 280-283, 377,
test.py 230). The loader rejects a non-minute or naive instant and an unknown root
(stage_e_rules.py 146-172). See NOTE-3 for the published-versus-scheduled instants.

**The preflight (screening/harness_freeze.py): can a session pass it without the frozen files?** Not by
editing, removing or adding a listed or unlisted source: a wrong expected hash is refused (86-88, 108-109),
a changed byte in any of the 1,028 files is refused (93-101), an unlisted *.py under a harness directory is
refused (91-92), the manifest cannot carry its own hash (note 280-281), and the tests prove each refusal
(tests/test_harness_freeze.py, 10 passed per the STATE file). The two ways found around it leave every
listed file byte-identical: F-1 (an unhashed package init the documented workflow creates) and F-2
(bytecode or extension shadowing). Both have small fixes that rebuild the manifest once.

---

## Findings table

| Id | Grade | Item | File:lines | One line |
|---|---|---|---|---|
| F-1 | BLOCKING | 3, 8 | screening/stage_e_freeze.py 87-96, 190-192; screening/harness_freeze.py 28-29, 67-78, 135-140; strategy/stage_e/_template.py 5-6 | `strategy/members/__init__.py` runs on every screening run and is hashed by neither the cluster freeze nor the harness manifest; proven to change a frozen constant with every check passing |
| F-2 | SHOULD FIX | 3, 8 | screening/harness_freeze.py 67-78, 93-101, 177 | an unchecked-hash `.pyc` (or a `.so`) beside a byte-identical listed source passes the preflight and is what runs; proven |
| F-3 | SHOULD FIX | 3, 6 | screening/stage_e_start_dates.py 183-200, 361-375, 428-445, 482-500 | S_X in a start-rule file is not re-derived from the file's own medians and the step 2 store it read is not pinned; a contradictory `s_x` is accepted; proven |
| F-4 | SHOULD FIX | 6 | screening/stage_e_stats.py 102, 247-256, 262-272; docs/DECISIONS.md 149-150 | `holm_alpha_k(9)` raises and `k_from_tiers` cannot count the route family, against V6's "at most 9" and 0.05 / (K + 1) |
| NOTE-1 | NOTE | 1 | screening/stage_e_engine.py 339-357, 443-471 | closure-gap and session-end exits fill at the decision bar's close (flagged, counted; not future information) |
| NOTE-2 | NOTE | 1 | screening/stage_e_rules.py 361-373 | the locked-market test reads the fill bar's whole range; conservative direction only |
| NOTE-3 | NOTE | 1, 8 | reports/stage_e2b_release_calendar.json (`moves`, `cancellations`) | published instants stand in for scheduled ones (15 moves, 14 cancellations, 2020-2026); cost side in the engine; say so in run summaries |
| NOTE-4 | NOTE | 2 | ml_route/store.py 118-131 | the training store trusts `trade_date` labels; add `check_bookings` as the runner and the compute rules do |
| NOTE-5 | NOTE | 2, 7 | ml_route/adapters.py 151-160 | the LSTM falls back to CPU silently when CUDA is unavailable; refuse by name and record the device |
| NOTE-6 | NOTE | 3 | screening/stage_e_freeze.py 150-165; stage_e_start_dates.py 361-375; stage_e_runner.py 291-300 | write-once and chmod 444 are the only guards on freeze, start-rule and record files; no git-blob check; `--out-dir` free |
| NOTE-7 | NOTE | 5 | data/trade_date_guard.py 30-32; data/step2_store.py 189-202 | the first hour of trade date 2024-03-01 (embargo) stays plaintext in the unsealed February chunk, dropped unread by the store (as for MES) |
| NOTE-8 | NOTE | 5 | data/pull_step2.py 618-636 | a seal failure on the resume path purges a paid-for chunk (cost, not integrity) |
| NOTE-9 | NOTE | 7 | compute/datarules.py 56-58, 319-345 | training and backtest roots are sibling directories on the PC; isolation by allowlist and code only |
| NOTE-10 | NOTE | 7 | compute/gitbundle.py 29-30, 102-119 | `.claude/settings.json`, `.claude/agents/*.md`, `docs/ACCESS.md`, `docs/HOLDOUT_UNLOCK_LOG.md` travel; no secret found in them; the harness travels only once committed |
| NOTE-11 | NOTE | 7 | ml_route/adapters.py 59-68, 151-160; ml_route/manifest.py 110-113 | V10-2's "machine chosen" is recorded per fit and in the probe, not as one field written before the first fit |

Non-findings, for the record: items 1 and 2 (no look-ahead, no leakage path), item 4 (every planted leak
caught; no canary that cannot fail), item 5 (no holdout exposure), item 7 (no path for a holdout bar, secret
or ledger to the PC; results refused without hashes; V10 keeps A-1 and every statistical choice), item 8
(calendar quotes and mapping verified on the sample).
