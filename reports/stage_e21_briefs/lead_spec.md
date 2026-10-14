# Stage E.21: the lead's operational spec for E21-T1..T4 (2026-10-14; drafted 03:13-03:18 PDT, amended 03:35-04:10 PDT; FROZEN with the prereg, before any bar)

This file turns the prompt's FIXED DESIGN (docs/prompts/STAGE_E.21.md, F1-F8) into code-level
definitions. It restates the prompt, applies reports/stage_e16_briefs/lead_spec.md sections 0-3 and 5
(binding after the prompt), or tightens them. Items marked [LEAD] are the lead's choices and go into the
return's Open choices. Section A at the end records the Step 1 literature amendments (added before the
freeze). The pre-registration (reports/stage_e21_prereg.md) restates this spec and is frozen with it.
Nothing here is chosen from data: no bar of any store has been read in this stage.

## 0. Inputs (all pinned by sha256 in reports/stage_e21_freeze.json)
- Roots (17): NG, NQ, ZN, 6E, GC, ZC (plan ext2010) and ZT, ZF, ZB, UB, TN, CL, ZL, ZS, RTY, HE, LE
  (plan ext2010h). Stores and sha256s: reports/stage_e17_run_manifest.json (the E.17 run manifest; its
  `stores` hold each root's step2 and ext2010 store). Loading: base_rules.store.load_product (the splice
  loader, both eras), preflight before the marker (no row read), every refusal of base_rules.store.
- Calendars, settlement table (S_p per date), windows, release rows, quotes record: the E.16 inputs
  base_rules uses (base_rules.guards.INPUT_ROLES and constants paths), loaded with base_rules' loaders.
- Windows (F1): reports/stage_e16_windows.json (window_start_on_or_after per root; TN 2016-01, RTY
  2017-06, HE 2017-07), R-S4 (no mark before RTY 2017-07-10, TN 2016-01-11, where the settlement table's
  minute is null), and R-S3 for E.21 [LEAD]: LE's 2010-06-07..2014-12-14 span is excluded for every
  test, so LE's first mark date is its first trade date on or after 2014-12-15. End 2024-02-29.
- Vehicles and costs: base_rules.costs.vehicle_cost(root) (E.12 vehicles: MNQ for NQ, M2K for RTY, MCL
  for CL, MGC for GC; full-size elsewhere) and base_rules.costs.build_release_rules (event window and
  fill guard).
- T4's H2 input: reports/stage_e17_runs/H2_result.json (sha256
  a661cebc2ac041866dec16210f6a8983661984d0acc815822a8c5b7908152dff): `component[case]` (date -> daily
  risk-unit value) and `grid_dates`, for case in base, stress, slip150. H2 is not recomputed.
- Nothing dated 2024-03-01 or later is read (base_rules refusals: holdout-2, embargo, research store,
  MES stores, data/sealed, any trade date after 2024-02-29).

## 1. Marks, prices and daily returns (F2)
- MK(i,d) = base_rules.common.settle_point(ctx, bars, i, d): the open of bar(i,d,S_i(d)), or under R-B1
  the close of bar(S_i - 1) when a scheduled closure begins at S_i. PS(i,d) = close of bar(i,d,S_i - 1)
  (the signal price; known at S_i, before MK's fill).
- Mark dates of root i: the trade dates d of root i's group calendar inside root i's window (section 0)
  on which ctx.listed(i,d) holds and MK(i,d) exists. A missing MK is None: the position's P&L carries to
  the next mark (as base_rules.sim does with a None mark).
- Daily return for sigma: r(i,d) = the same-contract chained return from MK(i,d_prev) to MK(i,d), where
  d_prev = the trade date immediately before d on root i's group calendar; r is undefined (skipped by the
  EWMA) when either mark is missing or d_prev and d lie in different store eras. Chaining at each splice
  between the two points exactly as base_rules.h2.chained_return does (the old segment ends at the
  close of the last usable bar before the splice; the new one starts at the open of the first usable
  bar at or after it); the start and end prices are the mark points' prices (open, or close under
  R-B1). A contract change without a recorded splice makes r undefined (counted).
- Lookback returns for signals: R_k(i, d, ref) = base_rules.h2.chained_return(bars, i_PS(ref), i_PS(d))
  (close to close of the two PS bars, split at splices). Store boundary [LEAD]: when the last ext2010
  bar and the first step2 bar carry different contracts and no splice is recorded between them, the
  chain is split there as at a splice (old segment to the close of the last ext2010 bar, new from the
  open of the first step2 bar); when they carry the same contract the chain runs through (a
  same-contract move). Counted: lookbacks split at the boundary.

## 2. Volatility (F3; Moskowitz, Ooi and Pedersen 2012, eq. 1; see section A for the reader check)
- sigma(i,d), annualized: sigma^2 = 261 x sum_k w_k (r_k - rbar)^2 / sum_k w_k, rbar = sum_k w_k r_k /
  sum_k w_k, w_k = (1 - delta) delta^k for the k-th most recent DEFINED daily return of root i dated
  strictly before d, delta / (1 - delta) = 60 (delta = 60/61). Equivalent to pandas
  Series.ewm(com=60, adjust=True).var(bias=True) x 261 on the returns before d.
- Warm-up [LEAD]: sigma(i,d) is defined once at least 60 defined daily returns of root i precede d.
  Undefined or zero sigma: no position (counted).

## 3. Month-end rebalance dates (T1, T2)
- e(i,M) = the last trade date of calendar month M on root i's group calendar.
- Rebalance date d*(i,M) [LEAD]: the latest date among the last 6 trade dates of month M (e(i,M) and up
  to 5 before it) that is an eligible action date of root i: base_rules.common.action_exclusion(ctx,
  bars, i, d) is None (in window, a trade date, not unsourced, not roll blackout, not early halt), MK and
  PS exist, and the MK fill point is not inside a D9.5a fill-guard window (ReleaseRules.guard; release
  times are calendar data, known in advance). If none exists: no rebalance for root i in month M
  (counted "no eligible rebalance date"); its current position is closed at the first eligible action
  date after e(i,M) (counted) and the root is flat until its next rebalance.
- Reference dates for a k-month lookback (k = 1, 3, 12) [LEAD]: ref(i,M,k) = the latest date among the
  last 6 trade dates of month M - k at which PS(i, .) exists and base_rules.common.reference_exclusion
  (ctx, i, d) is None (a roll-blackout date is allowed: a reference, not a trade). None: that lookback is
  undefined (counted).

## 4. Signals and positions
- T1 (TSMOM-12): s(i,M) = sign(R_12(i, d*(i,M), ref(i,M,12))).
- T2 (trend blend): s(i,M) = (sign(R_1) + sign(R_3) + sign(R_12)) / 3, each with its own reference;
  all three must be defined, else no position (counted). sign(0) = 0.
- Weight w(i,M) = s(i,M) x 0.40 / sigma(i, d*(i,M)).
- Divisor S_M [LEAD], calendar-defined (no data, no look-ahead across roots whose rebalance dates
  differ): the number of roots i for which e(i, M - 12) exists inside root i's window (the 12-month
  lookback's month lies in the window). A root counted in S_M whose signal or sigma is undefined holds
  zero (conservative scaling).
- Holding in vehicle contracts per unit of capital: n(i,M) = w(i,M) / (S_M x V(i,M)), V(i,M) = the
  vehicle contract's notional in dollars at the fill price = price ticks of MK(i, d*) x the vehicle's
  tick value in dollars. The holding changes from its current value to n(i,M) at the fill point
  MK(i, d*(i,M)) (one fill of the difference). It is constant between fills (fixed contracts, as a
  monthly-rebalanced book).
- First position: the first month M with a defined signal and sigma (about 12 months after the root's
  window start). Last rebalance [LEAD]: the rebalance of February 2024 sets every target to 0 (the
  following month is outside the window); no position is held after 2024-02-29.

## 5. T3 (turn of the month; NQ and RTY; see section A for the reader check)
- Days on the equity group calendar: day -1 = the last trade date of month M; day -2 = the trade date
  immediately before it (the month's second-to-last trade date); day +3 = the third trade date of month
  M + 1. Holding from MK(day -2) to MK(day +3) holds the returns of days -1, +1, +2 and +3.
- Unit u = (root, month M). Entry fill at MK(i, day -2), exit fill at MK(i, day +3). Both dates must be
  eligible action dates of root i (as section 3, including the fill-guard check), else the unit is
  excluded (counted by reason). Day +3 after 2024-02-29: excluded ("window end"). A hold spanning the
  store boundary: excluded ("store boundary"). Sigma undefined at day -2: excluded ("sigma warm-up").
- Weight w = +0.40 / sigma(i, day -2) (long only; one unit of risk per root: the same annualized 40%
  target as T1, constant over the hold) [LEAD reading of "scaled to the hold"].
- Divisor S_u = the number of roots with an eligible unit in month M (both enter at the same equity
  settlement on day -2; eligibility is calendar data and bar existence). n = w / (S_u x V at the entry
  fill).

## 6. T4 (combined book)
- Components (each cost case separately): T2's daily net series, T3's daily net series, H2's component
  series (section 0). Grid: the union of T2's series dates, T3's series dates and H2's grid_dates; a
  component is 0 on grid dates where it has no value.
- sigma_c(d) = sample std (ddof 1) of component c over the 60 grid dates strictly before d
  (base_rules.scaling.trailing_sigma). T4_d = mean over the components with a defined, positive
  sigma_c(d) of x_c(d) / sigma_c(d). The first 60 grid dates are warm-up; a grid date with no component
  scaled is not in the series (counted). This is base_rules.h5.combine's arithmetic; a test asserts
  equality with combine() on renamed synthetic components.

## 7. Store boundary, rolls and costs (F5)
- Store boundary [LEAD] (lead_spec section 2: a multi-day hold spanning the boundary is excluded): the
  ext2010 stores end 2019-04-30, the step2 stores begin 2019-05-06. T1/T2: the April 2019 rebalance sets
  every target to 0 and the book is flat until the May 2019 rebalance, which reopens it (counted;
  zero-value days). T3: the April/May 2019 unit is excluded.
- Rolls: a nonzero holding at a splice instant is rolled as base_rules.sim does: closed at the open of
  the last usable bar before the splice (old contract) and reopened at the open of the first usable bar
  at or after it (new contract), same contract count. Each roll leg is a fill.
- Every fill (rebalance, entry, exit, each roll leg) pays per side, per vehicle contract, the cost of
  base_rules.costs.VehicleCost.fill_costs(bar open ns, side, event) for each case (base = D8, stress =
  D8 + 1 vehicle tick per side, slip150 = 1.5 x slippage), with event = ReleaseRules.event(root, ts) and
  R-B2 for an uncalibrated bucket (counted). In capital units: |delta n| x cost cents / 100.
- Fill guard on a roll leg [LEAD]: the leg moves to the nearest usable bar of its contract outside every
  guard window (the old leg earlier, the new leg later); counted. (Rebalance, entry and exit dates
  already avoid guard windows by section 3's eligibility.)
- Limit locks [LEAD]: base_rules' limit-lock test is applied to every fill as a COUNTED DIAGNOSTIC only
  (a locked fill is reported, not moved or excluded), because making a rebalance depend on the fill bar's
  own high and low would use that bar's prices. A nonzero count is reported in the return.
- R-B3: no data condition raises during the run; a refused store excludes the root (counted, with the
  reason in the notes); only a code invariant stops the run.

## 8. Daily values and series dates
- Root value on mark date d (capital units, per cost case): v(i,d) = n_held x (same-contract dollar move
  of one vehicle contract from the previous mark to MK(i,d), roll legs included, as base_rules.sim's
  daily attribution) - sum over fills on d of |delta n| x cost / 100. A fill's date is its bar's trade
  date. Gross and cost parts are kept separately.
- Book value: x_d = sum_i v(i,d) (the divisors are inside n).
- Series dates (calendar-defined) [LEAD]: T1 and T2: every date that is a mark date of at least one of
  the 17 roots, from the first rebalance fill date of any root to 2024-02-29; zero when flat. T3: every
  equity-group trade date with an NQ or RTY mark, from the first T3 entry date to 2024-02-29; zero when
  flat. T4: section 6.

## 9. Statistics and pass bar (F6)
- Per test, base case: n dates, mean, sd (ddof 1), t = mean / (sd / sqrt n); p_t = one-sided Student t
  (n - 1 df); Newey-West t with Bartlett lags L (21 for T1, T2, T4; 5 for T3) as
  base_rules.stats.newey_west_se, p_nw one-sided normal; p = max(p_t, p_nw).
- Annualized net Sharpe = mean / sd x sqrt(252). 95% interval: circular moving-block bootstrap, block 21
  dates, 10,000 resamples, a fresh numpy.random.default_rng(20261014) per test [LEAD: fresh per test so
  order does not matter], percentile 2.5 and 97.5 of the resampled annualized Sharpe.
- Holm step-down over the four tests at family alpha 0.025: p ascending; reject while p_(k) <= 0.025 /
  (4 - k + 1); stop at the first failure. PASS iff Holm rejects AND annualized net Sharpe >= 0.3.
- Reported, never part of the bar: the stress and 1.5 x slippage cases (the prompt's stress case is
  1.5 x slippage); per calendar year (n, mean, Sharpe); per root (contribution, own t); gross, costs
  and costs as a share of gross; fills by kind; exclusions by reason; DSR at N = 532 (base_rules.stats
  dsr helper, descriptive); the published comparison (Step 1).

## 10. Descriptive economics (F8; after the verdict; reads result files, never a bar)
- The run writes per root: each rebalance or entry/exit (date, n per unit capital, price ticks, V), the
  per-contract daily dollar P&L series of one vehicle contract held (roll-adjusted), and per-fill costs
  per contract per case, so F8 needs no bar.
- Personal account and PropEd tables per the prompt's F8, computed by a separate step after the verdict
  from these files, reports/stage_e13_trend_carry.md (C2, C3) and reports/stage_e21_proped_rules.json.

## 11. Run discipline
- Freeze manifest reports/stage_e21_freeze.json (multiday.freeze_manifest build / verify --sha256):
  every multiday/*.py, tests/test_multiday_*.py, this spec, the prereg, every input file of section 0
  (sha256, bytes).
- Registration (lead): screening.trial_registry register --test E21 --ids E21-T1 E21-T2 E21-T3 E21-T4
  --freeze reports/stage_e21_freeze.json --freeze-sha256 <sha> --harness-sha256 ece91ae8...; N 528 ->
  532.
- One evaluation command (multiday.run evaluate): checks the freeze (every file), the registration
  (label E21, the four ids, this freeze sha256, the registry is ledger/trial_registrations.jsonl), the run
  manifest and every store's preflight (no row read), the output path free; writes
  reports/stage_e21_RUN_ONCE.json with O_EXCL BEFORE any bar is read; then loads one root at a time,
  computes T1..T4 and the verdict, writes reports/stage_e21_runs/ (per-test result JSON, per-root rows,
  the verdict JSON and a short markdown). A second run is refused. Exit codes as base_rules (2 refused
  before the marker, 0 complete, 1 stopped after the marker).
- A calendar-only command (no bar row read; store metadata via preflight is allowed) reports the
  rebalance dates moved by blackout, the T3 units and exclusions by reason, for the freeze text.

## A. Step 1 literature amendments (lead rulings 2026-10-14 03:35 PDT, before any bar)
Sources: reports/stage_e21_briefs/spec_trend.md (SpecReaderTrend), spec_tom.md (SpecReaderTOM),
spec_post2010.md (SpecReaderPost2010); quotes and pages there. No ruling uses this program's data.
- A1 T1 signal (MOP 2012): MATCH on the sign of the past 12-month excess return, no skip month, a
  one-month hold set at month end, 40%/sigma, the equal-weight average over available instruments. The
  lookback (section 1) is base_rules.h2.chained_return between two PS points: the product of
  same-contract segment ratios split at every recorded splice (h2.py lines 65-72), i.e. MOP p.231's
  compounding of the held contract's daily returns. SpecReaderTrend's "MISMATCH risk" (that the function
  fails on any window spanning a roll) is rejected: it returns None only for a contract change with no
  recorded splice, which makes the lookback undefined and is counted. No change.
- A2 Volatility (MOP eq. 1, p.233): 261 annualization and demeaning by the EWMA mean, returns strictly
  before d: as section 2 (the prompt was silent; the paper governs). MATCH.
- A3 Warm-up: MOP has no minimum-history rule (SILENT). Section 2's 60 defined returns stays [LEAD]:
  T3 has no 12-month lookback and needs a defined sigma; for T1/T2 the 12-month lookback binds first.
- A4 No floor on sigma and no cap on positions or leverage (MOP has none; footnote 8). Explicit.
- A5 Within-month holding: fixed contracts between fills (section 4) reproduce MOP eq. (5)'s monthly
  return w x r_{t,t+1} exactly between rolls; the daily series is its daily attribution. MATCH in effect.
- A6 T2 portfolio-level scaling: HOP 2017 scales the combined book to a 10% ex-ante volatility with a
  covariance of rolling three-year equally weighted monthly returns (HOP-JPM p.3 and endnote 7).
  NOT ADOPTED: a declared deviation [LEAD]. Reasons: (i) the prompt's FIXED DESIGN states T2's position
  formula explicitly and is binding first; (ii) the 36-month joint warm-up would move T2's first month
  from about 2011-07 to about 2013-08 and hold out TN, LE, RTY and HE for three more years, in a test
  already underpowered; (iii) a book-level scaler set at each root's own rebalance date (section 3
  moves dates by roll blackouts) would use other roots' same-month signals before they exist (a
  look-ahead) unless lagged, itself a departure. The scaler changes only the book's time-varying
  leverage, not relative weights; T4 already rescales T2 by its trailing 60-date sd. T2 is MOP's
  equal-weight 40%/sigma aggregation of HOP's three signals. No descriptive variant is run (SCOPE).
- A7 T2 otherwise MATCHES HOP 2017: lookbacks 1, 3 and 12 months, equal weights on the three signals,
  monthly rebalance; the per-position volatility estimator is MOP's (HOP 2013, "Demystifying", eq. 2).
- A8 T3 window: every source uses days -1, +1, +2, +3 (close to close; McConnell and Xu working paper,
  Table 1, PDF p.41). The prompt's parenthetical "(two trade dates before the month's last)" describes
  day -3 and would hold a five-day window; it is corrected: day -2 is the second-to-last trade date of
  the calendar month (one trade date before day -1). Section 5 already implements this. MISMATCH fixed.
- A9 T3 volatility scaling: the papers do not scale positions; 0.40/sigma is the prompt's choice
  (McConnell and Xu: turn-of-month volatility 0.98% vs 1.02% on other days). Noted, no change.
- A10 Published comparison for the return (not part of any verdict): AQR's TSMOM factor, 2010-07..
  2024-02, gross Sharpe 0.389 (t 1.44, 164 months; SpecReaderPost2010's computation from AQR's file);
  SG Trend (net) 0.352 on the same window and 0.237 over 2010-2025 (E.13: 0.24); HOP 2017's 2010-2016
  figures (read from exhibit images, flagged as such). Turn of the month after 2008: mostly decayed in
  cash indexes (spec_tom.md); no peer-reviewed post-2010 index-futures study found (spec_post2010.md).
- A11 PropEd (reports/stage_e21_proped_rules.md): no public page grants automation for any plan (terms
  section 8 "Copy trading and automated strategies may be used only where supported and permitted";
  the FAQ marks "EAs / Bots / Automated" not allowed). F8's PropEd table therefore covers every plan that
  allows overnight holds, each flagged "automation UNCONFIRMED" [LEAD]; this is descriptive only.
- A12 T3 day numbering (lead ruling 03:48 PDT, from the calendar-only counts, before any bar): the
  equity group calendar books US exchange holidays (Memorial Day, Labor Day, July 4, Thanksgiving, MLK
  Day ...) as trade dates with an early halt, while the papers count NYSE trading days. T3's days -2,
  -1, +1, +2, +3 are therefore numbered on the T3 trading days = the equity group calendar's trade dates
  that are not NYSE full-day closures [LEAD; follows the papers]. NYSE closures by rule: New Year's Day
  (Sunday -> Monday; Saturday -> no closure), MLK Day (third Monday of January), Presidents Day (third
  Monday of February), Good Friday (dateutil.easter - 2 days), Memorial Day (last Monday of May),
  Juneteenth (June 19, from 2022; Saturday -> Friday, Sunday -> Monday), Independence Day (July 4;
  Saturday -> Friday, Sunday -> Monday), Labor Day (first Monday of September), Thanksgiving (fourth
  Thursday of November), Christmas (December 25; Saturday -> Friday, Sunday -> Monday); special
  closures 2012-10-29, 2012-10-30 and 2018-12-05. Example: May 2016's day -2 is 2016-05-27 (not
  Memorial Day 2016-05-30); September 2016's day +3 is 2016-09-06 (not Labor Day). The entry and exit
  dates still pass section 3's eligibility (a half-day early halt such as the day after Thanksgiving
  still excludes the unit). The position is held through any futures-only holiday session inside the
  window (its P&L carries to the next mark). T1/T2 month-ends are unchanged (each root's own calendar).

## B. Freeze review rulings (reports/stage_e21_review_freeze.md, APPROVE WITH FIXES; lead 04:03 PDT, before any bar)
- FR-1 (SHOULD FIX) accepted: tests for the forced close at both era ends (2019-04 and 2024-02); the
  end-of-book check becomes non-fatal after the marker (R-B3): a position still held at an era end or
  the window end is force-closed at that era's last available mark, counted "forced close (backstop)".
- FR-2 (SHOULD FIX) accepted: tests for "missing roll bar" and "missing roll bar (fill guard)".
- FR-3 (NOTE): bar EXISTENCE (never price) at later dates moves a rebalance earlier or excludes a T3
  unit, as sections 3 and 5 prescribe; reported per test as a diagnostic, separate from calendar
  reasons (prereg section 2).
- FR-4 (NOTE): T4's trailing-sd scaling over mostly-zero H2 and early-T2 values is H5's frozen method,
  which the prompt prescribes ("as H5 combines"); no change; noted in the return.
- FR-5 (NOTE): capital units vs risk units and the constant 0.40/sigma reading of "scaled to the hold"
  are verdict-invariant (prereg section 2).
- FR-6 (NOTE): returns skipped for a missing previous mark are counted in the exclusions.
- FR-7 (NOTE): multiday/README.md and screening/trial_registry.py are added to the freeze.
- FR-8 (NOTE): the pre-marker order and O_EXCL marker are confirmed; no change.
- Recheck (04:10 PDT): APPROVE. FR-9 (NOTE) accepted as a hardening: the marks on each side of an era
  change are added to the precomputed fill dates, so a backstop close can never lack its fill (no raise
  after the marker).

Status: FROZEN with reports/stage_e21_prereg.md at the "E.21 freeze" commit (2026-10-14), before
registration and before any bar is read.
