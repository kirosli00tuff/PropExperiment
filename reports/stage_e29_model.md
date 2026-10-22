# Stage E.29: basket model declaration (written before any run)

Written by the lead (Opus 5.5, effort high, Pro plan) on 2026-10-21 at about 19:40 PDT, before any E.29 code or
computation. Its sha256 is logged in reports/stage_e29_STATE.md. Nothing in this file changes after the hash. If a
reviewer's BLOCKING finding forces a change, a new version is written beside it with its own hash and the diff is
shown in the return.

What the lead had read before writing it: the stage prompt (docs/prompts/STAGE_E.29.md), CLAUDE.md,
reports/stage_e28_ranking_spec.md sections 0, 1 and 3, reports/stage_e28_briefs/A3_econ.md sections 1 to 4 (the
model, the five 50K plans and their mappings), and these fields of A3_econ.json and A3_firm_products.json for QM, ZM,
MGC and MNQ at the five firms: listing, tick value v, sigma_T, c_lim, F_rt, flags, mu*_lim, mu*_mkt, cost per
attempt, position limits, product caps and restriction text. No E.29 result exists yet.

## 1. What is reused unchanged

E.28's economic model (reports/stage_e28_ranking_spec.md section 3) as implemented by E.28's EconCoder in
reports/stage_e28_briefs/work/A3_econ/ (A3_funnel.py, A3_models.py, A3_inputs.py and what they import from
prop_econ/): the five firms' 50K plans and every rule mapping in A3_econ.md sections 3 and 4, the funnel (evaluation
attempts, activation, one funded account, cycles), the fee and API conventions, the intraday Brownian-bridge minimum
(and maximum where a rule trails the intraday high), the 756-day horizon, 20,000 paths, the common random numbers
(seed 20261021, derive_seed tags "e28a3"), the 0.01 grid, the bisection plus grid confirmation of A3_econ.md section
2.4, the mu10K campaign of section 2.5 and the cost-per-attempt definition. E.28's files are imported read-only and
their sha256 values are recorded. prop_econ/ is not edited.

## 2. Baskets and the trade split (fixed by the prompt)

| basket | members, in this order | trades per day T_i (total 20) |
|---|---|---|
| B0 | QM | 20 |
| B1 | QM, ZM | 10, 10 |
| B2 | QM, MGC | 10, 10 |
| B3 | QM, ZM, MGC | 7, 7, 6 |
| B4 | QM, MNQ | 10, 10 |

Rounding rule: T_i = floor(20 / n), and the remainder goes one trade each to the members in basket order (B3: 6 + 1
for QM and ZM). Every member trades 1 contract per round trip.

Listing gate: QM, ZM, MGC and MNQ are listed at the 50K plan of all five firms (A3_firm_products.json listed_50k
"yes" for all 20 pairs), so every basket runs at every firm.

## 3. The combined account

For member i at firm f: tick value v_i, sigma_i = E.28's sigma_T (sigma_1m in ticks, with E.28's OC-1 siblings),
limit-case cost c_i = E.28's c_lim (F_rt / v_i), market-case cost c_i + S_rt,i with E.28's S_rt (1 tick for all four).
Gross P&L per trade in ticks is normal(mu_i, sigma_i^2), trades independent within a member, as in E.28.

Member daily P&L in USD: mean m_i = T_i (mu_i - c_i) v_i, SD s_i = sqrt(T_i) sigma_i v_i.
Pairwise correlation of members' daily P&L: rho, the same for every pair, on the grid {0, 0.25, 0.5, 0.75}.
The account's daily P&L is the sum: normal with mean M = sum_i m_i and SD S = sqrt(sum_i s_i^2 + 2 rho sum_{i<j}
s_i s_j). Within the day the members' cumulative P&L paths are Brownian motions with instantaneous correlation rho,
so the combined path is a Brownian motion with the same drift and variance per day, and E.28's bridge formulas for
the intraday minimum (and maximum) apply to the combined path with (M, S). This is a modelling choice (members trade
at times spread over the same session; ZM's shorter grain session is not modelled separately) and is logged as such.

Consequently every firm rule E.28 mapped (daily loss limit, trailing drawdown, its intraday or EOD test, target,
consistency, payout rules, minimum days, caps, buffers, splits, fees, API) acts on the combined daily P&L exactly as
on a single contract with daily mean M and SD S. The simulation uses E.28's standard draws unchanged: the combined
close is M + S z with E.28's z, so B0 reproduces E.28's QM numbers draw for draw, and all baskets, rho values and
edges share common random numbers.

## 4. Position limits, scaling and the news window (applied to the combined account)

Contract units: each firm's stated micro-to-mini ratio (10:1 at all five, A3_firm_products.json). QM, ZM count 1
lot each; MGC and MNQ count 0.1. A basket's largest possible open exposure is one contract per member at once:
B0 1, B1 2, B2 1.1, B3 2.1, B4 1.1 lots.

- Firm caps (Topstep Combine 5, Lucid 4, Tradeify 4, MFFU 4, Bulenox 7 lots; product caps Topstep QM 3, MGC 30;
  MFFU metals micros 5): no basket can exceed them. Logged as checked, non-binding.
- Topstep XFA scaling (2 / 3 / 5 lots by balance, E.19's tier_cap_vec): B3 (2.1 lots) exceeds the 2-lot first tier.
  Primary form: the strategy never opens a trade that would take open exposure above the current cap (it delays or
  skips the third concurrent position). Under this model (about one-minute holds, at most 7 trades per member a
  day) that changes no day's P&L distribution, so the primary numbers are unchanged; the share of Topstep B3 funded
  days spent at the 2-lot tier is reported. Sensitivity (conservative form, reported beside the primary): on every
  Topstep funded day at the 2-lot tier, B3 trades without MGC (QM 7 and ZM 7 trades; T falls to 14 that day), and
  the thresholds are recomputed. Every other basket fits every tier.
- Topstep Tier 1 news window (no new opens 5 minutes either side of CPI, FOMC, NFP, PPI on full-size equity index
  products; micros capped at 3 in the window; MGC under the same window as full-size metals; QM not affected):
  every basket trades 1 contract per member, under the 3-contract micro cap, and the strategy schedules no opens in
  the 10-minute windows. Applied as a scheduling constraint; non-binding on the P&L distribution; logged.
- Session and flat-by rules, inactivity and per-firm items marked "ignored" in A3_econ.md section 3 stay ignored for
  the reasons given there (one-minute holds, trades every day).

## 5. Edge settings

(i) Equal edge in break-even units. Every member at mu_i = k mu*_lim,i(f), where mu*_lim,i(f) is E.28's break-even
    of member i alone at firm f (A3_econ.json). k runs on the grid 0.00 to 4.00 in steps of 0.01. A member whose
    E.28 mu*_lim is "> 4" (MGC at Topstep, Tradeify, Bulenox; MNQ at MFFU, Bulenox) has its alone break-even
    computed here with E.28's model and search on an extended grid 0 to 12 ticks (the only E.29 run that extends
    E.28's grid; flagged). If it is still above 12 ticks, setting (i) is not run for baskets containing it at that
    firm ("n/a").
(ii) QM edge only. QM at mu_QM on the 0.01-tick grid 0 to 4; every other member at mu_i = 0 (it pays its costs and
    adds variance). B0 under (ii) is E.28's QM pair exactly.

## 6. Quantities reported per cell (cell = firm x basket x rho x edge setting)

- Break-even: setting (i) k* = the smallest grid k with EV >= 0; setting (ii) mu*_QM = the smallest grid mu_QM with
  EV >= 0. EV = mean net cash per cycle (withdrawals minus all fees, API included), limit case, as E.28.
- mu10K analogue: the smallest grid k (setting i) or mu_QM (setting ii) with P(net cash >= USD 10,000 within 250
  trading days) >= 0.5, limit case.
- Cost per attempt (expected evaluation-stage fees per attempt) at zero edge (all mu = 0; the same for both
  settings).
- At fixed reporting points, limit case: per-attempt pass rate (passes / attempts), P(at least one payout in a
  cycle), and EV per cycle. Reporting points: setting (i) k = 1.0, 1.5, 2.0; setting (ii) mu_QM = B0's E.28
  mu*_lim at that firm, 0.50 and 1.00 ticks.
- The account's daily SD S in USD at each rho, and S / MLL (analytic).
- Search and confirmation as E.28 section 2.4 (bisection, then the grid confirmation); "> 4" when the grid end fails.
- Market case (c_i + S_rt,i): for B0 and for the best basket at each firm only. In setting (i) market case, k is in
  units of each member's mu*_mkt (extended as in section 5 when "> 4"). Best basket at a firm, fixed now: the non-B0
  basket with the lowest setting-(i) limit-case k* at rho = 0.5; ties broken by lower setting-(ii) mu*_QM at rho
  = 0.5, then basket order.

## 7. Comparison with B0 and the answers

Each table shows the cell against B0 at the same firm and edge setting: k* / k*(B0) - 1 in setting (i) and
mu*_QM - mu*_QM(B0) in setting (ii), and the same for the mu10K analogue. A basket "beats QM alone" at a firm and
rho when its break-even is lower than B0's by more than the grid step (0.01) and its mu10K analogue is not higher.
The benefit "vanishes" at the smallest rho on the grid at which it no longer beats B0 (linear interpolation between
grid rho values for the stated crossing, marked as interpolated).

## 8. Measured correlations (reference only, never an input)

From owned one-minute bars only, all dated before 2024-03-01: the front contract (E.28's standard window
2022-11-01 to 2023-10-31, which also keeps the E.28 pilot window untouched) of CL, ZM (or the owned soybean-complex
sibling if ZM is not owned, named), GC and NQ. Daily close-to-close return correlations and daily high-low range
(in percent of price) correlations over common trade dates, pairwise, with the number of days. Roll days dropped.
The holdout status is checked before and after the read. No holdout, embargo, research-window or MES-sealed file is
read. These are price correlations; the model's rho is the correlation of a strategy's daily P&L, which for
direction-neutral short-hold trading can sit well below the price correlation. The return places the measured
values on the rho grid with that caveat.

## 9. Not done here

No outcome data, no purchase, no registration, N stays 538. Edges are assumed on a grid, never measured.
