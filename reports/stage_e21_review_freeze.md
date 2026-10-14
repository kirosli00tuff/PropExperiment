# Stage E.21 freeze review (FreezeReviewer-FableXHigh, 2026-10-14 03:51-04:08 PDT)

Reviewer: Fable 5.1, xhigh (independent of the Opus lead and the Opus coder). Inputs read: docs/prompts/STAGE_E.21.md
(FIXED DESIGN F1-F8, SCOPE), reports/stage_e21_prereg.md, reports/stage_e21_briefs/lead_spec.md (0-11, A1-A12),
multiday/README.md (Lead rulings Q1-Q4, A12; Coder choices 1-14), multiday_build.md, calendar_counts.md, every
multiday/*.py module, the test names and assertions of tests/test_multiday_*.py, and the base_rules functions the code
reuses (h2.chained_return, store splice helpers, common.settle_point / action_exclusion / reference_exclusion,
stats.unit_stats / newey_west_se / holm, scaling.trailing_sigma, h5.combine, costs.fill_costs / guard / event). No bar
of any real store was read; the H2 and H5 result files were inspected for keys, sizes and sha256 only.

## Verdict: APPROVE WITH FIXES

No BLOCKING finding. Two SHOULD FIX items are untested code paths that run only after the run-once marker and whose
failure would STOP the single attempt (exit 1, never rerun). The rest are NOTES for the return's text, none changes a
verdict number.

| Id | Severity | File:line | Concrete failure scenario | Proposed fix |
|---|---|---|---|---|
| FR-1 | SHOULD FIX | multiday/book.py:179-186 (forced close at the era's last mark; lead Q4, coder choice 3); tests: none (grep "forced" over tests/test_multiday_*.py is empty) | A root's six last February-2024 dates (or April-2019 dates) all lack a settlement bar on real data (the calendar counts ASSUME every bar is present), so d* is None, `first_eligible_after` returns None at the era end, and this path writes the only order that keeps `_run`'s invariant "the book ends with a position" (book.py:351-352) from raising AFTER the marker. The path is never executed by any test; a wrong `max(...)` day, a merge that loses the target-0 order, or a missing `rd.fills` entry for that date would convert a data gap into a STOPPED stage. | Add a synthetic test per era end (ext2010 April 2019, step 2 February 2024): no mark on the month's last six dates, a position open from the previous month; assert exactly one close fill at the era's last mark, its cost charged, the counter "forced close at the era's last mark" == 1, and the book ends flat. |
| FR-2 | SHOULD FIX | multiday/daily.py:196-206 ("missing roll bar", "missing roll bar (fill guard)"), multiday/book.py:280-291 (exclude and rerun); tests cover only "contract change" (tests/test_multiday_book.py:75-80) | A D9.5a guard window covering every old-contract bar between the previous mark and a splice (or the store's roll bar absent) makes `_interval` fail; `simulate_book` then zeroes the opening order and reruns. Untested: a wrong `last_j` would exclude the wrong order, silently dropping a month of a root or looping. The hold-exclusion counter and the per-root "per_contract_daily" None entry are also unverified for these reasons. | Add two synthetic tests (a splice with no usable old-contract bar in the interval; a guard window over every candidate roll_out bar) asserting the opener's target becomes 0, the counter "hold excluded: missing roll bar[ (fill guard)]" == 1, the next order reopens, and `per_contract_daily()` carries None on that interval's end date. |
| FR-3 | NOTE | multiday/signals.py:83-97 (action_why: has_mark, has_ps), 120-151 (d* scan), 294-306 (T3 exit eligibility) | Bar EXISTENCE at later dates decides earlier actions: d* moves from e(i,M) to an earlier date when e's settlement or signal bar is absent, and a T3 unit is never entered when its day +3 bar is absent. This is a look-ahead on data presence, not on price; every calendar reason (blackout, early halt, fill guard, unsourced) is known in advance. The spec (3, 5) prescribes it and the counters separate "missing bar (mark)"/"missing bar (signal)" from calendar reasons. | No code change. Declare in the prereg's reported items that the run reports, per test, the number of rebalance moves and T3 exclusions whose reason is bar absence, as a look-ahead diagnostic; a nonzero count is discussed in the return. |
| FR-4 | NOTE | multiday/combine.py:59-80 (h5.combine's arithmetic, asserted equal by test_multiday_stats.py:96) | H2's E.17 component is a daily mark-to-settlement series on its HOLD dates only: 280 dates, 2016-06-24..2024-01-31 (56 monthly units), 0 elsewhere on the union grid; T2 is 0 before its first fill (about 2011-07). The trailing 60-grid-date sd is therefore 0 (component skipped) until a component has history, is computed over mostly zeros for the first ~60 grid dates after T2 starts, and permanently for H2 (about 5 nonzero values per 60 dates), inflating x/sigma on those dates. T4 is T3 alone from the end of its warm-up (~2011-01) to ~2011-07. This is exactly H5's frozen method (E.16 lead_spec section 4; H5's E.17 grid was 3460 daily dates with H2 treated the same way), symmetric in sign, so no bias; it adds variance. | No change (SCOPE forbids variants). State in the return that T4 = T3 alone until mid-2011 and that H2's contribution is concentrated on its 280 hold dates; read T4's per-year table with that in mind. |
| FR-5 | NOTE | reports/stage_e21_prereg.md section 2 ("capital units") vs prompt F6/F4 ("risk units"); lead_spec 5 ("scaled to the hold" read as the constant 0.40/sigma) | Both are constant rescalings within a test: t, p (plain and NW), Holm, the annualized Sharpe and the bootstrap interval are invariant; costs scale with the same factor as gross (|delta n| x cost), so net scales too. T4 rescales each component by its own sd. | Add one sentence to the prereg: the verdict statistics are invariant to the unit choice and to any constant position scale. |
| FR-6 | NOTE | multiday/daily.py:255-275 | sigma's daily returns skip any (d_prev, d) pair whose previous mark is missing (for example a holiday session with no settlement bar), so the move across such a gap never enters the EWMA; spec section 1 prescribes this. Slightly low sigma (larger positions), the same in every year, no look-ahead. | No change; mention under exclusions ("return undefined: previous mark missing" count). |
| FR-7 | NOTE | multiday/freeze_manifest.py:52-57, 114 | The freeze pins multiday/*.py, tests/test_multiday_*.py, base_rules/*.py, the spec, the prereg and every input role; it does not pin screening/trial_registry.py (the registry check at run time) or multiday/README.md (the rulings text). The registry itself checks the harness v12 sha256 at registration. | Acceptable. Name the two unpinned files in the freeze text so the VerdictVerifier knows the registry code is covered by the harness hash, not the freeze. |
| FR-8 | NOTE | multiday/run.py:95-159 | Pre-marker order verified by reading: freeze (every listed file hashed), registry (label E21, the four ids, this freeze sha256, ledger path outside the test mode), marker absent, output free, run manifest (step 2 and ext2010 store for all 17 roots), context, each store's preflight (metadata), H2's result (status complete, pinned sha256). The marker is opened with O_WRONLY|O_CREAT|O_EXCL (mode 0444) before `evaluate` calls `load_or_exclude`. `--out-dir`, `--marker` and every input path are fixed outside the test mode. | None. |

## Checks run and what they showed

1. Spec vs prompt vs papers (check 1). constants.py matches F3-F6 and lead_spec 2-9: EWMA_COM 60, delta 60/61,
   261, warm-up 60 returns, TARGET_VOL 0.40, last-6-dates rule for d* and references, lookbacks (1, 3, 12), T1 12,
   S_M lookback 12, TOM entry day -2 / exit day +3, FLAT_MONTHS (2019-04, 2024-02), NW lags {T1 21, T2 21, T3 5,
   T4 21}, Holm 0.025, Sharpe bar 0.3, sqrt(252), block 21, 10,000 draws, seed 20261014, T4 window 60 / warm-up 60,
   H2 sha256 a661cebc... T1 = sign(R_12) (signals.py:186), T2 = (sign R_1 + sign R_3 + sign R_12)/3 with all three
   required (190-194), sign(0) = 0; n = s x 0.40 / sigma / (S_M x V) (book.py:235); T3 n = 0.40 / sigma / (S_u x V)
   long only (257). Rulings A1-A12 and Q1-Q4 are in the code: Q1 WINDOW_START_FLOOR (RTY 2017-07-10, TN 2016-01-11,
   LE 2014-12-15) applied by run.e21_starts to ctx.starts for every purpose; Q2 tom_sigma before divisor_su; A12
   t3_trading_days.
2. EWMA (daily.py:279-301): the recursion s0 = delta s0 + 1, s1 = delta s1 + r, s2 = delta s2 + r^2 gives weights
   delta^k on the k-th most recent return normalized by their finite sum (pandas adjust=True), the weighted mean is
   removed, only returns dated strictly before d enter (rs[j][0] < d), None before 60 returns. The test asserts
   equality with a direct summation and with pandas ewm(com=60, adjust=True).var(bias=True) x 261.
3. Timing (check 2). Signal price PS = close of bar S-1, fill MK = open of bar S (or the close of S-1 under R-B1, when
   the signal and the fill coincide at the same close, the frozen E.16 convention). sigma(d*) uses returns ending at
   MK(d*-1) at the latest. V uses the fill bar's own open only for the notional (coder choice 13; tested). S_M is
   built from calendars and windows alone (signals.py:198-208). S_u counts units eligible on calendar, bar existence
   and each root's own past sigma; both roots fill at the same equity settlement. See FR-3 for bar existence.
4. Chaining (check 3). chained_point_return (daily.py:233-252) is h2.chained_return's loop with point prices at the
   ends; lookbacks call h2.chained_return itself on bars with the store-boundary splice added only on a contract
   change (daily.py:315-333). Daily returns are undefined across the 2019-04-30 / 2019-05-06 boundary and T1/T2 are
   flat across it (FLAT_MONTHS); T3's April 2019 unit is a "store boundary" exclusion (exit 2019-05-03 is in no
   era). Roll legs: old contract closed at the open of the last usable bar before the splice, new opened at the open
   of the first usable bar at or after it, moved out of guard windows inside the interval only (daily.py:158-170,
   196-216); increments booked on the leg's trade date; the test asserts equality with base_rules.sim.simulate's
   daily attribution for a one-contract hold with a roll.
5. Costs (check 4). Every fill row (rebalance, close, entry, exit, roll_out, roll_in) carries
   VehicleCost.fill_costs(bar open ns, side, ReleaseRules.event) per case, with the R-B2 uncalibrated flag, the
   event flag, the guard flag and the limit-lock diagnostic; cost in capital units = |trade| x cents / 100
   (book.py:297-304, 346-349); roll legs trade -n then +n (332-337). Stress = D8 + 1 vehicle tick per side,
   slip150 = 1.5 x slippage (base_rules.costs). Rebalance, close-out, entry and exit dates avoid guard windows by
   eligibility (signals.py:95).
6. Series and statistics (check 5). T1/T2 series dates = every mark date of any root from the first fill to
   2024-02-29, T3 = every NQ/RTY mark date from the first entry, zero when flat (book.py:357-389). unit_stats: t =
   mean / (sd / sqrt n), NW Bartlett weights 1 - lag/(lags+1), p = max(Student one-sided, normal one-sided).
   holm: ascending, reject while p <= alpha/(m - i), stop at the first failure, an undefined p never rejected.
   Sharpe = mean / sd x sqrt(252). Bootstrap: ceil(n/21) block starts uniform on 0..n-1, each block wraps modulo n,
   concatenated and cut to n (circular moving block), 10,000 draws in fixed order, default_rng(20261014) fresh per
   test, percentiles 2.5/97.5 with sd-0 draws dropped and counted. PASS iff Holm rejects AND base Sharpe >= 0.3
   (stats.py:179-191). Reported cases, per year, per root, DSR at the registry's N, fills by kind, exclusions.
7. Run discipline (check 6): FR-8. Frozen files: `git status --porcelain base_rules screening data live ops ledger
   REGISTRATION.md` is empty; REGISTRATION.md is 0 bytes; reports/stage_e21_freeze.json, stage_e21_RUN_ONCE.json and
   stage_e21_runs/ do not exist yet. Nothing after 2024-02-29: ctx.last = 2024-02-29 bounds window_dates, marks and
   T3 units; stores are the E.12 training stores loaded by base_rules.store with its holdout/embargo refusals
   (reused, not re-audited here).
8. Tests (check 7): 57 passed in 10.3 s (`nice -n 10 uv run python -m pytest -q -p no:cacheprovider
   tests/test_multiday_*.py`). Claims covered: a planted future bar and changed later prices move no position, sigma,
   lookback, S_M or S_u up to the fill date (test_multiday_lookahead.py:58-131); each roll leg pays |n| x the
   per-contract cost with the right sides (book.py tests:41-59); chaining across a splice and across the boundary,
   contract change undefined; d*, blackout moves, the six-date limit, close-out after month end, February 2024
   close, April 2019 flat and May 2019 reopening, references, TOM days across month/year ends and holidays, day -2
   straddling a closure, NYSE closures by rule on the real equity calendar; EWMA; Holm; bootstrap determinism; T4 =
   h5.combine; pre-marker refusals and the second run refused. Claims with no test: FR-1 (forced close), FR-2
   (missing roll bar exclusions), the R-B2 uncalibrated count, the limit-lock diagnostic count, and
   `assemble`'s "series dates added" branch (none expected).
9. NYSE closures (A12), independent spot check of signals.nyse_closures for 2010-2024: 9/8/11/9/9/9/9/9/10/9/9/9/
   9/10/10 closures per year; Jan 1 on a Saturday gives no closure (2011, 2022); observed July 4 (2015 and 2020:
   Jul 3; 2010 and 2021: Jul 5); observed Christmas (2010, 2021: Dec 24; 2011, 2016, 2022: Dec 26); Sandy 2012-10-29/
   30; 2018-12-05; Juneteenth from 2022 (2022-06-20, 2023-06-19, 2024-06-19). All agree with the exchange's history.
10. H2 input: reports/stage_e17_runs/H2_result.json sha256 a661cebc2ac04186... matches the pin; status complete,
    test H2; component cases base/stress/slip150 with 280 dates each (2016-06-24..2024-01-31); grid_dates 280;
    H2's unit series has 56 units. H5's E.17 result consumed the same component on a 3460-date grid.

## Not checked (time box 35 min)

- No real bar read (by design): the real-data behaviour of the eligibility scans, the number of "missing bar"
  moves (FR-3), runtime and memory of `evaluate` on 17 roots.
- base_rules.store's refusals (holdout, embargo, research, MES, sealed) and base_rules.guards.check_registry_path:
  reused from E.16/E.17 and not re-audited.
- multiday/counts.py beyond metadata_blackout (the calendar-only estimate's internals) and the CalendarOracle versus
  BarOracle consistency.
- freeze_manifest.verify's handling of input overrides in the test mode, line by line.
- The limit-lock diagnostic's arithmetic (counted only, never moves a fill).

## Recheck of the applied fixes (FreezeReviewer-FableXHigh, 04:07-04:12 PDT; lead_spec section B)

Scope: multiday/book.py simulate_book and _run (lines 280-371), multiday/evaluate.py _return_counts (100-111, calls at
139 and 148), multiday/freeze_manifest.py pinned_files (57) and verify (116), tests/test_multiday_eraend.py (4 tests),
multiday/README.md "Freeze review fixes", multiday_build.md last section. Tests: 61 passed in 13.6 s
(`nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_multiday_*.py`); the 4 new tests are the
difference from 57.

### Verdict: APPROVE

What was verified:
- FR-1 (a) test_the_forced_close_at_each_era_end: with bar S absent on the last six dates of April 2019 and February
  2024, d* is None for both months, first_eligible_after returns None (the next window date is in no era, or there is
  none), the explicit "forced close (era end)" order lands on the era's last mark (apr[-7], feb[-7]), the fill sells
  the held n, pays |n| x the per-contract sell cost, the backstop counter stays 0 and the book ends flat. The asserted
  dates come from the fixture, not from the code under test. Meaningful.
- FR-1 (b) backstop (book.py:283-304, 341-342, 367-370): an interval failing "store boundary" with n != 0 returns
  ("backstop", marks[k-1].day), a position left after the last mark returns ("backstop", marks[-1].day); a target-0
  BACKSTOP order is merged on that date (the later order wins the merge, so the target is 0 even on a date with a
  rebalance) and the book is rerun. Termination: the merged order sets n = 0 before the failing interval (the order at
  mark k-1 is applied at the bottom of iteration k-1, the interval at the top of iteration k), so the same backstop
  cannot recur; hold exclusions zero the opener and cannot recur either. Fill-cost availability: both backstop dates
  are era-last marks, which process_root puts in `wanted` (book.py:111-120), so rd.fills has them; the test confirms
  this by adding fills only for the three non-wanted order dates and none for apr[-7]/feb[-7]. No new look-ahead:
  the close is at a fixed-date era end or the window end using that mark's own price, like every other close.
- Hold exclusions keyed by order date (book.py:290, 304, 358): equivalent to the index key because _merge makes dates
  unique, and stable when a BACKSTOP order is inserted and the list re-merged. The store-boundary crossing is now
  force-closed rather than excluded, as lead_spec B (FR-1) rules; consistent with Q4 and R-B3.
- FR-2 tests: "missing roll bar" (a splice at the 15:15 closure instant of an R-B1 mark, no new-contract bar inside
  the interval) and "missing roll bar (fill guard)" (every candidate roll_out bar guarded, the move stops at the mark
  bar since lo < i is required): intervals[k].fail asserted directly, then the opener's target 0, exactly one
  exclusion, the next order reopening with fills (+0.5, -0.5) only, per_contract_daily() None on the interval's end
  date. Meaningful.
- FR-6: _return_counts copies the per-root "return undefined: ..." counters into each test's exclusions (total and
  per root) before the books are built; no number changes.
- FR-7: pinned_files() = [multiday/README.md, screening/trial_registry.py] is in manifest_body and in verify's
  unlisted check; tests/test_multiday_run.py:191 asserts both are listed.
- No new raise after the marker: the only new raise ("a position with no mark at all") needs an order with no marks,
  which _run already refuses at line 326-328; everything else that used to raise now returns a backstop.

### New finding

| Id | Severity | File:line | Concrete failure scenario | Proposed fix |
|---|---|---|---|---|
| FR-9 | NOTE | multiday/book.py:341-342 with 111-120 (wanted) and 364 (rd.fills[o.day]) | The backstop date marks[k-1].day is assumed to be an era-last mark. It is, unless a mark falls on 2019-05-01..05-05 (era_of None, so not in era_last): then rd.fills has no entry for it and line 364 raises KeyError after the marker (STOPPED). base_rules.store refuses a date present in both stores and any date after 2024-02-29, but I found no explicit refusal of a step 2 row before 2019-05-06 (the step 2 file name encodes 2019-05-06 as its first date; E.17's H2/H3 relied on the same boundary constants). Practically unreachable; theoretically a STOP path. | Either add the mark on each side of an era change to `wanted` in process_root (one line: `wanted |= {marks[k-1].day for k in range(1, len(marks)) if era_of(marks[k-1].day) != era_of(marks[k].day)}`), or treat era_of(None) marks as a load refusal. Lead's call; not needed for registration if the store loader's date bounds are relied on as in E.17. |
