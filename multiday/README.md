# multiday: Stage E.21's multi-day tests E21-T1..T4

The code of reports/stage_e21_briefs/lead_spec.md (sections 0-11; section A's rulings change no
code-level rule): T1 TSMOM-12, T2 the trend blend, T3 the equity turn of the month (NQ, RTY), T4
the equal-risk combination of T2, T3 and H2's frozen E.17 component. It reuses base_rules and never
edits it: marks (common.settle_point), the splice loader (store.load_product, preflight and its
refusals), calendars, the settlement table, the windows, the release rules and costs
(costs.vehicle_cost, VehicleCost.fill_costs, ReleaseRules.event/guard through
context.context_from_freeze), h2.chained_return (lookbacks), scaling.trailing_sigma (T4),
stats.unit_stats / newey_west_se / holm / dsr_at_n, guards (registry path, sha256), the limit-lock
rule (common.lock_rule). Tests use synthetic series only.

## Modules

| Module | What it does |
|---|---|
| constants.py | Every parameter: roots, windows (R-S3 floor for LE, R-S4 listing dates), EWMA com 60 / 261 / warm-up 60 / target 0.40, the last-6-dates rule, lookbacks 1/3/12, TOM days -2/+3, flat months (2019-04, 2024-02), NW lags 21/5, Holm 0.025, Sharpe bar 0.3, bootstrap 21 / 10,000 / 20261014, test ids E21-T1..T4 (label E21), H2's pinned sha256, paths, schemas, exit codes. |
| daily.py | MK and PS, mark dates, the per-contract path (one vehicle contract, rolled at each splice as base_rules.sim, roll legs moved out of guard windows, per-contract costs per side and case), the point-to-point chained return, daily returns, the EWMA sigma, the store-boundary splice for lookbacks. |
| signals.py | Eligibility (BarOracle from bars; CalendarOracle for the counts), month-end rebalance dates d*, references, lookbacks (h2.chained_return), T1/T2 signals, the calendar-defined S_M, the T3 units and S_u. |
| book.py | Per-root processing (everything that needs bars, one root at a time), the T1/T2 and T3 orders, fractional holdings, fills, roll costs, hold exclusions, the daily series. |
| combine.py | T4 (h5.combine's arithmetic) and H2's component from its result file. |
| stats.py | Per-case statistics (t, NW, p = max), the Sharpe and its circular block bootstrap, Holm at 0.025, the pass bar, per-year tables. |
| evaluate.py | The evaluation on a context: roots one at a time, T1..T4, per-root rows (spec 10). |
| counts.py | Calendar-only counts (no bar row; store metadata only). |
| run.py | The CLI: `counts` and `evaluate` (guards, run-once marker). |
| freeze_manifest.py | `build` and `verify` of reports/stage_e21_freeze.json. |

## Commands, in order

1. Calendar-only counts (already run by the coder; no bar row):
   `uv run python -m multiday.run counts` -> reports/stage_e21_briefs/calendar_counts.json, .md.
2. Freeze (lead; refuses to overwrite): `uv run python -m multiday.freeze_manifest build`
   (multiday/*.py, tests/test_multiday_*.py, base_rules/*.py, the spec, the prereg, every input
   role: base_rules' E.16 inputs, reports/stage_e17_run_manifest.json,
   reports/stage_e17_runs/H2_result.json); then `verify --sha256 <sha>`.
3. Register (lead): `screening.trial_registry register --test E21 --ids E21-T1 E21-T2 E21-T3
   E21-T4 --freeze reports/stage_e21_freeze.json --freeze-sha256 <sha> ...`.
4. Evaluate once: `nice -n 10 uv run python -m multiday.run evaluate --freeze
   reports/stage_e21_freeze.json --freeze-sha256 <sha>`. Before the marker
   reports/stage_e21_RUN_ONCE.json (O_EXCL): the freeze (every file, code, tests, base_rules, every
   input role at its default path), the registry is ledger/trial_registrations.jsonl with E21-T1..T4
   registered together under E21 and this freeze sha256, the output is free, the run manifest (its
   freeze sha256; step 2 and ext2010 stores for all 17 roots), the context, every store's preflight
   (no row), H2's result (status complete, sha256 a661cebc...). Exit 2 refused, 0 complete, 1
   STOPPED after the marker. Outputs in reports/stage_e21_runs/: T1..T4_result.json, per_root/
   <ROOT>.json, verdict.json, summary.md (STOPPED.json on a stop). `--input-paths` (with `--out-dir`,
   `--marker`, `--registry`) is the TEST MODE only.

Tests: `nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_multiday_*.py`.

## Coder choices (the spec was silent; the conservative option, each a coding matter)

1. Window starts: see Lead ruling Q1 below (the latest of the windows file, R-S4, R-S3).
2. "Eligible action date" (spec 3: action exclusion None, listed, MK and PS present, the MK bar
   outside every guard window) is used literally for every fill date: rebalances, close-outs, T3
   entries AND exits.
3. A month with no eligible rebalance date: the close-out is the first eligible action date after
   e(i, M) in the SAME store era; none (April 2019 or the window end): a forced close at the era's
   last mark (any mark; it pays its cost; counted "forced close at the era's last mark"). When that
   mark is at or before the last order date, the close merges into that order (one fill).
4. Orders on one date merge: the later order's target wins, one fill of the difference.
5. A failed hold (a contract change at a mark without a splice, a missing roll bar, a roll leg with
   no unguarded bar inside its interval): the order that opened the hold gets target 0 and the book
   is rerun (counted "hold excluded: <reason>"); the next order reopens. This mirrors base_rules'
   unit exclusion. A position held across the store boundary or past the last mark is closed by
   the backstop instead (Freeze review fixes, FR-1).
6. The roll-leg guard move stays strictly inside the interval (after the previous mark's bar, at or
   before the next mark's bar). A splice exactly at a mark instant is rolled before that mark (sim
   applies the mark first; splices sit at session boundaries, never at a settlement minute).
7. R-B3 price guards: a non-positive price anywhere on a chain (start, splice points, end) makes a
   daily return or lookback undefined (counted); a non-positive notional V gives no position
   (counted). Without them a zero price would raise (CL traded below zero in April 2020).
8. Series dates: a value booked on a date outside the spec's series dates adds that date
   (counted; none expected).
9. The freeze also pins base_rules/*.py (the reused code); outside the test mode every input role
   must be its default path, --out-dir and --marker are fixed, and every root needs an ext2010 store.
10. DSR (descriptive) at the registry's N read at run time, with the expected 532 beside it.
11. Bootstrap draws with sd 0 are dropped from the percentiles (nanpercentile) and counted.
12. Limit locks: base_rules' lock rule on every fill, roll legs included, counted only; 2010-2019
   fill bars with high == low counted as a diagnostic.
13. V uses the fill bar's open (spec 4: price ticks of MK(d*)); tests show the fill bar's own open
   moves only V (never sigma or a signal) and nothing after the fill bar moves any position.
14. Calendar-only counts: a required bar is assumed present inside its session; the roll blackout
   comes from the stores' metadata; T3's sigma warm-up is estimated as fewer than 60 consecutive
   mark pairs before day -2.

## Lead rulings (2026-10-14, 03:47-03:49 PDT, before any bar)

- Q1 FIXED: a root's window, for every purpose (marks, S_M, references, T3), starts on or after the
  latest of the windows-file date, the R-S4 sourced-listing date (RTY 2017-07-10, TN 2016-01-11)
  and R-S3's LE start (2014-12-15): constants.WINDOW_START_FLOOR, run.e21_starts. S_M is 15 in
  2018-06 and 17 from 2018-07 (calendar_counts.json).
- Q2 FIXED: a T3 unit whose sigma at day -2 is undefined (warm-up) or zero is excluded ("sigma
  warm-up" / "sigma zero", counted) and NOT counted in S_u (book.tom_sigma).
- Q3 ACCEPTED: a non-positive price makes a return, lookback or notional undefined (counted);
  fixed-contract P&L n x delta P is unaffected.
- Q4 ACCEPTED: a forced close at the era's last mark when no eligible close date exists.
- Coder choices accepted as listed; a failed hold's count ("hold excluded: <reason>") is in each
  result's exclusions.
- A12 FIXED: T3's days -2, -1, +1, +2, +3 are numbered on T3 trading days = the equity group
  calendar's trade dates that are not NYSE full-day closures (signals.nyse_closures by rule:
  New Year's Sunday -> Monday and Saturday -> none; MLK; Presidents; Good Friday; Memorial;
  Juneteenth from 2022; July 4; Labor; Thanksgiving; Christmas, with Saturday -> Friday and
  Sunday -> Monday; specials 2012-10-29, 2012-10-30, 2018-12-05). Entry and exit eligibility is
  unchanged (section 3); T1/T2 unchanged.

## Freeze review fixes (reports/stage_e21_review_freeze.md, lead 2026-10-14)

- FR-1 (a): tests/test_multiday_eraend.py drops bar S on the last six trade dates of April 2019
  and of February 2024: d* is None, the close falls to the era's last mark (the seventh-last
  trade date of each month); asserted: the target-0 order, its sell fill of the held n, its
  cost |n| x the per-contract cost, the counter "forced close at the era's last mark" == 2, the
  book ending flat. (b) book.simulate_book: the end-of-book check is no longer fatal (R-B3). A
  position still held at an era end (an interval across the store boundary) or after the last
  mark gets a target-0 order merged at the last mark of that era, counted "forced close
  (backstop)", and the book is rerun; only a held position with no mark at all raises (a code
  invariant). Tested for both cases.
- FR-2: tests for a splice with no new-contract bar inside the interval ("missing roll bar", a
  splice at an R-B1 15:15 closure instant) and for roll-out bars all inside guard windows
  ("missing roll bar (fill guard)"): the opener's target becomes 0 (hold exclusions are now keyed
  by the order's date), one exclusion, the next order reopens, per_contract_daily() is None on the
  interval's end date.
- FR-6: each test's exclusions hold the daily returns sigma skipped, in total and per root
  ("return undefined: previous mark missing", "<ROOT>: return undefined: ...").
- FR-7: the freeze pins multiday/README.md and screening/trial_registry.py; verify requires them.
- FR-9: process_root precomputes the fill of the mark on each side of every era change (a mark
  in neither era, 2019-05-01..05-05, included), so every backstop date has a fill; tested.

## Questions for the lead

All four answered (Lead rulings above).
