# Stage E.16 pre-registration H1: settlement-window intraday momentum, pooled

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json; commit "E.16 base-rule freeze"). NOT
REGISTERED: Stage E.17 registers H1 to H5 together (N + 5) and runs this test once, in the order of
reports/stage_e16_handoff.md. Every definition shared by the five tests (prices and clock, costs, exclusions,
windows, the 2010-2024 splice and fallback rules, risk scaling, statistics, the pass bar, run discipline, the user
rulings U1 to U3b of 2026-10-09 and the lead's rulings) is in reports/stage_e16_prereg_common.md, which is part of
this pre-registration. Nothing here may be loosened; the code is base_rules/ as hashed in the freeze manifest.

## 1. The hypothesis as the stage prompt fixes it (docs/prompts/STAGE_E.16.md lines 83-89, verbatim)

```
H1, settlement-window intraday momentum, pooled. For each product p and
eligible date d: signal = sign of (price at S_p - 30 min on d minus the
settlement-minute price at S_p on the prior eligible date). Enter in the
signal's direction at the open of the bar at S_p - 30 on d; exit at the
open of the bar at S_p on d (both inside Topstep's 15:08 CT flatten).
Zero signal, no trade. Test statistic: the daily pooled net P&L, an
equal-risk average across products traded that date.
```

## 2. The operational definition (reports/stage_e16_briefs/lead_spec.md lines 122-129, verbatim)

```
H1 (settlement-window momentum, pooled; intraday). Product p, trade date d (eligible; S_p's
lead_grade "secondary" or better on d; S_p - 30 > O_p). Signal s = sign(close of bar(p,d,S_p-31) -
PS(p,d-1)). s = 0: no trade (counted). Entry: open of bar(p,d,S_p-30), direction s. Exit: open of
bar(p,d,S_p). Required bars: bar(p,d-1,S_p-1), bar(p,d,S_p-31), bar(p,d,S_p-30), bar(p,d,S_p). Unit:
the date d; value: the equal-weight mean, over products traded on d, of their risk-unit net P&L.
[LEAD] If S_p > 15:08 CT on some product-date, the trade still follows S_p (the hypothesis is about
the settlement window); the count of such product-dates is reported and the lead rules on it at the
freeze once Task 1's table exists.
```

## 3. Fixed parameters of this test

- Products and vehicles: the 27 price paths (24 from 2010-07-01; RTY from listing 2017-07-10; TN from listing 2016-01-11; HE from 2017-07-03); vehicles per E.12/D2.
- Venue: intraday; Topstep and IBKR.
- Unit of the test statistic: trade date (pooled equal-risk mean over products traded).
- Cost cases: base (frozen D8, size one; decides the pass, U3a); stress (base plus one tick per side; reported;
  must-survive at any later holdout-2 registration, U3a); 1.5 x slippage (reported).
- One-sided p: the larger of the plain-t p (Student t, n - 1 df) and the Newey-West p with 5 lag(s).
- Year stability: net P&L positive in at least two thirds of the calendar years holding at least
  10 units; fewer than 3 such years fails.
- Pass: Holm rejection at family-wise 0.05 across the registered tests, net mean > 0, n >= 30, year stability.
- Reported beside it: DSR at the program's N at run time, the stress and 1.5 x cases, exclusions by reason,
  per-product and per-year tables.
- Notes: Equity S_p was 15:15 CT before 2020-10-26 (R-S6; exits at the close of bar 15:14 by R-B1(a)); the result also shows the pooled statistics without product-dates with S_p > 15:08, marked descriptive (review F-14).

## 4. Relation to tested members (reports/stage_e16_overlap.md lines 113-126, verbatim; lead ruling: KEEP)

> H1 trades the same clock window as the program's CP1 port (entry at the open of the bar at S_p-30;
> CP1 exits one minute earlier, at the C-1 open, with C equal to D6's settlement minute) on 24 of
> H1's 27 markets, but with a different signal: the sign of the rest-of-day return from the prior
> date's settlement price to the close of bar S_p-31 (Baltussen, Da, Lammers and Martens), where CP1
> uses the overnight plus first-half-hour return (Gao, Han, Li and Zhou). The signals share their
> overnight component and are positively correlated. CP1 was Tier B on every cluster's research
> window (2025-04..2026-06; negative on rates, FX ex-6E, grains and livestock) and null on its only
> confirmation read (K4: NG 2019-05..2024-02, MCL 2021-07..2024-02). The rest-of-day form was never
> computed by the program; E.14's C2 drafted it on ES (T2 is H1's rule on ES) and stopped before any
> price was read. E.10 classed this form under the CP1 mechanism (X1) for K9; E.16 tests it as a
> separate signal and counts it in N. Gate 0 (2019-05..2024-02) tested CP1's signal and the
> since-the-open return (g04) as pooled features against intraday horizons that contain this window;
> neither was rejected.


## 5. Power at the priors (reports/stage_e16_power.json; method in the common file)

| Window | Prior | Net Sharpe (annual) | Units (calendar-only) | Qualifying years | P(pass all bars), Holm step 0.01 | at 0.05 | Analytic one-sided t power, 0.01 | at 0.05 |
|---|---|---|---|---|---|---|---|---|
| full | low | 0.3 | 3385 | 15 | 0.110 | 0.247 | 0.111 | 0.295 |
| full | high | 0.8 | 3385 | 15 | 0.707 | 0.853 | 0.733 | 0.904 |
| fallback | low | 0.3 | 1193 | 6 | 0.037 | 0.146 | 0.047 | 0.160 |
| fallback | high | 0.8 | 1193 | 6 | 0.265 | 0.521 | 0.278 | 0.537 |
