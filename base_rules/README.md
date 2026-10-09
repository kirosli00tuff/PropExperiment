# base_rules: the base-rule tests H1..H5 (Stage E.16 Task 3, run in E.17)

The code of the five tests of reports/stage_e16_briefs/lead_spec.md (H1 settlement-window momentum,
H2 month-end NQ/ZN pair, H3 Treasury auction cycle, H4 next-day reversal, H5 their equal-risk
combination). It is hashed into the freeze (reports/stage_e16_freeze.json, `code`). It never edits
a frozen module: screening/stage_e_engine.py's clock, screening/stage_e_frozen.py's D8 costs
(ProductCosts, slippage_cents, leg_inputs), screening/stage_e_rules.py's ReleaseCalendar,
data/stage_e_bars.py, data/hist_bars.py, data/hist_calendar.py, data/group_session.py,
rules/products.py, screening/trial_registry.py and screening/stage_e_verdict.py (DSR) are imported
and called unchanged. Synthetic data only in E.16: no store was read.

## Modules

| Module | What it does |
|---|---|
| constants.py | Every parameter: the 27 price paths and their E.12 vehicles, U2 windows (on-or-after dates) and the fallback, warm-ups 20 / 60, NW lags, year thresholds (H2 6), Holm 0.05, the cost cases, the tenor map, input paths, schemas, exit codes. |
| inputs.py | Task 1's settlement table (periods tile 2010-06-07..2024-02-29; null minute = not listed; `lead_grade` is the H1/H4 grade; the first-business-day-of-week open), U2's windows file, window starts recomputed from E.12's quote record (the EC-AUC rows: auctions.py). |
| calendars.py | Per group: the hist calendar (data.hist_calendar; livestock parsed from Task 3b's file) before 2019-05-01, the 2019-on calendar from it; trade dates, offsets, early halts, unsourced dates, open intervals, D6 day sessions. |
| store.py | The splice loader: run manifest (a fixed plan per root), the pre-marker preflight (no row read), path refusals, sha256, booking checks, plan/calendar metadata checks, no date in both stores, splices and roll blackout (L-8), ten columns read (high, low, volume, no-new-positions for F-07), closure-flagged bars unusable. |
| hist_plan.py | F-01: the 2010-2019 store of a root under its fixed plan (name, directories, plan window from an injectable resolver, metadata, bookings). |
| auctions.py | The EC-AUC rows with their announcement dates (F-04) and E.0's filter. |
| limits.py | F-07: the engine's limit-lock test applied to every fill. |
| costs.py | Per-fill cost in exact cents (base, stress = +1 vehicle tick per side, slip150), the release rules (event window and D9.5a guard through the frozen ReleaseCalendar on the combined 2010-2024 rows) and the conservative fallback for touching types with no 2010-2019 rows. |
| sim.py | The position simulator: fills at bar opens, rolls at splices, daily marks, exact cents, per-fill costs, daily attribution. |
| scaling.py | Section 3's trailing-20 sigma with warm-up, and H5's trailing-60 sigma. |
| common.py | The run context (window, O_p with the first-of-week rule, listing), the action-date and reference exclusions, risk-unit conversion, unit rows. |
| intraday.py, h2.py, h3.py, h5.py | The five runners (H1 and H4 share intraday.py). |
| stats.py | t, Newey-West, the larger-p rule, Holm, year stability, the pass bar, DSR at N (stage_e_verdict.dsr_table). |
| touch.py | Which release types touch an H fill minute (frozen 2019-05..2024-02 calendar alone). |
| counts.py, power.py, report.py | Calendar-only counts, the power table, the release-touch report (no bar). |
| guards.py, context.py, results.py, run.py | Freeze-manifest and registration checks, the run-once marker, contexts, result files, the E.17 CLI. |
| probe.py | The full-scale runtime probe on synthetic stores (never the repo). |

## E.17 commands, in order

1. Register the five ids under the fixed label (ruling R-B4) against THIS freeze manifest:
   `screening.trial_registry register --test E16 --ids E16-H1 E16-H2 E16-H3 E16-H4 E16-H5
   --freeze reports/stage_e16_freeze.json --freeze-sha256 <its sha256> ...`; the runner requires
   the registration's freeze sha256 to equal the `--freeze-sha256` it is given (F-02).
2. Write the run manifest (schema `stage_e16_run_manifest/1`): `{"stores": {ROOT: {"ext2010":
   {"path", "sha256", "plan"} | null, "step2": {"path", "sha256"}}}}` for all 27 roots; `null` =
   fallback window (2019-05-06..2024-02-29) for that root. `plan` is the root's FIXED plan (F-01):
   "ext2010" for NG, NQ, ZN, 6E, GC, ZC (C1's plan), "ext2010h" for the 21 others; any other plan is
   refused. The hist file must be `<base>/<plan>/<ROOT>/ohlcv-1m_<ROOT>_v_0_<first>_2019-04-30_
   <plan>.parquet` with 2010-06-06 <= first <= the product's window start, first and last equal to
   data.pull_hist.get_plan(plan)'s window (E.17's v12 must define "ext2010h" under exactly that
   name), its metadata naming the plan and holding its trade_date_range inside that window. Record
   the manifest's sha256.
3. `uv run python -m base_rules.run run --test H1 --freeze reports/stage_e16_freeze.json
   --freeze-sha256 <sha> --manifest <manifest> --manifest-sha256 <sha>`; then H2, H3, H4 the same;
   then `run --test H5 --freeze ... --freeze-sha256 <sha>` (H5 reads no bar: it combines the four
   complete component results, whose sha256s go into its marker).
4. `uv run python -m base_rules.run verdict --freeze ... --freeze-sha256 <sha>` (Holm across the
   five registered tests on the base case, no subset (F-03), the pass bar, DSR at N read from the
   registry). `--registry` must be ledger/trial_registrations.jsonl unless the test mode
   `--input-paths` is given; the registry's path and sha256 go into the marker, the result header
   and verdict.json (F-03).

Order inside `run` (ruling R-B3): every INPUT problem is found before the run-once marker, so a
run that writes its marker cannot be lost to a predictable refusal:
1. the freeze manifest: its sha256, every listed file (sha256 and size), every base_rules/*.py
   listed, every input role a listed file;
2. the registry is ledger/trial_registrations.jsonl (else refused outside the test mode) and the
   registration holds E16-Hx under label E16 AND this freeze manifest's sha256 (F-02, F-03);
3. the output path is free (no marker, no result or units file of the test);
4. H5: the four complete component results under the same freeze. H1-H4: the run manifest (its
   sha256, a store per product); the whole context (calendars with their pinned sha256s, the
   settlement table, the windows, the EC-AUC rows, the release rows and the touch report); then
   every store the test reads is preflighted WITHOUT reading a row (store.preflight: path layout
   and the root's fixed plan, existence, sha256, the plan's window from get_plan, parquet metadata
   plan, trade_date_range and calendar, rolls booked);
5. the marker (O_EXCL), before any bar is read; 6. the run.
During the run no DATA condition raises: a store refused once its rows are read (a booking, a
holdout row, a duplicate or off-grid bar, a date in both stores) excludes the product ("store
refused", the reason in the result's notes); a contract change, a missing bar, a missing roll bar
exclude the unit, counted. Only a code invariant can STOP a run.

Exit codes: 2 refused (nothing written, no bar read), 0 complete, 1 STOPPED after the marker (the
attempt is closed). Markers: `<out>/<test>_RUN_ONCE.json` (O_EXCL, written before any bar).
Freeze manifest: the lead's reports/stage_e16_freeze.json (reports/stage_e16_briefs/
freeze_manifest.py, schema `stage_e16_freeze/1`, a `files` list of path, sha256, bytes). Input
roles that must be files of it: reports/stage_e16_settlement.json, reports/stage_e16_windows.json,
reports/stage_e2b_release_calendar.json, reports/stage_e14_cal_releases.json (E.14's FOMC/NGS/WPSR
2010-2019 rows of the cost rule), reports/stage_e16_calendars/ec_auc_2010_2019.json,
reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json (F-04),
reports/stage_e16_calendars/hist2010_livestock.json, reports/stage_e12_quotes_ext2010.json and the
six data/calendars/hist2010/*.json. `--input-paths <json>` is the TEST MODE only (tests, the
synthetic probe): other paths per role, each still a file of the freeze; a registry other than the
ledger's; "plan_windows" for a plan harness v10 does not know. Fixtures:
tests/_base_rules_fixtures.py.
Outputs: `<out>/<test>_result.json` (series per cost case, statistics, year tables, exclusions by
reason, per-product counts, the H5 component series and grid, notes) and `<out>/<test>_units.jsonl`.

Calendar-only reports (no bar): `python -m base_rules.report counts --out-json ... --out-md ...`
and `python -m base_rules.report release-touch --out-md ...`.

## Tests

`uv run python -m pytest -q -p no:cacheprovider tests/test_base_rules_*.py` (synthetic only;
fixtures in tests/_base_rules_fixtures.py): the hand-computed multi-day trade (roll and overnight
mark), the frozen-engine match (ZN, NQ on MNQ, an event-window fill), causality (H1, H2, H4
signals, risk scaling, H5 scaling), planted edge and pure noise per runner, the splice loader, its
preflight and refusals, the exclusion counters, run-once, registration and pre-marker refusals,
statistics, power, inputs, costs, and the rulings (tests/test_base_rules_rulings.py: an
equity-15:15 closure day for H1, H4 and H2, the "no entry bar" case, a grains session-close day,
the uncalibrated bucket, a contract change counted, a refused store excluded, the fixed label,
"entry after closure"), the review fixes (tests/test_base_rules_review.py: the limit-lock test,
the no-new-positions count and the high == low diagnostic, the descriptive tables, the engine's
closure-gap fill against the R-B1 close point) and a second plan name in the store tests.

## Lead rulings applied (2026-10-09)

- R-B1, the settlement minute at a scheduled closure (an open interval of the trade date's
  calendar ends at S_p: equity 15:15 before 2020-10-26, grains 13:15 / 14:00 when the day session
  closed there): (a) an exit or a mark at the settlement minute is the CLOSE of bar(S_p - 1); bar
  S_p is never used; (b) an entry at the settlement or decision minute (H2 at max(S_NQ, S_ZN), H3
  at S_T) is the open of the first bar of the same trade date's session after the closure, else
  the unit is excluded ("no entry bar"); (c) H4's d-1 move uses H1's exit price on d-1 under (a);
  (d) inside an open interval nothing changes. PS (close of bar S_p - 1) is unchanged. A close fill
  happens at its bar's open + 60 s; its cost bucket, event window and fill guard are looked up at
  the bar's open (the engine's close_cost). Applied in H1, H2, H3, H4 (hence H5), the calendar-only
  counts and the release-touch report. H3 at t: a cover at t's settlement point and a long at t's
  entry point (one fill of two contracts when both are the same bar's open).
- R-B2: a fill whose 30-minute CT bucket has no frozen D8 calibration pays, per side, the
  product's largest per-side slippage over its frozen buckets (s_b plus depth) plus commission;
  stress and 1.5 x apply on top. Counted as "uncalibrated bucket" (units with such a fill).
- R-B3: no data condition raises during a run (above); input problems are refused before the
  marker.
- R-B4: label E16, ids E16-H1..E16-H5, hard-coded.

## Freeze review fixes applied (reports/stage_e16_review.md, the lead's rulings)

- F-01: fixed plan per root (above); base_rules.hist_plan checks the name, directories, plan
  window, metadata and books the rows as data.hist_bars does, with the plan window from an
  injectable resolver (data.pull_hist.get_plan by default; tests and the probe inject a stub).
- F-02: the registration must carry the given freeze sha256. F-03: no `verdict --tests`; the
  registry restricted to the ledger outside the test mode; its path and sha256 recorded.
- F-04: H3 counts an auction only if its announcemt_date is on or before t-3 ("announced after
  entry"; none on file: "no announcement date"), applied after the trade-date and t <= window-end
  checks and before the same-tenor overlap rule (an auction that does not count neither trades
  nor blocks a later one). Hist rows carry the field; the frozen 2019-05..2024-02 rows take it from
  reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json, joined on id (auction date and
  tenor must agree); E.0's filter applies to each field that exists. Calendar-only: 95 auctions
  announced after t-3 (49 in 2010-06..2019-04, 46 in 2019-05..2024-02, matching
  f04_t3_counts.json).
- F-07: high, low, volume and in_no_new_positions_window are read. base_rules.limits applies the
  engine's _locked test (prior-settlement proxy, limit_band, limit_prices) to EVERY fill on a
  hard-limit product where a LIMITS period exists (from 2019-05-01): a buy locked when low >= the
  limit up, a sell when high <= the limit down; the unit is excluded ("limit locked"). H1 and H4
  count entries in a no-new-positions bar ("no new positions (Topstep)") and report the pooled
  statistics without them as a descriptive Topstep-venue table (the base statistic keeps them).
  2010-2019 (no limit table): "diag: 2010-2019 fill bars with high == low", a diagnostic only.
- F-08: tests/test_base_rules_review.py runs the frozen engine on a frame whose closure print sits
  at the session close (a grains day closing at 13:15; an equity 15:15 case cannot reach the
  closure in the engine, whose Topstep flatten closes equity at 15:08) and asserts the engine's
  closure-gap fill equals the simulator's R-B1 close point: instant (the bar's open + 60 s),
  price, costs and event flag.
- F-09: R-B1 (b) is a departure from the engine (which cancels an opening order at a closure
  print); "entry after closure" counts the H2 months and H3 auctions it governs (results and the
  calendar-only exclusion tables).
- F-13: H4's result also reports its pooled statistics without the "uncalibrated bucket" units;
  F-14: H1's result also reports them without the product-dates with S_p > 15:08 CT. Both, and
  the Topstep table, are in the result's notes["descriptive"], marked DESCRIPTIVE.

## Coder choices (the spec was silent or ambiguous; the conservative option was taken)

1. Cost per side = exactly what the frozen engine charges at qty 1: `ProductCosts.
   side_slippage_ticks` (the bucket's s_b PLUS its depth term; in an event window the largest s_b
   plus the depth term, T12-4), ceil to the cent; the spec's "s_b" is read as that per-side
   slippage, since the engine match is binding. Stress adds one vehicle tick (exact cents) per
   side; slip150 multiplies the slippage ticks by 1.5 before the ceil. (R-B2 for uncalibrated
   buckets: the largest per-side slippage, event window or not.)
2. Release concerns: a release concerns a fill when its products list holds the price-path root OR
   the vehicle root (the union; NQ or MNQ). The event window and the fill guard apply to EVERY fill,
   roll and close fills included (the engine exempts only forced flattens, which these tests never
   make).
3. A row of E.14's release file without an instant (WPSR 2012-11-01, time unverified) becomes
   every CT clock time its type uses on that date (more event windows, never fewer).
4. A bar flagged `in_scheduled_closure` is never usable (absent), as the engine never fills on it
   (OC-T); with R-B1 a closure at S_p is handled by the close of bar S_p - 1 and the reopening bar.
5. A reference date must be inside the product's window (as well as section 2's rules); a
   reference date's S_p must be listed and, for H1/H4, lead-graded secondary or better; H4's d-1
   must also satisfy H1's S - 30 > O.
6. Marks are applied in time order: a mark before a leg's entry is not applied to it (H2's ZN leg
   enters at the decision minute after its own 14:00 mark on d5; NQ under R-B1 enters at 15:30
   after its 15:15 mark); that leg's d5 value is minus the entry cost and the move to the next mark
   is booked on the next date (unit totals unchanged).
7. H3: t is an action date (an exit and an entry) besides t-3 and t+5. The same-tenor overlap rule
   is applied on the calendar, before any bar (kept windows are compared with the last KEPT window).
   H3's daily H5 series sums the open units' risk-unit values (tenors can overlap in time).
8. g (section 3) holds every unit that passed every exclusion and has a non-zero signal (warm-up and
   sigma-undefined units included); sigma uses the g of units whose EXIT date is strictly before the
   unit's ENTRY date (identical to "strictly before the entry date" for H1/H4; causal for H2/H3).
9. H5's grid: the dates on which any product was H1- or H4-eligible (passed every exclusion,
   whatever its signal) and the trade dates t-3..t+5 / d5..dL of traded H2/H3 units.
10. (Replaced by R-B3.) A contract change is excluded and counted everywhere ("contract change").
11. (Replaced by R-B2.) No unit is excluded for a missing cost bucket.
12. Window starts: the windows file's on-or-after dates (U2); before the first trade date the
   product is "outside window". A product without a step 2 store is refused (the manifest must give
   one); one without an ext2010 store runs on the fallback window.

## Open notes for the lead

- H2 after R-B1 (calendar-only, real inputs): full window 80 eligible months, 60 after warm-up
  (2016-2024, 7-8 a year; 26 months "no entry bar": equity 2010-06..2012-11, when the session after
  15:15 belonged to the next trade date; 33 months in the ESTIMATED ZN roll blackout); fallback
  window 35 eligible, 15 after warm-up, 2 qualifying years, so H2 cannot pass on the fallback
  window. The run uses the stores' real roll metadata, so the blackout count will differ.
- Livestock 2010-2019: data.hist_calendar's loader only knows six groups; calendars.load_hist parses
  Task 3b's file with the frozen parser instead. E.17's harness must also let the store builder use
  it (data/calendars/hist2010/livestock.json and HIST_GROUPS).
- The runtime probe (reports/stage_e16_briefs/runtime_probe.md) ran before the rulings; R-B1..R-B4
  add no bar reads (the preflight hashes the stores once more before the marker).
