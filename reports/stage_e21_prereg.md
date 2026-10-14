# Stage E.21 pre-registration: E21-T1..T4 (multi-day round)

Status: FROZEN (lead, drafted 2026-10-14 03:19-03:20 PDT, amended 03:35-04:10 PDT). Frozen at the "E.21 freeze" commit, before
registration and before any bar is read. Written by the lead; no part is chosen from data.

## 1. What is registered
Four tests, registry label E21, ids E21-T1, E21-T2, E21-T3, E21-T4; N 528 -> 532 (F7). Each is
evaluated once, behind reports/stage_e21_RUN_ONCE.json, under the freeze manifest
reports/stage_e21_freeze.json and harness v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32.

| Id | Rule (F4) | Primary source | Universe | Hold |
|---|---|---|---|---|
| E21-T1 | TSMOM-12: sign of the past 12-month chained return x 0.40 / sigma | Moskowitz, Ooi and Pedersen (JFE 2012) | 17 roots | one month, month-end rebalance |
| E21-T2 | Trend blend: mean of the signs of the 1-, 3- and 12-month returns x 0.40 / sigma | Hurst, Ooi and Pedersen (2017) | 17 roots | one month, month-end rebalance |
| E21-T3 | Equity turn of the month: long from the settlement of day -2 to the settlement of day +3 | Lakonishok and Smidt (1988); McConnell and Xu (2008) | NQ, RTY | days -1, +1, +2, +3 |
| E21-T4 | Equal-risk combination of T2, T3 and H2 (E.16, frozen; E.17's series) | program (H5's method) | T2, T3, H2 | daily |

Code-level definitions: reports/stage_e21_briefs/lead_spec.md (frozen with this file), including its
section A (the Step 1 literature amendments). Where this file and the lead spec differ, the lead spec
governs; where either differs from docs/prompts/STAGE_E.21.md FIXED DESIGN, the prompt governs.

## 2. Hypotheses and the bar (F6)
For each test, H0: the mean daily net value (base case, D8 costs) is <= 0; H1: it is > 0. Statistic:
the test's daily net series in capital units, zero on flat days; t = mean / (sd / sqrt n); one-sided
p = max(plain-t p with n - 1 df, Newey-West p, normal) with Bartlett lags 21 (T1, T2, T4) and 5 (T3).
Holm step-down over the four tests at family alpha 0.025. PASS iff Holm rejects AND the annualized net
Sharpe (mean / sd x sqrt 252) >= 0.3. Anything else is FAIL. STOPPED only if the run stops on a code
invariant after its marker (exit 1); the attempt is then closed and not rerun.
Reported beside every verdict, never part of it: the 95% circular block-bootstrap interval of the
annualized Sharpe (block 21, 10,000 draws, seed 20261014), the stress cases (1.5 x slippage, the
prompt's stress case; D8 + 1 tick per side), per year, per root, costs as a share of gross, fills by
kind, exclusions by reason, DSR at N 532 (descriptive), and the published post-2010 figures.

Units (FR-5): the series are in capital units (fraction of capital) at the 0.40/sigma per-root target;
t, both p values, Holm, the annualized Sharpe and its interval are invariant to the unit and to any
constant position scale (costs scale with gross), so "risk units" and "capital units" give the same
verdict.
Data presence (FR-3): a missing settlement or signal bar at a later date moves a rebalance earlier or
excludes a T3 unit (lead_spec sections 3 and 5). This depends on bar existence, never on prices; the run
reports, per test, the rebalances moved and the units excluded for a missing bar, separately from the
calendar reasons, as a diagnostic.
Pinned beyond the code (FR-7): the freeze also pins multiday/README.md and screening/trial_registry.py;
harness v12 (registered with the tests) covers the rest of screening/.

## 3. Power (analytic, t ~ Sharpe x sqrt(years); for the record)
| True annual Sharpe | T1/T2/T4 (~12.6 y): E[t] | P(pass Holm step 1, z 2.50) | P(pass at step 4, z 1.96) | T3 (~13.4 y): E[t] |
|---|---|---|---|---|
| 0.24 (SG Trend 2010-2025, E.13) | 0.85 | 0.05 | 0.13 | 0.88 |
| 0.30 | 1.06 | 0.08 | 0.19 | 1.10 |
| 0.50 | 1.77 | 0.24 | 0.43 | 1.83 |
| 0.70 | 2.48 | 0.50 | 0.70 | 2.56 |
| 1.00 | 3.55 | 0.85 | 0.94 | 3.66 |
A PASS needs a realized Sharpe near 0.70 for the smallest p (Holm step 1) and near 0.55 at step 4.
A FAIL whose interval contains positive values is read as underpowered, not refuted (prompt F6).

## 4. Fixed before any bar is read
Everything in reports/stage_e21_briefs/lead_spec.md: inputs and windows (section 0), marks and returns
(1), the EWMA volatility (2), rebalance and reference dates (3), signals, weights and the calendar-
defined divisor (4), the turn-of-month days (5), the combination (6), the store boundary, rolls, costs,
fill guard and limit-lock diagnostic (7), series dates (8), statistics (9), the economics inputs (10)
and the run discipline (11). No lookback, volatility setting, rebalance day, window, cost, lag, alpha,
bar or seed changes after any bar is read. No test is added or run twice.

## 5. Calendar-only counts (no bar row read; reports/stage_e21_briefs/calendar_counts.md, after Q1, Q2, A12)
Calendars, the settlement table, windows, release rules and store roll METADATA only (preflight); a
required bar is assumed present, so the run adds "missing bar" exclusions.
- T1/T2 rebalance dates: every root-month of the 17 roots has an eligible date except ZC 2011-06 and
  2022-06 and ZL 2013-06 and 2018-06 (all six last dates in a roll blackout); about 446 rebalances move
  earlier by 1-5 trade dates (mostly Treasury, GC and ZN month-end roll blackouts).
- S_M (calendar-defined): 13 from 2011-07, 14 from 2015-12 (LE), 15 from 2017-01 (TN), 17 from 2018-07
  (RTY, HE).
- T3: NQ 154 of 164 months tradeable (entry early halt 2, exit early halt 3, sigma warm-up 3, store
  boundary 1, window end 1); RTY 73 of 80 (1, 1, 3, 1, 1). S_u is 1 in 81 months and 2 in 73.

## 6. Literature check (Step 1; rulings A1-A11 in lead_spec section A, 03:35 PDT, before any bar)
| Item | Primary source | Result | Freeze text |
|---|---|---|---|
| T1 signal, hold, sizing, average | MOP 2012 pp.231-236 | MATCH | as F4 |
| T1/T2 lookback across rolls | MOP p.231 (compound the held contract's daily returns) | MATCH (h2.chained_return splits at every recorded splice) | lead_spec 1 |
| Volatility: 261, EWMA-mean demeaning, strictly before d | MOP eq. 1, p.233 | prompt SILENT; paper adopted | lead_spec 2 |
| Warm-up, floor, cap | MOP: none | SILENT; 60 returns [LEAD]; no floor, no cap | lead_spec 2, A3, A4 |
| T2 lookbacks 1/3/12, equal weights, monthly | HOP 2017 p.3 | MATCH | as F4 |
| T2 book scaled to 10% ex-ante (3-year covariance) | HOP 2017 p.3, endnote 7 | MISMATCH, NOT adopted: declared deviation (A6) | T2 as F4 |
| T3 window days -1, +1, +2, +3 | McConnell and Xu (WP Table 1); Lakonishok and Smidt via MX | MATCH | entry at day -2 = the month's second-to-last trade date |
| T3 parenthetical "(two trade dates before the month's last)" | as above | MISMATCH (describes day -3): corrected (A8) | lead_spec 5 |
| T3 volatility scaling | papers: none | the prompt's choice, kept | lead_spec 5 |
| T3 day numbering on NYSE trading days | papers count NYSE trading days; the equity futures calendar books US holidays as early-halt trade dates | MISMATCH found in the calendar-only counts, fixed (A12, 03:48 PDT) | lead_spec 5 and A12 |

## 7. Descriptive economics (F8; not part of the verdict)
Computed after the verdict from the run's per-root files (no bar) and reports/stage_e21_proped_rules.json:
personal-account capital at integer micro contracts (15% and 25% annual volatility), and for each PropEd
plan allowing overnight holds and automation, the book's daily and 5-day dollar sigma at its smallest
integer size against the plan's drawdown and daily loss limit, and the share of 21-day windows whose worst
drawdown would breach it, with and without weekend holds; Phidias Premium 50K beside it. No fee or
payout model.
