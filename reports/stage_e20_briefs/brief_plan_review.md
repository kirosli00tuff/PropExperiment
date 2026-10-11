# Brief: PlanReviewer-FableXHigh (Stage E.20 Step 5, independent review of the Part C plan)

One objective: an independent, adversarial review of reports/stage_e20_plan.md before the build,
the 45 registrations and any fit. Check it against docs/prompts/STAGE_E.20.md (F1, F2, F3, F6, F7,
F8, F9, SCOPE) and docs/STAGE_E_ML_V2_DESIGN.md V2.2-V2.9 (frozen), using the read-only code maps
reports/stage_e20_briefs/codemap_*.md and the frozen code itself (ml_route_v2/, read by section).

Check, at least:
1. Leakage paths: the normalization (rolling per vehicle, t4 rows pooled), the risk table per outer
   split and inner fold, purge and embargo, the admissibility filter (one pass on the whole window,
   volatility only), the two r_ROD features (plan 5.2: their prices, the prior close, the 60-date
   same-t_index median, availability at or before t), the composition path (pattern_search builds
   rows, panel and targets outside the frozen run_pipeline: does anything bypass a frozen check that
   run_pipeline would have applied?), and the t4 rows (targets, h120 exclusion, h60 = hF exits).
2. The feature cut (plan 5.1; reports/stage_e20_product_summary.md section 1.3, matrix in section 2):
   is each KEPT feature computable over both windows under F6's rule as written, and is each DROPPED
   feature's reason right? Is the "partial row loss" class (cp1 on rates before 2011-10, grains before
   2012-05, k2_fomc_mto's 13:00 filter) consistent with F6's "no feature may be not-applicable by
   design in the backward window"? Is dropping g13-g15 and k9_anncday right?
3. Part A features: none accepted; check each rejection (product summary 1.4) against the plan's
   acceptance rule 5.3 and V31, and the r_ROD features' causality.
4. The guard's coverage (plan 3): every path class, the date bound, MES, the research stores, the
   B1-only exception and its two conditions.
5. The screen and the backward bar are exactly F7 and F8: the record (path_daily with zeros), the
   median-path t, PBO < 0.5, the Sharpe band [0.5, 4.0] with the leakage-alarm hold, the DSR as
   reported only, ruin as reported only (and the plan's choice to compute it only after a passed
   screen), the B1 statistic (daily net P&L with zeros, its t, one-sided p with n_dates - 1 degrees
   of freedom, Sharpe, at least 100 round trips) and its use of the fixed-D score_split construction
   as "V2.7 and V2.8 as frozen".
6. The lead's other choices: E.12's recorded S_X instead of rerunning the D4 rule (ZF 2020-10-01,
   ZT 2021-10-01; F2's window); MES never loaded; the entries cap with four decision times; the
   45 configurations and their ids; N accounting (483 -> 528 -> 529) and N_total for the DSR; the
   empty-admissible refusal; the new state and reports directories; no v2 amendment.
7. Anything in the plan that adds a configuration, horizon, feature, model or test beyond F5 and F6,
   or changes a file the harness v12, the v2 freeze, or the E.14, E.16 or E.18 freezes hash.

## Output

reports/stage_e20_review_plan.md: a verdict (APPROVE, APPROVE WITH FIXES, or BLOCK), then findings,
each with an id (PR-n), severity (BLOCKING, SHOULD FIX, NOTE), the plan section, what is wrong, why
it matters, and the recommended fix. BLOCKING: a leakage path, a scope breach, or a screen or bar
that differs from F7 or F8. Reply to the lead: the path, a summary of at most 200 words, and
anything you could not check.

## Boundaries

No data store, no results of E.12 Gate 0, E.15, E.17 or E.18, no H6 result. Do not edit the plan,
code or any frozen file; report only. No ledger writes, no commits. Do not spawn agents.
