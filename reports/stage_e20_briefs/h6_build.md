# Stage E.20 Step 2: h6_rod build record (H6Coder-OpusXHigh)

Built 2026-10-11 (first file 10:52 PDT, record written 11:10 PDT, from file mtimes and `date`).
The brief is reports/stage_e20_briefs/brief_h6_code.md. The rule is reports/stage_e20_prereg_H6.md
as it stood at 10:56 PDT, when the lead filled section 7 and added section 7a. Synthetic data only.
No store, no GEX value and no E.12/E.15/E.17/E.18 result file was opened. No existing file was edited.
Nothing was written to ledger/. Holdout `unlocks_logged` is 0.

Result: `uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py` gave **84 passed** (11:08 PDT,
nice 10). ruff is clean. Coverage of h6_rod is 91%: the real-store loader bodies and the CLI run
only in subprocesses or on real data.

## 1. Items stopped on (the lead decides; the code refuses until then)

**S1 (BLOCKING: registration cannot happen as written).** Prereg section 8's label `E20-H6` and ids
`E20-H6-T1/T2/T3` are refused by the frozen `screening.trial_registry`. Its label regex is
`[A-Z][A-Za-z0-9]{0,15}`, which allows no hyphen. Its ids must be `<label>-<suffix>`, with exactly
one hyphen. The code ships the prereg's values. `preflight.registry_names_valid` makes every entry
point refuse until both the text and `constants.REGISTRY_LABEL` / `TEST_IDS` change.
Options:
- (a) Label `E20H6`, ids `E20H6-T1`, `E20H6-T2`, `E20H6-T3`. This is the E16 pattern and the
  regex accepts it. The tests use it.
- (b) Label `E20`, ids `E20-H6T1`, `E20-H6T2`, `E20-H6T3`. This uses up the label `E20` for the
  stage, so Part C would need another label.
- (c) Change the registry regex. That is a harness change and is not mine to make.

**S2 (SHOULD FIX in the text: the code already follows the engine).** Section 3 says F on a
shortened day is "15 minutes before the early close", and that such trades exit at the flatten.
Section 7a repeats this. The frozen engine's F (rules/sessions.py, Topstep's derived close-by) is
the early close **minus 30 minutes** on every one of the 43 shortened days from 2019-05-06 to
2024-02-29. That is exactly C-30, the entry decision time. So every shortened-day entry is refused
by the engine as `engine_flatten_window`, which section 3 counts as an engine refusal with zero
P&L. The expected count of "flatten on a shortened day" trades is therefore 0, not a reported
group.
- The verdict window has 971 equity trade dates, 33 of them shortened. The overlap window has 277,
  10 of them shortened.
- `test_every_shortened_day_of_the_store_window_has_f_at_c_minus_30` pins this over the whole
  calendar.
- The brief's test "exit at the engine's flatten F" on a shortened day therefore cannot occur. I
  replaced it with two tests: the refused shortened-day entry at early close minus 31, and an F
  exit on a normal day (no bars from 14:58 to 15:07, so the forced flatten fills at 15:09).
- Text options: (a) describe F as the engine's F, note that 2019-2024 shortened days are refused
  at C-30, and drop the "such trades are counted" sentence and the 7a bullet; or (b) change the
  rule. Option (b) is not possible without touching the frozen engine.

**S3 (decision needed: affects at most one verdict date).** The text does not say which bars each
engine run starts from. MNQ is a hard-limit product under D9.7. The engine refuses an entry with no
prior-settlement proxy (`engine_price_limit_reference_unavailable`), and that proxy comes from the
previous trade date's bars streamed through the same run. So the first window date's entry is
refused unless the run also sees the day before it. `constants.ENGINE_LEAD_IN_DATES` ships as None
and every entry point refuses until the lead sets it.
- 0: frames hold the window's dates only. The 2020-06-01 entry, if eligible, is refused.
- 1: frames add the previous trade date (2020-05-29) as a lead-in. It is not a window date and
  has no schedule, so no entry can happen there. It gives the engine its D9.7 reference. The XFA
  account starts that day, but with no trade the MLL is unchanged (rules.xfa_rules has no
  inactivity rule).
- For the overlap window, 1 behaves like 0: the store starts on 2019-05-06, and that date is
  ineligible anyway (missing_prior_bar).
- `test_without_a_lead_in_the_first_date_has_no_d97_reference_and_is_refused` shows both settings.

**Lead-set constants per the brief** (the code refuses while each is None):
- `T3_REGISTERED`. Section 7 now says T3 is registered, so the lead sets True.
- `GEX_CSV_SHA256`. Section 7 and E.14's fetch record give
  51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62.

## 2. Confirm items (implemented as stated; the reviewer should confirm the reading)

- **C1, reason precedence.** When several eligibility conditions fail, the first in the text's
  listed order is recorded: missing_signal_bar, then missing_prior_bar, then instrument_change,
  then zero_signal. This affects the counts only.
- **C2, one engine run per test and window.** Each run has its own account, so T1, T2 and T3 do
  not share an MLL path. The overlap window gets its own runs with fresh accounts.
- **C3, the vehicle's roll blackout.** I used `ml_route_v2.pipeline.own_blackout({"NQ": NQ's L-8
  set}, ("MNQ",))`, which equals NQ's set. In the v2 world, MNQ's own store is never read (E.12
  P-1), and the guard forbids reading it. "Its root's" set therefore contributes nothing.
- **C4, a STOPPED test in Holm.** A STOPPED test enters Holm with p = 1 and m unchanged. This is
  conservative and only arises after an engine invariant error or a loader refusal.
- **C5, when check reads the store.** `check` (before registration) hashes the store and the GEX
  file but reads no bar and no GEX value. The price-free content checks run inside `evaluate`,
  after the registration check and before the marker. They are the frozen loader's
  `read_leg_dates` (bookings, holdout/embargo/out-of-store refusals, roll metadata), a
  duplicate-timestamp check on the ts column, the bar guard, and the GEX parse. Price-level defects
  (off-grid prices, OHLC errors) surface only in the engine after the marker. They make the
  affected test STOPPED and are recorded, never a crash. If the lead wants price checks before the
  marker, check would have to read price columns before the evaluation.

## 3. Prereg clause to function

| Prereg clause | Implemented by |
|---|---|
| s2 store path and sha256; read through the frozen loader with booking checks | `constants.NQ_STORE_REL/SHA256`; `run.load_leg` -> `data.stage_e_bars.load_confirmation_leg(NQ, STEP2_ROOT, 2019-05-06, expected_sha256)`; `run.validate_store` -> `read_leg_dates` before the marker; `run.check` hashes the store |
| s2 NQ price path, MNQ vehicle, prices as read, MNQ ticks and $0.50 | `engine.run_schedule`: NQ frame fed as the `MNQ` leg; `engine.make_rules`: `leg_inputs("MNQ")`; `stats.ticks` via `rules.tick_value("MNQ")` (50 cents) |
| s2 verdict window 2020-06-01..2024-02-29 of the frozen equity calendar | `constants.VERDICT_*`; `clock.trade_dates` (`data.group_session.trade_dates_between` on the equity calendar); `run._windows` |
| s2 T2 warm-up: the 60 trade dates before 2020-06-01; [60th, d); fewer than 60 gives "t2_warmup" | `clock.t2_warmup_first` (2020-03-06); `signal.t2_thresholds`; `signal.t2_schedule` |
| s2 overlap window 2019-05-06..2020-05-29, same rules, T2 from 2019-05-06 | `run._windows["overlap"]`; `run._evaluate_window("overlap")`; `report.window_record(verdict=False)` |
| s2 never read (hist, sealed, holdout, other stores, bars >= 2024-03-01) | `guard.check_store_path`, `guard.install_audit_hook`, `guard.check_bars`, `guard.check_trade_dates` |
| s3 clock: bar named by CT open; decide at close; fill at the next open | `clock.ct_ns`, `clock.signal_bar_ns`, `clock.exit_from_ns`; the frozen engine fills |
| s3 C: 15:00 normal, the early-halt time on a shortened day | `clock.close_ct` (`GroupCalendar.early_halt_ct`; `clock.normal_close_ct` checks the frozen day_session_ct equals 15:00) |
| s3 P(C-30) = close of the bar opening at C-31 | `clock.signal_bar_ns`; `signal.compute_facts` |
| s3 P(prior C) = close of the bar opening at the previous trade date's C-1 | `clock.previous_trade_date`, `clock.prior_bar_ns`; `signal.compute_facts` |
| s3 r_ROD; eligibility and the 4 reason codes | `signal.compute_facts`, `signal.eligibility_reason`, `signal.eligibility_counts` |
| s3 entry: market intent on the C-31 bar, sign(r_ROD), 1 MNQ, fills at the C-30 open | `signal.Entry`; `member.H6Member.on_minute` (that exact bar only, never resent) |
| s3 exit: first present bar at or after C-2, resent while refused; F and D9.7 as backstops | `member.H6Member._exit` (CP1's `exit_if_due` structure); engine `forced_reasons` |
| s3 frozen engine, unchanged (D8 buckets, event window, D9.5a, D9.12, D9.7, 2-min hold, XFA gate, MLL restart, roll blackout) | `engine.make_rules` (`StageERules`, `restart_on_terminal=True`), `engine.run_schedule` (`run_engine`); `engine.vehicle_blackout` (`own_blackout`) |
| s3 every engine refusal of an eligible entry counted; zero P&L | `report.entry_outcomes` (intent refusal reasons, fill-time cancellations); `stats.daily_net_usd` (zeros) |
| s3 T2: median of 60 most recent eligible |r|, strict > | `signal.t2_thresholds` (`np.median`), `signal.t2_schedule` |
| s3 T3: previous trade date's GEX row < 0 strictly; "gex_missing" | `signal.t3_schedule`; `gex.load_gex` (header, ISO dates, rows >= 2024-03-01 cut before parsing) |
| s4 gross, c, net per trade in MNQ ticks; dollars | `stats.trades_from` (flat-to-flat over Fill events; gross = summed `gross_realized_cents`, checked against fill prices in `price_check_ok`), `Trade.cost_cents`, `Trade.net_cents`, `stats.trade_frame` |
| s4 t_B and one-sided p by `gate0._b_test` (g = net, cost = c, trade_date) | `stats.b_test` (calls `ml_route_v2.gate0._b_test` itself) |
| s4 annualized net Sharpe over every window trade date, zeros, ddof 1, sqrt 252 | `stats.daily_net_usd`, `stats.annualized_sharpe` |
| s4 mean gross vs 1.5 x mean c | `stats.core_numbers`, `stats.pass_bar` |
| s5 Holm at 0.025 over the registered tests (m = 2 or 3) | `stats.holm`; `run.verdicts` |
| s5 pass bar: 4 items; floors 100 / 30 (T3); STOPPED with the rule quoted | `stats.pass_bar`; `report.stopped_record`; `engine.run_tests` keeps engine exceptions per test |
| s6 per-year (5 buckets) | `report.per_year` |
| s6 1.5 x slippage stress, commission unchanged | `report.stress` (`report._stressed`) |
| s6 gross and net in bp of the entry fill price | `report.basis_points` |
| s6 exit types (C-2, shortened flatten, D9.7, MLL) | `stats.exit_type`; `report.window_record["exit_types"]` |
| s6 refusal and exclusion counts | `Schedule.reason_counts`, `report.entry_outcomes`, engine counters, `signal.eligibility_counts` |
| s6 MLL breach dates | `report.mll_record` |
| s6 overlap reported separately | result JSON key `overlap`; `results_io.summary_md` |
| s9 guard imported by every H6 process; raises on the planted cases | `h6_rod/__init__.py` imports `guard`; `run.main` installs the audit hook first; tests/test_h6_rod_guard.py |

Run discipline (brief): `run.check`, `run.register`, `run.evaluate`, `preflight.*`, and
`python -m h6_rod check|register|evaluate --freeze-sha256 .. --harness-sha256 ..`. The harness sha
must equal the pinned v12 value (verified: `screening.harness_freeze.preflight` returns it on this
tree).

The freeze manifest has schema `stage_e20_h6_freeze/1` with files `{path, sha256, bytes}`. It must
list every h6_rod/*.py, the prereg, every ml_route_v2 module loaded by H6 (`run._import_dependencies`
loads clock, gate0 and pipeline first, because own_blackout imports ml_route_v2.clock lazily; the
result records any v2 module loaded after the check, expected []), and the GEX CSV when T3 is
registered. `preflight.manifest_body(preflight.required_files(tests))` builds a conforming body.

## 4. Choices (each with its reason)

1. **Schedules are precomputed and handed to the member, as the brief asks.** Each entry for date
   d uses only the bar closing at C-30 of d (the decision bar), the previous date's C bar, the
   |r_ROD| of earlier dates, and the previous date's GEX row. Nothing later is used.
2. **Bars are found by open instant only** (CP1: CT date plus clock). No trade-date cross-check is
   added, because the frozen loader already refuses any row whose label differs from its L-3
   booking.
3. **The bar guard's timestamp bound is 2024-03-01 00:00 UTC**, which is stricter than 00:00 CT.
   Bars of trade date 2024-03-01 that open on 2024-02-29 at 17:00 CT are caught by the trade-date
   check.
4. **The stress test re-prices each fill as `slippage_cents(qty, 1.5 x slippage_ticks, 50)`.** That
   is the frozen function with its ceil to the cent, applied to each fill's own recorded ticks. It
   is not 1.5 times the cents. This is descriptive only.
5. **The per-year fields** are n, means, t_B, p, net dollars, and the Sharpe over that bucket's
   equity trade dates. The text names the buckets but not the fields.
6. **The GEX rows are parsed once, before the marker, and reused**, so nothing about the file can
   fail after the marker. A row dated 2024-03-01 or later is cut once its date field is parsed.
   No other field of it is parsed (the test plants junk there).
7. **After the marker, nothing raises.** A loader refusal or OSError makes every test STOPPED and
   the result is still written. An engine invariant stops only its own test.
8. **The audit hook is installed only by the CLI process.** It cannot be removed, so tests run it
   in subprocesses: one per planted opener, plus a whole synthetic register-and-evaluate run under
   the hook.
9. **`n_obs` passed to `_b_test` is the trade count.** It is recorded only and does not change t
   or p.

## 5. Tests (tests/test_h6_rod_*.py; helper tests/_h6_rod_synth.py; 84 passed)

- signal (20): hand-computed r_ROD on a normal day; the bars read are 14:29 and the prior 14:59,
  and later bars do not matter; shortened-day C, the entry bar at early close minus 31, and the
  next day's prior bar at early close minus 1; each eligibility reason, parametrized, including
  precedence; a date with no bars; T2 at 59 versus 60 eligible dates; T2 strictness and the
  allowed range; W0 = 2020-03-06; the T3 mask, including a missing row and a zero row; GEX rows
  dated 2024-03-01 or later cut before parsing; 5 malformed-CSV cases; GEX sha256 and pin refusals.
- engine (11): entry fill at the 14:30 open and exit fill at the 14:59 open; a missing 14:58 bar
  exits at the 15:00 open; no bars 14:58-15:07 gives the forced flatten at 15:09; short side and
  one trade a day; the shortened-day entry refused (`engine_flatten_window`, S2); F = C-30 on
  every shortened day 2019-2024; roll-blackout refusal counted; no lead-in means no D9.7 reference
  (S3); the vehicle blackout equals NQ's; the round trip costs 122 + 41 + 41 = 204 cents (the D8
  14:30 bucket, 0.81742 ticks a side); an off-grid price stops only that test.
- stats (19): `_b_test` against a hand t and the scipy p; a single trade gives NaN and p = 1; 10
  Holm cases (m = 2 and 3, step-down stop, ties at the bound); Sharpe with zero days, sd 0 and
  n < 2; the pass bar item by item, including NaN and the T3 floor of 30; core numbers; stress
  rounding (62 and 66 cents); bp; exit-type names; per-year buckets.
- guard (19): 9 planted paths refused (hist, sealed, holdout-1 blob, holdout-2 root, the MES
  research and confirmation parquets, another root's step 2 store, another research store, vendor
  raw); class names; a non-store path; the NQ path passes with nothing opened; a symlink into
  sealed refused; audit decisions; the hook in a subprocess refuses all 27 opens (open, os.open,
  io.open_code); the bar guard on trade date and on ts; the guard is imported by the package.
- run (15): refusal while T3_REGISTERED is None; refusal while the lead-in is None; the prereg
  label refused (S1); the shipped CLI refuses in a subprocess; check passes; check refuses a wrong
  freeze sha, a foreign harness and a changed file; a manifest missing an h6 file is refused;
  evaluate before register refuses with no marker; the test registry needs the test mode; register
  once (N 471 -> 474 in the temporary registry), then a second register refuses, then evaluate
  writes the marker and results, then a second evaluate refuses; a loader refusal after the marker
  gives STOPPED and is written; a store-validation problem refuses before the marker; a STOPPED
  test enters Holm with p = 1; the default store functions refuse through the guard before
  opening; the whole synthetic run passes under the audit hook in a subprocess. The real
  ledger/trial_registrations.jsonl sha256 is unchanged before and after.

Engine speed probe on synthetic full sessions: 16 microseconds a bar, so about 80 s for every real
run (3 tests x verdict plus overlap, about 1.7M bars a pass).

## 6. Files

New: h6_rod/__init__.py, __main__.py, constants.py, guard.py, clock.py, signal.py, gex.py,
member.py, engine.py, stats.py, report.py, preflight.py, run.py, results_io.py;
tests/_h6_rod_synth.py, tests/test_h6_rod_signal.py, test_h6_rod_engine.py, test_h6_rod_stats.py,
test_h6_rod_guard.py, test_h6_rod_run.py; this record. No other file was touched.

## 7. Review fixes (reports/stage_e20_review_h6.md; applied 2026-10-11, tests 15:32 PDT)

- **H6R-1 (SHOULD FIX).** In `run.evaluate`, everything after the run-once marker, from
  `_windows(cal)` through `doc.update(verdicts(...))`, now sits in `try/except Exception`.
  - On any exception, `run._stop_all` sets every test's verdict and overlap record to STOPPED,
    with the reason and `traceback.format_exc()`. It records `post_marker_exception` (type,
    message, traceback) and falls through to `_write`, which stays outside the block. So the
    result file exists whenever the marker exists, and section 4 item 7 now holds for every
    exception class.
  - The existing loader-refusal path uses the same `_stop_all`, so it now records its traceback
    too.
  - `main` prints the exception and traceback to stderr. It returns `run.evaluation_exit_code(doc)`,
    which is RC_ERROR (1) when `post_marker_exception` is set and RC_OK otherwise.
  - New test: `test_any_exception_after_the_marker_stops_every_test_and_the_result_is_written`.
    The `releases` hook raises RuntimeError on its second call, the first one after the marker.
    The test asserts that the marker and the result file exist, every test in both blocks is
    STOPPED with the traceback recorded, and the exit code is RC_ERROR.
- **H6R-9 (NOTE).** member.py now has a comment where `trading_windows` is set: the value is
  nominal and unused on this path, because `run_engine` is called directly and only
  screening/stage_e_runner.py's D9 coverage check reads it.
- **H6R-10 (NOTE).** `test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha` also
  asserts "freeze manifest" in the CLI's stderr. The lead's versions of that test and of
  `test_the_ruled_names_are_accepted_and_a_hyphenated_label_refused_stop_item_s1`, and the lead's
  ruled constants (label E20H6, T3_REGISTERED True, ENGINE_LEAD_IN_DATES 1, the GEX sha256), are
  kept unchanged.
- Result: `nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py` gave **85
  passed**.
- ruff flags six E501 long lines (over 100 characters), all in the lead's edits: constants.py
  lines 79, 80, 84 and 88, and tests/test_h6_rod_run.py lines 55 and 56. I left them untouched as
  instructed. Every line I wrote passes ruff.
