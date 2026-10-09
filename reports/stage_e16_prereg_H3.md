# Stage E.16 pre-registration H3: Treasury auction cycle

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json; commit "E.16 base-rule freeze"). NOT
REGISTERED: Stage E.17 registers H1 to H5 together (N + 5) and runs this test once, in the order of
reports/stage_e16_handoff.md. Every definition shared by the five tests (prices and clock, costs, exclusions,
windows, the 2010-2024 splice and fallback rules, risk scaling, statistics, the pass bar, run discipline, the user
rulings U1 to U3b of 2026-10-09 and the lead's rulings) is in reports/stage_e16_prereg_common.md, which is part of
this pre-registration. Nothing here may be loosened; the code is base_rules/ as hashed in the freeze manifest.

## 1. The hypothesis as the stage prompt fixes it (docs/prompts/STAGE_E.16.md lines 100-109, verbatim)

```
H3, Treasury auction cycle (Lou, Yan and Zhang). Tenor map: 2-year to
ZT, 5-year to ZF, 10-year to ZN, 30-year to ZB, from the frozen EC-AUC
calendar (FiscalData, announcement strictly before the auction). For each
auction: short the tenor's contract at the settlement minute three
trading days before the auction date, cover at the auction date's
settlement minute, and go long at that same minute, exiting at the
settlement minute five trading days after the auction date. Multi-day:
IBKR venue only. Test statistic: per-auction net P&L of the two legs
combined. Auctions whose windows overlap the same tenor's next auction
keep the earlier and drop the later, counted.
```

## 2. The operational definition (reports/stage_e16_briefs/lead_spec.md lines 142-152, verbatim)

```
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
```

## 3. Fixed parameters of this test

- Products and vehicles: ZT (2-Year), ZF (5-Year), ZN (10-Year), ZB (30-Year), windows from 2010-07-01.
- Venue: multi-day; IBKR only.
- Unit of the test statistic: auction (dated by its auction date t).
- Cost cases: base (frozen D8, size one; decides the pass, U3a); stress (base plus one tick per side; reported;
  must-survive at any later holdout-2 registration, U3a); 1.5 x slippage (reported).
- One-sided p: the larger of the plain-t p (Student t, n - 1 df) and the Newey-West p with 3 lag(s).
- Year stability: net P&L positive in at least two thirds of the calendar years holding at least
  10 units; fewer than 3 such years fails.
- Pass: Holm rejection at family-wise 0.05 across the registered tests, net mean > 0, n >= 30, year stability.
- Reported beside it: DSR at the program's N at run time, the stress and 1.5 x cases, exclusions by reason,
  per-product and per-year tables.
- Notes: Tightened (review F-04): announcemt_date on or before t-3, else excluded ('announced after entry'; 49 of 420 in 2010-06..2019-04 and 46 of 231 in 2019-05..2024-02, mostly 2-year notes); no date on file, excluded.

## 4. Relation to tested members (reports/stage_e16_overlap.md lines 192-201, verbatim; lead ruling: KEEP)

> H3 trades the same Treasury auctions, filtered as E.0 (Note or Bond, not floating, not inflation-
> indexed, announced before the auction date), and the same short-before / long-after shape as
> K2-aucpre-01 and K2-aucpost-01, which held only the 180 minutes before and after the auction close on
> the auction day (also on TN and UB) and were Tier B on the research window 2025-04..2026-06. H3 holds
> across days: short from the settlement minute three trading days before to the auction day's
> settlement minute, then long to the settlement minute five trading days after. Its source, Lou, Yan
> and Zhang (E.0 log K2-001), was logged at E.0 as supporting evidence; its literal five-day form was
> excluded at E.0 for the flatten (X-03) and never tested. Gate 0 tested only intraday auction-clock
> flags (k2_auction_mto, k2_auction_msince) on 2019-05..2024-02; neither was rejected.


## 5. Power at the priors (reports/stage_e16_power.json; method in the common file)

| Window | Prior | Net Sharpe (annual) | Units (calendar-only) | Qualifying years | P(pass all bars), Holm step 0.01 | at 0.05 | Analytic one-sided t power, 0.01 | at 0.05 |
|---|---|---|---|---|---|---|---|---|
| full | low | 0.3 | 354 | 12 | 0.089 | 0.242 | 0.096 | 0.267 |
| full | high | 0.7 | 354 | 12 | 0.498 | 0.703 | 0.522 | 0.771 |
| fallback | low | 0.3 | 69 | 3 | 0.036 | 0.121 | 0.034 | 0.127 |
| fallback | high | 0.7 | 69 | 3 | 0.116 | 0.303 | 0.122 | 0.319 |
