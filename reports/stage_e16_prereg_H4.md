# Stage E.16 pre-registration H4: next-day reversal of the settlement-window move

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json; commit "E.16 base-rule freeze"). NOT
REGISTERED: Stage E.17 registers H1 to H5 together (N + 5) and runs this test once, in the order of
reports/stage_e16_handoff.md. Every definition shared by the five tests (prices and clock, costs, exclusions,
windows, the 2010-2024 splice and fallback rules, risk scaling, statistics, the pass bar, run discipline, the user
rulings U1 to U3b of 2026-10-09 and the lead's rulings) is in reports/stage_e16_prereg_common.md, which is part of
this pre-registration. Nothing here may be loosened; the code is base_rules/ as hashed in the freeze manifest.

## 1. The hypothesis as the stage prompt fixes it (docs/prompts/STAGE_E.16.md lines 111-117, verbatim)

```
H4, next-day reversal of the settlement-window move. For each product p
and eligible date d whose prior eligible date had an H1 window move m (the
gross move from S_p - 30 to S_p on that date): trade opposite to sign(m),
entering at the open of the bar at the day-session open O_p + 1 minute on
d, exiting at the open of the bar at S_p - 31 on d (so H4 never overlaps
H1's window). Intraday: both venues. Test statistic: the daily pooled net
P&L, as H1.
```

## 2. The operational definition (reports/stage_e16_briefs/lead_spec.md lines 154-158, verbatim)

```
H4 (next-day reversal; intraday; both venues). Product p, trade date d (eligible). m = open of
bar(p,d-1,S_p) - open of bar(p,d-1,S_p-30) (H1's gross window move on d-1, d-1 per section 2).
m = 0: no trade. Direction -sign(m). Entry: open of bar(p,d,O_p+1); exit: open of
bar(p,d,S_p-31). Required: bar(p,d-1,S_p-30), bar(p,d-1,S_p), bar(p,d,O_p+1), bar(p,d,S_p-31). Unit
and value as H1.
```

## 3. Fixed parameters of this test

- Products and vehicles: as H1.
- Venue: intraday; Topstep and IBKR.
- Unit of the test statistic: trade date (pooled, as H1).
- Cost cases: base (frozen D8, size one; decides the pass, U3a); stress (base plus one tick per side; reported;
  must-survive at any later holdout-2 registration, U3a); 1.5 x slippage (reported).
- One-sided p: the larger of the plain-t p (Student t, n - 1 df) and the Newey-West p with 5 lag(s).
- Year stability: net P&L positive in at least two thirds of the calendar years holding at least
  10 units; fewer than 3 such years fails.
- Pass: Holm rejection at family-wise 0.05 across the registered tests, net mean > 0, n >= 30, year stability.
- Reported beside it: DSR at the program's N at run time, the stress and 1.5 x cases, exclusions by reason,
  per-product and per-year tables.
- Notes: LE/HE entries at 08:01 in 2014-10-27..2016-02-28 pay the largest per-side slippage (R-B2); the result also shows the pooled statistics without those 'uncalibrated bucket' units, marked descriptive (review F-13).

## 4. Relation to tested members (reports/stage_e16_overlap.md lines 240-251, verbatim; lead ruling: KEEP)

> H4 enters at the same fill as the program's CP3 port (the open of the bar after the day-session
> open) on the same markets, and exits 30 minutes earlier (the S_p-31 open against CP3's C-1 open). Its
> signal differs: H4 trades against the sign of d-1's settlement-window move (S_p-30 to S_p, H1's
> window), every day the move is non-zero; CP3 trades with d-1's close location in its day range, only
> at CLV >= 0.8 or <= 0.2. The signals are negatively related. CP3 was Tier B on every cluster's research
> window and null on its K4 confirmation (NG 2019-05..2024-02, MCL 2021-07..2024-02). Before H4 was
> named, Gate 0 (2019-05..2024-02, all 27 products) showed reversal-leaning, unrejected pooled ICs for
> CP3's CLV (t -1.95 / -1.93 / -1.61) and the prior day's return (t -1.57 / -2.08 / -0.94), and K4-cp3-01
> NG's confirmation was negative; these are disclosed as seen results on the overlapping segment. The
> sign rests on Baltussen et al.'s "reverts over the next days" (logged at E.10 as K9O-018). No program
> member conditioned on the prior day's last-30-minute move.


## 5. Power at the priors (reports/stage_e16_power.json; method in the common file)

| Window | Prior | Net Sharpe (annual) | Units (calendar-only) | Qualifying years | P(pass all bars), Holm step 0.01 | at 0.05 | Analytic one-sided t power, 0.01 | at 0.05 |
|---|---|---|---|---|---|---|---|---|
| full | low | 0.2 | 3385 | 15 | 0.056 | 0.156 | 0.056 | 0.182 |
| full | high | 0.6 | 3385 | 15 | 0.432 | 0.640 | 0.454 | 0.715 |
| fallback | low | 0.2 | 1193 | 6 | 0.024 | 0.098 | 0.029 | 0.113 |
| fallback | high | 0.6 | 1193 | 6 | 0.141 | 0.354 | 0.153 | 0.367 |
