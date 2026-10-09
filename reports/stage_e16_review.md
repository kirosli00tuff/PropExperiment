# Stage E.16 freeze review (Task 4): FreezeReviewer-FableXHigh

Reviewer: Fable 5.1 at xhigh, independent of the Opus authors. Written 2026-10-09 01:44 PDT (time from `date`).
Reviewed: the candidate manifest reports/stage_e16_freeze.json (sha256
2b60b9159e94f9b08080d4216592af65b032ebfef618502f0d313a2e671192a3, 70 files), every file it lists that is code or a
rule (base_rules/*.py, tests/test_base_rules_*.py, tests/_base_rules_fixtures.py, the six pre-registration files,
lead_spec.md, rulings.md, settlement .json/.md, windows.json, calendars.md, the two Task 3b calendars' formats,
power .json/.md, overlap.md section 7), the hand-off, release_touch.md, runtime_probe.md, and for comparison
screening/stage_e_engine.py, screening/stage_e_rules.py, screening/stage_e_frozen.py, data/stage_e_bars.py,
data/hist_bars.py, data/hist_store.py, data/pull_hist.py, data/step2_store.py, screening/trial_registry.py,
rules/price_limits.py and C1's freeze section 11. No market data was read, no vendor called, no file edited but this
one. `uv run pytest -q -p no:cacheprovider tests/test_base_rules_*.py`: 65 passed in 4.97 s (synthetic only).
User rulings U1, U2, U3a, U3b are treated as binding and were checked for faithful application, not graded.

## Verdict

**APPROVE WITH FIXES.** One BLOCKING finding (the frozen store loader cannot read the stores E.17's hand-off tells it
to build), eight SHOULD FIX, seven NOTE. The hypotheses, windows, pass bar, costs and clock are fixed and faithful
to the prompt and to U1-U3b; the signals are causal under the engine's clock; the loader's refusals cover holdout-2,
the embargo, MES, the research store and every trade date after 2024-02-29; the splice and fallback rules are
decidable before any bar. The problems are in the seams between the freeze and E.17 (plan name, registration
binding, run-time knobs, manifest coverage) and in two places where the simulator admits what the engine would not
(entries at a closure, fills on limit-locked bars) or where H3's causality guard is weaker than its entry date.

Counts: BLOCKING 1 (F-01); SHOULD FIX 8 (F-02 to F-09); NOTE 7 (F-10 to F-16).

## What was checked and found sound (so the lead need not re-verify it)

- Clock: every signal closes before its fill bar opens. H1 uses close(S-31) and close(d-1, S-1); H4 uses d-1's
  H1 entry open and exit price; H2 uses close(S-1) of both legs at a decision minute at or after both settlements;
  H5's sigma uses the 60 grid dates strictly before d; risk sigma uses only units whose EXIT date precedes the
  unit's ENTRY date (scaling.py:42-58). The causality tests perturb every bar at or after the entry or decision
  instant with fresh random prices and assert the decision is unchanged (test_base_rules_runners.py:65-98, 148-159,
  210-216): real perturbations of the future, not of unrelated data.
- Costs: base = commission_side_cents + slippage_cents(1, side_slippage_ticks(bar open, side, event), tick value),
  byte-for-byte the engine's `_market_cost` at qty 1 (costs.py:78-88 vs stage_e_rules.py:337-345); stress adds one
  vehicle tick per side per fill; 1.5 x multiplies the slippage ticks before the ceil. The engine-match test runs the
  frozen engine (`run_engine` with `StageERules`) and asserts fill instants, prices, event flags, commission +
  slippage per fill, gross and net (test_base_rules_sim.py:124-153), on ZN, on NQ with MNQ's costs, and in an event
  window.
- U3a is applied as ruled (base case no extra tick; stress reported; must-survive stated for holdout-2); U3b (H2
  years with 6 units) is in constants.py:60 and stats.py; U2 windows re-derived here from the quote record agree
  with windows.json for all 27 products (24 at 2010-07-01, RTY 2017-06-01, TN 2016-01-01, HE 2017-07-01); U1's order
  is the hand-off's (C1 under v11 caps-only, C1 evaluated, then v12 with the plan, registration before purchase,
  fallback list written at registration).
- Pass bar: Holm 0.05 across the five on the base case, one-sided, n >= 30, year stability 2/3 of years with 10
  (H2 6) units, fewer than 3 qualifying years fails, p = the larger of the Student-t and Newey-West p (lags fixed
  per test): every item tightens or restates the prompt (stats.py:45-127).
- Windows and refusals: the step-2 store is refused by name unless 2019-05-06..2024-02-29 (store.py:59-83), every
  row is booked by the frozen `check_bookings` (holdout-1, holdout-2, the March 2024 embargo) and `check_hist_bookings`
  (unsourced and out-of-window rows), any trade date after 2024-02-29 refuses the file (store.py:228-230), a date in
  both stores refuses the product (store.py:283-287), MES, sealed and PROCESSED_ROOT paths are refused. The frozen
  2019-on calendars cover 2019-05-01..05-03 as trade dates, so `previous(2019-05-06)` is 2019-05-03 (verified) and
  2019-05-06 gets "no reference (missing bar)", as section 4 of the common file says. H3 units with t+5 after
  2024-02-29 are "window end".
- Settlement grades: the JSON's lead_grade fields equal the common file's table for all 27 products; R-S1 to R-S4
  are defensible on the sources listed (equity 15:15 to 2020-10-23 rests on three CME filings; grains 14:00 in
  2012-06-25..2013-04-07 on S22/S24; LE/HE 2010-2014 weak and excluded; RTY/TN before listing excluded). The
  livestock day opens (08:00, first trade date of the ISO week 09:05, 2014-10-27..2016-02-28) are in the table and
  applied by `open_minute` (common.py:53-61).
- Power: the method (i.i.d. normal per unit at SR_annual / sqrt(units per full year), the same p rule, all four bars,
  thresholds 0.01 and 0.05 bracketing Holm, analytic noncentral-t beside it, seed fixed) is sound for a planning
  table, stated for both windows, and rerun on the real inputs (provisional false). H2's 60 full-window units are
  explained by the 20-unit warm-up (literal reading of the prompt's rule), the 26 "no entry bar" months before
  2012-11-19 and the estimated ZN roll blackouts.
- Run discipline: every input check precedes the O_EXCL marker; after it no data condition raises (run.py:77-123,
  tests in test_base_rules_run.py and test_base_rules_rulings.py).

## Findings

### F-01 (BLOCKING) The frozen loader refuses every store E.17 is told to build for the 21 roots

- Where: base_rules/store.py:59-64 (`expected_name` hard-codes `..._2010-06-07_2019-04-30_ext2010.parquet`),
  store.py:80-83 (`refuse_path` requires that exact name), store.py:218-222 and 260-264 (`read_era` and `preflight`
  require parquet metadata `plan == "ext2010"`), store.py:225 (`check_hist_bookings(root, EXT2010, ...)`), against
  reports/stage_e16_handoff.md step 8 ("a new hist plan (suggested name "ext2010h")", "build plan "ext2010h" stores
  for the 21 roots") and data/hist_store.py:96-99 and 236 (the file is named `..._<plan>.parquet` under `<plan>/<ROOT>/`
  and the metadata records `"plan": plan.name`).
- What is wrong: C1's frozen plan "ext2010" holds six roots and 107 chunks, pinned by an assertion in
  data/pull_hist.py:148 and by C1's freeze section 11, so the 21 roots must be bought under a different plan name.
  Every store of that plan fails `refuse_path` (name) and the metadata plan check, before and after the marker. The
  only ways out in E.17 are to edit base_rules/store.py after the freeze (which breaks the freeze and forces a
  re-freeze under time pressure) or to misname the plan.
- Why it matters: the freeze's purpose is that no code changes between the freeze and the data; a guaranteed
  post-freeze edit to the loader, the one module that touches the stores, defeats it.
- Fix (before the commit): let the run manifest's `ext2010` entry carry the plan name
  (`{"path", "sha256", "plan"}`); `expected_name(root, era, plan)` builds `ohlcv-1m_{root}_v_0_{first}_{last}_{plan}
  .parquet` with first/last taken from `data.pull_hist.get_plan(plan)` and asserted equal to 2010-06-07..2019-04-30;
  `read_era`/`preflight` compare the metadata plan with the manifest's plan; `check_hist_bookings(root, plan, ...)`
  gets that plan. Add a store test with a second plan name. Update README's manifest schema and hand-off steps 8 and
  12 to name the plan per root. Keep the C1 roots on plan "ext2010". (Also fold F-05's label fix into step 8.)

### F-02 (SHOULD FIX) The runner never ties the registration to this freeze's sha256

- Where: base_rules/guards.py:94-95 and 98-106: `check_freeze` returns `registration_freeze_sha256:
  body.get("registration_freeze_sha256")`, which the lead's manifest does not contain (and cannot contain its own
  hash), so `check_registered` calls `require_registered(..., freeze_sha256=None)` and
  screening/trial_registry.py:158 skips the comparison. The CLI already holds the true value in `a.freeze_sha256`
  (run.py:80-82).
- Why it matters: a registration of label E16 made against any freeze file passes; the README's "the registration
  under label E16" check is weaker than lead_spec section 6 ("checks the test is registered ... against this
  stage's freeze manifest"). test_base_rules_run.py:108-116 tests the label, never the sha.
- Fix: `check_registered(test, freeze, registry, freeze_sha256=a.freeze_sha256)` passing it through to
  `require_registered`; drop the unused manifest key; add the test (register E16 under another sha, expect Refused).

### F-03 (SHOULD FIX) Two run-time knobs leave decisions to E.17's discretion

- Where: base_rules/run.py:175 (`verdict --tests`, default all five, any subset accepted; the README line 4 and the
  hand-off step 13 both say the family is the five) and run.py:170, 177 (`--registry`, any path; the marker and
  result record `registration: entry_id` only, run.py:103-106).
- Why it matters: `--tests` changes Holm's m after registration; `--registry` lets a run pass the registration check
  against a file other than ledger/trial_registrations.jsonl, and nothing in the outputs shows which registry was
  used. Item 1 of the brief (nothing left to the runner's discretion) is not met for these two.
- Fix: `verdict` refuses any `--tests` other than the registered five (keep the option only for a test fixture, or
  remove it: Task 2 dropped nothing); `run` and `verdict` write the registry path and its sha256 into the marker,
  the result header and verdict.json, and refuse a `--registry` outside the repository's ledger/ unless
  `--input-paths` (the test mode) is given.

### F-04 (SHOULD FIX) H3's causality guard is weaker than its entry date: 49 of 420 auctions were announced after t-3

- Where: lead_spec.md section 4 H3 and prereg_H3.md section 2 ("announcemt_date strictly before auction_date"),
  base_rules/inputs.py:216-229 (`e0_filter`, which only runs where the fields exist; the hist rows carry none, so
  the filter was applied once in reports/stage_e16_calendars/scripts/build_ec_auc.py), base_rules/h3.py:47
  (short entry at t-3).
- What is wrong: from the saved FiscalData CSV (metadata only, reports/stage_e16_briefs/pages/fiscaldata/
  auctions_query_notes_bonds_20100101_20190630.csv) and the frozen rates calendar: of the 420 2/5/10/30-year
  nominal auctions on rates trade dates 2010-06-07..2019-04-30, 49 (11.7%) have announcemt_date AFTER t-3 (47 of
  them 2-year notes in holiday-shifted weeks, e.g. 2010-09-27 announced 09-23 with t-3 = 09-22) and 111 have it ON
  t-3 (announcement 11:00 ET, entry 15:00 ET, causal). The short leg of those 49 is entered before the offering
  was formally announced. The frozen 2019-05..2024-02 rows carry no announcement date at all, so the same share is
  unknown there.
- Why it matters: the prompt fixes "announcement strictly before the auction" and the freeze may only tighten; as
  frozen, 11.7% of the sample trades on information (the auction's existence and date) whose public source at t-3
  is Treasury's tentative quarterly schedule, which the pre-registration never cites. Either basis is defensible;
  the freeze must say which.
- Fix (lead's choice, written into prereg_H3 section 3 and the common file section 4 either way): (a) tighten to
  "announcemt_date on or before t-3" (counted "announced after entry"), adding the field to the hist EC-AUC rows from
  the saved CSV and fetching FiscalData's metadata for 2019-05..2024-02 (public API, terms allow, no cost) for the
  frozen rows, with the loader applying the rule wherever the field exists; or (b) cite the tentative schedule as
  the public source of the date at t-3 and report the count of units announced after t-3 beside the result.

### F-05 (SHOULD FIX) Hand-off step 8 contradicts R-B4 and the placeholders must be filled from the final manifest

- Where: reports/stage_e16_handoff.md step 8 ("test label "H", test ids H1..H5") against rulings.md R-B4 and
  constants.py:21-22 (label E16, ids E16-H1..E16-H5); data/pull_hist.py:31 (the buy requires the plan's test to be
  registered). Also the `{{FREEZE_SHA}}`/`{{FREEZE_COMMIT}}` placeholders (steps 3, 13) and rulings.md:99-101 ("Lead
  rulings on the freeze review (pending)").
- Why it matters: with the plan's test set to "H", the purchase gate would look for a registration that cannot
  exist (a second registration would double-count N or fail the id check), or E.17 would improvise. And since
  rulings.md is a hashed file, writing the review rulings changes the manifest's sha256; every fix in this review
  does too.
- Fix: step 8 names the plan's test "E16" and ids E16-H1..E16-H5; the lead regenerates the manifest as the last
  act before the commit (after rulings.md, the code fixes and the prereg edits) and fills the placeholders from
  that final sha256 and the commit.

### F-06 (SHOULD FIX) The manifest does not pin the engine, the cost table or the booking code the runner imports

- Where: reports/stage_e16_briefs/freeze_manifest.py:24-50 (FROZEN_GLOBS and PINS). The runner imports and relies
  on screening/stage_e_frozen.py (D8 table reports/stage_e2a_costs.json, pinned inside that module),
  screening/stage_e_rules.py (ReleaseCalendar, event window, guard), screening/stage_e_engine.py (the clock the
  match test is against), data/stage_e_bars.py, data/hist_bars.py, data/group_session.py, data/session.py,
  data/hist_calendar.py, rules/products.py, screening/stage_e_verdict.py, screening/trial_registry.py. None is in the
  manifest; the only pin is the v10 harness manifest's sha256, which guards.check_freeze never verifies and which
  E.17's v11 and v12 supersede by design. Also: the glob `data/calendars/hist2010/*.json` will match the livestock
  copy v12 adds (hand-off step 8), so `freeze_manifest.py verify` fails spuriously after that step; and
  data/calendars/crypto.py is hashed though no test uses it.
- Why it matters: at run time under v12 nothing in base_rules refuses a changed cost table, release-window rule,
  booking check or registry module; the hand-off relies on Fable's review of the v11/v12 diffs alone.
- Fix: add the imported modules above (all but data/hist_calendar.py and data/config.py, which v12 changes by
  ruling R-C6 and U1) and reports/stage_e2a_costs.json, reports/stage_e2a_vehicle_sizes.json and the other tables
  stage_e_frozen.py names to FROZEN_GLOBS; enumerate the six hist2010 calendar files instead of the glob (or
  exclude livestock.json); drop crypto.py; regenerate.

### F-07 (SHOULD FIX) The simulator admits fills the engine refuses: limit-locked bars and the no-new-positions window

- Where: base_rules/sim.py:89-99 (`_fill` admits every fill with a usable bar) and store.py:51 (COLUMNS: no high,
  low, in_no_new_positions_window), against screening/stage_e_rules.py:361-381 (`_locked`: a strategy fill on a
  HARD_LIMIT_PRODUCTS leg is refused while the bar's high/low show the market locked at the limit band from the
  prior settlement; rules/price_limits.py LIMITS from 2019-05-01) and stage_e_rules.py:409, 497 (an opening order
  in a bar flagged in_no_new_positions_window is refused).
- Why it matters: the prompt's guardrail is "the same fill rule". A fill at a limit-locked price is not attainable,
  and for H1 (momentum into settlement on grains and livestock) locked days favour the signal's direction, so the
  omission is generous in the direction of a pass. The no-new-positions flag bears on H1's equity entries under the
  Topstep venue. Neither is counted today.
- Fix (lead's choice): read `high`, `low` and `in_no_new_positions_window` (memory headroom exists: 1.2 GB peak for
  6 columns), apply the engine's `_locked` test with `rules.price_limits.limit_band` where a LIMITS period exists
  (2019-05-01 on) and exclude the unit, counted "limit locked"; count entries in the no-new-positions window
  ("no new positions") and exclude them for the Topstep-venue reading of H1/H4; for 2010-2019, where no limit table
  exists, report the count of fill bars with high == low as a diagnostic. Or rule it a stated limitation in the
  common file section 6 with the counts still reported.

### F-08 (SHOULD FIX) No engine-match test covers the R-B1 close fill that now governs ten years of equity exits

- Where: tests/test_base_rules_sim.py:124-192 (every engine match is an open-to-open trade inside an open
  session); tests/test_base_rules_rulings.py:71-115 (R-B1 is tested against the simulator's own output only).
  The engine's behaviour to match is `close_on_closure_bar` and `_fill_prior_close` (stage_e_engine.py:443-471):
  a reducing order pending at a closure print fills at the close of the last tradable bar with `close_cost` looked
  up at that bar.
- Why it matters: R-B1 (a) decides H1's exit for every equity date before 2020-10-26 and every grains date before
  2015-07-06, H4's reference on the next date, and H2's exits and marks; the brief's item 3 asks that the single-day
  match be real; for this path it is asserted, not run.
- Fix: one more `_engine_vs_sim` case with a frame whose 15:15 bar is flagged `in_scheduled_closure` (and
  `skip_closure_bars` on), entry 14:45, exit ordered at 15:15; assert the engine's `closure_gap` fill equals the
  simulator's close point (instant, price, costs, event flag).

### F-09 (SHOULD FIX) R-B1 (b) lets the simulator open a position where the engine cancels the order

- Where: base_rules/common.py:100-110 (`entry_point` at a closure: the open of the first bar after it);
  base_rules/h2.py:99 and h3.py:72-76; against stage_e_engine.py:452-458 (at a closure print, an opening order is
  cancelled, "closure_bar_no_fill"; only reducing orders fill at the prior close).
- Why it matters: the fill price (the reopening bar's open, after the 15:15 decision) involves no look-ahead and
  the ruling is on record with its reason (H2 otherwise keeps 5 units), but it is a departure from "the same fill
  rule" that the pre-registration does not name as one; it affects every H2 NQ entry 2012-11-19..2020-10-23.
- Fix: state the departure in the common file section 6 (R-B1 b) and in prereg_H2 section 3, and add a counter
  "entry after closure" to the H2/H3 exclusion tables (the per-unit flag `entry_after_closure` already exists in
  h2.py:159). If the lead prefers the engine's rule, those months become "no entry bar".

### F-10 (NOTE) Files the pre-registration cites are not hashed

- reports/stage_e16_briefs/release_touch.md (cited in the common file section 6 for "FOMC is the only type that
  touches"), reports/stage_e16_briefs/derive_windows.py (cited in section 3 as the script behind windows.json),
  reports/stage_e16_briefs/freeze_manifest.py (E.17 runs it to verify; it carries C1's pin), and the hand-off
  (cited for the run order; it still holds placeholders, see F-05). Suggest adding the first three to
  FROZEN_GLOBS; the hand-off stays outside by design.

### F-11 (NOTE) The release-touch method looks only at 2019-2024 fill minutes

- base_rules/touch.py:45-88 and lead_spec section 1: the types that "touch" are found on the 2019-05..2024-02
  calendar with that era's S_p and O_p. Minutes that exist only in 2010-2019 (equity 14:45 entries, grains 09:31
  entries, livestock 08:01 and 09:06 entries, HG 11:30 under the 2011-2012 FOMC times) are not examined. Checked
  here against every type's product list in the frozen calendar: no type without 2010-2019 rows concerns a product
  at such a minute (ISM_SERVICES is equity and rates only; G17 metals; CPI metals, NQ and MBT; NFP FX; CROP, WASDE,
  CROP_PROGRESS grains and livestock at 11:00 or 15:00; API_WSB, NGS, WPSR energy), and E.14's FOMC rows carry the
  real 2010-2013 instants (13:15, 11:20-11:35, 13:00), so the conclusion holds. Record the check in the common file
  so E.17 does not have to repeat it.

### F-12 (NOTE) E.0's auction filter cannot be re-checked at run time

- The hist EC-AUC rows (reports/stage_e16_calendars/ec_auc_2010_2019.json) carry id, date, instant and products
  only; `original_security_term`, `security_type`, `floating_rate`, `inflation_index_security` and
  `announcemt_date` are absent, so inputs.e0_filter is a no-op on them and the tenor comes from the id suffix. The
  filter lives in the hashed build script and the saved CSV. Acceptable; F-04's fix (a) would add the fields.

### F-13 (NOTE) R-B2 trades a bucket the engine cannot price

- costs.py:77-83: a fill at 08:01 CT on LE (2014-12-15..2016-02-26, days other than the week's first) has no D8
  bucket; the engine raises CostLookupError and never fills; the simulator charges the product's largest per-side
  slippage. Not generous in cost, but it admits about 200 H4 units in a session segment D8 never measured. The
  ruling is on record and the count is reported ("uncalibrated bucket"); the H4 result should also show the
  statistic without those units, as a descriptive table.

### F-14 (NOTE) R-S6: the prompt's "both inside Topstep's 15:08 CT flatten" does not hold for equity before 2020-10-26

- H1's equity window is 14:45-15:15 for 2010-06-07..2020-10-23 (about 2,600 product-dates on NQ, YM and RTY), past
  the flatten on the Topstep venue; the lead follows S_p as it was and reports the count ("after 15:08",
  intraday.py:117). Defensible (the hypothesis is the settlement window; IBKR can trade it). Suggest the H1 result
  also reports the pooled statistic with those product-dates removed, marked descriptive, so the Topstep reading is
  visible without a second run.

### F-15 (NOTE) H2's warm-up of 20 monthly units removes about three years

- constants.py:54 applies the prompt's "first 20 eligible dates ... are warm-up" per leg to H2's monthly units, so
  no H2 unit is traded before 2016 and the full window holds about 60 units (power.md). A literal reading, not a
  loosening; recorded so the lead knows the power cost is the prompt's rule, not a defect.

### F-16 (NOTE) O_p for grains 2012-05-21..2013-04-05 is the floor open inside a continuous Globex session

- data/calendars/hist2010/grains.json: one 17:00-14:00 segment in that era with day_session (09:30, 14:00); the
  settlement table carries O_p 09:30 to 2013-04-07. H4 enters at 09:31, which is the pit open plus one in a session
  that had been trading since 17:00. Fixed by the frozen calendar and not a free parameter; worth one sentence in
  the common file section 5 so a reader does not take 09:30 for an electronic open.

## Items of the brief, in order

1. No free parameter: met except F-03 (two CLI knobs) and F-04 (which public source makes the auction known at t-3).
2. No look-ahead: met for H1, H2, H4, H5 and the risk scaling (code and tests); H3 see F-04.
3. Simulator never more generous: costs and the open-to-open fill rule match the engine (tested); exceptions F-07,
   F-09, F-13; F-08 for the untested close-fill path.
4. Windows and refusals: met.
5. Splice and fallback decidable before any bar: met; F-01 blocks the splice from being read at all for 21 roots.
6. Pass bars as amended by U3a/U3b: met.
7. Settlement grades and calendar rulings: defensible and applied by the code; F-16 is a wording note.
8. Power table: sound and stated for both windows; F-15.
9. Hand-off order: respects C1 section 11 and U1; F-05 (label), F-01 (plan name), placeholders.
10. Manifest coverage: F-06, F-10; nothing in it is market data (checked every path).

Not finished or not verifiable here: the E.17 stores do not exist, so the loader's plan check (F-01) is shown from
the code and the hand-off text, not from a file; the announcement-date share for 2019-05..2024-02 (F-04) cannot be
computed from the frozen rows.

## Recheck (2026-10-09)

Written 02:08 PDT (time from `date`) by FreezeReviewer-FableXHigh on the main tree after the 02:04 re-merge, against
the lead's rulings in reports/stage_e16_rulings.md "Lead rulings on the freeze review" and the candidate manifest
reports/stage_e16_freeze.json (97 files, sha256 5603a8d324d6ce9ae6b6900d7e0934a56776b4df48c5ea7f7150653d85e83180).
Checks run: `uv run pytest -q -p no:cacheprovider tests/test_base_rules_*.py` (75 passed in 5.67 s, synthetic only);
`freeze_manifest.py verify --expected 5603a8d3...` ("E.16 freeze OK: 97 files"). No market data read, no vendor
called, no file edited but this one.

**Verdict: APPROVE.** Every BLOCKING and SHOULD FIX finding is fixed or ruled with a reason; the fixes introduce no
free parameter, no look-ahead, no refusal on E.17's normal path, and no hashed file that v12 must change. Three
residual notes (R-1 to R-3) need no code change.

| Finding | Status | Where verified |
|---|---|---|
| F-01 | FIXED | base_rules/hist_plan.py:62-105 (fixed plan per root from constants.py:50-52, name pattern with last 2019-04-30 and first in 2010-06-06..the window start, directories `<plan>/<ROOT>/`, plan window from an injectable resolver, metadata plan and trade_date_range), store.py:68-88, 109-128, 221-238; `refuse_path` accepts the real layouts (data/processed_hist/ext2010/NG/..., data/processed_hist/ext2010h/RTY/..., data/processed_step2/NG/...; checked by calling it) and the frozen data/hist_store.py:400 writes `trade_date_range`, so C1's stores pass `check_plan`; hand-off step 8 names plan "ext2010h" and its layout; tests test_base_rules_store.py (second plan name, wrong plan refused, metadata/name agreement) |
| F-02 | FIXED | guards.py:98-108 (`require_registered(..., freeze_sha256=...)`), run.py:84; test_base_rules_run.py `test_an_e16_registration_under_another_freeze_sha256_is_refused` |
| F-03 | FIXED | run.py:138 (verdict over K.TESTS, no `--tests`), guards.py:111-121 (`check_registry_path`: the ledger unless test mode), run.py:83, 107-109, 136, 149-150 (registry path and sha256 in the marker, result header and verdict.json); test `test_a_registry_other_than_the_ledger_needs_the_test_mode` |
| F-04 | FIXED (option a, a tightening) | base_rules/auctions.py (E.0 filter where the fields exist, announcement date per row), h3.py:63-68 ("no announcement date", "announced after entry" when announcemt_date > t-3); fields added to ec_auc_2010_2019.json (684 rows, all 18 keys); ec_auc_announcements_2019_2024.json (231 rows = every frozen 2/5/10/30 row 2019-05-01..2024-02-29, no unmatched or ambiguous id; FiscalData metadata only, endpoint, query, saved page, sha256 and fetch time 2026-10-09T08:49:19Z recorded; built by the hashed scripts/build_ec_auc_announcements.py); f04_t3_counts.json (49 + 46 = 95 after t-3, matching my count for 2010-2019); lead_spec.md:146-148, prereg_common.md:81-87, prereg_H3.md section 3; power rerun (H3 full 354 units, fallback 69, exclusions "announced after entry: 95") |
| F-05 | FIXED | hand-off step 8 (label E16, ids E16-H1..E16-H5, plan "ext2010h"); the three placeholders remain by design until the manifest is written last and the commit exists (ruling) |
| F-06 | FIXED | freeze_manifest.py FROZEN_GLOBS: the twelve imported modules, the four stage_e2a tables, the six hist2010 calendars by name, the seven group calendars (crypto dropped); data/hist_calendar.py, pull_hist.py, hist_store.py, config.py left out on purpose, with hand-off step 8's stop rule if v12 must touch a hashed file |
| F-07 | FIXED | base_rules/limits.py (the engine's `_locked` on every fill: settlement proxy from the prior trade date's bars, `limit_band`, buy locked at low >= up, sell at high <= down; inactive before the table, 2019-05-01, and for non-hard-limit products), sim.py:93-99 ("limit locked"), store.py:56-57 (high, low, volume, no-new-positions read), intraday.py:142-153 ("no new positions (Topstep)" counted, descriptive table), common.py:115-130 (2010-2019 high == low diagnostic); test_base_rules_review.py:57-105; applied in H1, H4, H2 and H3 (h3.py:114, 137) |
| F-08 | FIXED (deviation accepted) | test_base_rules_review.py:122-159 runs the frozen engine on a grains day whose 13:15 bar is a closure print and asserts the `closure_gap` fill's instant, price, costs, event flag and gross equal the simulator's R-B1 close point. The grains day stands in for equity 15:15 for a sound reason: the engine's 15:08 Topstep flatten would close an equity position first, which is R-S6's point, not a mismatch of the close-fill rule |
| F-09 | ACCEPTED-AS-RULED | rulings.md (kept as a stated departure, raised to the user); prereg_common.md:158-162 and prereg_H2.md:51 state it; counter "entry after closure" in h2.py:160 and h3.py:143; test `test_h2_counts_entries_after_the_closure` |
| F-10 | FIXED | release_touch.md, derive_windows.py, make_prereg.py and freeze_manifest.py in FROZEN_GLOBS; the hand-off outside by design |
| F-11 | ACCEPTED-AS-RULED | prereg_common.md:164 records the product-list check |
| F-12 | FIXED | resolved by F-04's fields (auctions.py:51-65 re-applies E.0's filter on the hist rows) |
| F-13 | FIXED | intraday.py:152 descriptive H4 table without "uncalibrated bucket" units, marked never part of the bar |
| F-14 | FIXED | intraday.py:150-151 descriptive H1 table without S_p > 15:08 product-dates |
| F-15 | ACCEPTED-AS-RULED | prereg_common.md:42 |
| F-16 | ACCEPTED-AS-RULED | prereg_common.md:134 |

Looked for and not found: a new free parameter (the only new knobs, `plan_windows` and a non-ledger registry, exist
inside the `--input-paths` test mode and are recorded in every output); a new look-ahead (F-04 only removes units;
the lock rule reads the fill bar's own high/low and the prior date's closes); a refusal on E.17's normal path (the
real store roots are outside PROCESSED_ROOT; the frozen builders write `trade_date_range`; `get_plan("ext2010h")`
exists once v12 defines the plan under that exact name, as step 8 requires; `load_auctions` ran on the real files
for the power rerun without raising); a hashed file v12 must change (hist_calendar.py, pull_hist.py, hist_store.py
and config.py are unhashed; nothing else in step 8's diff is in the manifest).

Residual notes, none requiring a change before the commit:

- R-1 (NOTE) reports/stage_e16_review.md is itself hashed (manifest line 114), so this appended section changes its
  sha256; the manifest must be regenerated after this append, as the lead already ruled (written last).
- R-2 (NOTE) The test mode (`--input-paths`) unlocks a non-ledger registry; since the marker, the result header and
  verdict.json now record the registry's path and sha256 (run.py:107-109, 149-150), E.17's Fable recomputation
  should assert `registry.path == ledger/trial_registrations.jsonl` on every output.
- R-3 (NOTE) The full-scale runtime probe (runtime_probe.md) predates R-B1..R-B4 and these fixes; the loader now
  reads ten columns and the lock rule builds a settlement proxy per grains and livestock date from 2019-05, so expect
  a higher peak RSS (order 1.5 to 2 GB per process) and some more wall time, still inside the overnight profile.
  E.17 should keep `/usr/bin/time -v` on each run and record it. Also, v12's new tests must not be named
  tests/test_base_rules_*.py, or `freeze_manifest.py verify` reports them as unlisted.
