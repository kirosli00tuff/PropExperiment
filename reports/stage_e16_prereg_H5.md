# Stage E.16 pre-registration H5: equal-risk combination of H1 to H4

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json; commit "E.16 base-rule freeze"). NOT
REGISTERED: Stage E.17 registers H1 to H5 together (N + 5) and runs this test once, in the order of
reports/stage_e16_handoff.md. Every definition shared by the five tests (prices and clock, costs, exclusions,
windows, the 2010-2024 splice and fallback rules, risk scaling, statistics, the pass bar, run discipline, the user
rulings U1 to U3b of 2026-10-09 and the lead's rulings) is in reports/stage_e16_prereg_common.md, which is part of
this pre-registration. Nothing here may be loosened; the code is base_rules/ as hashed in the freeze manifest.

## 1. The hypothesis as the stage prompt fixes it (docs/prompts/STAGE_E.16.md lines 119-123, verbatim)

```
H5, the combination. The equal-risk daily combination of H1 to H4's net
daily P&L series (H2 and H3 marked to settlement daily while open, from
the same bars), each series scaled by its own trailing 60-date standard
deviation, computed strictly before the date. Test statistic: the daily
combined net P&L.
```

## 2. The operational definition (reports/stage_e16_briefs/lead_spec.md lines 160-169, verbatim)

```
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
```

## 3. Fixed parameters of this test

- Products and vehicles: those of H1 to H4.
- Venue: mixed (H2 and H3 are IBKR only).
- Unit of the test statistic: grid date (lead_spec section 4, H5).
- Cost cases: base (frozen D8, size one; decides the pass, U3a); stress (base plus one tick per side; reported;
  must-survive at any later holdout-2 registration, U3a); 1.5 x slippage (reported).
- One-sided p: the larger of the plain-t p (Student t, n - 1 df) and the Newey-West p with 5 lag(s).
- Year stability: net P&L positive in at least two thirds of the calendar years holding at least
  10 units; fewer than 3 such years fails.
- Pass: Holm rejection at family-wise 0.05 across the registered tests, net mean > 0, n >= 30, year stability.
- Reported beside it: DSR at the program's N at run time, the stress and 1.5 x cases, exclusions by reason,
  per-product and per-year tables.
- Notes: none beyond the common file.

## 4. Relation to tested members (reports/stage_e16_overlap.md lines 266-272, verbatim; lead ruling: KEEP)

> H5 combines the daily net P&L series of H1 to H4 at equal trailing-60-date risk; it inherits each
> component's relations (sections of H1 to H4). No program member combined base-rule P&L series. The
> nearest computation is Gate 0's family B (E.12, 2019-05..2024-02), a ridge combination of 64
> intraday features per product-horizon (including the CP1, CP3, prior-day-return, month-end and
> auction features), which failed with no pair rejected; ML route v2's portfolio and ML route v1 were
> never run.


## 5. Power at the priors (reports/stage_e16_power.json; method in the common file)

| Window | Prior | Net Sharpe (annual) | Units (calendar-only) | Qualifying years | P(pass all bars), Holm step 0.01 | at 0.05 | Analytic one-sided t power, 0.01 | at 0.05 |
|---|---|---|---|---|---|---|---|---|
| full | low | 0.8 | 3370 | 15 | 0.703 | 0.841 | 0.727 | 0.901 |
| full | high | 1.5 | 3370 | 15 | 0.999 | 1.000 | 0.999 | 1.000 |
| fallback | low | 0.8 | 1154 | 6 | 0.250 | 0.503 | 0.268 | 0.526 |
| fallback | high | 1.5 | 1154 | 6 | 0.802 | 0.930 | 0.810 | 0.941 |
