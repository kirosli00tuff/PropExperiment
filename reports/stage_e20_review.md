# Stage E.20 review

## H6 verification

**Verdict: VERIFIED WITH NOTES.** VerdictVerifier-FableXHigh, 2026-10-11 15:39 to 15:54 PDT.
Brief: reports/stage_e20_briefs/brief_h6_verify.md. The three H6 test verdicts (T1 FAIL, T2
FAIL, T3 FAIL), the Holm decisions (none rejected at family alpha 0.025, m = 3), the trade
counts, the eligibility, exclusion and refusal counts, the cost bar and the Sharpe bar are
reproduced by an independent bar-level reconstruction written from the frozen prereg and the
frozen inputs without importing h6_rod. T3 and the overlap window reproduce to the last digit.
T1 and T2 differ from the lead by exactly one trade each: the engine's trailing-MLL liquidation
(an engine-only effect the prereg names), which my reconstruction cannot produce; it is
quantified below, checked against the XFA 50K rule from the lead's own trade list, and does not
move any verdict component. No BLOCKING finding.

Artifacts (all mine, written before the lead's result was opened except the third):
- reports/stage_e20_briefs/h6_verify_recompute.py (the reconstruction) and
  reports/stage_e20_briefs/h6_verify_independent.json (written 15:47:51 PDT; per-date rows,
  per-trade rows, per-test statistics, counts).
- reports/stage_e20_briefs/h6_verify_compare.py and h6_verify_trade_diff.json (step 2, the
  per-trade join against reports/stage_e20_H6_result.json, written 15:50 PDT).

### Inputs verified before computing

| input | check | result |
|---|---|---|
| NQ store data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet | sha256 = prereg section 2 (08fae13f...be30aa) | match; 1,701,147 rows; max trade_date 2024-02-29; max CT date of any ts_event 2024-02-29 |
| GEX CSV reports/stage_e14_briefs/gex/DIX.csv | sha256 = prereg section 7 (51bef9ea...9ce62) | match; read columns date and gex only; 3,229 rows dated <= 2024-02-29 used, 650 rows >= 2024-03-01 never read into the map (lead's gex_load: 3,229 kept, 650 cut) |
| D8 cost table (screening.stage_e_frozen) | sha256 f4360bb7... verified by the frozen loader | MNQ: commission 122 cents round trip, 46 buckets, depth terms all 0; the 14:30 bucket (CT 14:30-14:59) s_b = 0.81742 ticks |
| Freeze manifest reports/stage_e20_h6_freeze.json | `h6_freeze_manifest.py verify 22e606f0...` | match True, files 91, bad [] |
| Equity calendar (data/calendars/equity.py, data/group_session.py) | trade dates and early halts | 971 verdict trade dates, 33 shortened (prereg: 971 / 33); 277 overlap dates, 10 shortened; T2 warm-up start 2020-03-06 (lead: t2_lookback_first 2020-03-06) |
| Flatten rule (rules/sessions.py flatten_time_ct) | F per date | 15:08 CT on normal days; early close minus 30 min on the 33 shortened days, so the C-30 entry fill is at F and refused |
| MNQ roll blackout | prereg: the v2 engine stage's set for MNQ, its root's and its price path's | no MNQ store exists for 2019-2024 (E.2a's covers 2025-04-01..2026-06-21), so ml_route_v2.pipeline.own_blackout reduces to the price path's set: the NQ store's 57 roll_blackout_dates (splice date + 2 prior sessions); 45 fall in the verdict window; equals the result's vehicle_roll_blackout_dates (57) |

### Independent numbers beside the lead's (verdict window 2020-06-01..2024-02-29)

Mine = reconstruction with the prereg's C-2 exit on every trade. Lead = reports/stage_e20_H6_result.json.
Every lead figure below was also recomputed from the lead's own per-trade list and agrees to 6 decimals.

| figure | T1 mine | T1 lead | T2 mine | T2 lead | T3 mine | T3 lead |
|---|---|---|---|---|---|---|
| trades | 893 | 893 | 446 | 446 | 134 | 134 |
| dates with a trade | 893 | 893 | 446 | 446 | 134 | 134 |
| mean gross (ticks) | 1.1613 | 1.2475 | -3.7713 | -3.2668 | -3.5224 | -3.5224 |
| mean c (ticks) | 4.0800 | 4.0800 | 4.0800 | 4.0800 | 4.0800 | 4.0800 |
| 1.5 x mean c | 6.12 | 6.12 | 6.12 | 6.12 | 6.12 | 6.12 |
| mean net (ticks) | -2.9187 | -2.8325 | -7.8513 | -7.3468 | -7.6024 | -7.6024 |
| t_B (_b_test; hand recomputation equal) | -0.5434 | -0.5280 | -1.0101 | -0.9476 | -0.3800 | -0.3800 |
| one-sided p | 0.7065 | 0.7012 | 0.8435 | 0.8281 | 0.6477 | 0.6477 |
| Holm rank / bound | 2 / 0.0125 | 2 / 0.0125 | 3 / 0.025 | 3 / 0.025 | 1 / 0.00833 | 1 / 0.00833 |
| Holm rejected | no | no | no | no | no | no |
| annualized net Sharpe (971 dates, zeros) | -0.2768 | -0.2690 | -0.5146 | -0.4828 | -0.1941 | -0.1941 |
| net total (USD) | -1,303.22 | -1,264.72 | -1,750.84 | -1,638.34 | -509.36 | -509.36 |
| cost bar (gross >= 1.5c) | fail | fail | fail | fail | fail | fail |
| min trades (100 / 100 / 30) | pass | pass | pass | pass | pass | pass |
| Sharpe >= 0.5 | fail | fail | fail | fail | fail | fail |
| **verdict** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** |

Counts (mine = lead on every line): verdict window 971 trade dates; eligible 956,
instrument_change 15 (the 15 splice dates), missing_signal_bar 0, missing_prior_bar 0,
zero_signal 0; engine refusals of eligible dates: engine_flatten_window 33, engine_roll_blackout
30 (the 45 blackout dates less the 15 splice dates, which are already ineligible); traded 893.
T2: t2_warmup 1 (2020-06-01: only 59 eligible dates in the warm-up, 2020-03-18 being a splice),
not above median 484, T2 dates 471, of which 25 refused by the engine (lead: 4 flatten + 21
blackout) and 446 traded. T3: gex_missing 27, GEX not negative 785, T3 dates 144, of which 10
refused (lead: 4 + 6) and 134 traded. Warm-up block: 60 trade dates, 59 eligible, 1
instrument_change (lead's t2_warmup block identical). Overlap window (descriptive): 277 dates,
272 eligible, 4 instrument_change, 1 missing_prior_bar (2019-05-06); trades 254 / 104 / 39 and
every statistic equal to the lead's to 6 decimals (T1 t_B 1.1635, mean net 13.3924, Sharpe
1.1097; T2 0.6745, 17.8046, 0.6444; T3 1.1934, 71.8944, 1.1330).

### Per-trade match

Join on trade date, per test and window (h6_verify_trade_diff.json): 893 + 446 + 134 verdict
dates and 254 + 104 + 39 overlap dates match one to one (no date only on one side). Side, entry
fill price, exit fill price, gross ticks, D8 round trip (204 cents = 122 commission + 41 + 41
slippage, 4.08 ticks) and net match to the cent on every trade except two:

| test | date | side | lead exit | my exit (C-2 rule) | gross lead / mine (ticks) | lead exit_type |
|---|---|---|---|---|---|---|
| T1 | 2023-11-30 | sell @ 15883.75 | 15967.00 at 14:53 CT | 15986.25 at 14:59 CT | -333 / -410 | mll_breach_flatten |
| T2 | 2021-10-07 | buy @ 14934.75 | 14927.75 at 14:35 CT | 14871.50 at 14:59 CT | -28 / -253 | mll_breach_flatten |

Replacing those two lead trades by my C-2 trades reproduces my statistics exactly (difference 0
on every figure), so the two liquidations are the whole of the T1 and T2 differences: +77 gross
ticks on T1 (+0.0862 per trade) and +225 on T2 (+0.5045 per trade), both in the lead's favour
and both far from any pass component.

### Findings

- **H6V-1 (NOTE, explained).** The two MLL liquidations are an engine-only effect the prereg
  allows (section 3: "the trailing MLL with restart on a terminal account (a breach does not end
  the sample; breaches are counted and reported)"). Checked against rules/xfa_rules.py XFA_50K
  (mll_cents 200,000, trailing to a lock at 0) from the lead's own trade list: T1 account 0 stood
  at -$339.86 realized with a running peak of +$1,492.98 (floor -$507.02) and the open short's
  -$168.54 took equity to -$508.40, below the floor; T2 account 0 stood at -$1,691.16 with a peak
  of +$293.88 (floor -$1,706.12) and the open long's -$16.04 took it to -$1,707.20. Each
  liquidation filled at the next bar's open after the breach bar, costs unchanged (4.08 ticks),
  the 2-minute hold respected, and a fresh account started on the next trade date (account_index
  1 from 2023-12-01 and 2021-10-13). The bar-by-bar mark-to-market inside the engine was not
  re-run; the realized-balance arithmetic above is the check.
- **H6V-2 (SHOULD FIX, descriptive output only).** The result's `mll.breach_dates` is `[]` for
  T1 and T2 although each had one MLL liquidation (`mll_liquidation_fill_dates`,
  `engine_counters.mll_liquidation` 1, `accounts_started` 2). h6_rod/report.py lines 91-96 fill
  `breach_dates` from DayClose events only, so an intraday liquidation never appears there. The
  prereg's section 6 names "MLL breach dates" as a descriptive output; a reader of `breach_dates`
  alone would conclude no breach occurred. No verdict figure depends on it. The fix is a reading
  note in the progress entry (breach dates = `mll_liquidation_fill_dates`), not a code change to
  a frozen file.
- **H6V-3 (NOTE).** No other engine effect occurred: my reconstruction found every verdict fill
  on its exact bar (0 entry-bar gaps, 0 exit-bar gaps over 893 trades), no fill inside a D8
  event window (the release calendar lists the same 313 instants for MNQ and NQ; none falls in
  14:00-14:59 CT), no D9.5a deferral (lead: filled_after_deferral 0), no D9.7 exit, no locked
  fill, no instrument change inside a trade; the lead's exit_types are 892 + 1 and 445 + 1 and
  134, and price_check_failures 0. Costs are therefore constant at 4.08 ticks on every trade.
- **H6V-4 (NOTE).** Statistic and bar reproduced two ways: `ml_route_v2.gate0._b_test` and a
  hand computation (per-date mean, mean / (sd(ddof 1) / sqrt(n)), Student t with n - 1 df,
  one-sided) agree to machine precision on every test; Holm at 0.025 over m = 3 gives the same
  ranks and bounds as the result's `holm.steps`; the Sharpe denominator is the 971 window dates
  with zeros (confirmed by recomputing the lead's Sharpe from its trades).
- **H6V-5 (NOTE).** Order of events verified from git, mtimes and the files' own fields, all
  2026-10-11 PDT: prereg last written 15:33:45; freeze manifest written 15:35:17 (created_pdt in
  the file; mtime equal); commit 498fd05 "E.20 H6 freeze" at 15:35:53 (105 files, including
  reports/stage_e20_h6_freeze.json, reports/stage_e20_prereg_H6.md, h6_rod/*, tests); registry
  line r004-E20H6 time_local 15:36:20 (ledger mtime 15:36:20), N 480 -> 483, ids E20H6-T1/T2/T3,
  freeze_sha256 22e606f0..., harness ece91ae8...; evaluate started 15:36:34 (h6_evaluate.log), the
  marker written 15:36:38 (written_local; O_EXCL per run.py) recording the same freeze sha and
  the registration entry; result written 15:38:15 recording freeze, registration, harness sha and
  marker path. One marker and one result exist; the log shows one run, exit status 0, 1:40.91
  wall, 942 MB peak RSS. `git diff --stat 498fd05` is empty for h6_rod, the prereg, the freeze
  manifest, ml_route_v2, screening, rules, sim and the calendar modules; no commit follows 498fd05.
  The registry's and marker's harness sha ece91ae8... is the one E.18 C1b's freeze and marker also
  carry.
- **H6V-6 (NOTE).** Guard: the result's `load` and `store_validation` name only the NQ store
  (sha 08fae13f...), 1,701,147 bars, first 2019-05-06, last 2024-02-29; `gex_load` cut 650 rows
  at or after 2024-03-01 (my count equal); h6_rod's only data paths are constants.NQ_STORE_REL and
  GEX_CSV_REL, the loader goes through guard.check_store_path, and the CLI installs the
  sys.addaudithook refusal for data/processed_hist, sealed and holdout stores, data/processed,
  data/processed_step2 (except the NQ file) and data/vendor; guard.check_bars raises on any
  ts_event or trade_date at or after 2024-03-01. tests/test_h6_rod_guard.py: 19 passed. The store
  itself holds no bar after 2024-02-29 (max trade_date and max CT date both 2024-02-29), so no
  such bar could have been read. `v2_modules_loaded_after_the_freeze_check` is empty.

### Not checked

- The engine's bar-by-bar MLL mark-to-market and the restart's account state (H6V-1 checks the
  realized balances and the fill convention only).
- D9.7 price-limit logic and locked-market fills: no such exit occurred, so there was nothing to
  compare.
- The audit hook's behaviour inside the detached evaluate process beyond the log (no refusal
  logged) and the subprocess tests.
- My script labels the 2020-03-06..2020-05-29 warm-up dates under the overlap window in its
  `counts` block (the T2 pool itself is built from all eligible dates and is unaffected); the
  warm-up eligibility count (59 of 60) was taken from the per-date rows directly.

## Search screen verification

Worker ScreenVerifier-FableXHigh (fable, xhigh), brief reports/stage_e20_briefs/brief_screen_verify.md.
Started 2026-10-11 20:16 PDT, finished 20:24 PDT (times from `date` and file mtimes). Status:
COMPLETE; verdict VERIFIED (end of this section). Sections were appended as each check finished.

Inputs read: reports/stage_e20_search.json and .md, reports/stage_e20_search/*.csv and
world_check.json, the run's state directory ~/.cache/propexp_e20_search (stages/*.pkl,
cpcv/cpcv_units.jsonl, ledger.jsonl), ledger/trial_registrations.jsonl, reports/stage_e20_briefs/
search_run.log, reports/stage_e20_plan.md sections 9 and 15, docs/prompts/STAGE_E.20.md F7, and the
code in pattern_search/ and ml_route_v2/cpcv.py, pipeline.py, configs.py. Nothing under
data/processed_hist, data/sealed or data/processed was opened; no store was read.

### 1. Recomputation from the saved nested record (own code; frozen functions beside it)

Source: ~/.cache/propexp_e20_search/cpcv/cpcv_units.jsonl (3,376 lines: 1 meta, 2,700 inner units
= 45 configs x 15 outer splits x 4 folds, 675 outer units = 45 x 15; no duplicates). My script
(scratchpad verify_screen.py, 35 checks, 35 pass) rebuilt the record without pattern_search or
cpcv.nested_cpcv: calendar from world.search_calendar() (exchange group calendars, no store;
1,248 dates 2019-05-06..2024-02-29), 6 blocks of 208, the 15 outer splits as C(6,2) in index
order, 5 paths (block b in path j is tested by the j-th split testing b), the per-split selection
re-derived from the raw inner fields (eligible iff all 4 folds have a finite score and >= 30 trades;
best mean score; tie-break (kind, size, -k, horizon) re-implemented), path_daily and config_daily
assembled from the outer units' `daily` dicts with 0.0 where a date has no entry.

| Quantity | Reported (search.json) | Mine | Match |
|---|---|---|---|
| Path t (5) | -1.33426, -0.78168, -0.86969, -1.40040, -1.57089 | identical to 1e-9 | yes |
| Median-path t | -1.3342551590804386 | -1.3342551590804386 | yes (fails >= 2.0) |
| Path-average daily Sharpe x sqrt(252) | -0.8256431101504558 | -0.8256431101504558 | yes (fails [0.5, 4.0]; no alarm) |
| Daily mean, path average ($) | -5.54539105740291 | -5.54539105740291 | yes |
| PBO, 16 blocks of 78, C(16,8) = 12,870 splits | 0.5958818958818959 | 0.5958818958818959 (7,669 of 12,870 at or below the OOS median) | yes (fails < 0.5) |
| Config Sharpe variance (population, 45 finite) | (not printed; n_finite 45) | 4.970242409339738e-4 | frozen fn equal |
| DSR at N = 528 | 1.3782366749592878e-05 | 1.3782366697523418e-05 (own normal ppf; diff 5e-15) | yes |
| DSR z; E[max SR]; observed daily SR | -4.1927054; 0.0684175; -0.0520315 | -4.1927054; 0.0684175; -0.0520315 | yes |
| Moments of the path average | n 1248, sd 106.578, skew 0.432, kurt 10.877 | same | yes |
| final_selection | ridge_l0.1_k2_h60 | ridge_l0.1_k2_h60 (39 of 45 eligible on all 15 outer splits; best mean outer score -0.0082) | yes |
| selected_per_split (15) | as listed in search.json | identical | yes |
| Verdict | FAIL (items 1, 2, 3 fail; final_selection passes; leakage_alarm false) | FAIL, same item pattern | yes |

Frozen functions on my arrays agree with the report: pipeline.record_figures (median t, Sharpe),
pipeline._daily_t per path, cpcv.pbo_cscv (pbo 0.5958818958818959, not degenerate, 12,870 splits,
block_dates 16 x 78), cpcv.sharpe_variance, cpcv.dsr_at_n (status computed, 1.3782366749592878e-05).

Record integrity: my path_daily equals reports/stage_e20_search/path_daily.csv (max abs diff
1.1e-13) and the cpcv.pkl checkpoint's nested.path_daily (< 1e-9); my config_daily equals
config_daily.csv (2.3e-13) and the checkpoint (45 columns in the frozen CONFIGS order); blocks,
splits' test blocks, paths and selected tuple equal the checkpoint's; the checkpoint pin is
{constants, freeze_sha256 94ee86b02d1c..., world "real"}. path_daily has 1,248 rows whose index
equals the training calendar exactly; zero-valued dates per path: 486, 285, 330, 300, 304 (no-trade
dates and dates without rows carry 0.0 as plan 9 says). configs.csv: all 45 rows re-derived
(CPCV OOS t and annualized Sharpe of each config_daily column, inner and outer eligible-split
counts, outer trades, mean outer score, selected_splits, config_sharpe_population to 1e-16);
registry ids E20S-01..45 in CONFIGS order. The final.pkl checkpoint holds ridge_l0.1_k2_h60, refit
on 57,377 rows, model sha256 2aac86ed6ab4....

Side observation (not a finding): the observed daily Sharpe is negative, so the DSR is ~0 at any N
(0.00020 at N = 45, 0.035 at N = 1); the N = 528 figure carries no information beyond the sign.

### 2. Record integrity: one outer split refit with the frozen code

Script verify_refit.py (scratchpad; 17 checks, 15 pass, the 2 "fails" were my own wrong
expectations, corrected below), nice 10, one ridge fit at a time, 0.7 s wall, 510 MB peak RSS.
Outer split 1 (test blocks 0 and 2, 416 test dates), its selected configuration ridge_l0.1_k2_h60
(also the final configuration), horizon h60. From the panel checkpoint (stages/panel.pkl, pin
freeze 94ee86b02d1c..., world real) and the filter checkpoint (51 admissible pairs, equal to the
JSON's list): frozen horizon_data, calendar_blocks, outer_splits, split_masks, assert_fold,
fit_model, predict, split_risk_fn (the split's own training-row risk table) and
score_fn_for(filt["risk"]) with risk= the split table, exactly as cpcv._fit_and_score does.

| Item | Saved outer unit (cpcv_units.jsonl) | My refit |
|---|---|---|
| n_train, n_test rows | 44,078; 13,159 | 44,078; 13,159 |
| Model sha256 | c80c18ce8890c776... | c80c18ce8890c776... (identical) |
| Daily net $ dict | 263 dates, total -2,011.5525718 | 263 dates, same keys, max abs diff 0.0, same total |
| Score (daily Sharpe), trades, risk_unknown | -0.07495405430102872; 202; 0 | identical |
| Dates all inside the split's test dates | yes | yes |

The three k-siblings of that (model, horizon) in split 1 carry the same model hash, as the shared
fit implies. The final model (final.pkl: ridge_l0.1_k2_h60 on all 57,377 admissible ok h60 rows)
refits to the identical sha256 2aac86ed6ab44fa1.... The record is reproducible from the frozen
code and the saved panel; the saved daily values are what the frozen scorer produces.

Panel checkpoint facts used for section 4: signal_names = the plan's 34 KEPT names (transcribed
from plan 5.1 into my script, same order) + rod_ret + rod_absratio (36; equal to
constants.FEATURE_NAMES); feature_cols = 94 = 36 z_ + 23 app_ + 35 frozen identifier columns
(id_root_* one-hot over the frozen 28-root universe, id_cluster_K1..K7); root column = the 17
vehicles (MNQ, M2K, ZT, ZF, ZN, TN, ZB, UB, 6E, MCL, NG, MGC, ZC, ZS, ZL, HE, LE; no MES); 57,775
rows (= panel.check.rows); trade_date 2019-11-19..2024-02-29; maximum timestamps decision
2024-02-29 20:08 UTC, exit_ts h60/hF 21:08 UTC, h120 21:00 UTC, all before 2024-03-01.

### 3. Plan section 9 and F7

- Bars: constants SCREEN_MEDIAN_T_MIN 2.0, SCREEN_PBO_MAX 0.5, SCREEN_SHARPE_MIN 0.5,
  SCREEN_SHARPE_MAX 4.0, PBO_BLOCKS 16, TRADE_DATES_PER_YEAR 252, N_TOTAL_AT_SCREEN 528 = 483 + 45:
  equal to plan 9 items 1-3 and F7 items 1-3; the DSR's N equals the registry's n_after.
- search.screen applies pass = item1 and pbo.passes and item3 and has_final, with PBO counted as
  not < 0.5 on degenerate, NaN or error (plan 9 item 2, PR-11). The record fails items 1, 2 and 3
  and passes final_selection: FAIL is the plan's verdict. Sharpe -0.826 < 4.0: leakage_alarm
  false, no Fable leakage audit is triggered by the plan.
- Reported-not-gating items present in the JSON `reported` block: dsr (status computed), configs
  (45 rows), final_own (own t -0.327, annual Sharpe -0.147), final_selection_table, oos (per-product
  round trips, 1.5x slippage path table, t4 share -0.0792 = 597.26 / -7543.69, r_ROD share -1.309 =
  1 - (-17419.48 / -7543.69)), ruin "not computed" with plan 9 / PR-6's reason. search.md's figures
  equal the JSON's.
- "A failed screen ends Part C: no freeze, no backward read": reports/stage_e20_B1_RUN_ONCE.json
  and no B1 registration exist in what I read; guard.backward_permitted() returns False; the
  data/processed_hist prefix is forbidden by the audit hook.

### 4. Order of events, feature list, grid order, read paths

Times are PDT from file birth/mtime (`stat`), the registry line and the run log.

| Event | Time | Source |
|---|---|---|
| Search freeze manifest written | 17:42:47.92 | reports/stage_e20_search_freeze.json mtime |
| `check --world` record written (no row, feature or fit) | 17:43:36 | world_check.json written_local; mtime 17:43:38 |
| Registry line r005-E20S, N 483 -> 528, 45 ids | 17:43:59 | ledger/trial_registrations.jsonl time_local; file mtime 17:43:59.82 |
| Run start | 17:44:15 | search_run.log line 1 |
| State directory and panel.pkl born | 17:45:10.64 | stat %w |
| State ledger: 45 configs registered (before the first fit) | 17:45:10.76 | ledger.jsonl entries and mtime |
| cpcv_units.jsonl born (first unit at or after this) | 17:45:10.86 | stat %w |
| cpcv.pkl written (cpcv wall 412.9 s) | 17:52:03 | mtime |
| final.pkl, oos.pkl, result JSON, run end rc 0 | 17:52:05, 17:52:19, 17:52:20 | mtimes; log "end 17:52:20" |

- Freeze: `uv run python -m pattern_search.freeze_manifest verify --sha256 94ee86b0...` -> "verified
  reports/stage_e20_search_freeze.json: 117 files", rc 0 (run by me at ~20:17 PDT). The registry
  line's freeze_sha256 and harness_sha256 equal the JSON's check block; the JSON's registry_entry
  equals the ledger line field for field; the ledger chain is baseline 471 -> C1 473 -> E16 478 ->
  C1b 480 -> E20H6 483 -> E20S 528 (6 lines).
- run.run_search checks the registry (`_registered`) before any stage; the audit hook is installed
  in main() before the parse. The registration precedes the run start by 16 s and the first CPCV
  unit by at least 71 s. Plan 15's order (freeze, check --world, registrations, panel, search,
  screen) is what the timestamps show.
- Feature list: section 2 above (panel.signal_names == plan 5.1's 34 KEPT + rod_ret, rod_absratio).
- Grid order: ml_route_v2.configs.CONFIGS (45, ridge_l0.01_k1.5_h60 first, lgbm_d3_k3_hF last) ==
  the state ledger order == config_daily.csv columns == configs.csv rows, whose registry ids are
  E20S-01..E20S-45 in that order; the registry's 45 test_ids are E20S-01..45.
- Read paths: guard.search_store_paths() lists exactly 17 files under data/processed_step2;
  forbidden prefixes are data/processed_hist, data/sealed (+ the MES holdout files), data/processed,
  and the rest of data/processed_step2, data/vendor/databento, data/raw. world.load_search_root
  calls guard.check_store_path then guard.check_bars; panel.build_search_panel and run.world_check
  call guard.check_frames. Outside guard.py no pattern_search module names processed_hist, sealed
  or data/processed (grep). search_run.log has no "refused" line and exit status 0. The 17 store
  sha256 values agree across the JSON check block, world_check.json and
  reports/stage_e17_run_manifest.json (step2), every root's last_trade_date is 2024-02-29, s_x values
  equal the recorded ones. The panel's maximum timestamps are on 2024-02-29 (section 2).

### Findings

- SV-1 (NOTE): 179 of the 1,248 calendar dates have no panel row (141 are the dates before the
  first row, 2019-11-19; ZF rows start 2021-04-19 and ZT 2022-04-19, about 6.5 months after their
  S_X), and path_daily is 0.0 on all of them, as plan 9 specifies ("zeros ... on dates without
  rows"). Of the 1,069 dates with rows, 38 are zero on all 5 paths; per-path zero counts on dates
  with rows are 307, 106, 151, 121, 125. The screen statistics therefore include 179 structural
  zeros (14% of the dates), which shrink |t| and |Sharpe| toward zero. With every path mean
  negative this cannot turn the fail into a pass; it is recorded so the magnitude of t and Sharpe
  is read with that dilution in mind. The panel record's rows_warmup_dropped = 0 counts only the
  r_ROD warm-up; the late start comes from the frozen pipeline's missing-value rule (rows dropped
  for missing data: 15,167), which is outside this brief.
- SV-2 (NOTE): the DSR at N = 528 (1.4e-5) is uninformative beyond its sign: the observed daily
  Sharpe is negative, so the DSR is near 0 at N = 45 (2.0e-4) and even at N = 1 (0.035). Reported
  as plan 9 asks; no action.
- SV-3 (NOTE): cpcv_units.jsonl carries no per-unit timestamps; "the first CPCV unit's time" is
  bounded below by the file's birth time (17:45:10.86 PDT), 71 s after the registration. Sufficient
  for the order of events.
- No BLOCKING or SHOULD FIX finding.

### Verdict: VERIFIED

Every number in the SCREEN FAIL verdict recomputes from the saved nested record with independent
code (median-path t -1.3342551590804386, PBO 0.5958818958818959, annualized net Sharpe
-0.8256431101504558, DSR at 528 = 1.38e-5, final configuration ridge_l0.1_k2_h60), the frozen
functions give the same values on my arrays, the saved record reproduces from the frozen fit and
scorer on one outer split and the final refit (identical hashes and daily values), the screen's bars
and composition are plan 9 / F7's, and the registration precedes the run and the first fit.

### Not checked

- Only one outer split (split 1) and the final refit were reproduced; the other 674 outer and 2,700
  inner units are taken from the record (their assembly into the statistics is fully recomputed).
- The frozen scorer's internals (score_split, accept_trades, fixed_d_daily_pnl), the c/sigma
  filter and the panel's feature values: I reproduced their outputs from the saved panel, not their
  correctness. The panel itself was not rebuilt from the stores (no store was opened).
- The oos block's own numbers (round trips per product, 1.5x slippage paths, t4 and r_ROD shares):
  read and cross-checked between search.md and search.json only; not recomputed (reported, not
  gating).
- The cause of the 2019-11-19 first panel row (SV-1) was not traced into the frozen feature code.
- Times are file timestamps and logged strings; the lead's STATE file was not consulted.

Finished 2026-10-11 20:24 PDT (`date`).
