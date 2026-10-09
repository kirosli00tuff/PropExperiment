# Stage E.16 pre-registration H2: month-end NQ/ZN rebalancing pair

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json; commit "E.16 base-rule freeze"). NOT
REGISTERED: Stage E.17 registers H1 to H5 together (N + 5) and runs this test once, in the order of
reports/stage_e16_handoff.md. Every definition shared by the five tests (prices and clock, costs, exclusions,
windows, the 2010-2024 splice and fallback rules, risk scaling, statistics, the pass bar, run discipline, the user
rulings U1 to U3b of 2026-10-09 and the lead's rulings) is in reports/stage_e16_prereg_common.md, which is part of
this pre-registration. Nothing here may be loosened; the code is base_rules/ as hashed in the freeze manifest.

## 1. The hypothesis as the stage prompt fixes it (docs/prompts/STAGE_E.16.md lines 91-98, verbatim)

```
H2, month-end rebalancing pair (Harvey, Mazzoleni and Melone). Equity leg
NQ (vehicle MNQ), bond leg ZN. On the fifth-last trading day of each
month, at the settlement minute, compute month-to-date returns of NQ and
ZN from the prior month's last settlement. If NQ outperformed ZN: short
NQ and long ZN; else long NQ and short ZN. Legs are volatility-matched by
the risk rule. Exit both legs at the settlement minute of the month's
last trading day. Multi-day: IBKR venue only. Test statistic: per-month
net P&L of the pair.
```

## 2. The operational definition (reports/stage_e16_briefs/lead_spec.md lines 131-140, verbatim)

```
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
```

## 3. Fixed parameters of this test

- Products and vehicles: NQ (vehicle MNQ) and ZN (vehicle ZN), windows from 2010-07-01.
- Venue: multi-day; IBKR only.
- Unit of the test statistic: month (dated by its last joint trading day dL).
- Cost cases: base (frozen D8, size one; decides the pass, U3a); stress (base plus one tick per side; reported;
  must-survive at any later holdout-2 registration, U3a); 1.5 x slippage (reported).
- One-sided p: the larger of the plain-t p (Student t, n - 1 df) and the Newey-West p with 1 lag(s).
- Year stability: net P&L positive in at least two thirds of the calendar years holding at least
  6 units; fewer than 3 such years fails.
- Pass: Holm rejection at family-wise 0.05 across the registered tests, net mean > 0, n >= 30, year stability.
- Reported beside it: DSR at the program's N at run time, the stress and 1.5 x cases, exclusions by reason,
  per-product and per-year tables.
- Notes: Decision minute NQ's S on d5 (15:15 CT before 2020-10-26). Stated departure from the engine (review F-09): before 2020-10-26 NQ's entry is the open of the first bar after the 15:15 closure on the same trade date (R-B1(b)); none (equity before 2012-11-19): excluded, 'no entry bar'; counted 'entry after closure'. Warm-up 20 monthly units per leg (review F-15): no unit before 2016. H2 cannot pass on the fallback window (2 qualifying years).

## 4. Relation to tested members (reports/stage_e16_overlap.md lines 156-166, verbatim; lead ruling: KEEP)

> H2's bond leg overlaps K2-monthend-01, which bought ZN (and ZT, ZF, TN, ZB, UB) in the day sessions
> of the last two trade dates of each month (07:21-15:05 CT, unconditional; Tier B on the research
> window 2025-04..2026-06, ZN t -0.48). H2 differs in four ways: it holds overnight from the
> fifth-last joint trading day to the last day's settlement, it has an NQ leg, its direction comes from
> the NQ-versus-ZN month-to-date return (Harvey, Mazzoleni and Melone's rebalancing flow), and the two
> legs are volatility matched. E.0 excluded the multi-day bond month-end hold (X-04 K2-eom2d-01) for
> the flatten and never tested it. K3-mehedge-01 (Tier B) used month-to-date equity returns to sign a
> month-end FX trade; MES's turn-of-month long (E-H4) was null on 2020-02..2024-02. Gate 0 tested only
> intraday month-end flags (g16_month_end, k2_monthend_msince) on 2019-05..2024-02; neither was
> rejected. No program test read a month-to-date NQ or ZN return or held a position across days.


## 5. Power at the priors (reports/stage_e16_power.json; method in the common file)

| Window | Prior | Net Sharpe (annual) | Units (calendar-only) | Qualifying years | P(pass all bars), Holm step 0.01 | at 0.05 | Analytic one-sided t power, 0.01 | at 0.05 |
|---|---|---|---|---|---|---|---|---|
| full | low | 0.4 | 60 | 8 | 0.105 | 0.258 | 0.112 | 0.301 |
| full | high | 0.9 | 60 | 8 | 0.534 | 0.750 | 0.569 | 0.811 |
| fallback | low | 0.4 | 15 | 2 | 0.000 | 0.000 | 0.034 | 0.131 |
| fallback | high | 0.9 | 15 | 2 | 0.000 | 0.000 | 0.113 | 0.318 |
