# Stage E.21: multiday build (MultidayCoder-OpusXHigh, 2026-10-14 03:20-03:47 PDT)

## Paths

- Package: multiday/ (__init__.py, constants.py, daily.py, signals.py, book.py, combine.py,
  stats.py, evaluate.py, counts.py, run.py, freeze_manifest.py, README.md)
- Tests (synthetic only): tests/test_multiday_world.py (world builders + 1 test),
  test_multiday_daily.py, test_multiday_dates.py, test_multiday_book.py,
  test_multiday_lookahead.py, test_multiday_stats.py, test_multiday_power.py, test_multiday_run.py
- Calendar-only counts (real inputs, no bar row): reports/stage_e21_briefs/calendar_counts.json and
  calendar_counts.md
- Not written (lead's steps): reports/stage_e21_freeze.json, the registration,
  reports/stage_e21_RUN_ONCE.json, reports/stage_e21_runs/.

## Summary

multiday/ implements lead_spec sections 0-11 (section A's rulings A1-A11 change no code rule;
A4, A6, A8 and A1 are pinned by tests). Everything bar-dependent per root is computed while that
root is loaded (process_root), then the T1/T2/T3 books are assembled from bar-free per-root data;
T4 is h5.combine's arithmetic on T2, T3 and H2's frozen component. Reused unchanged: settle_point,
load_product / preflight, calendars, settlement, context_from_freeze (release rules exactly as
E.17), VehicleCost.fill_costs, h2.chained_return, trailing_sigma, unit_stats / newey_west_se /
holm / dsr_at_n, lock_rule, guards.

Tests: 52 passed in about 10 s (`nice -n 10 uv run python -m pytest -q -p no:cacheprovider
tests/test_multiday_*.py`). Ruff: all checks passed on multiday/ and the test files. The whole
suite was not run (the lead's detached run owns it).

Calendar counts headline (17 roots, 2,502 root-months): 2,497 rebalance dates; 446 moved earlier
(Treasury roots about 54 of 164 each, GC 65, ZN 55: month-end roll blackouts; HE and LE 3 dates each
skipped for a fill guard); 5 months with no eligible date (ZC 2011-06 and 2022-06, ZL 2013-06 and
2018-06: all six dates in a roll blackout; RTY 2017-06: not listed before 2017-07-10). T3: NQ 164
months, 137 tradeable (calendar estimate; early halt 22, sigma warm-up 3, store boundary 1, window
end 1); RTY 81 months, 66 tradeable (early halt 9, not listed 1, warm-up 3, store boundary 1,
window end 1). S_M: 13 from 2011-07, 14 from 2015-12 (LE), 15 from 2017-01 (TN), 16 in 2018-06
(RTY), 17 from 2018-07 (HE). The counts run took 5.7 s, peak RSS 219 MB.

## Tests (what the prompt requires, where)

- Chaining across a splice, daily return and lookback: test_multiday_daily (point return equals
  h2.chained_return for close points; the daily return by hand across a splice; a contract change
  without a splice is undefined); a 12-month lookback over three splices equals the product of
  segment ratios (test_multiday_dates, lead A1).
- No look-ahead (T1, T2, T3): test_multiday_lookahead changes every price after a fill bar and
  plants a future bar; positions, sigma, lookbacks, S_M and S_u up to that date are unchanged, later
  ones do move; the fill bar's own open moves only V.
- Roll costs: test_multiday_book (each leg pays |n| x the per-contract cost, long and short);
  the per-contract path equals base_rules.sim.simulate's daily attribution for a one-contract hold
  with a roll, and each fill's cost equals VehicleCost.fill_costs (test_multiday_daily).
- Dates: month-end d*, a blackout moving it earlier, the 6-date limit, its close-out, the
  February 2024 close-out, the April 2019 flat month and the May 2019 reopening, references (an
  early-halt skipped, a blackout allowed), turn-of-month days -2 and +3 across month and year ends
  and holidays, day -2 the SECOND-to-last date when the last two straddle a closure (lead A8), the
  2019-04 TOM unit a store-boundary exclusion.
- EWMA equals a direct summation and pandas ewm(com=60, adjust=True).var(bias=True) x 261; the
  60-return warm-up; returns strictly before d.
- S_M calendar-defined; S_u; no sigma floor and no position cap (lead A4); T2 the mean of three
  signs with no book-level scaling (lead A6).
- T4 equals base_rules.h5.combine on renamed synthetic components.
- Statistics: t, NW at fixed lags, p = max, Holm at 0.025 stopping when the second test fails, the
  pass bar, Sharpe annualization, the circular block construction, bootstrap determinism (seed,
  chunk-invariant).
- Run: pre-marker refusals (unregistered, another label, wrong freeze sha256, a changed frozen
  file, an existing output, fixed paths outside the test mode), the full evaluate end to end on 17
  synthetic step 2 stores in the real layout (marker, four results, verdict, summary, per-root
  rows), a second run refused.
- A planted trend T1 and T2 detect (t > 3) and pure noise T1 does not (p > 0.025).
- R-B3: a zero or negative price makes a return or lookback undefined, never an exception.

## Coder choices (each the conservative coding option; full list in multiday/README.md)

1. Window starts from the windows file, LE floored to 2014-12-15 (R-S3); R-S4 through
   RunContext.listed.
2. Section 3's eligible action date is applied literally to every fill date (rebalance, close-out,
   T3 entry and exit): MK and PS present, outside every guard window.
3. No eligible close inside the same store era (April 2019, the window end): a forced close at the
   era's last mark, paying its cost, counted.
4. Orders on one date merge (the later target wins, one fill).
5. A failed hold (contract change without a splice, missing roll bar, no unguarded roll bar inside
   the interval) is excluded by setting its opening order's target to 0 and rerunning, counted.
6. Roll legs moved out of a guard window stay inside their interval; a splice at a mark instant is
   rolled before the mark.
7. R-B3 price guards (non-positive price: undefined return or lookback; non-positive V: no
   position), counted.
8. The freeze also pins base_rules/*.py; outside the test mode every input role must be its default
   path, --out-dir and --marker are fixed, and all 17 roots need an ext2010 store.
9. DSR at the registry's N read at run time (expected 532 shown beside it).
10. Bootstrap draws with sd 0 dropped from the percentiles and counted.
11. Limit-lock and 2010-2019 high == low checks on every fill, roll legs included, counted only.

## Questions for the lead

1. S_M and R-S4 (RTY). The window start used for S_M is the windows file's (RTY 2017-06-01), so
   e(RTY, 2017-06) counts and S_M = 16 in 2018-06 although RTY cannot hold a position that month
   (its 12-month reference is not listed before 2017-07-10): every other root is scaled by 1/16
   instead of 1/15 for one month, and RTY's June 2017 shows "no eligible rebalance date" (no
   position, no effect). The alternative, E.20's PR-8 reading ("the later of the json start and
   R-S4's listing date"), is a one-line change: add RTY 2017-07-10 and TN 2016-01-11 to
   constants.WINDOW_START_FLOOR (TN changes nothing; RTY moves S_M 2018-06 to 15). Kept as written
   (it is the conservative scaling of section 4); please confirm.
2. S_u (T3) counts a root whose unit is eligible on dates and bars but whose sigma is still in
   warm-up; that root holds zero, so the other root's position is halved in those months (RTY's
   first three months). Section 5 says eligibility is "calendar data and bar existence", which
   this follows; please confirm sigma is not part of it.
3. Non-positive prices (CL, April 2020): coded as undefined returns, lookbacks and V (counted)
   rather than chaining through them. A statistical rule? If the lead prefers chaining negative
   prices, only the guard in daily.chain_prices' two callers changes.
4. Forced close at an era's last mark when no eligible close date exists before the store boundary
   or the window end (coder choice 3): the spec covers only "the first eligible action date after
   e(i, M)". Calendar counts show no such case at April 2019 or February 2024 (every root has an
   eligible date there); it can only arise from missing bars.

## Not finished or not verified

- Nothing ran on real bars (by design). The real-scale runtime and memory of `evaluate` are not
  measured: per root one splice-loader read (as E.17) plus light per-date work; expect E.17's
  per-root load times, one root in memory at a time.
- calendar_counts assume every in-session bar exists; the real run will add "missing bar" counts.

## Update after the lead's rulings (2026-10-14 03:48-03:51 PDT)

Applied: Q1 (window start = the latest of the windows file, R-S4 listing, R-S3 LE start, for every
purpose), Q2 (a T3 unit with sigma undefined or zero at day -2 is excluded and not in S_u), A12
(T3 days numbered on equity trade dates that are not NYSE full-day closures, nyse_closures by
rule plus the three specials). Q3, Q4 and the coder choices accepted. Holdings rows now also carry
"vehicle" and "mark_price_ticks". Tests: 57 passed; ruff clean. Counts re-run (overwritten):
- Rebalances: 2,501 root-months, 2,497 rebalance dates, 446 moved earlier, 4 with no eligible
  date (ZC 2011-06, 2022-06; ZL 2013-06, 2018-06). RTY: 80 months from 2017-07, none without a date.
- S_M: 13 from 2011-07, 14 from 2015-12, 15 from 2017-01, 17 from 2018-07 (15 in 2018-06).
- T3 (calendar estimate): NQ 164 months: 154 tradeable; entry early halt 2, exit early halt 3,
  sigma warm-up 3, store boundary 1, window end 1. RTY 80 months: 73 tradeable; entry early halt 1,
  exit early halt 1, sigma warm-up 3, store boundary 1, window end 1. S_u: 1 in 81 months, 2 in 73.

## Freeze review fixes (2026-10-14, FR-1, FR-2, FR-6, FR-7)

Applied as listed in multiday/README.md ("Freeze review fixes"): forced-close tests at both era
ends; a non-fatal backstop close (counted "forced close (backstop)") replacing the end-of-book
raise; tests for "missing roll bar" and "missing roll bar (fill guard)"; per-root return-skip
counts in the exclusions; README and screening/trial_registry.py pinned by the freeze. Tests: 61
passed (tests/test_multiday_*.py, new file tests/test_multiday_eraend.py); ruff clean.
