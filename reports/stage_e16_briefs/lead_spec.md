# Stage E.16: the lead's operational spec for H1 to H5 (2026-10-09 00:12 PDT, before any spawn)

This file turns the prompt's hypothesis text (docs/prompts/STAGE_E.16.md, "THE FIVE HYPOTHESES")
into code-level definitions. Every item restates the prompt, applies a user ruling of 2026-10-09
(section U), or tightens the prompt; nothing loosens it except where a user ruling says so. Items
marked [LEAD] are the lead's choices and go into the return's Open choices. Task 4's
pre-registrations restate this spec with Task 1's table, Task 2's relations and the power table.
Its sha256 goes into reports/stage_e16_STATE.md.

## U. User-side rulings, 2026-10-09 (relayed from the planning chat after the lead's three points)

- U1 Harness for E.17: not cap-only for the whole stage. E.17 does C1 first under a harness whose
  only diff from v10 is the acct-2 cap and the session caps (C1 freeze section 11), completes C1's
  evaluation, and only then writes a further harness that adds the purchase plan (and the hist
  store and calendar support) for the remaining 21 extension roots.
- U2 Windows: each product's window starts at the first priced month after its last unpriced gap
  before 2019-05 in reports/stage_e12_quotes_ext2010.json, plus warm-up; every product's start is
  recorded in the freeze before any bar exists.
- U3a Costs: the BASE case is the frozen D8 cost with NO extra tick (D8 is a measured round trip).
  D8 plus one extra tick per side is the STRESS case, reported for every test and a must-survive
  condition for any later holdout-2 registration. (The prompt's 1.5 x slippage case is reported
  as well.)
- U3b H2 year stability: years with at least 6 monthly units qualify for H2; 10 units for the
  other tests.

## 0. Clock and prices (all tests)

- Bars are one-minute bars labelled by their open minute (UTC ns; CT for every clock time below,
  America/Chicago, DST-aware). The frozen engine's clock (screening/stage_e_engine.py): a bar
  reaches the decision maker at its close (open + 60 s); an order fills at the open of a LATER bar
  of its own leg.
- S_p: the CT minute at which product p's daily settlement window ENDS (for example 15:00 for
  equity index: the window 14:59:30-15:00:00). Per date from Task 1's table
  reports/stage_e16_settlement.json (periods tile 2010-06-07..2024-02-29).
- O_p: the product's day-session open minute (CT) per date, from the same table (Task 1 tabulates
  it from the frozen group calendars' SessionSpec.day_session_ct, and from Task 3b's livestock
  calendar for LE and HE 2010-2019).
- bar(p, d, m): the bar of product p, trade date d, opening at CT minute m on the CT clock of the
  session that trade date d books. A REQUIRED bar that is absent excludes the unit, counted under
  "missing bar". [LEAD] No forward fill and no next-bar substitution anywhere.
- Settlement price used in a signal: PS(p, d) = close of bar(p, d, S_p - 1 min), the last price at
  S_p. [LEAD] A signal never uses the open of the bar it fills on.
- Fills at "the settlement minute": the open of bar(p, d, S_p). Daily marks (H2, H3, H5) use the
  same price: MK(p, d) = open of bar(p, d, S_p).

## 1. Costs (all tests; U3a)

- Base case: each fill (entry, exit, roll leg) of one vehicle contract pays, per side, the frozen D8
  one-side cost at size one: commission per side plus the bucket slippage s_b of the fill minute's
  30-minute CT bucket, with D8's event-window rule (a fill in [release, release + 30 min) of a
  release that concerns the product pays the product's largest s_b). Money in exact cents as the
  engine (slippage ceil to the cent, Fraction tick values). The single-day base-case fill and cost
  match the frozen engine's (screening/stage_e_engine.py with StageERules) fill for fill.
- Stress case (U3a): base plus one extra tick of the vehicle per side on every fill. Reported for
  every test; must-survive for any later holdout-2 registration; not part of this stage's pass bar.
- 1.5 x slippage case (prompt): s_b x 1.5, commission unchanged. Reported for every test.
- Release calendars [LEAD]: the event-window rule and the D9.5a fill guard ([release, release +
  2 min): no fill there; the unit is excluded, counted "fill guard") use the frozen release calendar
  (reports/stage_e2b_release_calendar.json) from 2019-05-06, and for 2010-2019 the release rows
  that exist (E.14's FOMC 2010-2019 table, C1's NG release table where it applies, Task 3b's EC-AUC
  2010-2019). The build reports, from the 2019-05..2024-02 frozen calendar alone, which release types
  ever touch an H fill minute; for any such type with no 2010-2019 rows, every 2010-2019 fill whose
  CT minute lies in [t, t + 30 min) for any clock time t that type uses in 2019-2024 pays the
  largest s_b, and no 2010-2019 fill lies in [t, t + 2 min) (conservative).
- Price path and vehicle per E.12 (D2): P&L = price-path ticks x the vehicle's tick value (MNQ for
  NQ, MYM for YM, M2K for RTY, MCL for CL, MGC for GC, MHG for HG; the full-size contract
  elsewhere); costs are the vehicle's.

## 2. Exclusions and references (all tests)

- Trade dates: the product's group calendar (2019-05-06 on: data/calendars/<group>.py; 2010-2019:
  data/calendars/hist2010/<group>.json; livestock 2010-2019: Task 3b's file). Excluded as action
  dates (entry, exit, H1/H4 trade dates), each counted by reason: roll-blackout dates (the splice
  date and the two group trade dates before it, from the store's roll metadata, as data.stage_e_bars
  L-8), every EARLY_HALT or halt date of the group calendar whatever its halt minute, unsourced
  calendar dates (hist calendars), dates outside the product's window, and missing required bars.
- "Prior eligible date" for a REFERENCE price (H1's prior settlement, H4's prior window move)
  [LEAD]: the immediately preceding trade date d-1 of the product's group calendar. It may be a
  roll-blackout date (a reference, not a trade); it must have its required bars and must not be an
  early-close or halt date or an unsourced date. Otherwise d gets no signal (counted "no
  reference"); this includes d-1 outside both stores (2019-05-01..05-03). The reference bar and d's
  bars must be the same contract (raw symbol); if not, excluded (counted "contract change"; by the
  blackout rule this cannot happen on a tradeable d, and the code asserts it).
- Rolls inside a multi-day hold (H2, H3) [LEAD]: the stores are spliced front-contract paths. A
  position held across its leg's splice instant is rolled: closed at the open of the last bar before
  the splice (old contract) and reopened at the open of the first bar at or after the splice (new
  contract), each a fill paying section 1's cost. The splice instants are store metadata known in
  advance, so both fills follow the engine's clock. A unit whose ENTRY or EXIT date is excluded is
  excluded; a roll alone does not exclude it.
- Multi-day returns used in a SIGNAL (H2's month-to-date returns) chain across splices: the product
  of same-contract segment returns, split at each splice (the old segment ends at the close of the
  last bar before the splice; the new one starts at the open of the first bar at or after it).
- Store boundary [LEAD]: the ext2010 stores end 2019-04-30, the E.12 stores begin 2019-05-06;
  2019-05-01..05-03 are in neither. A trade date present in both stores is refused (no double
  count). A multi-day unit whose holding period (entry fill to exit fill) spans the boundary is
  excluded, counted "store boundary". References across the boundary follow the rule above.
- Window per product (U2), from reports/stage_e12_quotes_ext2010.json, start = the first trade date
  of the first priced month after the product's last unpriced gap before 2019-05: 24 products
  2010-07-01 (2010-01..2010-06 unpriced); RTY 2017-06-01; TN 2016-01-04 (2012-06..2015-12
  unpriced); HE 2017-07-03 (2017-06 unpriced). [LEAD, R-S4] No unit of any test on a date before the
  product's sourced listing, where the settlement table's minute is null: RTY from 2017-07-10, TN from
  2016-01-11. Then the warm-up (section 3). End 2024-02-29. The
  per-product fallback (2019-05-06..2024-02-29) is recorded at E.17's registration, per the prompt.
- No market-data byte is read in Stage E.16. Runners take store paths and sha256s from a manifest
  E.17 writes; they refuse holdout-2, the embargo, the research store, MES's stores, any trade date
  after 2024-02-29 and any path under data/sealed.

## 3. Risk scaling (all tests) [LEAD]

- Per test and per product (per leg for H2; per tenor for H3): the hypothetical per-trade GROSS P&L
  series g in dollars per vehicle contract, signed by the rule's direction, one value per unit the
  rule would trade (zero-signal units have no value). sigma for a unit = sample std (ddof 1) of the
  last 20 values of g strictly before the unit's entry date. The first 20 eligible units of each
  product are warm-up: computed for g, never traded or counted. A unit with sigma 0 or undefined is
  not traded (counted).
- The unit's net P&L in risk units: (gross dollars - cost dollars) / sigma, one contract notional.
  For H2 the pair's unit P&L is the sum of the two legs' risk-unit P&Ls (volatility matched). For
  H3 the unit is the two legs combined (one sigma per tenor, from the combined g).

## 4. Tests

H1 (settlement-window momentum, pooled; intraday). Product p, trade date d (eligible; S_p's
lead_grade "secondary" or better on d; S_p - 30 > O_p). Signal s = sign(close of bar(p,d,S_p-31) -
PS(p,d-1)). s = 0: no trade (counted). Entry: open of bar(p,d,S_p-30), direction s. Exit: open of
bar(p,d,S_p). Required bars: bar(p,d-1,S_p-1), bar(p,d,S_p-31), bar(p,d,S_p-30), bar(p,d,S_p). Unit:
the date d; value: the equal-weight mean, over products traded on d, of their risk-unit net P&L.
[LEAD] If S_p > 15:08 CT on some product-date, the trade still follows S_p (the hypothesis is about
the settlement window); the count of such product-dates is reported and the lead rules on it at the
freeze once Task 1's table exists.

H2 (month-end NQ/ZN rebalancing pair; multi-day; IBKR). Trading days: the dates that are trade
dates of BOTH the equity and the rates group calendars. d5 = the month's fifth-last such day; dL =
its last. Signal [LEAD]: the decision minute on d5 is max(S_NQ(d5), S_ZN(d5)), NQ's S (15:15 CT before
2020-10-26, 15:00 CT from then; ZN's settlement at 14:00 is known by then). MTD_X = chained return (section 2)
from PS(X, last trading day of the prior month) to PS(X, d5), X in {NQ, ZN}. If MTD_NQ > MTD_ZN:
short NQ, long ZN; else long NQ, short ZN (the prompt's else branch, ties included). Entries: both
legs at the open of their bar at the decision minute on d5 (ZN's leg enters one or one and a quarter
hours after its own settlement, the first fill the decision allows). Exits: each leg at the open of bar(X, dL, S_X). Daily marks
MK(X, d) for H5. Required: both legs' signal and fill bars; d5 and dL not excluded for either leg.
Unit: the month (dated dL). Vehicles: MNQ and ZN. Year stability: years with >= 6 units (U3b).

H3 (Treasury auction cycle; multi-day; IBKR). Auctions: Task 3b's EC-AUC 2010-2019 and the frozen
EC-AUC rows from 2019-05, filtered as E.0 (security_type Note or Bond, floating_rate No,
inflation_index_security No, announcemt_date strictly before auction_date), tenor from
original_security_term: 2-Year ZT, 5-Year ZF, 10-Year ZN, 30-Year ZB (others ignored). t = auction
date (a rates trade date, else skipped, counted). [REVIEW F-04] Also announcemt_date on or before t-3
(Treasury announces at 11:00 ET, before the 14:00 CT entry); else excluded, counted "announced after
entry"; an auction with no announcement date on file is excluded, counted "no announcement date". Short at the open of bar(T, t-3, S_T); at the open
of bar(T, t, S_T) cover and go long (two sides); exit at the open of bar(T, t+5, S_T); t-3 and t+5
in rates-group trade dates. Same-tenor windows [t-3, t+5] that overlap: keep the earlier, drop the
later, counted. A unit whose t+5 is after 2024-02-29 is excluded (counted "window end"). Unit: the
auction (dated t).

H4 (next-day reversal; intraday; both venues). Product p, trade date d (eligible). m = open of
bar(p,d-1,S_p) - open of bar(p,d-1,S_p-30) (H1's gross window move on d-1, d-1 per section 2).
m = 0: no trade. Direction -sign(m). Entry: open of bar(p,d,O_p+1); exit: open of
bar(p,d,S_p-31). Required: bar(p,d-1,S_p-30), bar(p,d-1,S_p), bar(p,d,O_p+1), bar(p,d,S_p-31). Unit
and value as H1.

H5 (combination; daily). Components x_1..x_4: H1's and H4's daily pooled net series (0 on grid
dates with no trade); H2's and H3's daily mark-to-settlement net series in risk units (entry-date
value = MK - entry fill - entry cost, which is minus the entry cost for a settlement-minute entry;
the daily change of MK while open; exit-date value = exit fill - prior MK - exit cost; roll fills on
their date; 0 when flat; a missing MK carries the P&L to the next mark). Grid [LEAD]: the union of
the trade dates on which any component is defined (any product's H1 or H4 eligible date, any open
H2 or H3 date). sigma_i,d = sample std (ddof 1) of x_i over the 60 grid dates strictly before d.
H5_d = mean over the components with a defined, positive sigma_i,d of x_i,d / sigma_i,d. The first
60 grid dates are warm-up. Unit: the grid date. Each cost case (base, stress, 1.5 x) builds its own
H5 from that case's component series.

## 5. Statistics and pass bar (fixed by the prompt and U3; [LEAD] items tighten)

- Per test: n units, mean net, sd, t = mean / (sd / sqrt n). [LEAD] The one-sided p is the larger
  of the plain-t p (Student t, n - 1 df) and the Newey-West p (normal), NW lags fixed now: H1, H4,
  H5 5 units; H2 1 unit; H3 3 units (same-week auctions of different tenors overlap in time).
- Holm at family-wise 0.05 across the registered tests (five unless Task 2 drops one before
  registration), on the base case. Pass: Holm rejects, mean > 0, n >= 30, year stability.
- Year stability: net P&L positive in at least two thirds of the calendar years (unit date's year)
  that hold at least 10 units (H2: 6 units, U3b). [LEAD] Fewer than 3 such years: the criterion
  FAILS (not vacuous).
- Reported, never part of this stage's bar: the stress case (U3a; must-survive later), the 1.5 x
  slippage case, DSR at the program's N read from ledger/trial_registrations.jsonl at run time
  (expected 478 if C1 registers first), exclusions by reason, per-product and per-year tables.
- Power (Task 3 computes, the freeze states): at the priors' low and high net Sharpe per test, for
  the full window and for the fallback window, the probability of passing every bar (Holm at
  0.05/5 = 0.01 and at 0.05, both shown; n >= 30; year stability with the expected units per year
  from the calendars and the expected exclusion rates), by simulation, with the analytic t-test
  power beside it.

## 6. Run discipline (E.17)

A run-once marker per test written before any bar is read; a second run refused. The runner checks
the test is registered (screening.trial_registry) and every input sha256 against this stage's
freeze manifest before reading a bar. One run per test, under the freeze, after E.17's
registration.
