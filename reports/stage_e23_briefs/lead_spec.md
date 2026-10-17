# Stage E.23: the lead's operational spec for the trigger-hold books (DRAFT 2026-10-17 02:21 PDT; frozen with the prereg before any outcome read)

This file turns docs/prompts/STAGE_E.23.md P2.1 to P2.6 into code-level definitions for the package `trigger_hold/`.
Items marked [LEAD] are the lead's choices and go into the return's Open choices. Where this file and the prompt differ,
the prompt governs. Nothing here is chosen from data. Section numbers are cited by the code.

## 0. Inputs and reuse (pinned by sha256 in the E.23 freeze manifest)
- Roots: the 17 roots of E.21 (multiday/constants.py ROOTS). Stores, sha256s and loading exactly as E.21 section 0
  (reports/stage_e21_briefs/lead_spec.md): reports/stage_e17_run_manifest.json, base_rules.store.load_product (both eras),
  preflight before any marker, every base_rules refusal. Calendars, the settlement table S_i(d), windows (E.16 windows plus
  E.21's R-S3/R-S4), release rules, quotes record: as E.21 section 0.
- Marks, daily returns, volatility, rolls, costs, guards, daily attribution and series assembly: E.21 sections 1, 2, 7 and 8,
  through the frozen E.21 code (multiday.book.process_root, RootData, Order, simulate_book, multiday.daily.*). trigger_hold
  imports these and never edits multiday/, base_rules/, screening/, data/, rules/, sim/, strategy/ or any frozen file.
- Vehicles and costs: base_rules.costs.vehicle_cost(root) (MNQ for NQ, M2K for RTY, MCL for CL, MGC for GC; full-size
  elsewhere), VehicleCost.fill_costs, ReleaseRules.event; cases: base = D8; stress = D8 commission + 2 x the D8 one-side
  slippage (the prompt's stress case; computed from the same components as base, never a new calibration).
- Trend regressors: the per-root E.21 T1 (TSMOM-12) and T2 (1/3/12 blend) base daily net values v_T1(i,d), v_T2(i,d)
  (capital units), recomputed by the frozen E.21 code because reports/stage_e21_runs/per_root stores holdings and fills,
  not per-root daily series [state this in the return]. Check: for every date, sum over roots of v_T1(i,d) equals the
  T1_result.json base series value (|diff| <= 1e-12, all 3,205 dates), and the same for T2. Written once to
  reports/stage_e23_trend_per_root/<root>.json with that check's result.
- Nothing dated 2024-03-01 or later is read; the research window, holdout-2, the March 2024 embargo, MES's sealed stores
  and data/sealed are never opened (base_rules refusals stay on).

## 1. Windows [LEAD; see the prereg for the reasoning]
- W_ext (17 roots with ext2010/ext2010h stores): book dates d with max(2011-07-27, the root's E.21 first mark date) <= d
  <= 2019-04-30. 2011-07-27 is the first date of the E.21 T1/T2 series. A regressor value absent on a book date (the
  root's T1/T2 book had no position yet: for ZF, ZN, ZB and NQ the first per-root values are dated 2011-07-29) is zero,
  E.21's own zero-when-flat convention (amended 03:25 PDT on review R-02).
- W_cf: book dates d with max(2019-05-06, the trigger's declared S_X where one exists) <= d <= 2024-02-29.
- A unit belongs to the window holding both its entry and exit mark dates; a unit spanning the store boundary or a window
  edge is excluded (counted by reason). Book series dates: the root's mark dates inside the window from the book's first
  unit entry mark date on (amended 02:36 PDT: a book does not exist before its first unit); zero when flat.
- Events are extracted from 2011-06-01 (W_ext) so that units entering on or after 2011-07-27 are complete; a unit with
  entry before the window start is excluded (counted).

## 2. Triggers to units
- A trigger event e = (trade date d0, decision timestamp tau, side s in {+1, -1}): the frozen member's entry event, from
  the trigger extraction (trigger_hold/events, section 6). Only the event is used: never the member's fill price, exit or
  P&L.
- Entry mark date d_e [LEAD]: d0 if tau is strictly before the open of the settlement bar S_i(d0) (MK's fill point, E.21
  section 1); otherwise the next mark date of root i. A missing or unusable MK on d_e (E.21 T3's entry rules: missing
  mark, early halt, guard window) excludes the unit (counted by reason).
- Unit direction u = s x m, with m = +1 (the multi-day position takes the member's side) or -1 (the opposite side),
  fixed per trigger in the freeze from the mechanism memo (P1.2), never from data.
- Exit mark date d_x: the h-th mark date of root i after d_e (h in {5, 20}); P&L runs from MK(d_e) to MK(d_x). A missing
  MK carries P&L to the next mark exactly as E.21 does.

## 3. Position, sizing and fills
- net(i,d) = clip(sum of u over units active on (d_e, d_x], -1, +1); the book changes position only on a mark date where
  net changes value (0 -> +-1 opens, +-1 -> 0 closes, +-1 -> -+1 flips). A new unit that leaves net unchanged trades
  nothing (it may extend the holding). [LEAD]
- Size when net opens or flips on date d: n = net x 0.40 / (sigma(i,d) x notional(i,d)) contracts per unit capital, the
  E.21 T1 per-root formula with signal = net and no divisor; sigma per E.21 section 2 (EWMA com 60, returns strictly
  before d; undefined or zero sigma: the opening is skipped and counted). n is held unchanged until net changes again.
- Fills at MK of the change date; rolls, roll fill guards, limit-lock diagnostics, event-window costs and per-side costs
  for each case exactly as E.21 section 7 (through simulate_book).
- Daily values v(i,d) per case exactly as E.21 section 8 (gross and costs kept separately).

## 4. Statistics per trigger-hold, per window, per case (base, stress)
- y = the book's daily net values on its series dates; n, mean, sd (ddof 1); net Sharpe = mean / sd x sqrt(252).
- Raw: t = mean / (sd / sqrt n) and the Newey-West t (Bartlett, lags h; base_rules.stats.newey_west_se).
- Alpha: OLS y_d = a + b1 v_T1(i,d) + b2 v_T2(i,d) + e_d over the same dates. Alpha t_NW = a / se_HAC(a), the HAC
  (Bartlett, lags h, the same kernel as newey_west_se) sandwich standard error; plain OLS t beside it.
  p_alpha = max(one-sided Student p of the plain t with n - 3 df, one-sided normal p of t_NW). Reported: a, b1, b2,
  R^2, the correlations of y with each regressor.
- Also: units entered, units excluded by reason, non-overlapping events (section 5), gross, costs, costs as a share of
  gross, fills by kind, per year (n, mean, Sharpe).
- DESCRIPTIVE only, never part of a bar (amended 02:36 PDT): alpha3 = the same OLS with a third regressor, the root's own
  long buy-and-hold daily value (the guard against a mostly-long calendar book counting the root's drift as alpha), and
  the in-market fraction (share of series dates with net != 0).

## 5. Power before any outcome read (P2.3)
- From trigger events and calendars only (no mark price, no forward return): units per window (entry eligibility by mark
  existence and calendar, never by price), non-overlapping events (greedy in entry order: count a unit when its entry
  mark date is on or after the previous counted unit's exit mark date), n_dates (the window's book series dates, section 1)
  and the in-market fraction.
- E[t] = 0.5 x sqrt(n_dates / 252) (true net Sharpe 0.5 on the daily series, the program's convention: E.21 section 3,
  E.22 F1). power_gate = 1 - Phi(2.0 - E[t]) (the per-test hurdle alpha t >= 2.0); power_holm1 = 1 - Phi(max(2.0,
  z_{1 - 0.05/K}) - E[t]) reported beside it. [LEAD]
- The confirmation gate (section 7) uses the hurdle b = max(2.0, z_{1 - 0.05/S}); power_gate above is its S = 1 value
  (amended 03:25 PDT on review R-03).
- A trigger-hold with fewer than 30 non-overlapping events in a window, or power_gate < 0.2, is "inconclusive by design"
  for that window and is not read there.

## 6. Trigger extraction (trigger_hold/events)
- For each shortlisted trigger and window: run the FROZEN member or rule (unchanged module, imported) on that window's
  minute bars and record only its entry events (d0, tau, s) plus counts by reason (no signal, guard, missing bar, halt).
- Bars: base_rules.store.load_product for W_ext; for W_cf, the same loader, validated against the Stage E harness's own
  run of the member on W_cf (identical entry dates and sides, or every difference explained and accepted by the lead).
- Calendar inputs a member takes as a parameter (e.g. FOMC statement dates) come from the program's sourced tables for
  2010-2019 (reports/stage_e14_cal_releases.json; base_rules auctions), filtered to rows matching the member's frozen
  definition (e.g. a statement at 13:00 CT); rows outside the definition are not trigger dates (counted).
- Output: reports/stage_e23_events/<trigger>__<window>.json (events, counts, input hashes). No price, P&L, mark or
  forward return is written, printed or logged.

## 7. Bars (P2.4)
- Discovery screen: Holm step-down over the K registered trigger-holds (one-sided alpha 0.05 on p_alpha); a survivor
  needs Holm rejection AND alpha t_NW >= 2.0 AND base net Sharpe >= 0.3; at most 4 survivors (the 4 largest alpha t_NW;
  ties by base net Sharpe). Computed by code from the discovery results file.
- Descriptive on discovery: DSR at the new N (base_rules.stats dsr helper, Sharpe variance over the K discovery Sharpes)
  and CSCV PBO over the K registered daily series (8 contiguous blocks).
- Confirmation (once per survivor, only if its power gate on W_cf passes at b = max(2.0, z_{1 - 0.05/S}), S = the number
  of survivors): Holm over the survivors at one-sided 0.05 on p_alpha; then alpha t_NW >= 2.0, base net Sharpe >= 0.3,
  stress net Sharpe > 0, DSR > 0.95 at the new N, CSCV PBO < 0.5 on the discovery window. Verdicts: PASS, NULL,
  INCONCLUSIVE BY DESIGN, UNCONFIRMABLE ON OWNED DATA.

## 8. Run discipline
- Freeze manifest reports/stage_e23_freeze.json (trigger_hold.freeze_manifest build / verify --sha256): every
  trigger_hold/*.py, tests/test_trigger_hold_*.py, this spec, the prereg, the events files, the power table, every input.
- Registration: screening.trial_registry register --test E23 --ids <E23 ids> --freeze reports/stage_e23_freeze.json
  --freeze-sha256 <sha> --harness-sha256 dd2bcc60...; N 533 -> 533 + K.
- `python -m trigger_hold.run evaluate --phase discovery`: verifies the freeze (every file), the registration (label E23,
  the ids, this freeze sha256), the run manifest and every store's preflight (no row read), the output path free; writes
  reports/stage_e23_RUN_ONCE_discovery.json with O_EXCL BEFORE any bar is read; computes; writes
  reports/stage_e23_runs/discovery/. A second run is refused. `--phase confirmation`: the same with
  reports/stage_e23_RUN_ONCE_confirmation.json, requires the discovery results (sha256 recorded in its marker), derives
  the survivors and the power gate by code, and reads nothing for a gated trigger-hold. Exit codes as base_rules (2 refused
  before the marker, 0 complete, 1 stopped after the marker).
- Before the run-once, no code path computes a unit book on real bars inside W_ext or W_cf. Real-bar checks before the
  freeze are limited to: the trend regressor recomputation (E.21's own series), reproducing E.21 T3 with the unit engine
  (T3's units, already read in E.21), and trigger extraction (events only).

## R. Lead rulings on BookCoder's questions (2026-10-17 02:43 PDT, before any outcome read)
Source: reports/stage_e23_briefs/bookcoder_report.md "Questions for the lead". All thirteen conservative choices are
accepted as written there; the ones that change behaviour:
- R1. Exit eligibility: the exit date d_x must be an eligible action date (E.21 T3's exit rule), else the unit is excluded
  and counted ("excluded: exit: <why>"). Exclusions come from calendars and bar existence only, never from a price.
- R2. Entry eligibility is multiday.signals.action_why in full (action exclusions incl. roll blackout, early halt,
  unsourced; listed; MK and PS present; MK outside guard windows). Treasury roll blackouts sit at quarter month-ends, so
  K2-monthend-01 loses about a third of its units (calendar fact from the synthetic-event dry run; the harness's roll
  blackout also stops the member itself on those dates).
- R3. Stress per side = commission + 2 x (base - commission).
- R6. Discovery runs on a context ending 2019-04-30 (no W_cf mark, sigma or path is computed in discovery).
- R7. A trigger date without a settlement minute: entry at the next mark date, never earlier than the event.
- R8. Holm's m counts every registered trigger-hold.
- R9. alpha3 uses the per-contract dollar move over the notional at the interval's opening mark (costs excluded).
- R11. Survivor ties after alpha t and Sharpe: id ascending.
- R12. A store-refused root in confirmation is UNCONFIRMABLE ON OWNED DATA.
- s_x: null for every row (W_cf from 2019-05-06): K2's confirmation never ran, so no trigger S_X was declared (no K2
  start-rule file exists); E.12's ML-panel S_X for the ZF path (2020-10-01) is a panel start, not this trigger's S_X. The
  choice only lengthens W_cf, which is power-gated under either start (review R-04).
- Rulings on TriggerCoder's questions (reports/stage_e23_briefs/triggercoder_report.md section 10, 03:10 PDT): all eight
  accepted as written. Trigger ids are the freeze labels ("K2-monthend-01 ZF", "E20H6-T1 NQ") and the registration config
  uses them; an event is an accepted entry that filled; D9 coverage recorded, nothing dropped (0.982-0.997); D9.7 (MNQ price
  limits) not applied on W_ext (no limit table before 2019-05; it refused no H6 entry on W_cf); H6's lead-in clamp at
  2019-05-06 not applied on W_ext; the hist store's early-halt flags and the month-end table (equal to pattern_search
  backward S6) are used as the harness would.
