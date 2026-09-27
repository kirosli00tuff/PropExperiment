# Stage E.2b return: screening runner, ML pipeline, canaries, step 2 path, Windows backend, harness freeze

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh; session 0d3e5a56. Date: 2026-09-26. All times PDT (America/Vancouver).

## 1. Verdict summary

**Frozen and committed (not pushed): 273c27b, "Stage E harness freeze". Manifest sha256
cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45 (1,032 files).**

- **Built:** the generalized Stage E runner with cross-product alignment, the D4 power check, the D5 screen and tiers, the
  start rule, the member template and the cluster code freeze (MES regressions C1, C2, C4 bit for bit); the ML route
  pipeline with every M7 test and its test side; canaries for every group, cross-product and the ML wrapper; the trade-date
  purchase guard, the step 2 path with per-product holdout-2 sealing and the step 2 store; the Windows backend
  (localhost-tested), its guide and the V10 amendment; and two inputs the frozen design needed that no stage had built: the
  release calendar and the start-date builder.
- **Not built:** the non-MES composite verdict (OC-Q; blocks edge claims only). Nothing bought.
- **Review (Fable max):** no look-ahead, no leakage path, no holdout exposure, every canary can fail; 1 BLOCKING (an
  unhashed member package init) and 3 SHOULD FIX, all fixed.
- **Quotes:** ML route $189.31 (acct-2 top-up $167.79; cap to at least $292.79); K2's confirmation $40.50 (top-up $18.98).
- **K2's screening session is unblocked** (no purchase needed; its power check waits for the step 2 purchase).

## 2. Guardrail evidence

**Start checks (12:33-12:40 PDT), verbatim:**
```
$ git status --short
(empty)
$ git log --oneline -3
2634b65 docs: Stage E.2b prompt adds the Windows compute backend as an optional machine (V10)
3017e97 Revert "docs: Stage E.2b prompt adds the Windows compute backend (user decision V10)"
4330a05 docs: Stage E.2b prompt adds the Windows compute backend (user decision V10)
$ git merge-base --is-ancestor a3c3292 HEAD   -> a3c3292 is ancestor
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status   (summary of the keys)
all_ok True, unlocks_logged 0, unlock_log_ok True; holdout_2.all_ok True, holdout_2.unlocks_logged 0,
holdout_2.unsealed_plaintext_present [], holdout_2.confirmation_has_no_holdout2_rows True
$ python3 check_frozen.py   (reports/stage_e2b_briefs/check_frozen.py)
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
OK       reports/stage_e2a_costs.json f4360bb7...df14
OK       reports/stage_e2a_vehicle_sizes.json 280d7e9d...7325
OK       reports/stage_e2a_vehicles.json 1f1cafee...9913
OK       reports/stage_e2a_vehicle_rule_readings.md 8c3c29dd...b458
OK       reports/stage_e2a_epsilon_declaration.md ccdb8ec5...8c7c
OK       reports/stage_e2a_epsilon_declaration_addendum.md e6253be2...8d32
OK       reports/stage_e2a_source_window_amendment.md 9fe401c1...f13d
OK       reports/stage_e2a_epsilon.json 4e2c7731...f496
ALL_OK
$ uv run pytest -q
1891 passed, 2 skipped, 1 xfailed, 53 warnings in 347.95s (0:05:47)
```
The audit files of the two earlier manifests are compared at their freeze-commit blobs (848f331 and ba67073), as those
manifests' notes require. The ledger at start: ledger/databento_spend.jsonl, 9,155 lines.

**End checks, verbatim:** run at 19:16 PDT, right after the freeze commit; the suite 19:16:49-19:30:40.
```
$ git status --short
?? reports/E.2b_RETURN.md
?? reports/stage_e2b_STATE.md
?? reports/stage_e2b_briefs/
?? reports/stage_e2b_g2a_inputs_worker.md
?? reports/stage_e2b_g2b_calendar_worker.md
?? reports/stage_e2b_g4_mltest_worker.md
?? reports/stage_e2b_release_names_worker.md
?? reports/stage_e2b_task1_runner_worker.md
?? reports/stage_e2b_task1_stats_worker.md
?? reports/stage_e2b_task2_ml_worker.md
?? reports/stage_e2b_task3_canaries_worker.md
?? reports/stage_e2b_task4_purchase_worker.md
?? reports/stage_e2b_task5_windows_worker.md
$ git log --oneline -3
273c27b feat: Stage E harness freeze (Stage E.2b), manifest sha256 cf939270
2634b65 docs: Stage E.2b prompt adds the Windows compute backend as an optional machine (V10)
3017e97 Revert "docs: Stage E.2b prompt adds the Windows compute backend (user decision V10)"
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2: all_ok True unlocks_logged 0 unsealed_plaintext_present [] confirmation_has_no_holdout2_rows True products {}
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
OK       reports/stage_e2a_costs.json f4360bb7...df14
OK       reports/stage_e2a_vehicle_sizes.json 280d7e9d...7325
OK       reports/stage_e2a_vehicles.json 1f1cafee...9913
OK       reports/stage_e2a_vehicle_rule_readings.md 8c3c29dd...b458
OK       reports/stage_e2a_epsilon_declaration.md ccdb8ec5...8c7c
OK       reports/stage_e2a_epsilon_declaration_addendum.md e6253be2...8d32
OK       reports/stage_e2a_source_window_amendment.md 9fe401c1...f13d
OK       reports/stage_e2a_epsilon.json 4e2c7731...f496
ALL_OK
$ uv run python -m screening.harness_freeze verify --expected cf939270...
preflight OK: cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
$ git diff --stat
(empty)
$ uv run pytest -q
2863 passed, 2 skipped, 1 xfailed, 54 warnings in 829.30s (0:13:49)
```
The untracked files are the return document, the STATE file, the briefs and the worker reports, left for review; after this document was finished, progress.md and docs/STAGES.md are also modified and uncommitted (their entries for this stage). Earlier full runs: 17:42-17:56 2780 passed, 3 skipped, 1 xfailed (before the review); 19:00-19:14 2863 passed, 2 skipped, 1 xfailed (after the fixes, manifest v2).

**Ledger diff.** `git diff --numstat -- ledger/databento_spend.jsonl`: 5668 added, 0 removed. By script: all 5,668 added
lines are `"event": "quote"` under session `stage-E.2b-2026-09-26`, account acct-2, with `usd` 0.0 and
`session_cumulative_usd` 0.0 on every line; `shared_cumulative_usd` is 103.477194 on every line (unchanged: acct-2's
spend to date, so $21.52 of its $125.00 cap remains). `quoted_usd` carries each quote's price. No purchase, no cap change
(data/config.py adds the E.2b block with $0.00 session and request caps and STEP2_ROOT; ACCOUNT_2_CAP_USD unchanged).

**Which bars were read, and why.** Only MES's own research-window bars, by RunnerCoder's three MES regressions
(tests/test_stage_e_mes_regression.py) and the MES engine-parity tests. Every other test ran on synthetic data. No Stage
E product's price, volume or bar row was read. One boundary deviation, reported by the worker: at about 13:03 RunnerCoder
read the parquet SCHEMA and key metadata (no rows) of data/processed/ZN/ohlcv-1m_ZN_v_0_2025-04-01_2026-06-19_research.parquet
with pyarrow.read_schema, which showed column names and types, the metadata key names and ZN's first roll record; no bar,
price or volume. Free Databento metadata/cost calls were made for the quotes only. The release sourcers fetched public web
pages (BLS, Federal Reserve, EIA, USDA, ISM via PR Newswire, API, FiscalData), saved under data/vendor/release_pages/.
No TopstepX reference or call; nothing under live/ or ops/; docs/NULL_CRITERIA.md, reports/stage_d1f_confirmation_list.md,
every E.1/E.2a frozen file and every E.2a hashed table untouched (end checks above); REGISTRATION.md 0 bytes; nothing run
or configured on the Windows PC (the backend was tested against a user-level SSH server on 127.0.0.1 only).

## 3. Results per task

Test counts per new test file are in the table at the end of this section (collected after the last fixes).

**Task 1: the generalized screening runner (D11.5, D11.6).** RunnerCoder-OpusXHigh, ScreenStatsCoder-OpusXHigh, and
InputsCoder-OpusXHigh for the start dates. screening/runner.py is byte-identical (lead ruling OC-A); the Stage E path is
new code: screening/stage_e_runner.py (the one entry: `python -m screening.stage_e_runner --harness-sha256 SHA --cluster
K# (--member LABEL | --all) --window research|confirmation --research-root DIR --step2-root DIR --out-dir DIR`),
stage_e_engine.py (multi-leg engine; sim/engine.py untouched), stage_e_rules.py (the D9 constraint set, the D8 event-window
cost at the largest s_b (T12-4), the fill guard, the CPI window, R-F1/R-F4 flattens, vendor-unit ticks), stage_e_frozen.py
(the four E.2a tables loaded only after their sha256 checks), stage_e_align.py (D4 windows, the shared UTC minute grid, no
forward fill, D9 coverage), stage_e_freeze.py (per-cluster member code freeze with the static member allowlist),
stage_e_mes_rules.py, stage_e_mes_regression.py, data/stage_e_bars.py (bars booked by each product's group calendar;
holdout-1, holdout-2 and March 2024 rows refused by trade date, MBT's 2026-06-22 rows included), strategy/stage_e/
(interface.py, _template.py) and strategy/members/__init__.py (empty, frozen). Statistics: screening/stage_e_stats.py
(+ _units, _power, _start): the D4 power check (analytic n_b and n_a, block bootstrap where they differ by more than 15%,
the larger; "inconclusive by design"), the D5 screen (mean > 0 and daily t >= 1.0, zeros on no-trade days) and Tiers
A/B/excluded, Holm at 0.05 / K with K up to 9 (V6), and the D4 start rule. The runner computes all of them.
- E.2a carried items: roll blackouts from each group calendar (L-8); vendor-unit ticks (ZC, ZW, ZS, ZL, HE, LE at 100 x the
  E.0 tick); R-F1 and R-F4 flattens; the event-window cost at the largest s_b (T12-4); MBT's 2026-06-22 rows refused
  (L-9); 2026-06-18 and 2026-06-19 excluded from every product's research window as possible unseen roll-blackout dates
  (UR-1, accepted by the lead: symbology ends before 2026-06-21, and NG, MNG, QG, grains, metals and MBT had rolls due).
- **MES regressions (bit for bit)** on MES's own research bars, D.1's 289-date train-union window. Recorded =
  reports/stage_d1d_accounting.json; every series (daily net, trip P&L, daily trips, trip micros) is also float-for-float
  equal to the unchanged screening.runner.screen_candidate:

| Trial (class) | n_trips | net P&L USD | p / R | daily mean / sd / t | Equal |
|---|---|---|---|---|---|
| A-H2 RTH close window, buy (C1) | 266 | 587.95 | 0.49248 / 1.12819 | 2.034429 / 64.415517 / 0.5369 | yes |
| B-H1 ORB hold 75 (C2) | 276 | -292.95 | 0.53261 / 0.85684 | -1.013668 / 121.35494 / -0.142 | yes |
| D-H2 inverse-vol sizing, 1-5 micros (C4) | 276 | -2320.19 | 0.46014 / 0.84350 | -8.028339 / 69.528841 / -1.963 | yes |

- ScreenStatsCoder reproduced all 95 measured D.1e power-check members at eps 34 (n_a, n_b, 1,689 curve points, flags) and
  D.1f's start rule (V_ref 1763, S = 2020-02-03; 2020-01-02 at 0.15, 2020-03-02 at 0.40).

**Added inputs the frozen design requires (lead rulings OC-J, OC-K).** (a) The release calendar,
reports/stage_e2b_release_calendar.json (sha256 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8): 2,609
release instants, 2019-05-01..2026-06-21, for D8's event-window cost, D9.5a's fill guard, D9.12's CPI window and the ML
features F13-F15. Sources: reports/stage_e2b_release_sources_macro.json (NFP 85, CPI 85, FOMC 57; 0 unverified),
..._commodity.json (EIA WPSR 371, EIA gas storage 373 of which 365 [unverified] from EIA's standing Thursday rule because
the Wayback Machine refused connections from about 14:00, Crop Production 85 + 7 annual, WASDE 85), ..._named.json (PPI,
ISM Services, G.17, API bulletin 372 from API's announced schedules, Crop Progress, Treasury 2-30 year nominal coupon
auctions; 1,461). Every quote verified verbatim against its saved page by script; the Fable review re-checked 25 random
entries (25/25) and re-derived the F6.4 product mapping. Member-named releases come from
reports/stage_e2b_release_names.json (64 members read, 18 distinct releases; five daily price benchmarks excluded,
OC-N). (b) The start dates: screening/stage_e_start_dates.py builds reports/stage_e_start_rule_<SET>.json per cluster or
for the ML route from the research and step 2 stores (D6's day session for every root, OC-S), write-once; the one shared
loader re-derives S_X from each file's own medians and pins the step 2 store's sha256 (review F-3). No start-rule file
exists yet (no step 2 data).

**Task 2: the ML route pipeline and M7 tests (D11.7).** MLPipelineCoder-OpusXHigh, then MLTestCoder-OpusXHigh (OC-L).
Dependencies (done 12:44-12:52, before any other work): lightgbm 4.7.0, torch 2.14.0+cu130 (CUDA 13.0 wheels for linux
x86_64 and win_amd64; arch list includes sm_75 and sm_86), scikit-learn 1.9.1 (the frozen ML-A11 needs it); no existing
package's pinned version changed (numpy, pandas, pyarrow identical). ml_route/ holds the feature pipeline with
availability times and the validator (M4, M7.1), the net target with D8 costs and D9.5a's fill-guard deferral (OC-M), the
calendar-only six-block cut and the CPCV splitter (10 splits, purge, one-trade-date embargo; M7.3), LightGBM and LSTM jobs
with fixed seeds, frozen thread counts, resumable JSONL ledgers and the model hash chain (M7.6), the training store
reader (step 2 root only, path allowlist, every row booked by the group calendar, rows on or after 2024-03-01 and before
S_X refused, store sha256 pinned to the start-rule file), the surrogate trees and block-6 pre-test (M5, ML-A01, ML-A02),
the rule wrapper and the Stage E adapter (one engine run per exposure, M5's mean over products with rows; OC-P), the
E.ML-test entry (hash chain verified before any bar; zeros on window dates without rows, RT-4), the training-window DSR
and PBO (M6), lstm_machine.json before the first LSTM fit (V10-2), and the route manifest writer. Every M7 test, 1 to 7,
with known answers (the two M7.1 canaries, perturbation incl. cross-product F16, fold, the planted research bar and
planted research path, normalization, hash chain, the wrapper through the existing canaries).
- **Probes** (reports/stage_e2b_ml_probes.json; synthetic data of the real size, about 450,000 rows x 20 features x 31
  products, on this ThinkPad):

| Challenger | Measured | Peak memory | Projected full run (M8's grid) |
|---|---|---|---|
| LightGBM, one CPCV split, 8 threads | 3.9 s fit (largest configuration), 4.9 s fit + score | 774 MiB RAM | 0.29 h (upper 0.38 h) for 24 configurations x 11 fits |
| LSTM, one epoch, RTX 3050 (driver 595.91.07, CUDA 13.0) | 3.4 s per epoch at batch 512 | 1,528 MiB RAM; 302 MiB VRAM peak (138 MiB reserved + 164 MiB context) | 0.70 h (upper 1.06 h) for 12 configurations x 11 fits x 8 epochs |

  A-1's batch plan kept 512 (3,794 MiB of 4 GB free, far above 0.5 GB). These are far below M8's guesses (7-14 h and 18-35
  h); building the row table from real bars was not timed, so E.ML-train re-times its first real fit. E.ML-test at
  research-window size: 85 s and 439 MB per exposure (synthetic).

**Task 3: canaries (D11.9).** CanaryCoder-OpusXHigh: tests/test_stage_e_canaries.py (208) and tests/_stage_e_canary_kit.py.
One synthetic product per group (MNQ, ZN, 6E, MCL, MGC, ZC, LE, MBT): planted future bars, planted settlement values,
release values, hindsight flags and a planted bar inside a closure, each paired with a deliberately broken control that it
catches; cross-product (MNQ traded, ZN signal): a planted future bar in ZN changes no MNQ decision, and leg-peek,
misaligned and backfilled leaks are caught; the ML wrapper's canary on the Stage E adapter catches a misaligned lead and a
two-bar engine peek. Every canary fails loudly when its leak is planted. It found one runner defect (C-1: after a vendor
gap on an early-close date the engine could fill at a bar inside a scheduled closure), fixed under ruling OC-T; the 24
cases pass. The Fable review planted nine further leaks in scratch copies of the real code: all nine caught.

**Task 4: the step 2 purchase path and quotes (no purchase).** PurchaseCoder2-OpusXHigh. data/trade_date_guard.py books
every minute of a request to its CME trade date before any vendor call; the step 1 buy (pull_universe) and the step 2 path
refuse holdout-1 minutes, and holdout-2 minutes outside the sealing download (the L-9 fix; MBT's case is a test).
data/pull_step2.py (ohlcv-1m monthly chunks 2019-05..2025-03, oldest first, per product from its first priced month:
MBT 2021-04, MCL 2021-06, MHG 2022-04 (OC-R); per-cluster mode including every signal-leg root; ML-route mode; acct-2
gate and ledger; resume; `--quote-only` issues no billable request; `--buy` runs the preflight and refuses at the $0.00
E.2b caps), data/step2_seal.py (each holdout-2 chunk, range=2024-03-01_2024-04-01 through range=2025-03-01_2025-04-01,
sealed in the download call after its byte check, one sealed store per product, the same unlock log),
data/step2_store.py (the step 2 bar store in its own root data/processed_step2/ (OC-G): trade dates
2019-05-06..2024-02-29, rows booked to 2024-03-01 or later dropped unread, sealed chunks never opened), data/holdout.py's
status extended additively to per-product holdout-2 stores. **Quotes** (reports/stage_e2b_step2_quotes.json and .md;
session stage-E.2b-2026-09-26, $0.00 caps; acct-2 credit $21.52 by the gate's arithmetic, cap $125.00):

| Request set | Quoted | acct-2 top-up at the quote | at quote + 10% (D13) | ACCOUNT_2_CAP_USD needed |
|---|---|---|---|---|
| (a) ML route, 31 price-path contracts, 2019-05..2025-03 | $189.31 | $167.79 | $186.72 | at least $292.79 ($311.72 with 10%) |
| (b) each cluster's chosen vehicles | $128.34 | $106.82 | $119.65 | at least $231.82 |
| (b2) each cluster's purchase: traded vehicles plus every signal-leg root | $162.78 | $141.26 | $157.53 | at least $266.26 |

Per cluster, set (b2) alone: K1 $22.11 (top-up $0.59), **K2 $40.50 (top-up $18.98; $23.03 with 10%)**, K3 $49.34 ($27.81),
K4 $11.46 ($0), K5 $9.74 ($0), K6 $26.52 ($5.00), K7 $3.11 ($0), K8 $29.65 ($8.13). Cluster top-ups do not add up (each is
that cluster alone against today's credit).

**Task 5: the Windows compute backend (V10).** WindowsBackendCoder-OpusXHigh. compute/ (remote.py, agent.py, datarules.py,
gitbundle.py, jobspec.py, transport.py, detach.py, ledger.py, files.py, machine.py, platform.py, synthetic_job.py): the
ThinkPad runs the preflight, checks every data file, exports the frozen commit's tree without ledger/ as a reproducible
single commit (git history carries the ledger) and sends it as a git bundle over SSH; the agent checks HEAD, every tracked
file's bytes, the installed library versions against uv.lock and the preflight, runs the job detached at below-normal
priority with a thread cap, and results come back with a sha256 manifest that must verify. Data rules refuse sealed
chunks, any bar booked to a holdout-1, holdout-2 or embargo trade date (by booking every row on the CME calendar), the
Databento key (by content scan), the ledger; a training job's root may hold only the step 2 store. Tested end to end over
SSH to a user-level asyncssh server on 127.0.0.1 (no system SSH server exists here), including an interrupted-and-resumed
run on either side, a job surviving the SSH session's end, hash-mismatch refusal, and planted forbidden files.
tests/test_cross_platform_static.py flags Linux-only calls in everything the PC runs (import closure of the far side's
entry modules); purchases, sealing and the ledger are exempt by name (ThinkPad-only by V10-4); one lead-reviewed entry
(funnel/simulator.py's default-context pool, portable under spawn; OC-O). docs/WINDOWS_SETUP.md is the user's guide, with
an 18-item E.2c checklist of everything only the real PC can verify. The V10 amendment
(reports/stage_e2b_v10_amendment.md, lead) and its docs/DECISIONS.md entry: the PC is optional for ML training and
backtests; V10-2 fixes one machine and one A-1 batch size per LSTM grid before the first fit; V10-4 what never travels;
V10-5 M7.4 kept by separate roots; no statistical choice changes. The Fable review found no path for a holdout bar, a
secret or the ledger to reach the PC and confirmed V10 leaves A-1 and every statistical choice intact.

**Task 9: MBT's holdout-1 rows.** docs/DECISIONS.md entry (2026-09-26): the 1,617 bars booked to 2026-06-22 arrived inside
the step 1 files because the guard checked timestamps, were dropped unread by the bar builder, never written to any
parquet, and are now refused by the loader (tests/test_stage_e_loader.py::test_mbt_rows_booked_to_holdout1_trade_date_2026_06_22_are_refused_ruling_L9),
the purchase guard (tests/test_e2b_trade_date_guard.py::test_mbt_request_ending_2026_06_21_is_booked_partly_to_holdout1_and_refused)
and the Windows backend's data rules. Nothing deleted.

**Task 6: the harness freeze manifest.** screening/harness_freeze.py (preflight and builder; lead):
reports/stage_e2b_harness_freeze.json lists every file in rules/, sim/, screening/, funnel/, data/ (code and calendars;
data sub-directories excluded), ml_route/, compute/, strategy/stage_e/ and strategy/members/__init__.py; the repo-internal
import closure of the Stage E entry points (strategy/interface.py, the pinned D.1f statistics); the frozen inputs (the
E.2a hashed tables and funnel cells, the release calendar and its sources, the probes, the V10 amendment, pyproject.toml,
uv.lock); both earlier manifests and every file they list; and the Stage E tests (M7.8's "every M7 test"). The preflight
requires the manifest's sha256 on each entry's command line (`--harness-sha256`), refuses any listed file that differs
by one byte, any unlisted module in a harness directory, member code outside strategy/members/k1..k8, unlisted binary
modules or loose bytecode, and any bytecode Python would load in place of a harness source that does not match it.
Deliberately not frozen: append-only logs (unlock log, ACCESS.md, ledger), start-rule files, quote reports, data files.
**Manifest v3, committed in 273c27b: sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45**, 1,032 files (harness_code 135, frozen_input 808, earlier_freeze 38, import_closure 11, stage_e_test 40), HEAD 2634b65 at creation; verified by script (`python -m screening.harness_freeze verify --expected ...`); v1 (eb78185a..., reviewed) and v2 (ef2074f7..., after the fixes) are refused. tests/test_harness_freeze.py proves the refusal of a one-byte change to a listed file and to a frozen table, a missing file, an unlisted module, a manifest rebuilt without the expected hash, member code outside k1..k8, and unchecked-hash, forged-timestamp, binary and loose bytecode.

| Test file | Tests | What it proves |
|---|---|---|
| tests/test_build_release_calendar.py | 43 | calendar assembly: F6.4 and named mapping, quotes and instants verified, write-once |
| tests/test_compute_datarules.py | 36 | what may never reach the PC: sealed chunks, holdout/embargo bars, the key, the ledger |
| tests/test_compute_remote_e2e.py | 23 | end to end over SSH to localhost: run, resume on either side, detachment, hash refusal |
| tests/test_compute_units.py | 61 | job spec, ledgers, export commit, agent checks, priority, thread caps |
| tests/test_cross_platform_static.py | 6 | no Linux-only call in anything the PC runs |
| tests/test_e2b_pull_step2.py | 39 | step 2 plan, sealing order, caps on acct-2, resume, quote-only, listing months (OC-R) |
| tests/test_e2b_step2_store.py | 12 | step 2 store: 2024-03-01+ rows dropped unread, sealed chunks never opened |
| tests/test_e2b_trade_date_guard.py | 20 | the trade-date purchase guard (L-9), MBT's case |
| tests/test_harness_freeze.py | 17 | the preflight refuses one-byte changes, unlisted modules, rebuilt manifests, stray bytecode (F-2) |
| tests/test_stage_e_alignment.py | 10 | UTC minute grid, no forward fill, a leg without a bar blocks opening, D4 cross-product windows |
| tests/test_stage_e_canaries.py | 208 | canaries per group, cross-product, closure bars (C-1), ML wrapper |
| tests/test_stage_e_engine_mes_parity.py | 9 | the Stage E engine under MES rules equals sim/engine.py |
| tests/test_stage_e_freeze.py | 44 | cluster code freeze; the empty members init; the member import allowlist (review F-1) |
| tests/test_stage_e_frozen.py | 10 | the E.2a tables load only at their recorded sha256 |
| tests/test_stage_e_loader.py | 19 | trade-date booking; holdout-1, holdout-2, embargo refusals; MBT 2026-06-22; step 2 store pinning |
| tests/test_stage_e_mes_regression.py | 7 | C1, C2, C4 MES trials bit for bit against D.1d's record and the unchanged runner |
| tests/test_stage_e_rules.py | 23 | D9 constraints, event-window cost (largest s_b), fill guard, CPI window, flattens, closure bars |
| tests/test_stage_e_runner.py | 25 | the entry: frozen inputs only, preflight first, tiers, refusals recorded by name, start-rule pinning |
| tests/test_stage_e_start_dates.py | 72 | start-date builder and loader: D6 day session, rule re-derived, conflicts refused (F-3) |
| tests/test_stage_e_stats.py | 45 | D5 screen, tiers A/B/excluded (OC-H), Holm with K up to 9 (F-4), units |
| tests/test_stage_e_stats_power.py | 35 | D4 power check, n_a (OC-I), D.1e's 95 members reproduced |
| tests/test_stage_e_stats_start.py | 18 | D4 start rule, D.1f's MES S reproduced |
| tests/test_stage_e_template.py | 3 | the member template passes the freeze and runs |
| tests/test_ml_route_*.py (13 files) | 187 | every M7 item 1-7 with known answers, CPCV, hash chain, store allowlist and bookings, adapter, E.ML-test, DSR/PBO, probes, the review fixes |
| **total (new)** | **972** | plus tests/_stage_e_synthetic.py, tests/_stage_e_canary_kit.py, tests/_compute_fixtures.py (helpers) |

## 4. Delegation record

| Agent | Worker file | Model | Effort | Objective | Status | Deviations |
|---|---|---|---|---|---|---|
| RunnerCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 1: the Stage E runner, alignment, E.2a carried items, template, cluster freeze, MES regressions; follow-ups OC-T (canary C-1..C-3) and review F-1 | done | read ZN's research parquet schema and metadata once (no rows); moved MesRules to a new module to keep the engine under 800 lines |
| ScreenStatsCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 1: D4 power check, D5 screen and tiers, Holm, D4 start rule; follow-ups OC-I (n_a) and review F-4 | done | a never-reached power grid is labelled from bounds (conservative; D.1e silently kept the analytic figure) |
| MLPipelineCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: dependencies, ml_route pipeline, M7 tests, probes | done | also pinned scikit-learn (ML-A11 needs it) |
| PurchaseCoder2-OpusXHigh | worker-xhigh | opus | xhigh | Task 4: trade-date guard, step 2 path and sealing, step 2 store, quotes; follow-up OC-R, holdout status, set (b2) | done | none |
| WindowsBackendCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 5: compute/, localhost SSH tests, static check, docs/WINDOWS_SETUP.md | done | export commit without ledger/ instead of the frozen commit (accepted); asyncssh dev dependency |
| ReleaseNamesExtractor-SonnetMed | worker-medium | sonnet | medium | release names in the frozen catalog (complex extraction) | done | none |
| ReleaseSourcerMacro-OpusHigh | worker-high | opus | high | NFP, CPI, FOMC instants 2019-05..2026-06 | done | none; found D.1f's missing 2020-01-29 FOMC entry |
| ReleaseSourcerCommodity-OpusHigh | worker-high | opus | high | EIA WPSR, EIA gas storage, Crop Production, WASDE instants | done after the usage-limit pause | 365 gas-storage dates [unverified] (Wayback down) |
| ReleaseSourcerNamed-OpusHigh | worker-high | opus | high | PPI, ISM Services, G.17, API bulletin, Crop Progress, Treasury auctions | done | API dates from announced schedules |
| MLTestCoder-OpusXHigh | worker-xhigh | opus | xhigh | the ML route's test side (OC-L): adapter, E.ML-test, DSR/PBO, loaders; follow-ups OC-P, RT-4, review NOTE-4/5/11, F-4 wiring, F-3 (b) | done | one edit to MLPipelineCoder's test (a temporary root) |
| InputsCoder-OpusXHigh | worker-xhigh | opus | xhigh | start dates and the shared loader (OC-K), runner Q10; follow-ups OC-S/Q-3/Q-4 and review F-3 | done | none |
| CanaryCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 3: canaries per group, cross-product, ML wrapper | done after the usage-limit pause | none; finding C-1 |
| CalendarAssembler-OpusXHigh | worker-xhigh | opus | xhigh | assemble and verify the release calendar (OC-J, OC-N) | done | two helper modules to stay under 800 lines |
| HarnessAuditor-FableMax | worker-max | fable | max | Task 7: the adversarial harness review | done | none |

Planned but not spawned as named: none. Unplanned spawns (lead rulings, section 6): ScreenStatsCoder (OC-B), the four
release workers and CalendarAssembler (OC-J), InputsCoder (OC-K), MLTestCoder (OC-L). Resumed workers (small follow-ups,
SendMessage): RunnerCoder x2, ScreenStatsCoder x2, MLTestCoder x3, InputsCoder x2, PurchaseCoder2 x1, CanaryCoder x1 and
ReleaseSourcerCommodity x1 after the pause. Concurrency never exceeded 4.

## 5. Verification

The single adversarial review: HarnessAuditor-FableMax (fable, max; wrote none of the code), 17:58-18:26, against manifest
v1 (eb78185a36e4c5a31e864aa4bdc2eb4d425e5705b67029af4ceb6a438de44662): reports/stage_e2b_harness_review.md. Headline: no
look-ahead in the runner, no leakage path in the ML pipeline, no holdout exposure in the step 2 path, no way for a holdout
bar, a secret or the ledger to reach the PC, V10 keeps A-1 and every statistical choice; every canary can fail (nine
planted leaks caught). Findings: 1 BLOCKING, 3 SHOULD FIX, 11 NOTE. The lead's rulings and every fix:
reports/stage_e2b_harness_rulings.md. In brief:

| Id | Grade | Finding | Ruling and fix |
|---|---|---|---|
| F-1 | BLOCKING | strategy/members/__init__.py ran unhashed on every screening run (proven: it changed a frozen runner constant with every check passing) | fixed: the empty init is frozen; the cluster freeze refuses a non-empty init; the preflight refuses member code outside k1..k8; a static allowlist checks every member module at freeze and run time |
| F-2 | SHOULD FIX | an unchecked-hash .pyc beside a byte-identical source passed the preflight and ran (proven) | fixed: the preflight refuses unlisted binary modules, loose .pyc, unchecked hash-based .pyc, and any trusted timestamp .pyc that differs from its source |
| F-3 | SHOULD FIX | a start-rule file's s_x was not re-derived from its own medians; the step 2 store it read was unpinned (proven) | fixed: the loader re-runs the rule and refuses any mismatch; confirmation reads and the ML store refuse a store whose sha256 differs from the recorded input |
| F-4 | SHOULD FIX | Holm capped K at 8; V6 makes the route a ninth family | fixed: K up to 9; k_from_tiers requires route_tested |
| NOTE-4, 5, 11 | NOTE | training store trusted trade_date labels; LSTM fell back to CPU silently; V10-2's machine record missing | fixed |
| NOTE-1, 2, 3, 6, 7, 8, 9, 10 | NOTE | fills at the decision bar's close on closure gaps; conservative locked-market test; published instants for moved releases; write-once guards; the embargo's first hour in the February chunk; a seal failure purges a paid chunk; sibling roots on the PC; files that travel | accepted, or instructions for later sessions (section 7) |

No BLOCKING finding required a change to a frozen design. The review was not re-run. The files changed after the audit
are listed in the rulings file; manifest v2 hashes them. No number enters a verdict in this session, so there is no
separate Fable xhigh number check.

## 6. Open choices (the lead's own decisions, each with its reason; each can be overturned)

Scheduling and method
- **OC-A** screening/runner.py stays byte-identical (the D.1f-frozen MES runner); the Stage E runner is new modules. Reason: the MES record rests on it, and the regressions then compare a new path with the old one.
- **OC-B** Task 1 split into RunnerCoder and ScreenStatsCoder (CLAUDE.md: several short workers with one objective each).
- **OC-C** The step 2 bar store builder went to PurchaseCoder2 (it defines the chunk layout); Task 2 kept the ML job's reading side.
- **OC-D** The lead wrote two interface files before spawning (screening/harness_freeze.py's preflight, compute/platform.py), so parallel workers shared one contract.
- **OC-E** Only MLPipelineCoder changed the Python environment; every other worker ran `uv run --no-sync` (one exception: WindowsBackendCoder's asyncssh dev dependency, after the ML dependencies landed).
- **OC-F** Heavy jobs went through a two-slot flock gate (reports/stage_e2b_briefs/heavy.sh), nice 10.
- **OC-G** The step 2 store has its own root, data/processed_step2/, so M7.4 and V10's separate roots are structural.
- **Preflight design** The expected manifest sha256 is a required command-line argument, and unlisted modules are refused (the D.1f review's F1 and F3 lessons); data sub-directories are neither listed nor scanned; append-only logs, start-rule files and quote reports are not frozen. A purchase session's spend-policy edit in data/config.py changes a frozen file: that session writes a new manifest whose only difference is data/config.py's entry and states its sha256.
- **ETA table** The prompt asks for the estimate table "in chat and in the STATE file"; CLAUDE.md says it goes into no markdown file. CLAUDE.md won; the conflict is logged.

- **Commit contents** The freeze commit holds the prompt's list (harness code, tests, manifest, review, rulings,
  docs/DECISIONS.md, quote reports) plus what a fresh checkout needs for the preflight to pass (the frozen inputs:
  release calendar, its sources and names, the ML probes, the V10 amendment, pyproject.toml, uv.lock, .gitignore), the
  user's guide docs/WINDOWS_SETUP.md, and the ledger's 5,668 $0.00 quote lines (the record behind the quote reports).
  Left uncommitted for review, as in E.2a: this document, progress.md, docs/STAGES.md, the STATE file, the briefs and
  the worker reports.
- **Manifest v3** At staging, tests/_compute_fixtures.py (the compute tests' helper) was outside the frozen test patterns;
  adding it made v3, committed; nothing else differs from v2 (reports/stage_e2b_harness_rulings.md).
- **LSTM end-to-end test** skips on a machine without CUDA (review NOTE-5 made training refuse there); it runs here.
- **Resumes over fresh workers** Every follow-up (rulings, the pause, the review fixes) resumed the worker that wrote the
  code, by SendMessage, as small briefs (CLAUDE.md allows this for small follow-ups).

Rulings on the frozen text (each applied in code and tested)
- **OC-H** D9 labels: coverage < 0.95 is excluded before screening; a mean hold under 10 minutes, more than 20 entries a day or a hold under 2 minutes is screened but excluded before confirmation; tiers are A, B or excluded.
- **OC-I** n_a (NULL_CRITERIA_E 5) is computed descriptively at one-sided 0.05 / (9 x the cluster's frozen member count) and joins the simulation lengths as in D.1e; the label depends on n_b alone.
- **OC-J** The release calendar is built in E.2b: D9.12 calls it "a harness input", D8, D9.5a and F13-F15 need it, and no stage had built it.
- **OC-K** A start-date builder and one shared loader, per-set files, used by the runner and the ML route.
- **OC-L** The ML route's test side (adapter, E.ML-test, training DSR/PBO) is built now, because M7.8 freezes "the selection, surrogate, pre-test, ranking and write-up code".
- **OC-M** A training target's fills follow D9.5a (deferred out of [release, release + 2 min), event-window cost inside 30 minutes), as the engine does.
- **OC-N** Release names: F6.4 plus every release a catalog member names (CPI, PPI, ISM Services, G.17, API bulletin, WASDE, Crop Progress, Treasury auctions), for the products the naming members trade; five daily price benchmarks (ECB, London 4pm and Tokyo fixes, LBMA auctions, CME CF BRR) are not releases of information and are present on all five E.2a cost-sample dates, so the time-of-day buckets already price them.
- **OC-O** funnel/simulator.py's default-context pool is portable under spawn; the file is D.1f-frozen and in the epsilon's provenance, so it gets a reviewed static-check entry instead of an edit.
- **OC-P** An ML route rule runs one engine run per exposure and combines by M5's mean over products with rows (M5 step 1's words).
- **OC-Q** The confirmation-window composite verdict (robust zero-edge gate and drift sub-checks) is not generalized beyond MES: the gate is MES-calibrated and generalizing it is a design question outside E.2b's list. It blocks edge claims only, not null statements.
- **OC-R** The step 2 plan starts each contract at its first priced month (MBT 2021-04, MCL 2021-06, MHG 2022-04): months before listing cannot be bought.
- **OC-S** "Day session" is D6's (O_X, C_X) for every root (D1's windows are declared for the coverage proxy only).
- **OC-T** The engine never fills or checks the MLL on a bar inside a scheduled closure; a pending exit or forced flatten before a closure print fills at the last tradable bar's close (the existing session-end convention), flagged and counted; a cost-lookup failure is a named member refusal.
- **V10-2** One machine and one A-1 batch size per LSTM grid, recorded before the first fit.
- Worker questions ruled (details in reports/stage_e2b_STATE.md): runner UR-1 (2026-06-18/19 excluded), Q7 (blackout dates removed, not zeros), Q8 (member modules under strategy/members/k#/), Q10 and Q-3 (mean <= 0 is Tier B; an empty start window is supply 0, inconclusive by design), Q-2 and Q-4 (start-rule sets refused whole; strict cross-file comparison); ML RT-4 (zeros on window dates without rows), RT-5 (one failing exposure excludes the rule); release data (365 [unverified] gas-storage dates and 372 announced API dates kept; CROP_ANNUAL de-duplicated; roots outside rules/products.py dropped from the calendar: NKD, GE, 6M, MET, PL, never traded); Windows (export commit without ledger/, data/build_bars_run.py ThinkPad-only, ML finalize on the ThinkPad); step 2 (shared unlock count kept; sealing ThinkPad-only; MES keeps D.1f's confirmation parquet).

## 7. What the next session must do first

**Push (the planning chat).** origin/main is at 2634b65; the one freeze commit 273c27b is local and unpushed. The
return document, progress.md, docs/STAGES.md, reports/stage_e2b_STATE.md, the worker reports and the briefs are uncommitted
for review (the commit holds the harness, its tests, the manifest, the review, the rulings, docs/DECISIONS.md, the quote
reports and the frozen inputs).

**Frozen files and hashes.** The Stage E harness manifest reports/stage_e2b_harness_freeze.json, sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
(1,032 files): every Stage E command takes `--harness-sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45`, and each session prompt must
state it. Earlier freezes, unchanged: reports/stage_e1_freeze.json (96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c),
reports/stage_e2a_ml_freeze.json (077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2); the eight E.2a tables
(section 2). The release calendar: 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8. Launch every Stage E
entry point with a fresh `PYTHONPYCACHEPREFIX` outside the repository (review F-2's third point).

**Funding the user owes.** acct-2 holds $21.52 of its $125.00 cap. The ML route's history (set a): $189.31 quoted, a top-up
of $167.79 ($186.72 at D13's +10%), and ACCOUNT_2_CAP_USD raised to at least $292.79 ($311.72); the cap is the user's
(Q-1 of E.2a). The first cluster, K2: its screening session needs no purchase; its confirmation purchase is $40.50 (top-up
$18.98, $23.03 at +10%). Every purchase session edits data/config.py (session id, caps), which changes a frozen file: that
session writes manifest v3 whose only difference is data/config.py's entry, shows the diff, and uses the new sha256.

**Manual Windows setup the user owes before E.2c** (docs/WINDOWS_SETUP.md): install Git, uv (and Python through uv), the
NVIDIA driver (about 580 or later, for the CUDA 13.0 torch wheels), and the Windows OpenSSH server; add the ThinkPad's
public key (administrators_authorized_keys if the account is an administrator); set `git config core.autocrlf false`;
set the power plan so the PC does not sleep overnight; open the firewall for SSH on the private profile and the local
subnet only; then E.2c sends the frozen export by git bundle, runs `uv sync` there, and works through the guide's 18-item
checklist (CUDA on the RTX 2060 Super, detachment across SSH disconnect, below-normal priority, long paths, both probes
repeated there with `python -m ml_route.probes versions|lgbm|lstm`). Nothing in the guide stores a secret on the PC.

**What K2's screening session needs from this harness.**
1. Code the members from strategy/stage_e/_template.py under strategy/members/k2/ (strategy/members/__init__.py exists,
   empty and frozen); only the template's import allowlist is accepted.
2. Write the cluster freeze (screening.stage_e_freeze.write_cluster_freeze), then state its sha256 in the run's record and
   the session's return (NOTE-6).
3. Run `PYTHONPYCACHEPREFIX=<fresh dir> uv run python -m screening.stage_e_runner --harness-sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
   --cluster K2 --all --window research --research-root data/processed --step2-root data/processed_step2 --out-dir <dir>`.
   The runner computes the D5 screen and the tiers; the D4 power check needs S_X, which needs the step 2 purchase, so it
   is recorded as not run in the screening session and runs in K2's confirmation session after the purchase and the
   start-rule build (`python -m screening.stage_e_start_dates`), before the list is hashed.
4. Run summaries say that moved and cancelled releases use the published instants (NOTE-3).
5. A member that reads ES, NKD, MET, 6M or BTC as a leg has no D6 session record and its start-rule set is refused by name
   (question 6 below).

**Decisions owed by the user (each refused by name in code until ruled).**
1. The composite verdict (robust zero-edge gate and drift) for non-MES products (OC-Q): needed before any edge claim.
2. A member whose research series has zero variance: the power check is undefined (PowerCheckUndefined).
3. A limit-locked exit still locked at the session end (runner Q4: carry, or close with a flag).
4. D4's union of signal-leg roll blackouts against the K8 catalog text "not excluded" (D4 applied).
5. The five daily price benchmarks left out of the release calendar (OC-N).
6. Start-rule roots without a D6 session record: ES, NKD, MET, 6M, BTC.
7. The ML route: F17's roughly 120-date warm-up leaves about 160 of 300 research dates without route rows (holdout-2
   precedes the research window), so a route rule trades on about half the research window.
8. E.ML-test's Holm K, DSR at program N, composite verdict and per-exposure null ordinal (Q-T1..Q-T4).
9. One unlock count shared by every holdout-2 store (the frozen "same unlock log").
10. K3's two stock-index signal legs are not GLBX futures (step 2 cannot buy them); K8 needs CL if CL is ever declared
    MCL's price path; an empty start window's full-size fallback (D4).
11. D.1f's frozen release table misses the scheduled FOMC statement of 2020-01-29 (found by ReleaseSourcerMacro; D.1f's
    E-H1/E-H2 confirmation series lack that date; D.1f untouched).
12. Data follow-ups: re-crawl the 365 [unverified] EIA gas-storage dates when the Wayback Machine answers; G.17's
    2025-11-24 annual revision is not in the calendar.

## 8. Session cost

Wall clock 12:33-19:40 PDT (7 h 07 min), including one pause: the plan's session usage limit, about 15:07-16:40
(1 h 33 min; HTTP 429 "resets 4:40pm"), which stopped CanaryCoder and ReleaseSourcerCommodity mid-task; both were resumed
from their transcripts. Work time 5 h 34 min. The initial estimate was about 8 h 30 min before the scope grew (the release
calendar, the start-date builder and the ML test side were added by rulings OC-J, OC-K, OC-L). Tokens are from this
session's transcripts (the lead's .jsonl and 14 subagent .jsonl files, each assistant message counted once by message id;
script reports/stage_e2b_briefs/token_accounting.py), taken at 19:31; the lead's last minutes of writing are not included.

**Final table.** Times are first and last transcript entries, with the active segments from the STATE file.

| Task / spawn | Agent | Worker file | Model | Effort | Active segments (PDT) | Active time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup, checks, briefs, interfaces | lead | - | opus | xhigh | 12:33-12:45 | 12 min | in the lead's total | done |
| 1 runner core; OC-T; F-1 | RunnerCoder-OpusXHigh | worker-xhigh | opus | xhigh | 12:43-13:33, 16:51-17:00, 18:27-18:33 | 1 h 05 | 77,444,246 | done; ZN schema read (no rows) |
| 1 statistics; OC-I; F-4 | ScreenStatsCoder-OpusXHigh | worker-xhigh | opus | xhigh | 12:43-13:08, 18:26-18:27 | 27 min | 16,184,829 | done |
| 2 ML pipeline, probes | MLPipelineCoder-OpusXHigh | worker-xhigh | opus | xhigh | 12:43-13:32 | 49 min | 30,323,714 | done; scikit-learn pinned (ML-A11) |
| 4 step 2 path, quotes; OC-R | PurchaseCoder2-OpusXHigh | worker-xhigh | opus | xhigh | 12:43-14:37, 16:43-17:41 | 2 h 52 | 60,054,084 | done |
| 5 Windows backend, guide | WindowsBackendCoder-OpusXHigh | worker-xhigh | opus | xhigh | 13:08-13:59 | 51 min | 33,519,097 | done; export commit without ledger/ |
| release names (OC-J) | ReleaseNamesExtractor-SonnetMed | worker-medium | sonnet | medium | 13:35-13:51 | 16 min | 8,757,586 | done |
| NFP, CPI, FOMC instants | ReleaseSourcerMacro-OpusHigh | worker-high | opus | high | 13:35-13:44 | 9 min | 4,896,274 | done |
| EIA, USDA instants | ReleaseSourcerCommodity-OpusHigh | worker-high | opus | high | 13:44-15:07, 16:43-16:55 | 1 h 35 | 27,345,884 | done after the pause; 365 [unverified] |
| ML test side (OC-L); OC-P, RT-4; review fixes | MLTestCoder-OpusXHigh | worker-xhigh | opus | xhigh | 13:52-14:45, 16:47-16:52, 18:26-18:44 | 1 h 16 | 64,181,458 | done |
| named releases | ReleaseSourcerNamed-OpusHigh | worker-high | opus | high | 14:01-14:27 | 26 min | 14,439,648 | done |
| start dates (OC-K); OC-S; F-3 | InputsCoder-OpusXHigh | worker-xhigh | opus | xhigh | 14:27-14:49, 16:43-16:47, 18:26-18:34 | 34 min | 25,786,753 | done |
| 3 canaries | CanaryCoder-OpusXHigh | worker-xhigh | opus | xhigh | 14:35-15:07, 16:43-16:56 | 45 min | 31,798,723 | done after the pause; finding C-1 |
| calendar assembly | CalendarAssembler-OpusXHigh | worker-xhigh | opus | xhigh | 16:52-17:11 | 19 min | 14,776,022 | done |
| 7 adversarial review | HarnessAuditor-FableMax | worker-max | fable | max | 17:56-18:24 | 28 min | 7,001,014 | done |
| 5L V10 amendment, DECISIONS | lead | - | opus | xhigh | 12:45-12:48 | 3 min | lead | done |
| 9 MBT entry | lead | - | opus | xhigh | 14:34-14:36 | 2 min | lead | done |
| 6 manifest builder, tests, v1 | lead | - | opus | xhigh | 16:48-16:56, 17:56 | 10 min | lead | done |
| integration: static fix, full suite | lead | - | opus | xhigh | 13:59-14:01, 17:01-17:04, 17:42-17:56 | 19 min | lead | done |
| 8 rulings, preflight fixes, suites, v2, v3, commit | lead | - | opus | xhigh | 18:24-19:16 | 52 min | lead | done; v3 for the compute test fixture |
| end checks, return, progress, cost | lead | - | opus | xhigh | 19:16-19:40 | 24 min | lead | done |
| PAUSE (usage limit) | - | - | - | - | 15:07-16:40 | 1 h 33 (excluded) | - | - |
| **Stage total** | lead + 14 workers | | | | 12:33-19:40 | **5 h 34 work** (7 h 07 wall) vs about 8 h 30 estimated | **511,214,353** | lead 94,705,021 (18.5%), workers 416,509,332 (81.5%) |

**Tokens per model:**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 3,588 | 2,596,716 | 476,395,094 | 16,460,355 | 495,455,753 |
| claude-fable-5-1 | 612 | 108,119 | 6,304,637 | 587,646 | 7,001,014 |
| claude-sonnet-5 | 124 | 46,403 | 8,491,786 | 219,273 | 8,757,586 |
| all | | | | | 511,214,353 |

Delegation share: lead 18.5%, workers 81.5%; by tier: Opus 96.9% (lead 18.5%, workers 78.4%), Fable 1.4%, Sonnet 1.7%.
Cache reads are 96.1% of all tokens. The largest workers were the longest-lived with resumed follow-ups (RunnerCoder 77M,
MLTestCoder 64M, PurchaseCoder2 60M); the three research sourcers together used 47M. The session cannot read the /usage
meter; the user records it.
